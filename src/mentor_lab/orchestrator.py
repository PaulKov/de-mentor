"""Mode-aware live lesson orchestration for mentor-led sessions."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from mentor_lab.runbooks import RunbookCatalog, RunbookStage


@dataclass(frozen=True)
class OrchestratorMode:
    code: str
    title: str
    timer_policy: str
    decision_rule: str
    next_action: str


@dataclass(frozen=True)
class OrchestratedStage:
    lab_name: str
    route: str
    stage_number: int
    total_stages: int
    mode: OrchestratorMode
    stage: RunbookStage

    def render(self) -> str:
        commands = "\n".join(f"- `{command}`" for command in self.stage.commands)
        links = "\n".join(f"- {link}" for link in self.stage.links)
        return "\n".join(
            [
                "# Live Lesson Orchestrator",
                "",
                f"Lab: {self.lab_name}",
                f"Route: {self.route}",
                f"Mode: {self.mode.code}",
                f"Stage: {self.stage_number}/{self.total_stages} - {self.stage.title}",
                f"Slides: {self.stage.slides}",
                f"Timebox: {self.stage.timebox}",
                f"timer: {self.mode.timer_policy}",
                "",
                "## Mentor script",
                self.stage.mentor_talk,
                "",
                "## Commands to show",
                commands or "- Нет команд на этом этапе.",
                "",
                "## Ask student",
                f"- Question: {self.stage.question}",
                f"- Expected answer: {self.stage.expected_answer}",
                "",
                "## Decision gate",
                f"- Check: {self.stage.check}",
                f"- Rule: {self.mode.decision_rule}",
                "",
                "## Next action",
                f"- {self.mode.next_action}",
                "",
                "## Evidence hooks",
                f"- `python3 mentor-lab.py observe {self.lab_name} start`",
                f"- `python3 mentor-lab.py evidence {self.lab_name} collect redistribute-join`",
                f"- `python3 mentor-lab.py debrief {self.lab_name} --student <name> --submission submissions/query-tuning.md`",
                "",
                "## Cross-links",
                links,
                "",
            ]
        )


class LiveLessonOrchestrator:
    """Builds a single-stage mentor control view from the runbook catalog."""

    _MODES: Dict[str, OrchestratorMode] = {
        "simple": OrchestratorMode(
            code="simple",
            title="Основной маршрут",
            timer_policy="держать базовый timebox, parking lot для deep questions",
            decision_rule="если ученик отвечает evidence-first, переходи к следующему этапу",
            next_action="продолжить простой маршрут и не открывать appendix без запроса ученика",
        ),
        "deep": OrchestratorMode(
            code="deep",
            title="Deep-dive маршрут",
            timer_policy="дать +5 минут на EXPLAIN/QD/QE детали и сверять cognitive load",
            decision_rule="если ученик связывает Motion, slice и gang, переходи к source anchors",
            next_action="добавить coach-plan и один source-level вопрос",
        ),
        "recovery": OrchestratorMode(
            code="recovery",
            title="Восстановление понимания",
            timer_policy="сократить объяснение до 3 минут и сразу дать мини-эксперимент",
            decision_rule="если ответ без SQL/evidence, повторить вопрос через конкретный план",
            next_action="показать одну команду, спросить вывод, затем вернуться к runbook",
        ),
        "fast-student": OrchestratorMode(
            code="fast-student",
            title="Сильный ученик",
            timer_policy="сжать базу и потратить высвободившееся время на hidden incident",
            decision_rule="если ученик быстро называет risk и validation, выдать hard scenario",
            next_action="перейти к timed challenge и попросить полный RCA",
        ),
    }

    @classmethod
    def default(cls) -> "LiveLessonOrchestrator":
        return cls(RunbookCatalog.default())

    def __init__(self, runbooks: RunbookCatalog) -> None:
        self._runbooks = runbooks

    def build(
        self,
        lab_name: str,
        route: str,
        stage_number: int,
        mode: str = "simple",
    ) -> OrchestratedStage:
        runbook = self._runbooks.get(lab_name, route)
        if stage_number < 1 or stage_number > len(runbook.stages):
            raise ValueError(f"Stage must be between 1 and {len(runbook.stages)}.")
        try:
            orchestrator_mode = self._MODES[mode]
        except KeyError as exc:
            available = ", ".join(sorted(self._MODES))
            raise KeyError(f"Unknown orchestrator mode '{mode}'. Available: {available}.") from exc
        return OrchestratedStage(
            lab_name=runbook.lab_name,
            route=runbook.route,
            stage_number=stage_number,
            total_stages=len(runbook.stages),
            mode=orchestrator_mode,
            stage=runbook.stages[stage_number - 1],
        )

    @classmethod
    def modes(cls) -> List[str]:
        return sorted(cls._MODES)
