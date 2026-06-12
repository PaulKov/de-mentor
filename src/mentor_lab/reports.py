"""Markdown mentor reports for lesson outcomes."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from mentor_lab.checks import CheckResult, CheckStatus
from mentor_lab.grading import Grade


class MentorReport:
    """Writes a concise Markdown report for mentor follow-up."""

    @staticmethod
    def default_path(lesson_code: str) -> Path:
        return Path("reports") / f"{lesson_code}-report.md"

    def write(
        self,
        path: Path,
        lesson_code: str,
        checks: Iterable[CheckResult],
        grade: Grade,
    ) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        check_list = list(checks)
        path.write_text(
            self._render(lesson_code, check_list, grade),
            encoding="utf-8",
        )
        return path

    def _render(
        self,
        lesson_code: str,
        checks: Iterable[CheckResult],
        grade: Grade,
    ) -> str:
        lines = [
            f"# Mentor Report: {lesson_code}",
            "",
            f"Generated at: {datetime.now(timezone.utc).isoformat()}",
            "",
            f"Score: {grade.score}/100",
            f"Level: {grade.level}",
            "",
            "## Skill Matrix",
            "",
        ]
        for skill, score in grade.skill_scores.items():
            lines.append(f"- {skill}: {score}")

        lines.extend(["", "## Checks", ""])
        for check in checks:
            marker = "PASS" if check.status == CheckStatus.PASS else "FAIL"
            lines.append(f"- {marker} `{check.code}`: {check.title} - {check.detail}")
            if check.remediation:
                lines.append(f"  Remediation: {check.remediation}")

        lines.extend(["", "## Next Actions", ""])
        if grade.next_actions:
            for action in grade.next_actions:
                lines.append(f"- {action}")
        else:
            lines.append("- Move to the capstone review and ask the student to defend trade-offs.")

        return "\n".join(lines) + "\n"

