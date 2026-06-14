"""Full environment doctor guidance for Academy self-service flows."""

from __future__ import annotations

from dataclasses import dataclass

from mentor_lab.session_contract import PORTAL_APP_PATH, PORTAL_REPOSITORY


@dataclass(frozen=True)
class DoctorCheckGroup:
    """One group of commands a user can run to validate their environment."""

    title: str
    commands: tuple[str, ...]

    def render(self) -> str:
        lines = [self.title]
        lines.extend(f"  {command}" for command in self.commands)
        return "\n".join(lines)


class FullDoctorReport:
    """Renders the full local readiness checklist for mentor and student modes."""

    def render(self) -> str:
        groups = [
            DoctorCheckGroup(
                "Core repo",
                (
                    "python3 --version",
                    "git status --short",
                    "python3 -m pytest tests -q",
                    "python3 -m compileall -q src mentor-lab.py",
                ),
            ),
            DoctorCheckGroup(
                "Docker Compose",
                (
                    "docker --version",
                    "docker compose version",
                    "python3 mentor-lab.py up greenplum --dry-run",
                    "python3 mentor-lab.py check greenplum --dry-run",
                ),
            ),
            DoctorCheckGroup(
                "Portal repo",
                (
                    f"git clone {PORTAL_REPOSITORY}.git {PORTAL_APP_PATH}",
                    f"cd {PORTAL_APP_PATH}",
                    "npm ci",
                    "npm run check",
                ),
            ),
            DoctorCheckGroup(
                "Quality guard",
                (
                    "python3 -m pytest tests/test_quality_guards.py -q",
                    "SLOC <= 400 per module",
                    "avg clustering <= 0.180",
                ),
            ),
        ]
        lines = [
            "Full environment doctor",
            "",
            "Run these checks before a professional lesson delivery.",
            "",
        ]
        for group in groups:
            lines.append(group.render())
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"
