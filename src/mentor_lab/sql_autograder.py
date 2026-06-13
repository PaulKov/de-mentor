"""Evidence-first SQL autograder for Greenplum submissions."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class SqlGradeCriterion:
    code: str
    title: str
    weight: int
    signals: List[str]
    remediation: str

    def passed(self, normalized_submission: str) -> bool:
        return all(signal.lower() in normalized_submission for signal in self.signals)


@dataclass(frozen=True)
class SqlGradeItem:
    criterion: SqlGradeCriterion
    passed: bool


@dataclass(frozen=True)
class SqlAutogradeResult:
    lab_name: str
    score: int
    items: List[SqlGradeItem]
    live_output: str = ""

    @property
    def accepted(self) -> bool:
        return self.score >= 85

    @property
    def passed_codes(self) -> List[str]:
        return [item.criterion.code for item in self.items if item.passed]

    def render(self) -> str:
        lines = [
            f"# Real SQL Autograde: {self.lab_name}",
            "",
            f"Score: {self.score}/100",
            f"Accepted: {'yes' if self.accepted else 'no'}",
            "",
            "## Проверки",
            "| Code | Вес | Статус | Что проверяем |",
            "|---|---:|---|---|",
        ]
        for item in self.items:
            status = "PASS" if item.passed else "FAIL"
            lines.append(
                "| "
                f"{item.criterion.code} | {item.criterion.weight} | {status} | "
                f"{item.criterion.title} |"
            )
        missing = [item for item in self.items if not item.passed]
        if missing:
            lines.extend(["", "## Что Исправить"])
            lines.extend(f"- {item.criterion.remediation}" for item in missing)
        if self.live_output:
            lines.extend(["", "## Live SQL Output", "```text", self.live_output.strip(), "```"])
        lines.extend(
            [
                "",
                "## Следующий Шаг",
                (
                    "- Если Accepted: yes, переходи к Lesson 02 partitioning/statistics."
                    if self.accepted
                    else "- Добавь недостающие evidence markers и прогони autograde повторно."
                ),
                "",
            ]
        )
        return "\n".join(lines)


class SqlSubmissionGrader:
    """Grades submitted SQL or markdown by required Greenplum evidence markers."""

    _SUPPORTED_LABS = {"greenplum"}

    @classmethod
    def default(cls) -> "SqlSubmissionGrader":
        return cls(
            [
                SqlGradeCriterion(
                    "distributed_by",
                    "DDL содержит `DISTRIBUTED BY` для MPP data placement.",
                    15,
                    ["distributed by"],
                    "Добавь явный `DISTRIBUTED BY (...)` и объясни join/locality rationale.",
                ),
                SqlGradeCriterion(
                    "partition_by_range",
                    "DDL содержит `PARTITION BY RANGE` для pruning/retention.",
                    15,
                    ["partition by range"],
                    "Добавь `PARTITION BY RANGE (...)` и привяжи его к filter/retention workload.",
                ),
                SqlGradeCriterion(
                    "aoco_storage",
                    "Storage выбран явно: AOCO через appendoptimized/orientation.",
                    15,
                    ["appendoptimized=true", "orientation=column"],
                    "Добавь storage choice: `appendoptimized=true, orientation=column` для append fact.",
                ),
                SqlGradeCriterion(
                    "explain_analyze",
                    "Есть план или runtime evidence через `EXPLAIN ANALYZE`.",
                    15,
                    ["explain analyze"],
                    "Добавь `EXPLAIN ANALYZE` для ключевого запроса.",
                ),
                SqlGradeCriterion(
                    "segment_evidence",
                    "Есть проверка распределения через `gp_segment_id`.",
                    15,
                    ["gp_segment_id"],
                    "Добавь segment-level check с `gp_segment_id` и row counts.",
                ),
                SqlGradeCriterion(
                    "statistics_refresh",
                    "Есть `ANALYZE` или policy обновления статистики.",
                    10,
                    ["analyze"],
                    "Добавь `ANALYZE` после load или обоснуй statistics policy.",
                ),
                SqlGradeCriterion(
                    "validation_before_after",
                    "Есть validation before/after после изменения.",
                    15,
                    ["validation", "before/after"],
                    "Добавь before/after comparison: plan shape, row counts или skew spread.",
                ),
            ]
        )

    def __init__(self, criteria: Iterable[SqlGradeCriterion]) -> None:
        self._criteria = list(criteria)

    def grade_file(
        self,
        lab_name: str,
        submission_path: Path,
        live_output: str = "",
    ) -> SqlAutogradeResult:
        return self.grade_text(
            lab_name,
            submission_path.read_text(encoding="utf-8"),
            live_output=live_output,
        )

    def grade_text(
        self,
        lab_name: str,
        submission: str,
        live_output: str = "",
    ) -> SqlAutogradeResult:
        normalized_lab = lab_name.lower()
        if normalized_lab not in self._SUPPORTED_LABS:
            raise KeyError(f"Unknown SQL autograde lab: {lab_name}")
        normalized_submission = _normalize_sql(submission)
        items = [
            SqlGradeItem(criterion, criterion.passed(normalized_submission))
            for criterion in self._criteria
        ]
        score = sum(item.criterion.weight for item in items if item.passed)
        return SqlAutogradeResult(
            lab_name=normalized_lab,
            score=score,
            items=items,
            live_output=live_output,
        )


def build_transactional_sql(submission: str) -> str:
    """Wraps user SQL so live checks can be run without persisting changes."""

    return "\n".join(
        [
            "BEGIN;",
            submission.strip().rstrip(";") + ";",
            "ROLLBACK;",
        ]
    )


def _normalize_sql(submission: str) -> str:
    return " ".join(submission.lower().replace("\n", " ").split())
