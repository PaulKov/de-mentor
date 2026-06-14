"""Student-facing self-service command guides."""

from __future__ import annotations

from dataclasses import dataclass

from mentor_lab.domain import LabDefinition


@dataclass(frozen=True)
class StudentPlatformProfile:
    """Command prefix and setup hints for one student OS."""

    label: str
    python_command: str
    setup_notes: tuple[str, ...]


class StudentSelfServiceGuide:
    """Renders bootstrap and homework instructions without side effects."""

    _PROFILES = {
        "macos": StudentPlatformProfile(
            label="macOS",
            python_command="python3",
            setup_notes=("Docker Desktop", "Terminal", "Git", "Python 3.9+"),
        ),
        "windows": StudentPlatformProfile(
            label="Windows",
            python_command="py",
            setup_notes=("Docker Desktop", "WSL 2", "PowerShell", "Git", "Python 3.9+"),
        ),
        "linux": StudentPlatformProfile(
            label="Linux",
            python_command="python3",
            setup_notes=("Docker Engine", "Docker Compose plugin", "Git", "Python 3.9+"),
        ),
    }

    def bootstrap(self, lab: LabDefinition, platform: str) -> str:
        profile = self._PROFILES[platform]
        prefix = profile.python_command
        lines = [
            f"Student bootstrap: {lab.name}",
            f"Platform: {profile.label}",
            "",
            "Prepare:",
        ]
        lines.extend(f"- {note}" for note in profile.setup_notes)
        lines.extend(
            [
                "",
                "Commands:",
                f"  {prefix} mentor-lab.py doctor --full",
                f"  {prefix} mentor-lab.py readiness {lab.name} --platform {platform}",
                f"  {prefix} mentor-lab.py runbook {lab.name} prep",
                f"  {prefix} mentor-lab.py academy {lab.name} start --student <your-name>",
                "",
                "Docs:",
                "  docs/lessons/01-greenplum/runbooks/student-prep.md",
                "  labs/greenplum/README.md",
            ]
        )
        return "\n".join(lines) + "\n"

    def homework(self, lab: LabDefinition) -> str:
        lines = [
            f"Student homework: {lab.name}",
            "",
            "Read:",
            "  docs/lessons/01-greenplum/homework.md",
            "  docs/lessons/01-greenplum/runbooks/homework-plan.md",
            "  docs/lessons/01-greenplum/student-workbook.md",
            "",
            "Self-check commands:",
            f"  python3 mentor-lab.py runbook {lab.name} homework",
            f"  python3 mentor-lab.py check {lab.name}",
            f"  python3 mentor-lab.py grade {lab.name} --dry-run",
            "",
            "Bring to Lesson 02:",
            "  DDL, distribution rationale, partitioning rationale, skew checks, EXPLAIN evidence.",
        ]
        return "\n".join(lines) + "\n"
