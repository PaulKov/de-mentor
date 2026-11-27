"""Install and optionally run the starter flow in the local NiFi lab."""

import argparse
import json
from pathlib import Path
import ssl
from time import monotonic, sleep
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

WEB_URL = "https://localhost:28443"
GROUP_NAME = "Lab 01 · Kafka and PostgreSQL"
FORMATS_NAME = "Lab 02 · XML and Groovy"
TOPIC = "nifi.orders.v1"
FIXTURES = Path(__file__).with_name("fixtures")


class NiFi:
    def __init__(self, web_url=WEB_URL):
        # The Compose listener is bound to loopback and uses a lab certificate.
        self.context = ssl._create_unverified_context()
        self.api = web_url + "/nifi-api"
        self.client_id = str(uuid4())
        self.token = None
        self.token = self.request(
            "POST", "/access/token",
            urlencode({"username": "student", "password": "Practice-Only-2026"}).encode(),
        )

    def request(self, method, path, body=None):
        headers = {}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        if isinstance(body, bytes):
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif body is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(body).encode()
        request = Request(self.api + path, data=body, method=method, headers=headers)
        try:
            with urlopen(request, context=self.context, timeout=25) as response:
                data = response.read().decode()
                return json.loads(data) if "application/json" in response.headers.get("Content-Type", "") else data
        except HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:1200]
            raise RuntimeError(f"{method} {path}: HTTP {exc.code} {detail}") from None

    def revision(self, previous=None):
        return {"clientId": self.client_id, "version": previous["revision"]["version"] if previous else 0}

    def wait(self, predicate, description):
        deadline = monotonic() + 25
        while monotonic() < deadline:
            result = predicate()
            if result:
                return result
            sleep(0.25)
        raise RuntimeError(f"Timed out waiting for {description}")

    def controller(self, group, type_name, name, properties):
        item = self.request("POST", f"/process-groups/{group}/controller-services", {
            "revision": self.revision(),
            "component": {"name": name, "type": type_name, "properties": properties},
        })
        service = item["id"]
        self.request("PUT", f"/controller-services/{service}/run-status", {
            "revision": self.revision(item), "state": "ENABLED",
        })
        def enabled():
            current = self.request("GET", f"/controller-services/{service}")["component"]
            if current.get("validationStatus") == "INVALID":
                raise RuntimeError(f"{name}: {current.get('validationErrors')}")
            return current.get("state") == "ENABLED"
        self.wait(enabled, name)
        return service

    def processor(self, group, type_name, name, x, y, properties, terminate=()):
        item = self.request("POST", f"/process-groups/{group}/processors", {
            "revision": self.revision(),
            "component": {
                "name": name, "type": type_name, "position": {"x": x, "y": y},
                "config": {"properties": properties, "autoTerminatedRelationships": list(terminate)},
            },
        })
        return item["id"]

    def connect(self, group, source, target, *relationships):
        self.request("POST", f"/process-groups/{group}/connections", {
            "revision": self.revision(),
            "component": {
                "source": {"id": source, "groupId": group, "type": "PROCESSOR"},
                "destination": {"id": target, "groupId": group, "type": "PROCESSOR"},
                "selectedRelationships": list(relationships),
                "backPressureObjectThreshold": 100,
                "backPressureDataSizeThreshold": "25 MB",
            },
        })

    def set_status(self, processor, state):
        path = f"/processors/{processor}"
        current = self.request("GET", path)
        if state == "RUNNING" and current["component"]["state"] == state:
            return
        if state != "STOPPED":
            current = self.wait(
                lambda: self.valid_processor(path), current["component"]["name"] + " validation"
            )
        self.request("PUT", path + "/run-status", {"revision": self.revision(current), "state": state})

    def valid_processor(self, path):
        entity = self.request("GET", path)
        component = entity["component"]
        status = component.get("validationStatus")
        if status == "INVALID":
            raise RuntimeError(f"{component['name']}: {component.get('validationErrors')}")
        return entity if status == "VALID" else None


