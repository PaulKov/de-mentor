"""Stateful Academy Experience session artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


ACADEMY_VERSION = "Academy Experience v5"
PORTAL_FRAMEWORK = "Vue 3 + Nuxt 3 + Vite"
PORTAL_PATH = "apps/academy-portal"


@dataclass(frozen=True)
class SessionStage:
    """A visible lesson stage for the live portal and mentor timeline."""

    code: str
    title: str
    timebox: str
    mentor_focus: str
    student_action: str
    command: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "code": self.code,
            "title": self.title,
            "timebox": self.timebox,
            "mentor_focus": self.mentor_focus,
            "student_action": self.student_action,
            "command": self.command,
        }


@dataclass(frozen=True)
class SkillNode:
    """A single observable skill in the lesson skill graph."""

    code: str
    title: str
    level: str
    evidence: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "code": self.code,
            "title": self.title,
            "level": self.level,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class SessionEvent:
    """A timestamped event recorded during the lesson."""

    event_type: str
    note: str
    created_at: str

    @classmethod
    def create(cls, event_type: str, note: str) -> "SessionEvent":
        return cls(
            event_type=event_type,
            note=note,
            created_at=_timestamp(),
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "event_type": self.event_type,
            "note": self.note,
            "created_at": self.created_at,
        }


@dataclass
class AcademySession:
    """Serializable state shared by CLI artifacts and the Nuxt portal."""

    lab_name: str
    student_name: str
    created_at: str
    stages: List[SessionStage]
    skill_graph: List[SkillNode]
    commands: List[str]
    events: List[SessionEvent] = field(default_factory=list)
    current_stage_code: str = "environment"

    @property
    def current_stage(self) -> SessionStage:
        for stage in self.stages:
            if stage.code == self.current_stage_code:
                return stage
        return self.stages[0]

    def to_dict(self) -> Dict[str, Any]:
        dev_command = (
            f"MENTOR_LAB_SESSION=/absolute/path/to/session.json "
            f"npm --prefix {PORTAL_PATH} run dev"
        )
        return {
            "academy_version": ACADEMY_VERSION,
            "lab_name": self.lab_name,
            "student_name": self.student_name,
            "created_at": self.created_at,
            "current_stage": self.current_stage.to_dict(),
            "stages": [stage.to_dict() for stage in self.stages],
            "skill_graph": [node.to_dict() for node in self.skill_graph],
            "commands": self.commands,
            "events": [event.to_dict() for event in self.events],
            "portal": {
                "framework": PORTAL_FRAMEWORK,
                "app_path": PORTAL_PATH,
                "session_env": "MENTOR_LAB_SESSION",
                "dev_command": dev_command,
            },
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "AcademySession":
        return cls(
            lab_name=payload["lab_name"],
            student_name=payload["student_name"],
            created_at=payload["created_at"],
            current_stage_code=payload["current_stage"]["code"],
            stages=[
                SessionStage(
                    code=item["code"],
                    title=item["title"],
                    timebox=item["timebox"],
                    mentor_focus=item["mentor_focus"],
                    student_action=item["student_action"],
                    command=item["command"],
                )
                for item in payload["stages"]
            ],
            skill_graph=[
                SkillNode(
                    code=item["code"],
                    title=item["title"],
                    level=item["level"],
                    evidence=item["evidence"],
                )
                for item in payload["skill_graph"]
            ],
            commands=list(payload["commands"]),
            events=[
                SessionEvent(
                    event_type=item["event_type"],
                    note=item["note"],
                    created_at=item["created_at"],
                )
                for item in payload.get("events", [])
            ],
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


def _default_stages(lab_name: str) -> List[SessionStage]:
    return [
        SessionStage(
            code="environment",
            title="Окружение и паспорт кластера",
            timebox="00:00-10:00",
            mentor_focus="Проверить Docker, поднять Greenplum, показать topology.",
            student_action="Запустить doctor/check и назвать coordinator/segments.",
            command=f"python3 mentor-lab.py check {lab_name} --dry-run",
        ),
        SessionStage(
            code="storage",
            title="Heap, AO row, AOCO",
            timebox="10:00-22:00",
            mentor_focus="Сравнить row-store и column-store на DDL и catalog checks.",
            student_action="Объяснить, где включается orientation=column.",
            command=(
                "docker compose -f labs/greenplum/docker-compose.yml exec -T -u "
                "gpadmin greenplum psql -U gpadmin -d mentor -f "
                "/mentor-lab/examples/storage-and-partitioning.sql"
            ),
        ),
        SessionStage(
            code="plan-reading",
            title="EXPLAIN, Motion, QD/QE/gang/slice",
            timebox="22:00-40:00",
            mentor_focus="Показать, как Motion режет план на slices.",
            student_action="Найти Redistribute/Broadcast/Gather Motion в плане.",
            command=f"python3 mentor-lab.py coach-plan {lab_name} --query bad_customer_join --sample",
        ),
        SessionStage(
            code="practice",
            title="Практика и evidence",
            timebox="40:00-55:00",
            mentor_focus="Собрать evidence pack и проверить SQL submission.",
            student_action="Сформулировать причину, фикс и проверку до/после.",
            command=(
                f"python3 mentor-lab.py autograde-sql {lab_name} "
                "--submission labs/greenplum/examples/student-solution-example.sql"
            ),
        ),
        SessionStage(
            code="homework",
            title="Домашка и следующий урок",
            timebox="55:00-60:00",
            mentor_focus="Передать student handoff, критерии и Lesson 02.",
            student_action="Назвать, что принесет на следующий урок.",
            command=f"python3 mentor-lab.py session {lab_name} report --session <session-dir>",
        ),
    ]


def _default_skill_graph() -> List[SkillNode]:
    return [
        SkillNode(
            code="topology",
            title="Кластер и topology",
            level="intro",
            evidence="Ученик объясняет coordinator/master, primary segments и gp_segment_configuration.",
        ),
        SkillNode(
            code="qd-qe",
            title="QD/QE/gang/slice",
            level="core",
            evidence="Ученик связывает QD, QE, gang, slice и Motion с EXPLAIN.",
        ),
        SkillNode(
            code="storage",
            title="Heap/AO/AOCO",
            level="core",
            evidence="Ученик показывает appendoptimized=true и orientation=column в DDL.",
        ),
        SkillNode(
            code="explain-motion",
            title="EXPLAIN и Motion",
            level="core",
            evidence="Ученик отличает Broadcast Motion, Redistribute Motion и Gather Motion.",
        ),
        SkillNode(
            code="evidence",
            title="Evidence-first debugging",
            level="practice",
            evidence="Submission содержит симптом, план, skew check, фикс и validation.",
        ),
    ]


def _default_commands(lab_name: str) -> List[str]:
    return [
        "python3 mentor-lab.py doctor",
        f"python3 mentor-lab.py readiness {lab_name} --platform macos",
        f"python3 mentor-lab.py up {lab_name}",
        f"python3 mentor-lab.py check {lab_name}",
        f"python3 mentor-lab.py runbook {lab_name} simple",
        f"python3 mentor-lab.py teach {lab_name} simple --stage 1",
        f"python3 mentor-lab.py coach-plan {lab_name} --query bad_customer_join --sample",
        f"python3 mentor-lab.py dataset {lab_name} generate --scale small --seed 42 --skew high --late-facts --wide-rows --output artifacts/generated-enterprise.sql",
        f"python3 mentor-lab.py evidence {lab_name} collect redistribute-join --output submissions/redistribute-join.md",
        f"python3 mentor-lab.py autograde-sql {lab_name} --submission labs/greenplum/examples/student-solution-example.sql --output artifacts/sql-autograde.md",
        f"python3 mentor-lab.py session {lab_name} report --session <session-dir> --output artifacts/{lab_name}-session-report.md",
        f"python3 mentor-lab.py ci-smoke {lab_name} --dry-run",
    ]


def _render_timeline(session: AcademySession) -> str:
    lines = [
        "## Лента Сессии",
        "",
        f"- Версия: {ACADEMY_VERSION}",
        f"- Лаборатория: {session.lab_name}",
        f"- Ученик: {session.student_name}",
        f"- Current stage: {session.current_stage.code}",
        "",
        "### Этапы",
    ]
    for stage in session.stages:
        marker = "current stage" if stage.code == session.current_stage.code else "stage"
        lines.append(f"- `{stage.timebox}` `{marker}` `{stage.code}`: {stage.title}")
    lines.extend(["", "### События"])
    for event in session.events:
        lines.append(f"- `{event.created_at}` `{event.event_type}` {event.note}")
    lines.append("")
    return "\n".join(lines)


def _render_skill_graph(session: AcademySession) -> str:
    lines = [
        "## Skill Graph",
        "",
        "```mermaid",
        "flowchart LR",
        '  topology["Кластер и topology"] --> qdqe["QD/QE/gang/slice"]',
        '  qdqe --> motion["EXPLAIN и Motion"]',
        '  storage["Heap/AO/AOCO"] --> evidence["Evidence-first debugging"]',
        "  motion --> evidence",
        "```",
        "",
    ]
    for node in session.skill_graph:
        lines.append(f"- `{node.code}` {node.title}: {node.evidence}")
    lines.append("")
    return "\n".join(lines)


def _render_mentor_cockpit(session: AcademySession, session_dir: Path) -> str:
    report_command = (
        f"python3 mentor-lab.py session {session.lab_name} report "
        f"--session {session_dir} --output artifacts/{session.lab_name}-session-report.md"
    )
    portal_command = (
        f"MENTOR_LAB_SESSION={session_dir / 'session.json'} "
        f"npm --prefix {PORTAL_PATH} run dev"
    )
    lines = [
        f"# Mentor Cockpit: {session.lab_name}",
        "",
        f"{ACADEMY_VERSION} для ученика: {session.student_name}.",
        "",
        "## Команды",
        "",
        "```bash",
        portal_command,
        report_command,
        f"python3 mentor-lab.py lesson-doctor {session.lab_name}",
        "```",
        "",
        "## Что Смотреть Во Время Урока",
        "",
        "- current stage в Nuxt portal;",
        "- misconceptions/events в timeline;",
        "- skill graph и evidence checklist;",
        "- команды с классом copy-command в интерфейсе.",
        "",
    ]
    return "\n".join(lines)


def _render_student_handoff(session: AcademySession, session_dir: Path) -> str:
    lines = [
        f"# Student Handoff: {session.lab_name}",
        "",
        f"Ученик: {session.student_name}",
        "",
        "## Как Открыть Портал",
        "",
        "```bash",
        f"MENTOR_LAB_SESSION={session_dir / 'session.json'} npm --prefix {PORTAL_PATH} run dev",
        "```",
        "",
        "## Что Сделать После Урока",
        "",
        "- поднять стенд через `python3 mentor-lab.py up greenplum`;",
        "- выполнить workbook и homework;",
        "- собрать evidence pack;",
        "- проверить SQL через `python3 mentor-lab.py autograde-sql greenplum --submission <file>`.",
        "",
    ]
    return "\n".join(lines)


def _render_report(session: AcademySession) -> str:
    lines = [
        f"# Session Report: {session.lab_name.title()}",
        "",
        f"- Version: {ACADEMY_VERSION}",
        f"- Student: {session.student_name}",
        f"- Current stage: {session.current_stage.title}",
        f"- Events: {len(session.events)}",
        "",
        "## Skill Graph",
        "",
    ]
    for node in session.skill_graph:
        lines.append(f"- `{node.code}` {node.title}: {node.evidence}")
    lines.extend(["", "## Timeline", ""])
    for event in session.events:
        lines.append(f"- `{event.created_at}` `{event.event_type}` {event.note}")
    lines.extend(
        [
            "",
            "## Next actions",
            "",
            "- Передать student handoff и homework-plan.",
            "- Попросить ученика принести EXPLAIN evidence и SQL submission.",
            "- Следующий урок: Lesson 02 partitioning, statistics and incremental loads.",
            "",
        ]
    )
    return "\n".join(lines)


def _session_slug(lab_name: str, student_name: str) -> str:
    clean_student = "".join(
        char.lower() if char.isalnum() else "-"
        for char in student_name.strip()
    ).strip("-") or "student"
    return f"{lab_name}-{clean_student}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def _timestamp() -> str:
    return datetime.now().replace(microsecond=0).isoformat()
