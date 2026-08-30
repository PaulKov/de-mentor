from pathlib import Path

from mentor_lab.registry import create_default_registry


def test_registry_exposes_greenplum_as_shared_gp625_stand():
    registry = create_default_registry(Path("/workspace"))

    lab = registry.get("greenplum")

    assert lab.name == "greenplum"
    assert lab.status == "ready"
    assert lab.compose_file == Path("labs/greenplum-625/docker-compose.yml")
    assert lab.service_name == "greenplum-625"
    assert lab.default_database == "mentor"
    assert lab.default_user == "gpadmin"
    assert lab.port == 15436
    assert lab.bootstrap_database == "postgres"
    assert lab.env_script == ". /usr/local/gpdb/greenplum_path.sh"


def test_registry_exposes_greenplum_625_as_alias_of_same_stand():
    registry = create_default_registry(Path("/workspace"))

    primary = registry.get("greenplum")
    alias = registry.get("greenplum-625")

    assert alias.status == "ready"
    assert alias.compose_file == primary.compose_file
    assert alias.service_name == primary.service_name
    assert alias.port == primary.port
    assert alias.default_database == "mentor"
    assert alias.bootstrap_database == "postgres"


def test_registry_documents_future_learning_platforms():
    registry = create_default_registry(Path("/workspace"))

    lab_names = [lab.name for lab in registry.list()]

    assert lab_names == [
        "greenplum",
        "greenplum-625",
        "spark",
        "postgres",
        "clickhouse",
        "hadoop-hdfs",
        "spark-yarn",
        "spark-k8s",
    ]
    assert registry.get("spark-k8s").status == "planned"


def test_registry_exposes_ready_spark_lesson_stand():
    registry = create_default_registry(Path("/workspace"))

    lab = registry.get("spark")

    assert lab.status == "ready"
    assert lab.runtime == "spark"
    assert lab.compose_file == Path("labs/spark/docker-compose.yml")
    assert lab.service_name == "spark-client"
    assert lab.port == 4040
    assert not lab.supports_sql_console


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
