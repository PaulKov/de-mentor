"""Live Greenplum smoke plan for local runs and GitHub Actions."""

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class SmokeStep:
    title: str
    command: str


@dataclass(frozen=True)
class CiSmokePlan:
    lab_name: str
    steps: List[SmokeStep]

    def render(self) -> str:
        lines = [
            f"# Greenplum Live Smoke Plan: {self.lab_name}",
            "",
            "Эти команды проверяют, что учебный стенд реально поднимается, seed воспроизводим, SQL examples выполняются, а autograder принимает evidence-rich submission.",
            "",
            "```bash",
        ]
        lines.extend(step.command for step in self.steps)
        lines.extend(["```", ""])
        lines.extend(["## Steps"])
        for step in self.steps:
            lines.append(f"- {step.title}: `{step.command}`")
        lines.append("")
        return "\n".join(lines)


class CiSmokePlanBuilder:
    """Builds deterministic smoke commands for Greenplum."""

    _SUPPORTED_LABS = {"greenplum"}

    def build(self, lab_name: str) -> CiSmokePlan:
        normalized = lab_name.lower()
        if normalized not in self._SUPPORTED_LABS:
            raise KeyError(f"Unknown CI smoke lab: {lab_name}")
        return CiSmokePlan(
            lab_name=normalized,
            steps=[
                SmokeStep("Render generated dataset", "python3 mentor-lab.py dataset greenplum generate --scale small --seed 42 --skew high --late-facts --wide-rows --output artifacts/generated-enterprise.sql"),
                SmokeStep("Start Greenplum", "python3 mentor-lab.py up greenplum"),
                SmokeStep("Check Greenplum", "python3 mentor-lab.py check greenplum"),
                SmokeStep("Run storage SQL", _example_sql_command("storage-and-partitioning.sql")),
                SmokeStep("Run partitioning SQL", _example_sql_command("partitioning-strategies.sql")),
                SmokeStep("Autograde sample SQL", "python3 mentor-lab.py autograde-sql greenplum --submission labs/greenplum/examples/student-solution-example.sql --live --output artifacts/sql-autograde.md"),
                SmokeStep("Stop Greenplum", "python3 mentor-lab.py down greenplum"),
            ],
        )

    def write(self, path: Path, lab_name: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.build(lab_name).render(), encoding="utf-8")
        return path


def _example_sql_command(filename: str) -> str:
    return (
        "docker compose -f labs/greenplum/docker-compose.yml exec -T -u gpadmin "
        "greenplum bash -lc \". /usr/local/greenplum-db/greenplum_path.sh && "
        f"psql -U gpadmin -d mentor -v ON_ERROR_STOP=1 -f /mentor-lab/examples/{filename}\""
    )
