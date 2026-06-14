"""Typed mentor runbook model."""

from dataclasses import dataclass
from typing import List, Optional


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
                f"Ожидаемый ответ: {self.expected_answer}",
                f"Как проверяем: {self.check}",
                "Ссылки:",
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
    deck_path: str = "artifacts/greenplum-theory.pptx"
    workbook_path: str = "docs/lessons/01-greenplum/student-workbook.md"
    homework_path: str = "docs/lessons/01-greenplum/homework.md"
    sql_examples: Optional[List[str]] = None

    def render(self) -> str:
        """Render a complete route for CLI usage."""

        lines = [
            f"# {self.title}",
            "",
            self.description,
            "",
            f"Deck: {self.deck_path}",
            f"Workbook: {self.workbook_path}",
            f"Homework: {self.homework_path}",
        ]
        lines.extend(f"SQL example: {path}" for path in self._sql_examples())
        lines.append("")
        for index, stage in enumerate(self.stages, start=1):
            lines.append(stage.render(index))
            lines.append("")
        return "\n".join(lines)

    def _sql_examples(self) -> List[str]:
        """Return examples with the legacy Lesson 01 defaults preserved."""

        if self.sql_examples is not None:
            return self.sql_examples
        return [
            "labs/greenplum/examples/storage-and-partitioning.sql",
            "labs/greenplum/examples/partitioning-strategies.sql",
            "labs/greenplum/examples/cluster-monitoring.sql",
        ]
