"""Live lab observation checklists and evidence trail reports."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ObservationChecklist:
    lab_name: str

    def render(self) -> str:
        return "\n".join(
            [
                f"# Live Lab Observation: {self.lab_name}",
                "",
                "## Что фиксировать во время урока",
                "- Команды ученика и выводы, которые он сам проговорил.",
                "- EXPLAIN / EXPLAIN ANALYZE фрагменты с Motion, join, slice.",
                "- Segment evidence: `gp_segment_id`, skew ratio, row distribution.",
                "- Catalog evidence: storage, partitions, statistics freshness.",
                "- Misconception check: что ученик перепутал и какой мини-эксперимент помог.",
                "- Validation: before/after после изменения.",
                "",
                "## Быстрые команды",
                "```bash",
                f"python3 mentor-lab.py analyze-plan {self.lab_name} --query bad_customer_join --sample",
                f"python3 mentor-lab.py diagnostics {self.lab_name} show segment-skew",
                f"python3 mentor-lab.py misconception {self.lab_name} diagnose --text \"partition key это то же самое что distribution key\"",
                "```",
                "",
                "## Ручной лог",
                "- [ ] Ученик назвал symptom.",
                "- [ ] Ученик нашел Motion.",
                "- [ ] Ученик проверил `gp_segment_id`.",
                "- [ ] Ученик отделил partition key от distribution key.",
                "- [ ] Ученик сделал validation before/after.",
                "",
            ]
        )

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
        return path


@dataclass(frozen=True)
class ObservationReport:
    lab_name: str
    commands_path: Path
    command_text: str

    @property
    def has_explain(self) -> bool:
        return "explain" in self.command_text.lower() or "analyze-plan" in self.command_text

    @property
    def has_segment_evidence(self) -> bool:
        return "gp_segment_id" in self.command_text

    @property
    def has_misconception_check(self) -> bool:
        return "misconception" in self.command_text.lower()

    @property
    def has_validation(self) -> bool:
        lowered = self.command_text.lower()
        return "validation" in lowered or "before/after" in lowered or "explain analyze" in lowered

    def render(self) -> str:
        return "\n".join(
            [
                f"# Observation Report: {self.lab_name}",
                "",
                f"Commands log: `{self.commands_path.as_posix()}`",
                "",
                "## Evidence Coverage",
                f"- EXPLAIN evidence: {_yes_no(self.has_explain)}",
                f"- Segment evidence: {_yes_no(self.has_segment_evidence)}",
                f"- Misconception check: {_yes_no(self.has_misconception_check)}",
                f"- Validation evidence: {_yes_no(self.has_validation)}",
                "",
                "## Mentor Follow-up",
                "- Если EXPLAIN evidence отсутствует: начать следующий touchpoint с `coach-plan`.",
                "- Если segment evidence отсутствует: дать короткую проверку `gp_segment_id`.",
                "- Если misconception check отсутствует: спросить partition vs distribution и Motion cost.",
                "",
            ]
        )

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
        return path


class ObservationBuilder:
    """Creates observation artifacts without requiring a running database."""

    def start(self, lab_name: str) -> ObservationChecklist:
        return ObservationChecklist(lab_name=lab_name)

    def report(self, lab_name: str, commands_path: Path) -> ObservationReport:
        return ObservationReport(
            lab_name=lab_name,
            commands_path=commands_path,
            command_text=commands_path.read_text(encoding="utf-8"),
        )


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"
