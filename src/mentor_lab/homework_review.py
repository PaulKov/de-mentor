"""Evidence-first homework review for Greenplum lesson 01."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class HomeworkCriterion:
    name: str
    markers: List[str]
    guidance: str

    def score(self, content_lower: str) -> int:
        hits = sum(1 for marker in self.markers if marker.lower() in content_lower)
        return round(hits * 100 / len(self.markers))


@dataclass(frozen=True)
class HomeworkReview:
    score: int
    accepted: bool
    skill_scores: Dict[str, int]
    missing: List[str]
    next_actions: List[str]

    def render(self) -> str:
        lines = [
            "# Homework review",
            "",
            f"Score: {self.score}/100",
            f"Accepted: {'yes' if self.accepted else 'no'}",
            "",
            "## Skill scores",
        ]
        for skill, score in self.skill_scores.items():
            lines.append(f"- {skill}: {score}/100")
        lines.extend(["", "## Missing evidence"])
        for item in self.missing or ["No missing evidence"]:
            lines.append(f"- {item}")
        lines.extend(["", "## Lesson 02 readiness"])
        for action in self.next_actions:
            lines.append(f"- {action}")
        return "\n".join(lines) + "\n"


class HomeworkReviewer:
    """Scores homework for physical-design evidence, not prose volume."""

    _ACCEPTANCE_SCORE = 80
    _MISSING_THRESHOLD = 60
    _CRITERIA = [
        HomeworkCriterion(
            "Fact/dimension modeling",
            ["fact", "dimension", "grain"],
            "зафиксировать facts, dimensions и grain до выбора ключей",
        ),
        HomeworkCriterion(
            "Distribution design",
            ["distribution", "distributed by", "join pattern", "cardinality"],
            "обосновать distribution key через join pattern и cardinality",
        ),
        HomeworkCriterion(
            "Partitioning design",
            ["partition", "partition by", "partition key", "distribution key"],
            "развести partition key и distribution key, показать pruning workload",
        ),
        HomeworkCriterion(
            "Storage design",
            ["storage", "aoco", "appendoptimized", "orientation=column"],
            "выбрать heap/AO/AOCO под workload и объяснить компромисс",
        ),
        HomeworkCriterion(
            "Catalog evidence",
            ["pg_partition_tree", "gp_toolkit.gp_partitions", "leaf_partitions"],
            "добавить catalog evidence по partitions",
        ),
        HomeworkCriterion(
            "EXPLAIN/gp_segment_id evidence",
            ["explain", "gp_segment_id", "validation"],
            "доказать дизайн через EXPLAIN, gp_segment_id и before/after validation",
        ),
        HomeworkCriterion(
            "Risk analysis",
            ["risk", "stale statistics", "broadcast motion", "residual risk"],
            "описать риски: stale stats, Broadcast Motion, skew и coordinator path",
        ),
        HomeworkCriterion(
            "Lesson 02 readiness",
            ["lesson 02", "partition pruning", "statistics", "incremental loads"],
            "принести вопросы по partition pruning, statistics и incremental loads",
        ),
    ]

    @classmethod
    def default(cls) -> "HomeworkReviewer":
        return cls(cls._CRITERIA)

    def __init__(self, criteria: Iterable[HomeworkCriterion]) -> None:
        self._criteria = list(criteria)

    def review(self, path: Path) -> HomeworkReview:
        return self.review_text(path.read_text(encoding="utf-8"))

    def review_text(self, content: str) -> HomeworkReview:
        content_lower = content.lower()
        skill_scores = {
            criterion.name: criterion.score(content_lower)
            for criterion in self._criteria
        }
        score = round(sum(skill_scores.values()) / len(skill_scores))
        missing = [
            criterion.name
            for criterion in self._criteria
            if skill_scores[criterion.name] < self._MISSING_THRESHOLD
        ]
        return HomeworkReview(
            score=score,
            accepted=score >= self._ACCEPTANCE_SCORE and not missing,
            skill_scores=skill_scores,
            missing=missing,
            next_actions=_next_actions(self._criteria, skill_scores),
        )


def _next_actions(
    criteria: Iterable[HomeworkCriterion],
    skill_scores: Dict[str, int],
) -> List[str]:
    actions = [
        criterion.guidance
        for criterion in criteria
        if skill_scores[criterion.name] < HomeworkReviewer._ACCEPTANCE_SCORE
    ]
    if actions:
        return actions
    return [
        "перейти к Lesson 02: partition pruning, statistics after load и incremental loads",
        "усложнить работу через late-arriving facts и AOCO partitions",
    ]
