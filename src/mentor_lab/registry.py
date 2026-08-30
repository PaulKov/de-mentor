"""Factory for the default mentorship lab registry."""

from pathlib import Path

from mentor_lab.domain import LabDefinition, LabRegistry

# Shared Greenplum 6.25 academy stand (Lessons 01–03).
_GP625_COMPOSE = Path("labs/greenplum-625/docker-compose.yml")
_GP625_ENV = ". /usr/local/gpdb/greenplum_path.sh"
_GP625_PORT = 15436


def create_default_registry(project_root: Path) -> LabRegistry:
    """Create the default registry.

    `project_root` is accepted to keep the factory signature stable for future
    registry implementations that may read project-local metadata.
    """

    _ = project_root
    greenplum_academy = dict(
        compose_file=_GP625_COMPOSE,
        service_name="greenplum-625",
        default_user="gpadmin",
        default_database="mentor",
        port=_GP625_PORT,
        env_script=_GP625_ENV,
        bootstrap_database="postgres",
    )
    return LabRegistry(
        [
            LabDefinition(
                name="greenplum",
                title="Greenplum MPP academy (GP 6.25)",
                description=(
                    "Shared Docker Compose stand for Lessons 01–03: distribution, "
                    "partitioning, OLAP decomposition and Legacy vs GPORCA."
                ),
                status="ready",
                docs_path=Path("labs/greenplum-625/README.md"),
                **greenplum_academy,
            ),
            LabDefinition(
                name="greenplum-625",
                title="Greenplum 6.25 academy lab",
                description=(
                    "Alias of the shared academy stand (same container/port as "
                    "`greenplum`). Prefer either name; data lives in DB mentor."
                ),
                status="ready",
                docs_path=Path("labs/greenplum-625/README.md"),
                **greenplum_academy,
            ),
            LabDefinition(
                name="spark",
                title="Apache Spark 4.2 PySpark academy",
                description=(
                    "Self-service Spark Standalone cluster for Lesson 04: one "
                    "master, two workers, a PySpark client and observable Spark UI."
                ),
                status="ready",
                compose_file=Path("labs/spark/docker-compose.yml"),
                service_name="spark-client",
                default_user="spark",
                default_database="",
                port=4040,
                docs_path=Path("labs/spark/README.md"),
                runtime="spark",
                env_script="",
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
