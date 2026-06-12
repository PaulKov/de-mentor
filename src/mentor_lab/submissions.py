"""Student submission templates and lightweight evidence review."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class SubmissionReview:
    score: int
    skill_hits: List[str]
    missing_evidence: List[str]

    def render(self) -> str:
        lines = ["# Submission review", "", f"Score: {self.score}/100", ""]
        lines.append("## Skill hits")
        for skill in self.skill_hits or ["No skill evidence detected"]:
            lines.append(f"- {skill}")
        lines.extend(["", "## Missing evidence"])
        for item in self.missing_evidence or ["No required evidence missing"]:
            lines.append(f"- {item}")
        return "\n".join(lines) + "\n"


class SubmissionTemplate:
    """Writes assignment templates that force evidence-first answers."""

    _TEMPLATES: Dict[str, str] = {
        "advanced-joins": """# Submission: Advanced Joins

## EXPLAIN evidence

Paste plan fragments for:

- bad customer join with `Redistribute Motion`;
- good customer join;
- product join with `Broadcast Motion`.

## Segment evidence

Paste `gp_segment_id` distribution checks.

## RCA

Explain how distribution key, join key, Hash Join, Broadcast Motion and Redistribute Motion interact.
""",
        "query-tuning": """# Submission: Query Tuning Lab

## Symptom

## EXPLAIN evidence

## Change

## Validation
""",
    }

    @classmethod
    def default(cls) -> "SubmissionTemplate":
        return cls()

    def write(self, path: Path, assignment: str) -> Path:
        try:
            content = self._TEMPLATES[assignment]
        except KeyError as exc:
            available = ", ".join(sorted(self._TEMPLATES))
            raise KeyError(
                f"Unknown assignment '{assignment}'. Available assignments: {available}."
            ) from exc
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class SubmissionReviewer:
    """Scores submitted markdown by checking for required evidence markers."""

    _CRITERIA = {
        "EXPLAIN literacy": ["Redistribute Motion", "Broadcast Motion", "Hash Join"],
        "MPP diagnostics": ["gp_segment_id"],
        "Architecture communication": ["RCA", "distribution key", "join key"],
    }

    @classmethod
    def default(cls) -> "SubmissionReviewer":
        return cls()

    def review(self, path: Path) -> SubmissionReview:
        content = path.read_text(encoding="utf-8")
        total = sum(len(markers) for markers in self._CRITERIA.values())
        hits = 0
        skill_hits: List[str] = []
        missing: List[str] = []
        for skill, markers in self._CRITERIA.items():
            skill_hit = False
            for marker in markers:
                if marker.lower() in content.lower():
                    hits += 1
                    skill_hit = True
                else:
                    missing.append(marker)
            if skill_hit:
                skill_hits.append(skill)
        return SubmissionReview(
            score=round(hits * 100 / total),
            skill_hits=skill_hits,
            missing_evidence=missing,
        )
