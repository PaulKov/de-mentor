"""Typed mentor runbook model."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RunbookStage:
    """One teachable block in a mentor-facing route."""

    timebox: str
    slides: str
    title: str
    mentor_talk: str
    commands: List[str]
    question: str
    expected_answer: str
    check: str
    links: List[str]

    def render(self, index: int) -> str:
        """Render the stage as compact Markdown for terminal output."""

        lines = [
            f"## Stage {index}: {self.timebox} - {self.title}",
            f"Slides: {self.slides}",
            f"Mentor: {self.mentor_talk}",
            "",
            "Команды:",
        ]
        lines.extend(f"  {command}" for command in self.commands)
        lines.extend(
            [
                f"Что спрашиваем: {self.question}",
                f"Expected answer: {self.expected_answer}",
                f"Как проверяем: {self.check}",
                "Links:",
            ]
        )
        lines.extend(f"- {link}" for link in self.links)
        return "\n".join(lines)


@dataclass(frozen=True)
class Runbook:
    """Full mentor route for a Greenplum lesson variant."""

    lab_name: str
    route: str
    title: str
    description: str
    stages: List[RunbookStage]

    def render(self) -> str:
        """Render a complete route for CLI usage."""

        lines = [
            f"# {self.title}",
            "",
            self.description,
            "",
            "Deck: artifacts/greenplum-theory.pptx",
            "Workbook: docs/lessons/01-greenplum/student-workbook.md",
            "Homework: docs/lessons/01-greenplum/homework.md",
            "SQL examples: labs/greenplum/examples/storage-and-partitioning.sql",
            "Partitioning examples: labs/greenplum/examples/partitioning-strategies.sql",
            "Monitoring examples: labs/greenplum/examples/cluster-monitoring.sql",
            "",
        ]
        for index, stage in enumerate(self.stages, start=1):
            lines.append(stage.render(index))
            lines.append("")
        return "\n".join(lines)
