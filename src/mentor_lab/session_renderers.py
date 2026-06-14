"""Markdown renderers for Academy session artifacts."""

from __future__ import annotations

from pathlib import Path

from mentor_lab.session_contract import PORTAL_APP_PATH, PORTAL_REPOSITORY
from mentor_lab.session_model import ACADEMY_VERSION, AcademySession

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
        "npm run dev"
    )
    lines = [
        f"# Mentor Cockpit: {session.lab_name}",
        "",
        f"{ACADEMY_VERSION} для ученика: {session.student_name}.",
        "",
        "## Команды",
        "",
        "```bash",
        f"git clone {PORTAL_REPOSITORY}.git",
        f"cd {PORTAL_APP_PATH}",
        portal_command,
        "cd -",
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
        f"git clone {PORTAL_REPOSITORY}.git",
        f"cd {PORTAL_APP_PATH}",
        f"MENTOR_LAB_SESSION={session_dir / 'session.json'} npm run dev",
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
