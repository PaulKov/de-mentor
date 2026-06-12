"""Factory for the default mentorship lab registry."""

from pathlib import Path

from mentor_lab.domain import LabDefinition, LabRegistry


def create_default_registry(project_root: Path) -> LabRegistry:
    """Create the default registry.

    `project_root` is accepted to keep the factory signature stable for future
    registry implementations that may read project-local metadata.
    """

    _ = project_root
    return LabRegistry(
        [
            LabDefinition(
                name="greenplum",
                title="Greenplum MPP basics",
                description=(
                    "Ready Docker Compose stand for distribution keys, skew, "
                    "Motion nodes, and first warehouse modeling exercises."
                ),
                status="ready",
                compose_file=Path("labs/greenplum/docker-compose.yml"),
                service_name="greenplum",
                default_user="gpadmin",
                default_database="mentor",
                port=15432,
                docs_path=Path("labs/greenplum/README.md"),
            ),
            LabDefinition(
                name="postgres",
                title="PostgreSQL foundations",
                description="Planned OLTP and SQL baseline lab.",
                status="planned",
                compose_file=Path("labs/postgres/docker-compose.yml"),
                service_name="postgres",
                default_user="postgres",
                default_database="mentor",
                port=15433,
                docs_path=Path("labs/postgres/README.md"),
            ),
            LabDefinition(
                name="clickhouse",
                title="ClickHouse columnar analytics",
                description="Planned columnar OLAP and MergeTree lab.",
                status="planned",
                compose_file=Path("labs/clickhouse/docker-compose.yml"),
                service_name="clickhouse",
                default_user="default",
                default_database="mentor",
                port=18123,
                docs_path=Path("labs/clickhouse/README.md"),
            ),
            LabDefinition(
                name="hadoop-hdfs",
                title="Hadoop HDFS",
                description="Planned distributed storage lab.",
                status="planned",
                compose_file=Path("labs/hadoop-hdfs/docker-compose.yml"),
                service_name="namenode",
                default_user="hdfs",
                default_database="",
                port=9870,
                docs_path=Path("labs/hadoop-hdfs/README.md"),
            ),
            LabDefinition(
                name="spark-yarn",
                title="Spark on YARN",
                description="Planned batch processing lab on YARN.",
                status="planned",
                compose_file=Path("labs/spark-yarn/docker-compose.yml"),
                service_name="spark-client",
                default_user="spark",
                default_database="",
                port=8088,
                docs_path=Path("labs/spark-yarn/README.md"),
            ),
            LabDefinition(
                name="spark-k8s",
                title="Spark on Kubernetes",
                description="Planned Spark operator and Kubernetes execution lab.",
                status="planned",
                compose_file=Path("labs/spark-k8s/docker-compose.yml"),
                service_name="spark-client",
                default_user="spark",
                default_database="",
                port=4040,
                docs_path=Path("labs/spark-k8s/README.md"),
            ),
        ]
    )