def install(nifi, group):
    standard = "org.apache.nifi.processors.standard."
    kafka_type = "org.apache.nifi.kafka.processors."
    read = lambda filename: (FIXTURES / filename).read_text(encoding="utf-8").strip()
    kafka = nifi.controller(group, "org.apache.nifi.kafka.service.Kafka3ConnectionService", "Lab Kafka",
                            {"bootstrap.servers": "kafka:29092", "security.protocol": "PLAINTEXT"})
    db = nifi.controller(group, "org.apache.nifi.dbcp.DBCPConnectionPool", "Lab PostgreSQL", {
        "Database Connection URL": "jdbc:postgresql://postgres:5432/integration",
        "Database Driver Class Name": "org.postgresql.Driver",
        "Database Driver Locations": "/opt/nifi/jdbc/postgresql.jar",
        "Database User": "student", "Password": "practice-only-db",
    })
    reader = nifi.controller(group, "org.apache.nifi.json.JsonTreeReader", "Lab JSON Reader", {})
    generate = nifi.processor(group, standard + "GenerateFlowFile", "1 Seed orders (run once)", 0, 0,
                              {"Custom Text": read("orders.json")})
    jolt = nifi.processor(group, "org.apache.nifi.processors.jolt.JoltTransformJSON",
                          "2 Normalize JSON", 390, 0, {"Jolt Specification": read("orders.jolt.json")})
    publish = nifi.processor(group, kafka_type + "PublishKafka", "3 Publish to Kafka", 780, 0, {
        "Kafka Connection Service": kafka, "Topic Name": TOPIC,
    }, ["success"])
    consume = nifi.processor(group, kafka_type + "ConsumeKafka", "4 Consume from Kafka", 0, 270, {
        "Kafka Connection Service": kafka, "Topics": TOPIC, "Group ID": "nifi-orders-db-v1",
        "auto.offset.reset": "earliest",
    })
    insert = nifi.processor(group, standard + "PutDatabaseRecord", "5 UPSERT orders", 390, 270, {
        "Database Connection Pooling Service": db, "Record Reader": reader,
        "Database Type": "PostgreSQL", "Statement Type": "UPSERT", "Table Name": "integration_events",
        "Update Keys": "event_id", "Unmatched Column Behavior": "Ignore Unmatched Columns",
    }, ["success"])
    dlq = nifi.processor(group, standard + "PutFile", "Quarantine with original content", 390, 565, {
        "Directory": "/lab/output/quarantine", "Conflict Resolution Strategy": "fail",
    }, ["success"])
    hold = nifi.processor(group, "org.apache.nifi.processors.attributes.UpdateAttribute",
                          "Hold quarantine write errors", 780, 565, {}, ["success"])
    nifi.connect(group, generate, jolt, "success")
    nifi.connect(group, jolt, publish, "success")
    nifi.connect(group, jolt, dlq, "failure")
    nifi.connect(group, publish, dlq, "failure")
    nifi.connect(group, consume, insert, "success")
    nifi.connect(group, insert, dlq, "failure", "retry")
    nifi.connect(group, dlq, hold, "failure")
    return processor_ids(nifi, group)


def processor_ids(nifi, group):
    return {
        p["component"]["name"]: p["id"]
        for p in nifi.request("GET", f"/flow/process-groups/{group}")["processGroupFlow"]["flow"]["processors"]
    }


def install_formats(nifi, group):
    standard = "org.apache.nifi.processors.standard."
    xml = nifi.processor(group, standard + "GenerateFlowFile", "Seed XML (run once)", 0, 0,
                         {"Custom Text": (FIXTURES / "order.xml").read_text(encoding="utf-8")})
    json_input = nifi.processor(group, standard + "GenerateFlowFile", "Seed JSON (run once)", 0, 270,
                                {"Custom Text": '{"event_id":"  o-101  ","qty":2}'})
    xslt = nifi.processor(group, standard + "TransformXml", "Apply stylesheet", 390, 0, {
        "XSLT Document": "/lab/fixtures/order.xsl", "Secure Processing": "true",
    })
    groovy = nifi.processor(group, "org.apache.nifi.processors.groovyx.ExecuteGroovyScript",
                            "Normalize event ID", 390, 270, {"Script File": "/lab/fixtures/normalize.groovy"})
    results = nifi.processor(group, standard + "PutFile", "Save transformed content", 780, 0, {
        "Directory": "/lab/output/transformed", "Conflict Resolution Strategy": "fail",
    }, ["success"])
    errors = nifi.processor(group, standard + "PutFile", "Save transform errors", 780, 270, {
        "Directory": "/lab/output/transform-errors", "Conflict Resolution Strategy": "fail",
    }, ["success"])
    hold = nifi.processor(group, "org.apache.nifi.processors.attributes.UpdateAttribute",
                          "Hold file write errors", 1170, 270, {}, ["success"])
    nifi.connect(group, xml, xslt, "success")
    nifi.connect(group, json_input, groovy, "success")
    for processor in (xslt, groovy):
        nifi.connect(group, processor, results, "success")
        nifi.connect(group, processor, errors, "failure")
    for processor in (results, errors):
        nifi.connect(group, processor, hold, "failure")
    return processor_ids(nifi, group)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-once", action="store_true", help="run the sample producer once")
    parser.add_argument("--formats", action="store_true", help="install the XML and Groovy examples")
    args = parser.parse_args()
    nifi = NiFi()
    root = nifi.request("GET", "/flow/process-groups/root")["processGroupFlow"]
    name = FORMATS_NAME if args.formats else GROUP_NAME
    groups = [g["id"] for g in root["flow"]["processGroups"] if g["component"]["name"] == name]
    if not groups:
        group = nifi.request("POST", f"/process-groups/{root['id']}/process-groups", {
            "revision": nifi.revision(),
            "component": {"name": name, "position": {"x": 120 if not args.formats else 540, "y": 100}},
        })["id"]
        ids = install_formats(nifi, group) if args.formats else install(nifi, group)
    else:
        group = groups[0]
        ids = processor_ids(nifi, group)
    if len(ids) < 7:
        raise RuntimeError("Starter group exists but is incomplete. Inspect the group in NiFi before rerunning.")
    print(f"Flow: {WEB_URL}/nifi/#/process-groups/{group}")
    if args.run_once:
        for name, processor in ids.items():
            if "(run once)" not in name and not name.startswith("Hold "):
                nifi.set_status(processor, "RUNNING")
        for name, processor in ids.items():
            if "(run once)" in name:
                nifi.set_status(processor, "RUN_ONCE")
        print("Seed requested once. Inspect output and queues in NiFi.")


if __name__ == "__main__":
    main()
