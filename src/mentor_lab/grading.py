"""Rubric and grade calculation for lesson checks."""

from dataclasses import dataclass
from typing import Dict, Iterable, List

from mentor_lab.checks import CheckResult, CheckStatus


@dataclass(frozen=True)
class Grade:
    lesson_code: str
    score: int
    level: str
    skill_scores: Dict[str, int]
    next_actions: List[str]


class GradeCalculator:
    """Maps check results to a mentor-friendly score and skill matrix."""

    _WEIGHTS = {
        "greenplum_connection": ("Environment readiness", 10),
        "lesson_schema": ("Environment readiness", 10),
        "seed_data": ("Data setup", 10),
        "bad_distribution_skew": ("MPP diagnostics", 20),
        "good_distribution_balance": ("Distribution design", 25),
        "motion_plan": ("EXPLAIN literacy", 25),
    }

    @classmethod
    def default(cls) -> "GradeCalculator":
        return cls()

    def calculate(self, lesson_code: str, checks: Iterable[CheckResult]) -> Grade:
        score = 0
        skill_scores: Dict[str, int] = {}
        next_actions: List[str] = []

        for check in checks:
            skill, weight = self._WEIGHTS.get(check.code, ("Other", 0))
            if check.status == CheckStatus.PASS:
                score += weight
                skill_scores[skill] = skill_scores.get(skill, 0) + weight
            else:
                skill_scores.setdefault(skill, 0)
                if check.remediation:
                    next_actions.append(check.remediation)

        return Grade(
            lesson_code=lesson_code,
            score=score,
            level=_level(score),
            skill_scores=skill_scores,
            next_actions=next_actions,
        )


def _level(score: int) -> str:
    if score >= 90:
        return "Production-ready"
    if score >= 70:
        return "Solid"
    if score >= 50:
        return "Developing"
    return "Needs practice"

