"""Submission-ready evidence packs for practical Greenplum exercises."""

from dataclasses import dataclass
from pathlib import Path
from typing import List

from mentor_lab.scenario_dsl import ScenarioDefinition, ScenarioDslCatalog


@dataclass(frozen=True)
class EvidenceCommand:
    title: str
    command: str


@dataclass(frozen=True)
class EvidencePacket:
    scenario: ScenarioDefinition
    commands: List[EvidenceCommand]

    def render(self) -> str:
        lines = [
            f"# Evidence Pack: {self.scenario.code}",
            "",
            f"Scenario: {self.scenario.title}",
            f"Difficulty: {self.scenario.difficulty}",
            f"Seed profile: {self.scenario.seed_profile}",
            "",
            "## Skills",
        ]
        lines.extend(f"- {skill}" for skill in self.scenario.skills)
        lines.extend(["", "## Commands To Run"])
        for command in self.commands:
            lines.extend([f"### {command.title}", "```bash", command.command, "```", ""])

        lines.extend(
            [
                "## Symptom",
                "",
                "Опиши, что именно медленно или неправильно работает.",
                "",
                "## EXPLAIN evidence",
                "",
                "Вставь фрагмент плана с `Redistribute Motion`, `Broadcast Motion`, `Hash Join`, `Gather Motion` или другим важным узлом.",
                "",
                "## Segment evidence",
                "",
                "Вставь проверку `gp_segment_id`, `gp_toolkit` или другой segment-level диагностики.",
                "",
                "## Physical cause",
                "",
                "Объясни связь между distribution key, join key, partition key, storage и фактическим движением данных.",
                "",
                "## Change",
                "",
                "Опиши DDL/SQL изменение или дизайн-решение.",
                "",
                "## Validation",
                "",
                "Приложи before/after: `EXPLAIN ANALYZE`, row counts, skew check или catalog query.",
                "",
                "## Residual risk",
                "",
                "Что может остаться рискованным после исправления?",
                "",
                "## Review Commands",
                "```bash",
                f"python3 mentor-lab.py adaptive-review {self.scenario.lab} --submission submissions/{self.scenario.code}.md",
                f"python3 mentor-lab.py learning-loop {self.scenario.lab} --pre 40 --post 85 --submission submissions/{self.scenario.code}.md --output artifacts/{self.scenario.lab}-learning-loop.md",
                "```",
                "",
            ]
        )
        return "\n".join(lines)

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
        return path


class EvidenceCollector:
    """Creates deterministic evidence packs without requiring a live database."""

    @classmethod
    def default(cls) -> "EvidenceCollector":
        return cls(ScenarioDslCatalog.default())

    def __init__(self, scenarios: ScenarioDslCatalog) -> None:
        self._scenarios = scenarios

    def collect(self, lab_name: str, task_code: str) -> EvidencePacket:
        scenario = self._scenarios.get(lab_name, task_code)
        return EvidencePacket(
            scenario=scenario,
            commands=_commands_for(scenario),
        )


def _commands_for(scenario: ScenarioDefinition) -> List[EvidenceCommand]:
    commands = [
        EvidenceCommand(
            "Показать сценарий",
            f"python3 mentor-lab.py scenario {scenario.lab} show {scenario.code}",
        ),
        EvidenceCommand(
            "Подготовить профиль данных",
            f"python3 mentor-lab.py seed {scenario.lab} --profile {scenario.seed_profile}",
        ),
        EvidenceCommand(
            "Проверить skew по сегментам",
            f"python3 mentor-lab.py diagnostics {scenario.lab} show segment-skew",
        ),
        EvidenceCommand(
            "Проверить статистику",
            f"python3 mentor-lab.py diagnostics {scenario.lab} show table-statistics",
        ),
    ]
    if scenario.code == "redistribute-join":
        commands.insert(
            2,
            EvidenceCommand(
                "Получить план проблемного join",
                f"python3 mentor-lab.py analyze-plan {scenario.lab} --query bad_customer_join --sample",
            ),
        )
    if scenario.code == "large-gather":
        commands.insert(
            2,
            EvidenceCommand(
                "Найти Gather Motion",
                f"python3 mentor-lab.py analyze-plan {scenario.lab} --query large_result_query --sample",
            ),
        )
    return commands
