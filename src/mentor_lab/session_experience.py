"""Academy Experience session orchestration facade."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from mentor_lab.control_plane import ControlPlaneBuilder
from mentor_lab.session_contract import PORTAL_FRAMEWORK
from mentor_lab.session_defaults import (
    _default_commands,
    _default_skill_graph,
    _default_stages,
)
from mentor_lab.session_model import (
    AcademySession,
    ACADEMY_VERSION,
    SessionEvent,
    SessionStage,
    SkillNode,
    _timestamp,
)
from mentor_lab.session_renderers import (
    _render_mentor_cockpit,
    _render_report,
    _render_skill_graph,
    _render_student_handoff,
    _render_timeline,
)

class SessionManager:
    """Creates and updates session artifacts for the Academy Experience portal."""

    def start(
        self,
        lab_name: str,
        student_name: str,
        output_dir: Optional[Path] = None,
    ) -> Path:
        session_dir = output_dir or Path("artifacts") / "sessions" / _session_slug(
            lab_name,
            student_name,
        )
        session_dir.mkdir(parents=True, exist_ok=True)
        session = AcademySession(
            lab_name=lab_name,
            student_name=student_name,
            created_at=_timestamp(),
            stages=_default_stages(lab_name),
            skill_graph=_default_skill_graph(),
            commands=_default_commands(lab_name),
            control_plane=ControlPlaneBuilder().build(lab_name).to_dict(),
            events=[
                SessionEvent.create(
                    "session-start",
                    f"Сессия {ACADEMY_VERSION} создана для {student_name}.",
                )
            ],
        )
        self._write_session(session_dir, session)
        return session_dir

    def record_event(self, session_dir: Path, event_type: str, note: str) -> Path:
        session = self.load(session_dir)
        session.events.append(SessionEvent.create(event_type, note))
        self._write_session(session_dir, session)
        return session_dir / "timeline.md"

    def report(self, session_dir: Path, output: Optional[Path] = None) -> str:
        session = self.load(session_dir)
        rendered = _render_report(session)
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
        return rendered

    def load(self, session_dir: Path) -> AcademySession:
        path = session_dir / "session.json"
        if not path.exists():
            raise FileNotFoundError(f"Session file does not exist: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        return AcademySession.from_dict(payload)

    def _write_session(self, session_dir: Path, session: AcademySession) -> None:
        payload = session.to_dict()
        (session_dir / "session.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (session_dir / "timeline.md").write_text(
            _render_timeline(session),
            encoding="utf-8",
        )
        (session_dir / "skill-graph.md").write_text(
            _render_skill_graph(session),
            encoding="utf-8",
        )
        (session_dir / "mentor-cockpit.md").write_text(
            _render_mentor_cockpit(session, session_dir),
            encoding="utf-8",
        )
        (session_dir / "student-handoff.md").write_text(
            _render_student_handoff(session, session_dir),
            encoding="utf-8",
        )


def _session_slug(lab_name: str, student_name: str) -> str:
    clean_student = "".join(
        char.lower() if char.isalnum() else "-"
        for char in student_name.strip()
    ).strip("-") or "student"
    return f"{lab_name}-{clean_student}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
