"""Student-facing self-service command guides."""

from __future__ import annotations

from dataclasses import dataclass

from mentor_lab.domain import LabDefinition
from mentor_lab.lesson_routes import LearningRoute


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

    def bootstrap(self, lab: LabDefinition, route: LearningRoute, platform: str) -> str:
        profile = self._PROFILES[platform]
        prefix = profile.python_command
        lines = [
            f"Student bootstrap: {route.name}",
            f"Physical lab: {lab.name}",
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
                f"  {prefix} mentor-lab.py up {lab.name}",
                f"  {prefix} mentor-lab.py check {lab.name}",
                f"  {prefix} mentor-lab.py runbook {route.name} simple",
                f"  {prefix} mentor-lab.py academy {route.name} start --student <your-name>",
                "",
                "Docs:",
                f"  {route.prep_runbook_path}",
                f"  {route.workbook_path}",
                f"  {route.homework_path}",
                f"  {lab.docs_path}",
            ]
        )
        return "\n".join(lines) + "\n"

    def homework(self, lab: LabDefinition, route: LearningRoute) -> str:
        lines = [
            f"Student homework: {route.name}",
            f"Physical lab: {lab.name}",
            "",
            "Read:",
            f"  {route.homework_path}",
            f"  {route.docs_root}/runbooks/homework-plan.md",
            f"  {route.workbook_path}",
            "",
            "Self-check commands:",
            f"  python3 mentor-lab.py runbook {route.name} homework",
            f"  python3 mentor-lab.py check {lab.name}",
            f"  python3 mentor-lab.py grade {lab.name} --dry-run",
            "",
            f"Bring to {_lesson_label(route.next_lesson.code)}:",
            "  DDL, EXPLAIN evidence, partition catalog checks, statistics policy, validation.",
        ]
        return "\n".join(lines) + "\n"


def _lesson_label(code: str) -> str:
    if code.startswith("02-"):
        return "Lesson 02"
    if code.startswith("03-"):
        return "Lesson 03"
    return code
