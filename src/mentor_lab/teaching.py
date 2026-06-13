"""One-button mentor facilitation mode built from existing runbooks."""

from dataclasses import dataclass
from typing import List, Optional

from mentor_lab.runbooks import Runbook, RunbookCatalog, RunbookStage


@dataclass(frozen=True)
class TeachingStage:
    number: int
    total: int
    stage: RunbookStage
    lab_name: str
    route: str

    def render(self) -> str:
        commands = "\n".join(f"- `{command}`" for command in self.stage.commands)
        links = "\n".join(f"- {link}" for link in self.stage.links)
        return "\n".join(
            [
                f"## Stage {self.number}/{self.total}: {self.stage.title}",
                f"Тайминг: {self.stage.timebox}",
                f"Слайды: {self.stage.slides}",
                "",
                f"Что сказать: {self.stage.mentor_talk}",
                "",
                "Команды сейчас:",
                commands,
                "",
                f"Что спросить: {self.stage.question}",
                f"Ожидаемый ответ: {self.stage.expected_answer}",
                f"Как проверить: {self.stage.check}",
                "",
                "Evidence checkpoint:",
                (
                    "- если ученик выполнял практику, собери evidence через "
                    f"`python3 mentor-lab.py evidence {self.lab_name} collect redistribute-join`"
                ),
                "",
                "Полезные ссылки:",
                links,
                "",
            ]
        )


@dataclass(frozen=True)
class TeachingSession:
    runbook: Runbook
    stages: List[TeachingStage]

    def render(self) -> str:
        lines = [
            f"# Teach Mode: {self.runbook.title}",
            "",
            self.runbook.description,
            "",
            "Команды завершения урока:",
            f"- `python3 mentor-lab.py homework {self.runbook.lab_name} check --submission submissions/homework.md`",
            f"- `python3 mentor-lab.py learning-loop {self.runbook.lab_name} --pre 40 --post 85 --submission submissions/query-tuning.md --output artifacts/{self.runbook.lab_name}-learning-loop.md`",
            "",
        ]
        lines.extend(stage.render() for stage in self.stages)
        return "\n".join(lines)


class TeachingSessionBuilder:
    """Builds a mentor-facing route from the runbook catalog."""

    @classmethod
    def default(cls) -> "TeachingSessionBuilder":
        return cls(RunbookCatalog.default())

    def __init__(self, runbooks: RunbookCatalog) -> None:
        self._runbooks = runbooks

    def build(
        self,
        lab_name: str,
        route: str,
        stage_number: Optional[int] = None,
    ) -> TeachingSession:
        runbook = self._runbooks.get(lab_name, route)
        total = len(runbook.stages)
        if stage_number is None:
            selected = [
                TeachingStage(index, total, stage, runbook.lab_name, runbook.route)
                for index, stage in enumerate(runbook.stages, start=1)
            ]
        else:
            if stage_number < 1 or stage_number > total:
                raise ValueError(f"Stage must be between 1 and {total}.")
            selected = [
                TeachingStage(
                    stage_number,
                    total,
                    runbook.stages[stage_number - 1],
                    runbook.lab_name,
                    runbook.route,
                )
            ]
        return TeachingSession(runbook=runbook, stages=selected)
