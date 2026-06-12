"""Adaptive rubric scoring for student evidence submissions."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class AdaptiveReview:
    score: int
    skill_scores: Dict[str, int]
    missing: List[str]
    next_task: str

    def render(self) -> str:
        lines = ["# Adaptive review", "", f"Score: {self.score}/100", ""]
        lines.append("## Skill scores")
        for skill, score in self.skill_scores.items():
            lines.append(f"- {skill}: {score}")
        lines.extend(["", "## Missing evidence"])
        for item in self.missing or ["No required evidence missing"]:
            lines.append(f"- {item}")
        lines.extend(["", "## Recommended next task", f"- {self.next_task}"])
        return "\n".join(lines) + "\n"


class AdaptiveReviewer:
    """Scores reasoning quality, not just keyword presence."""

    _RUBRIC = {
        "EXPLAIN evidence": ["Redistribute Motion", "Hash Join"],
        "Segment diagnostics": ["gp_segment_id"],
        "Root cause reasoning": ["Physical cause", "distribution key", "join key"],
        "Change design": ["Change", "DISTRIBUTED BY"],
        "Validation": ["Validation", "EXPLAIN ANALYZE"],
        "Risk awareness": ["Residual risk", "Broadcast Motion"],
    }

    @classmethod
    def default(cls) -> "AdaptiveReviewer":
        return cls()

    def review(self, path: Path) -> AdaptiveReview:
        content = path.read_text(encoding="utf-8")
        content_lower = content.lower()
        skill_scores: Dict[str, int] = {}
        missing: List[str] = []

        for skill, markers in self._RUBRIC.items():
            hits = sum(1 for marker in markers if marker.lower() in content_lower)
            for marker in markers:
                if marker.lower() not in content_lower:
                    missing.append(marker)
            skill_scores[skill] = round(hits * 100 / len(markers))

        score = round(sum(skill_scores.values()) / len(skill_scores))
        return AdaptiveReview(
            score=score,
            skill_scores=skill_scores,
            missing=missing,
            next_task=_next_task(score, missing),
        )


def _next_task(score: int, missing: List[str]) -> str:
    if score >= 90:
        return "Run the hard timed challenge and explain coordinator risk."
    if any("Broadcast" in item or "Redistribute" in item for item in missing):
        return "Repeat Broadcast vs Redistribute plan reading with the visualizer."
    if any("Validation" in item or "EXPLAIN ANALYZE" in item for item in missing):
        return "Add before/after validation evidence to the submission."
    return "Redo the scenario with a stricter evidence contract."
