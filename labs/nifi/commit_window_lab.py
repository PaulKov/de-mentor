"""Crash NiFi at the call site before commitSync and identify both copies in its queue."""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from uuid import uuid4

from bootstrap import NiFi
from points_lab import BROKER, HERE, command, exclusive_worker, kafka, positions, wait

COMPOSE = ["docker", "compose", "-f", "compose.yaml", "-f", "compose.window.yaml"]
NODE = "nifi-window"
WEB = "https://127.0.0.1:28445"
BREAKPOINT = "org.apache.nifi.kafka.service.consumer.Kafka3ConsumerService:157"


def inside(*args):
    return command(*COMPOSE, "exec", "-T", NODE, *args)


def ready():
    try:
        return NiFi(WEB)
    except (OSError, RuntimeError):
        return None


@contextmanager
def debugger():
    # Only the event thread stops. NiFi's API and queue listing stay available.
    with TemporaryDirectory() as scratch:
        path = Path(scratch) / "jdb.log"
        with path.open("wb") as log, subprocess.Popen(
            [*COMPOSE, "exec", "-T", NODE, "jdb", "-attach", "127.0.0.1:8000"],
            cwd=HERE, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT, text=True,
        ) as proc:
            def send(line):
                proc.stdin.write(line + "\n")
                proc.stdin.flush()

            def output():
                return path.read_text(encoding="utf-8", errors="replace")

            try:
                wait(lambda: "Initializing jdb" in output(), "local JDK debugger", 25)
                send("stop thread at " + BREAKPOINT)
                wait(lambda: ("Set breakpoint" in output() or "Deferring breakpoint" in output()),
                     "commitSync breakpoint installed", 25)
                yield output
            finally:
                proc.stdin.close()
                try:
                    proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    proc.terminate()


def install(api, topic, group_id):
    root = api.request("GET", "/flow/process-groups/root")["processGroupFlow"]
    group = api.request("POST", f"/process-groups/{root['id']}/process-groups", {
        "revision": api.revision(), "component": {"name": f"Before commitSync · {group_id}",
        "position": {"x": 100, "y": 100 + 170 * len(root["flow"]["processGroups"])}}})["id"]
    service = api.controller(group, "org.apache.nifi.kafka.service.Kafka3ConnectionService",
                             "Kafka", {"bootstrap.servers": BROKER, "security.protocol": "PLAINTEXT"})
    source = api.processor(group, "org.apache.nifi.kafka.processors.ConsumeKafka", "Read one event", 0, 0, {
        "Kafka Connection Service": service, "Topics": topic, "Group ID": group_id,
        "Commit Offsets": "true", "auto.offset.reset": "earliest"})
    hold = api.processor(group, "org.apache.nifi.processors.attributes.UpdateAttribute",
                         "Inspect queue (keep stopped)", 390, 0, {}, ["success"])
    api.connect(group, source, hold, "success")
    flow = api.request("GET", f"/flow/process-groups/{group}")["processGroupFlow"]["flow"]
    return group, service, source, flow["connections"][0]["id"]


def queue(api, connection):
    path = f"/flowfile-queues/{connection}"
    listing = api.request("POST", path + "/listing-requests")["listingRequest"]
    request_path = path + "/listing-requests/" + listing["id"]

    def finished():
        status = api.request("GET", request_path)["listingRequest"]
        if status.get("failureReason"):
            raise RuntimeError(status["failureReason"])
        return status if status["finished"] else None

    try:
        result = []
        for item in api.wait(finished, "queue listing").get("flowFileSummaries", []):
            file_path = path + "/flowfiles/" + item["uuid"]
            attrs = api.request("GET", file_path)["flowFile"]["attributes"]
            payload = api.request("GET", file_path + "/content")
            if isinstance(payload, str):
                payload = json.loads(payload)
            result.append({"uuid": item["uuid"], "topic": attrs["kafka.topic"],
                           "partition": int(attrs["kafka.partition"]), "offset": int(attrs["kafka.offset"]),
                           "event_id": payload["event_id"]})
        return sorted(result, key=lambda item: item["uuid"])
    finally:
        api.request("DELETE", request_path)


