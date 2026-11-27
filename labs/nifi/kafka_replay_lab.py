"""Measure Kafka output and the input group around a real crash of the isolated NiFi."""
import argparse
import json
from pathlib import Path
from uuid import uuid4

from points_lab import BROKER, COMPOSE, WEB, command, connect, exclusive_worker, kafka, positions, wait


def records(topic, with_headers):
    """Scan the whole single partition, including any unexpected extra application records."""
    args = ["--topic", topic, "--partition", "0", "--offset", "earliest",
            "--isolation-level", "read_committed", "--timeout-ms", "3500",
            "--command-property", "enable.auto.commit=false", "--formatter-property", "print.offset=true"]
    if with_headers:
        args.extend(["--formatter-property", "print.headers=true"])
    result = []
    for line in kafka("console-consumer", *args).splitlines():
        fields = line.split("\t")
        offset = fields[0].removeprefix("Offset:")
        record = {"offset": int(offset), "value": json.loads(fields[-1])}
        if with_headers:
            record["headers"] = dict(pair.split(":", 1) for pair in fields[1].split(","))
        result.append(record)
    return result


def install(api, topic_in, topic_out, group_id):
    root = api.request("GET", "/flow/process-groups/root")["processGroupFlow"]
    group = api.request("POST", f"/process-groups/{root['id']}/process-groups", {
        "revision": api.revision(), "component": {"name": f"Kafka replay · {group_id}", "position": {
            "x": 100, "y": 100 + 180 * len(root["flow"]["processGroups"])}}})["id"]
    conn = api.controller(group, "org.apache.nifi.kafka.service.Kafka3ConnectionService", "Kafka",
                          {"bootstrap.servers": BROKER, "security.protocol": "PLAINTEXT"})
    source = api.processor(group, "org.apache.nifi.kafka.processors.ConsumeKafka", "Read input", 0, 0, {
        "Kafka Connection Service": conn, "Topics": topic_in, "Group ID": group_id,
        "Commit Offsets": "false", "auto.offset.reset": "earliest"})
    sink = api.processor(group, "org.apache.nifi.kafka.processors.PublishKafka", "Publish output", 410, 0, {
        "Kafka Connection Service": conn, "Topic Name": topic_out, "Transactions Enabled": "true",
        "acks": "all", "FlowFile Attribute Header Pattern": r"uuid|kafka\.(topic|partition|offset)",
        "Failure Strategy": "Rollback"}, ["success", "failure"])
    api.connect(group, source, sink, "success")
    return group, source, sink


def run(report):
    event = {"event_id": str(uuid4()), "points": 100}
    tag = event["event_id"][:12]
    topic_in, topic_out, group_id = (prefix + tag for prefix in ("replay.in.", "replay.out.", "replay-group-"))
    command(*COMPOSE, "up", "-d", "--wait", "--wait-timeout", "240", "nifi-points", timeout=300)
    api = connect()
    for topic in (topic_in, topic_out):
        kafka("topics", "--create", "--topic", topic, "--partitions", "1", "--replication-factor", "1")
    # Establish a numeric baseline while the input is empty and the new group has no members.
    kafka("consumer-groups", "--group", group_id, "--topic", topic_in + ":0",
          "--reset-offsets", "--to-offset", "0", "--execute")
    if positions(topic_in, group_id) != [0, 0, 0]:
        raise RuntimeError("Failed to initialize the dedicated group at offset zero")
    group, source, sink = install(api, topic_in, topic_out, group_id)
    ui = f"{WEB}/nifi/#/process-groups/{group}"
    print(f"group={group_id} in={topic_in} out={topic_out}\n{ui}", flush=True)

    def start_flow():
        api.set_status(sink, "RUNNING")
        api.set_status(source, "RUNNING")

    snapshots = []

    def observe(stage):
        output = records(topic_out, with_headers=True)
        pos = positions(topic_in, group_id)
        if pos is None:
            raise RuntimeError(f"Missing group offset at {stage}")
        for record in output:
            hdr = record["headers"]
            if (record["value"] != event or hdr["kafka.topic"] != topic_in or
                    hdr["kafka.partition"] != "0" or hdr["kafka.offset"] != "0" or not hdr["uuid"]):
                raise RuntimeError(f"Unexpected origin or payload: {record}")
        snapshots.append({"stage": stage, "current_offset": pos[0], "log_end_offset": pos[1],
                          "lag": pos[2], "output": output})
        print(f"{stage}: input current/end/lag={pos}, committed output offsets="
              f"{[r['offset'] for r in output]}", flush=True)

    def output_available():
        return records(topic_out, with_headers=True)

    container = command(*COMPOSE, "ps", "-q", "nifi-points")
    down = False
    try:
        start_flow()
        kafka("console-producer", "--topic", topic_in, data=json.dumps(event) + "\n")
        wait(output_available, "first committed output")
        observe("before_crash")
        if len(snapshots[-1]["output"]) != 1:
            raise RuntimeError("Expected a single committed output before the crash")
        down = True
        command(*COMPOSE, "kill", "-s", "SIGKILL", "nifi-points")
        code = command("docker", "inspect", "-f", "{{.State.ExitCode}}", container)
        if code != "137":
            raise RuntimeError(f"Unexpected exit code: {code}")
        observe("nifi_down")
        command(*COMPOSE, "start", "nifi-points")
        api = connect(recover_container=container)
        down = False
        start_flow()
        wait(lambda: len(output_available()) >= 2, "second committed output from the restarted node", 150)
        observe("after_recovery")
    finally:
        if down:
            command(*COMPOSE, "start", "nifi-points")
            api = connect(recover_container=container)
        api.set_status(source, "STOPPED")
        api.set_status(sink, "STOPPED")

    wait(lambda: "Empty" in kafka("consumer-groups", "--describe", "--group", group_id, "--state"),
         "dedicated consumer group to leave")
    observe("after_stop")
    input_records = records(topic_in, with_headers=False)
    before, offline, recovered, stopped = snapshots
    output = recovered["output"]
    if (input_records != [{"offset": 0, "value": event}] or offline["output"] != before["output"]
            or len(output) != 2 or output[:1] != before["output"] or stopped["output"] != output
            or len({r["headers"]["uuid"] for r in output}) != 2
            or any(s["current_offset"] != 0 or s["log_end_offset"] != 1 for s in snapshots[:3])):
        raise RuntimeError(f"Unexpected observations: {snapshots}, input: {input_records}")
    proof = {"input_topic": topic_in, "output_topic": topic_out, "group": group_id, "ui": ui,
             "input": input_records, "nifi_exit_code": int(code), "stages": snapshots}
    if report:
        report.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print("PASS: one input, two committed outputs with distinct FlowFile UUIDs.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    command(*COMPOSE, "up", "-d", "--wait", "--wait-timeout", "240", "postgres", "kafka", timeout=300)
    with exclusive_worker():
        run(args.report)
