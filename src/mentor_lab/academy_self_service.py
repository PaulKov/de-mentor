"""One-command Academy lesson bootstrap orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from mentor_lab.docker_compose import DockerComposeRunner
from mentor_lab.domain import LabDefinition
from mentor_lab.portal_launcher import PortalLauncher
from mentor_lab.session_experience import SessionManager


@dataclass(frozen=True)
class AcademyStartOptions:
    """User-facing parameters for starting a lesson workspace."""

    student: str
    session_dir: Path
    portal_dir: Path
    route: str = "simple"
    platform: str = "macos"
    host: str = "127.0.0.1"
    port: int = 3000
    dry_run: bool = False
    skip_lab: bool = False


@dataclass(frozen=True)
class AcademyStartResult:
    """Rendered outcome of an Academy start command."""

    session_dir: Path
    portal_dir: Path
    plan: str
    messages: List[str]
    exit_code: int = 0

    def render(self) -> str:
        lines = [*self.messages, "", self.plan]
        return "\n".join(line for line in lines if line is not None).rstrip() + "\n"


class AcademySelfService:
    """Coordinates session, lab and portal startup without owning CLI parsing."""

    def __init__(
        self,
        runner: DockerComposeRunner,
        session_manager: Optional[SessionManager] = None,
        portal_launcher: Optional[PortalLauncher] = None,
    ) -> None:
        self._runner = runner
        self._session_manager = session_manager or SessionManager()
        self._portal_launcher = portal_launcher or PortalLauncher()

    def start(self, lab: LabDefinition, options: AcademyStartOptions) -> AcademyStartResult:
        plan = self.render_plan(lab, options)
        if options.dry_run:
            return AcademyStartResult(
                session_dir=options.session_dir,
                portal_dir=options.portal_dir,
                plan=plan,
                messages=[],
                exit_code=0,
            )

        session_dir = self._session_manager.start(
            lab.name,
            options.student,
            options.session_dir,
        )
        export_result = self._portal_launcher.export_session(session_dir, options.portal_dir)
        messages = [
            f"Academy session prepared at {session_dir}",
            f"Portal state exported to {export_result.session_file}",
        ]
        if options.skip_lab:
            exit_code = 0
            messages.append("Lab start skipped by --skip-lab")
        else:
            exit_code = self._runner.run(self._runner.build_up_command(lab))
            if exit_code != 0:
                messages.append(f"Lab start failed with exit code {exit_code}")
        return AcademyStartResult(
            session_dir=session_dir,
            portal_dir=options.portal_dir,
            plan=plan,
            messages=messages,
            exit_code=exit_code,
        )

    def render_plan(self, lab: LabDefinition, options: AcademyStartOptions) -> str:
        session_file = options.session_dir / "session.json"
        portal_plan = self._portal_launcher.build_start_plan(
            session_file,
            options.portal_dir,
            host=options.host,
            port=options.port,
            require_existing=False,
        )
        lines = [
            "Academy self-service start plan",
            f"- Lab: {lab.name}",
            f"- Student: {options.student}",
            f"- Route: {options.route}",
            f"- Platform: {options.platform}",
            "",
            "Commands:",
            "  python3 mentor-lab.py doctor --full",
            f"  python3 mentor-lab.py session {lab.name} start --student {options.student} --output {options.session_dir}",
            f"  python3 mentor-lab.py up {lab.name}",
            f"  python3 mentor-lab.py portal {lab.name} export --session {options.session_dir} --portal-dir {options.portal_dir}",
            f"  python3 mentor-lab.py runbook {lab.name} {options.route}",
            "",
            "Portal:",
        ]
        lines.extend(f"  {command}" for command in portal_plan.commands)
        lines.extend(
            [
                "",
                "Student handoff:",
                f"  python3 mentor-lab.py student {lab.name} bootstrap --platform {options.platform}",
                f"  python3 mentor-lab.py student {lab.name} homework",
            ]
        )
        return "\n".join(lines)