def run(report):
    command(*COMPOSE, "up", "-d", "--wait", "--wait-timeout", "240", NODE, timeout=300)
    api = wait(ready, "NiFi API", 180)
    root = api.request("GET", "/flow/process-groups/root")["processGroupFlow"]["id"]
    running = api.request("GET", f"/process-groups/{root}")["runningCount"]
    if running:
        raise RuntimeError("Another flow is running on the dedicated crash node")
    # Set the two startup properties on this node only. Remove the debugger option from disk
    # as soon as the JVM is up, so recovery uses an ordinary JVM with no debugger listener.
    inside("sed", "-i", "s/^nifi.flowcontroller.autoResumeState=true$/nifi.flowcontroller.autoResumeState=false/",
           "conf/nifi.properties")
    inside("grep", "-qx", "nifi.flowcontroller.autoResumeState=false", "conf/nifi.properties")
    debug_option = "java.arg.windowdebug=-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=127.0.0.1:8000"
    inside("sh", "-ec", "sed -i '/^java.arg.windowdebug=/d' conf/bootstrap.conf; echo \"$1\" >> conf/bootstrap.conf",
           "sh", debug_option)
    command(*COMPOSE, "restart", NODE)
    api = wait(ready, "isolated node ready for debugging", 210)
    inside("sed", "-i", "/^java.arg.windowdebug=/d", "conf/bootstrap.conf")
    event_id = str(uuid4())
    topic, group_id = "window.in." + event_id[:12], "window-" + event_id[:12]
    group, service, source, connection = install(api, topic, group_id)
    ui = f"{WEB}/nifi/#/process-groups/{group}"
    print(f"{ui}\ntopic={topic} group={group_id} event={event_id}", flush=True)
    kafka("topics", "--create", "--topic", topic, "--partitions", "1", "--replication-factor", "1")
    kafka("consumer-groups", "--group", group_id, "--topic", topic + ":0",
          "--reset-offsets", "--to-offset", "0", "--execute")
    if positions(topic, group_id) != [0, 0, 0]:
        raise RuntimeError("Initial group position must be zero on the empty topic")
    kafka("console-producer", "--topic", topic, data=json.dumps({"event_id": event_id}) + "\n")
    stages = []

    def observe(label, expected, files):
        offsets = positions(topic, group_id)
        if offsets != expected:
            raise RuntimeError(f"{label}: expected {expected}, observed {offsets}")
        if files is not None and any(
            (f["event_id"], f["topic"], f["partition"], f["offset"]) != (event_id, topic, 0, 0) for f in files
        ):
            raise RuntimeError(f"Unexpected input in {files}")
        stages.append({"stage": label, "current": offsets[0], "end": offsets[1], "lag": offsets[2], "queue": files})
        print(f"{label}: {offsets}, UUIDs={None if files is None else [f['uuid'] for f in files]}", flush=True)

    cid = command(*COMPOSE, "ps", "-q", NODE)
    down = False
    try:
        with debugger() as output:
            api.set_status(source, "RUNNING")
            wait(lambda: "Breakpoint hit:" in output(), "stop just before commitSync", 90)
            pid = next(line.split()[0] for line in inside("jcmd", "-l").splitlines()
                       if "org.apache.nifi.NiFi" in line)
            stack = inside("jcmd", pid, "Thread.print")
            frames = next((block for block in stack.split("\n\n")
                           if "Kafka3ConsumerService.commit(Kafka3ConsumerService.java:157)" in block), "")
            if "ConsumeKafka.commitOffsets" not in frames:
                raise RuntimeError(f"Unexpected suspended thread: {frames}\n{output()}")
            trace = [line.strip() for line in frames.splitlines() if any(name in line for name in (
                     "Kafka3ConsumerService.commit(", "ConsumeKafka.commitOffsets(", "ConsumeKafka.lambda$onTrigger",
                     "StandardProcessSession."))]
            first = queue(api, connection)
            if len(first) != 1:
                raise RuntimeError(f"Expected one queued FlowFile: {first}")
            observe("before_commitSync", [0, 1, 1], first)
            down = True
            command(*COMPOSE, "kill", "-s", "SIGKILL", NODE)
        code = command("docker", "inspect", "-f", "{{.State.ExitCode}}", cid)
        if code != "137":
            raise RuntimeError(f"Expected SIGKILL, observed {code}")
        observe("nifi_down", [0, 1, 1], None)
        command(*COMPOSE, "start", NODE)
        api = wait(ready, "NiFi after crash", 210)
        down = False
        if api.request("GET", f"/processors/{source}")["component"]["state"] != "STOPPED":
            raise RuntimeError("Expected manual resume on this test node")
        recovered = queue(api, connection)
        if recovered != first:
            raise RuntimeError(f"Expected original UUID before resuming: {recovered}")
        observe("recovered_source_stopped", [0, 1, 1], recovered)
        svc = api.request("GET", f"/controller-services/{service}")
        if svc["component"]["state"] != "ENABLED":
            api.request("PUT", f"/controller-services/{service}/run-status",
                        {"revision": api.revision(svc), "state": "ENABLED"})
            api.wait(lambda: api.request("GET", f"/controller-services/{service}")["component"]["state"] == "ENABLED",
                     "connection service enabled")
        api.set_status(source, "RUNNING")
        wait(lambda: positions(topic, group_id) == [1, 1, 0], "offset 1 after natural replay", 120)
        final = queue(api, connection)
        if len(final) != 2 or first[0] not in final or len({f["uuid"] for f in final}) != 2:
            raise RuntimeError(f"Expected original and reread: {final}")
        observe("after_kafka_reread", [1, 1, 0], final)
    finally:
        if down:
            command(*COMPOSE, "start", NODE)
            api = wait(ready, "restored crash-test node", 210)
        api.set_status(source, "STOPPED")
    proof = {"topic": topic, "group": group_id, "event_id": event_id, "ui": ui, "connection": connection,
             "exit_code": int(code), "stack_before_kill": trace, "stages": stages}
    if report:
        report.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print("PASS: same UUID after queue recovery, new UUID after Kafka replay.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    command(*COMPOSE, "up", "-d", "--wait", "kafka", "postgres", timeout=240)
    with exclusive_worker():
        run(args.report)
