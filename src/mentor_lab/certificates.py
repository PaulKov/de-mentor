"""Completion certificate artifact for lesson outcomes."""

from datetime import datetime, timezone
from pathlib import Path

from mentor_lab.grading import Grade


class CertificateWriter:
    """Writes a concise markdown completion artifact."""

    def write(self, path: Path, lab_name: str, grade: Grade) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._render(lab_name, grade), encoding="utf-8")
        return path

    def _render(self, lab_name: str, grade: Grade) -> str:
        lines = [
            "# Greenplum Lesson Completion",
            "",
            f"Lab: {lab_name}",
            f"Lesson: {grade.lesson_code}",
            f"Generated at: {datetime.now(timezone.utc).isoformat()}",
            "",
            f"Score: {grade.score}/100",
            f"Level: {grade.level}",
            "",
            "## Demonstrated Skills",
        ]
        for skill, score in grade.skill_scores.items():
            lines.append(f"- {skill}: {score}")
        lines.extend(
            [
                "",
                "## Next recommended challenge",
                "- Run `incident start greenplum slow-product-analytics` and submit an RCA.",
            ]
        )
        if grade.next_actions:
            lines.extend(["", "## Follow-up Actions"])
            for action in grade.next_actions:
                lines.append(f"- {action}")
        return "\n".join(lines) + "\n"
