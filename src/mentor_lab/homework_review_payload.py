"""Structured homework review payload for the mentor portal."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from mentor_lab.homework_review import HomeworkReview, HomeworkReviewer


@dataclass(frozen=True)
class SqlSnippet:
    """Copy-ready SQL or CLI snippet for screen-shared homework review."""

    title: str
    command: str
    explanation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "command": self.command,
            "explanation": self.explanation,
        }


class HomeworkReviewPayloadBuilder:
    """Builds `homework_review` for `academy-session/v1`."""

    _SUPPORTED_LESSONS = {"lesson-01"}

    def __init__(self, reviewer: HomeworkReviewer | None = None) -> None:
        self._reviewer = reviewer or HomeworkReviewer.default()

    def build(
        self,
        lesson_code: str,
        submission_path: Optional[Path] = None,
    ) -> dict[str, Any]:
        if lesson_code not in self._SUPPORTED_LESSONS:
            supported = ", ".join(sorted(self._SUPPORTED_LESSONS))
            raise ValueError(
                f"Unsupported homework review lesson '{lesson_code}'. "
                f"Supported lessons: {supported}."
            )

        review = self._review(submission_path)
        return {
            "lesson_code": lesson_code,
            "title": "Lesson 01 Homework Walkthrough",
            "submission_status": "submitted" if submission_path else "not_submitted",
            "submission_path": str(submission_path or ""),
            "score": review.score,
            "accepted": review.accepted,
            "rubric_items": self._rubric_items(review),
            "missing_evidence": review.missing,
            "next_actions": review.next_actions,
            "live_checklist": _live_checklist(),
            "sql_snippets": [snippet.to_dict() for snippet in _sql_snippets()],
            "mentor_conclusion": _mentor_conclusion(review, bool(submission_path)),
            "next_lesson_plan": _next_lesson_plan(),
        }

    def _review(self, submission_path: Optional[Path]) -> HomeworkReview:
        if submission_path is None:
            return self._reviewer.review_text("")
        return self._reviewer.review(submission_path)

    def _rubric_items(self, review: HomeworkReview) -> list[dict[str, Any]]:
        items = []
        for criterion in self._reviewer.criteria():
            score = review.skill_scores[criterion.name]
            items.append(
                {
                    "code": _slug(criterion.name),
                    "title": criterion.name,
                    "score": score,
                    "passed": score >= 80,
                    "expected_evidence": ", ".join(criterion.markers),
                    "mentor_prompt": criterion.guidance,
                    "conclusion_hint": _conclusion_hint(score, criterion.name),
                }
            )
        return items


def _live_checklist() -> list[dict[str, Any]]:
    return [
        _check("context", "Понять, что ученик пытался спроектировать."),
        _check("rubric", "Пройти rubric по одному пункту, не прыгая сразу к оценке."),
        _check("evidence", "Попросить evidence: DDL, EXPLAIN, gp_segment_id, catalog checks."),
        _check("repair", "Показать, как закрыть самый важный gap прямо на уроке."),
        _check("handoff", "Сформулировать понятный план до Lesson 02."),
    ]


def _check(code: str, label: str) -> dict[str, Any]:
    return {"code": code, "label": label, "done": False}


def _sql_snippets() -> list[SqlSnippet]:
    return [
        SqlSnippet(
            "Проверить домашку CLI",
            "python3 mentor-lab.py homework greenplum check --submission lessons/lesson-01/submissions/homework.md",
            "Показывает score, missing evidence и Lesson 02 readiness.",
        ),
        SqlSnippet(
            "Сегментный skew",
            "SELECT gp_segment_id, count(*) FROM lesson01.fact_sales_good GROUP BY gp_segment_id ORDER BY gp_segment_id;",
            "Объясняет, почему evidence через gp_segment_id обязателен для MPP.",
        ),
        SqlSnippet(
            "EXPLAIN для Motion",
            "EXPLAIN SELECT customer_id, sum(amount) FROM lesson01.fact_sales_good GROUP BY customer_id;",
            "Фиксирует привычку доказывать физический план, а не только писать DDL.",
        ),
        SqlSnippet(
            "Storage demo",
            "\\i /mentor-lab/examples/storage-and-partitioning.sql",
            "Возвращает ученика к heap/AO/AOCO и catalog checks.",
        ),
    ]


def _mentor_conclusion(review: HomeworkReview, submitted: bool) -> dict[str, str]:
    if not submitted:
        return {
            "decision": "needs_guided_walkthrough",
            "summary": "Домашка не была сдана: разбор проводим как guided walkthrough.",
            "recommendation": "Закрыть ключевые evidence gaps вместе и выдать короткий план до Lesson 02.",
        }
    if review.accepted:
        return {
            "decision": "ready_for_lesson_02",
            "summary": "Домашка принята: evidence достаточно для перехода к Lesson 02.",
            "recommendation": "На следующем уроке усложнить partition pruning, statistics и incremental loads.",
        }
    return {
        "decision": "needs_follow_up",
        "summary": "Домашка требует доработки перед уверенным переходом к Lesson 02.",
        "recommendation": "Выбрать один самый дорогой gap и закрыть его live через SQL/evidence.",
    }


def _next_lesson_plan() -> dict[str, Any]:
    return {
        "lesson_code": "lesson-02",
        "title": "Partitioning, statistics and incremental loads in MPP",
        "focus": "Partition pruning, statistics after load, incremental loads and late-arriving facts.",
        "action_items": [
            "Повторить difference: partition key != distribution key.",
            "Принести EXPLAIN/catalog evidence по исправленной домашке.",
            "Подготовить вопросы про ANALYZE и bounded reload window.",
        ],
        "commands": [
            "python3 mentor-lab.py runbook greenplum-partitioning simple",
            "python3 mentor-lab.py student greenplum-partitioning homework",
        ],
    }


def _conclusion_hint(score: int, title: str) -> str:
    if score >= 80:
        return f"{title}: evidence достаточно, можно закрепить как сильную сторону."
    return f"{title}: нужно показать конкретный артефакт, а не только объяснение."


def _slug(value: str) -> str:
    return value.lower().replace("/", "-").replace(" ", "-")
