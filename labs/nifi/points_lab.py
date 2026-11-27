"""Crash an isolated NiFi after the PostgreSQL commit and verify each replay."""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
from time import monotonic, sleep
from uuid import uuid4

from bootstrap import NiFi

HERE = Path(__file__).resolve().parent
WEB = "https://127.0.0.1:28444"
BROKER = "kafka:29092"
COMPOSE = ["docker", "compose", "-f", "compose.yaml", "-f", "compose.points.yaml"]


def command(*args, data=None, timeout=65):
    result = subprocess.run(args, input=data, text=True, encoding="utf-8", errors="replace",
                            capture_output=True, cwd=HERE, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"{' '.join(args)}\n{result.stderr}\n{result.stdout}")
    return result.stdout.strip()


def sql(query):
    return command(*COMPOSE, "exec", "-T", "postgres", "psql", "-X", "-qAt",
                   "-v", "ON_ERROR_STOP=1", "-U", "student", "-d", "integration", data=query)


@contextmanager
def exclusive_worker():
    # All runs share the crash-test node. Keep this DB session alive across the NiFi restart.
    with subprocess.Popen([*COMPOSE, "exec", "-T", "postgres", "psql", "-XqAt",
                           "-v", "ON_ERROR_STOP=1", "-U", "student", "-d", "integration"],
                          cwd=HERE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as owner:
        try:
            owner.stdin.write("SELECT pg_try_advisory_lock(202611, 28444);\n")
            owner.stdin.flush()
            if owner.stdout.readline().strip() != "t":
                raise RuntimeError("Another points experiment owns the crash-test node")
            yield
        finally:
            owner.stdin.close()


def kafka(tool, *args, data=None):
    return command(*COMPOSE, "exec", "-T", "kafka", f"/opt/kafka/bin/kafka-{tool}.sh",
                   "--bootstrap-server", BROKER, *args, data=data)


def wait(check, description, seconds=100):
    end = monotonic() + seconds
    last = None
    while monotonic() < end:
        last = check()
        if last:
            return last
        sleep(1)
    raise RuntimeError(f"Timed out: {description}; last observation: {last!r}")


def connect(recover_container=None):
    restarts = 0

    def ready():
        nonlocal restarts
        if recover_container:
            state = command("docker", "inspect", "-f", "{{.State.Status}} {{.State.Health.Status}}",
                            recover_container)
            if state.startswith("exited "):
                if restarts >= 2:
                    raise RuntimeError("NiFi exited repeatedly during recovery; inspect nifi-points logs")
                restarts += 1
                print(f"Restarting exited crash-test node during recovery ({restarts}/2)", flush=True)
                command(*COMPOSE, "start", "nifi-points")
                return None
            if state != "running healthy":
                return None
        try:
            return NiFi(WEB)
        except (OSError, RuntimeError):
            return None
    return wait(ready, "NiFi REST API on port 28444", 210)


def install(api, topic, group_id):
    root = api.request("GET", "/flow/process-groups/root")["processGroupFlow"]
    group = api.request("POST", f"/process-groups/{root['id']}/process-groups", {
        "revision": api.revision(),
        "component": {"name": f"Points · {topic}", "position": {
            "x": 100, "y": 100 + 180 * len(root["flow"]["processGroups"])}}})["id"]
    broker_service = api.controller(group, "org.apache.nifi.kafka.service.Kafka3ConnectionService",
                                    "Lab Kafka", {"bootstrap.servers": BROKER, "security.protocol": "PLAINTEXT"})
    db = api.controller(group, "org.apache.nifi.dbcp.DBCPConnectionPool", "Points database", {
        "Database Connection URL": "jdbc:postgresql://postgres:5432/integration",
        "Database Driver Class Name": "org.postgresql.Driver",
        "Database Driver Locations": "/opt/nifi/jdbc/postgresql.jar",
        "Database User": "student", "Password": "practice-only-db"})
    source = api.processor(group, "org.apache.nifi.kafka.processors.ConsumeKafka", "1 Read points", 0, 0, {
        "Kafka Connection Service": broker_service, "Topics": topic, "Group ID": group_id,
        "auto.offset.reset": "earliest", "Commit Offsets": "true"})
    sink = api.processor(group, "org.apache.nifi.processors.groovyx.ExecuteGroovyScript",
                         "2 Credit points in PostgreSQL", 390, 0, {
                             "Script File": "/lab/points/apply.groovy", "CTL.points": db}, ["success"])
    hold = api.processor(group, "org.apache.nifi.processors.attributes.UpdateAttribute",
                         "Inspect conflicting events", 780, 180, {}, ["success"])
    api.connect(group, source, sink, "success")
    api.connect(group, sink, hold, "failure")
    return group, source, sink


def positions(topic, group_id):
    output = kafka("consumer-groups", "--describe", "--group", group_id)
    for line in output.splitlines():
        cols = line.split()
        if cols[:3] == [group_id, topic, "0"] and all(c.isdecimal() for c in cols[3:6]):
            return list(map(int, cols[3:6]))
    return None


def verify(event, stage, measured_positions, decisions):
    event_id = event["event_id"]
    account = event["account_id"]
    snapshot = json.loads(sql(f"""
        SELECT json_build_object(
          'balance', (SELECT balance FROM points_lab.protected_balances WHERE account_id = '{account}'),
          'control_balance', (SELECT balance FROM points_lab.control_balances WHERE account_id = '{account}'),
          'inbox_rows', (SELECT count(*) FROM points_lab.inbox WHERE event_id = '{event_id}'),
          'attempts', (SELECT json_agg(json_build_object(
              'decision', decision, 'offset', kafka_offset, 'flowfile', flow_uuid,
              'partition', partition_id, 'topic', topic) ORDER BY attempt_id)
            FROM points_lab.attempts WHERE event_id = '{event_id}'));
    """))
    snapshot.update(stage=stage, current_offset=measured_positions[0],
                    log_end_offset=measured_positions[1], lag=measured_positions[2])
    attempts = snapshot["attempts"] or []
    if ([a["decision"] for a in attempts] != decisions or snapshot["balance"] != 100
            or snapshot["control_balance"] != 100 * len(decisions) or snapshot["inbox_rows"] != 1):
        raise RuntimeError(f"Unexpected database evidence: {snapshot}")
    print(f"{stage}: position/end/lag={measured_positions}  balance={snapshot['balance']}  "
          f"control={snapshot['control_balance']}  attempts={len(attempts)}", flush=True)
    return snapshot


def run(report):
    event_id = str(uuid4())
    tag = event_id[:12]
    topic, group_id = "nifi.points." + tag, "points-db-" + tag
    event = {"event_id": event_id, "account_id": "student-" + tag, "points": 100, "pause_after_commit": True}
    payload = json.dumps(event) + "\n"
    print(f"event={event_id} account={event['account_id']} topic={topic} group={group_id}", flush=True)
    command(*COMPOSE, "up", "-d", "--wait", "--wait-timeout", "240", "nifi-points", timeout=300)
    sql((HERE / "points/schema.sql").read_text(encoding="utf-8"))
    kafka("topics", "--create", "--topic", topic, "--partitions", "1", "--replication-factor", "1")
    api = connect()
    group, source, sink = install(api, topic, group_id)
    ui = f"{WEB}/nifi/#/process-groups/{group}"
    print(ui, flush=True)
    stages = []
    container = command(*COMPOSE, "ps", "-q", "nifi-points")
    node_down = False

    def start_flow():
        api.set_status(sink, "RUNNING")
        api.set_status(source, "RUNNING")

    def observe(label, positions_wanted, decisions):
        def caught_up():
            offsets = positions(topic, group_id)
            return offsets if offsets == positions_wanted else None
        observed = wait(caught_up, f"Kafka positions {positions_wanted}")
        wait(lambda: int(sql(f"SELECT count(*) FROM points_lab.attempts WHERE event_id='{event_id}'")) >= len(decisions),
             f"{len(decisions)} committed attempts")
        snap = verify(event, label, observed, decisions)
        stages.append(snap)
        return snap["attempts"]

    def at_gate():
        return sql(f"""SELECT count(*) FROM pg_stat_activity WHERE application_name='points-drill:{event_id}'
                    AND state='active' AND wait_event='PgSleep' AND query LIKE '%points_lab_gate%'""") == "1"

    try:
        start_flow()
        kafka("console-producer", "--topic", topic, data=payload)
        wait(at_gate, "credit committed and sink sleeping before session.transfer")
        observe("before_crash", [1, 1, 0], ["applied"])
        if not at_gate():
            raise RuntimeError("Crash window closed; refusing to claim a crash in the requested window")
        node_down = True
        command(*COMPOSE, "kill", "-s", "SIGKILL", "nifi-points")
        exit_code = command("docker", "inspect", "-f", "{{.State.ExitCode}}", container)
        if exit_code != "137":
            raise RuntimeError(f"Expected SIGKILL exit 137, observed {exit_code}")
        observe("nifi_down", [1, 1, 0], ["applied"])
        command(*COMPOSE, "start", "nifi-points")
        api = connect(recover_container=container)
        node_down = False
        start_flow()
        attempts = observe("queue_recovery", [1, 1, 0], ["applied", "duplicate"])
        if attempts[0]["flowfile"] != attempts[1]["flowfile"]:
            raise RuntimeError("Expected the recovered NiFi FlowFile UUID")

        api.set_status(source, "STOPPED")
        wait(lambda: "Empty" in kafka("consumer-groups", "--describe", "--group", group_id, "--state"),
             "dedicated consumer group to become empty")
        kafka("consumer-groups", "--group", group_id, "--topic", topic + ":0",
              "--reset-offsets", "--to-offset", "0", "--execute")
        observe("group_rewound", [0, 1, 1], ["applied", "duplicate"])
        api.set_status(source, "RUNNING")
        attempts = observe("broker_replay", [1, 1, 0], ["applied", "duplicate", "duplicate"])
        if attempts[2]["flowfile"] == attempts[1]["flowfile"]:
            raise RuntimeError("Kafka reread should have produced a new FlowFile")

        kafka("console-producer", "--topic", topic, data=payload)
        attempts = observe("business_republish", [2, 2, 0], ["applied"] + ["duplicate"] * 3)
        if ([a["offset"] for a in attempts] != [0, 0, 0, 1]
                or any(a["partition"] != 0 or a["topic"] != topic for a in attempts)):
            raise RuntimeError(f"Unexpected source coordinates: {attempts}")
    finally:
        if node_down:
            command(*COMPOSE, "start", "nifi-points")
            api = connect(recover_container=container)
        # Keep the UI, queues and evidence. End this run's consumer membership.
        api.set_status(source, "STOPPED")
        api.set_status(sink, "STOPPED")

    proof = {"event": event, "topic": topic, "group": group_id, "ui": ui,
             "nifi_exit_code": int(exit_code), "stages": stages}
    if report:
        report.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS: one credit for four attempts.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="write all measured snapshots to a JSON file")
    args = parser.parse_args()
    command(*COMPOSE, "up", "-d", "--wait", "--wait-timeout", "240", "postgres", "kafka", timeout=300)
    with exclusive_worker():
        run(args.report)
