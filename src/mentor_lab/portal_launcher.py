"""Cross-repository launch helpers for the Nuxt Academy portal."""

from __future__ import annotations

import shutil
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List


@dataclass(frozen=True)
class PortalLaunchPlan:
    """Rendered commands needed to run the Nuxt portal for one session."""

    session_file: Path
    portal_dir: Path
    url: str
    commands: List[str]

    def render(self) -> str:
        lines = [
            "Portal start plan",
            f"- Session: {self.session_file}",
            f"- Portal directory: {self.portal_dir}",
            f"- URL: {self.url}",
            "",
            "Commands:",
        ]
        lines.extend(f"  {command}" for command in self.commands)
        return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class PortalExportResult:
    """Files written for a local portal checkout."""

    session_file: Path
    env_file: Path


class PortalLauncher:
    """Builds and applies portal launch plans without owning CLI concerns."""

    def build_start_plan(
        self,
        session_path: Path,
        portal_dir: Path,
        host: str = "127.0.0.1",
        port: int = 3000,
    ) -> PortalLaunchPlan:
        session_file = self.resolve_session_file(session_path)
        url = f"http://{host}:{port}"
        return PortalLaunchPlan(
            session_file=session_file,
            portal_dir=portal_dir,
            url=url,
            commands=[
                f"cd {portal_dir}",
                "npm ci",
                f"MENTOR_LAB_SESSION={session_file} npm run dev -- --host {host} --port {port}",
            ],
        )

    def export_session(self, session_path: Path, portal_dir: Path) -> PortalExportResult:
        session_file = self.resolve_session_file(session_path)
        public_dir = portal_dir / "public"
        public_dir.mkdir(parents=True, exist_ok=True)
        exported_session = public_dir / "session.json"
        shutil.copyfile(session_file, exported_session)
        env_file = self.write_env_file(portal_dir, session_file)
        return PortalExportResult(session_file=exported_session, env_file=env_file)

    def write_env_file(self, portal_dir: Path, session_file: Path) -> Path:
        portal_dir.mkdir(parents=True, exist_ok=True)
        env_file = portal_dir / ".env"
        env_file.write_text(f"MENTOR_LAB_SESSION={session_file}\n", encoding="utf-8")
        return env_file

    def open_url(
        self,
        url: str,
        opener: Callable[[str], bool] = webbrowser.open,
    ) -> bool:
        return opener(url)

    def resolve_session_file(self, session_path: Path) -> Path:
        session_file = session_path / "session.json" if session_path.is_dir() else session_path
        if not session_file.exists():
            raise FileNotFoundError(f"Session file does not exist: {session_file}")
        return session_file
