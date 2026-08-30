"""Self-service command boundary for the Apache Spark teaching stand.

The module deliberately owns Spark-specific container paths and commands so
the generic Docker Compose runner remains independent of a particular engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from mentor_lab.docker_compose import Command, DockerComposeRunner
from mentor_lab.domain import LabDefinition


@dataclass(frozen=True)
class SparkProfile:
    """A deterministic lesson dataset profile."""

    name: str
    events: int
    customers: int
    skew_percent: int


class SparkProfileCatalog:
    """Read-only catalog of laptop-safe dataset sizes."""

    _PROFILES = {
        "tiny": SparkProfile("tiny", events=25_000, customers=1_000, skew_percent=20),
        "lesson04": SparkProfile(
            "lesson04", events=250_000, customers=10_000, skew_percent=35
        ),
        "class": SparkProfile(
            "class", events=250_000, customers=10_000, skew_percent=35
        ),
        "deep": SparkProfile("deep", events=1_000_000, customers=50_000, skew_percent=55),
    }

    @classmethod
    def get(cls, name: str) -> SparkProfile:
        """Return a named profile or raise an actionable error."""

        try:
            return cls._PROFILES[name]
        except KeyError as exc:
            available = ", ".join(sorted(cls._PROFILES))
            raise KeyError(
                f"Unknown Spark seed profile '{name}'. Available profiles: {available}."
            ) from exc


class SparkLabCommands:
    """Build safe Spark commands for the Docker Compose client service."""

    _CLIENT_SERVICE = "spark-client"
    _SPARK_SUBMIT = "/opt/spark/bin/spark-submit"
    _MASTER_URL = "spark://spark-master:7077"

    def __init__(
        self,
        project_root: Path,
        lab: LabDefinition,
        runner: DockerComposeRunner,
    ) -> None:
        if lab.runtime != "spark":
            raise ValueError(f"Lab '{lab.name}' is not a Spark runtime.")
        self._project_root = project_root.resolve()
        self._lab = lab
        self._runner = runner

    @staticmethod
    def documented_check_codes() -> tuple[str, ...]:
        """Stable readiness markers printed by the smoke application."""

        return (
            "spark_master_reachable",
            "spark_version",
            "spark_workers_registered",
            "pyspark_dataframe",
            "spark_shuffle_plan",
            "spark_output_roundtrip",
        )

    def build_seed_command(self, profile_name: str) -> Command:
        """Build the deterministic dataset generator command."""

        profile = SparkProfileCatalog.get(profile_name)
        return self.build_submit_command(
            self._project_root / "labs/spark/seed/generate_lesson04_data.py",
            (
                "--events",
                str(profile.events),
                "--customers",
                str(profile.customers),
                "--skew-percent",
                str(profile.skew_percent),
                "--output",
                "/workspace/labs/spark/data/lesson04",
            ),
        )

    def build_check_command(self) -> Command:
        """Build the live Spark readiness smoke command."""

        return self.build_submit_command(
            self._project_root / "labs/spark/examples/lesson04_smoke.py",
            (),
        )

    def build_submit_command(
        self,
        script_path: Path,
        script_args: Sequence[str],
    ) -> Command:
        """Build a spark-submit command for a Python file inside the repository."""

        container_script = self._container_path(script_path)
        command = [
            self._SPARK_SUBMIT,
            "--master",
            self._MASTER_URL,
            "--conf",
            "spark.ui.port=4040",
            "--conf",
            "spark.eventLog.enabled=true",
            "--conf",
            "spark.eventLog.dir=file:/workspace/labs/spark/data/event-log",
            container_script,
            *script_args,
        ]
        return self._runner.build_exec_command(
            self._lab,
            self._CLIENT_SERVICE,
            command,
        )

    def _container_path(self, script_path: Path) -> str:
        resolved = script_path.resolve()
        if resolved.suffix != ".py":
            raise ValueError("Spark submit accepts only Python .py files in this course.")
        if not resolved.exists():
            raise FileNotFoundError(f"Spark application does not exist: {resolved}")
        try:
            relative = resolved.relative_to(self._project_root)
        except ValueError as exc:
            raise ValueError(
                f"Spark application must be inside repository: {self._project_root}"
            ) from exc
        return f"/workspace/{relative.as_posix()}"
