from pathlib import Path

from mentor_lab.registry import create_default_registry


def test_registry_exposes_greenplum_as_ready_lab():
    registry = create_default_registry(Path("/workspace"))

    lab = registry.get("greenplum")

    assert lab.name == "greenplum"
    assert lab.status == "ready"
    assert lab.compose_file == Path("labs/greenplum/docker-compose.yml")
    assert lab.service_name == "greenplum"
    assert lab.default_database == "mentor"
    assert lab.default_user == "gpadmin"


def test_registry_documents_future_learning_platforms():
    registry = create_default_registry(Path("/workspace"))

    lab_names = [lab.name for lab in registry.list()]

    assert lab_names == [
        "greenplum",
        "postgres",
        "clickhouse",
        "hadoop-hdfs",
        "spark-yarn",
        "spark-k8s",
    ]
    assert registry.get("spark-k8s").status == "planned"


def test_unknown_lab_error_names_available_labs():
    registry = create_default_registry(Path("/workspace"))

    try:
        registry.get("oracle")
    except KeyError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected unknown lab to raise KeyError")

    assert "oracle" in message
    assert "greenplum" in message
    assert "spark-k8s" in message

