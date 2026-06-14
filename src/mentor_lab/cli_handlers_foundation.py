"""Core mentor-lab CLI handlers."""

from __future__ import annotations

from pathlib import Path

from mentor_lab.cli_context import _lab_or_none, _project_root, _registry, _sql_client
from mentor_lab.explain_analyzer import ExplainPlanAnalyzer
from mentor_lab.full_doctor import FullDoctorReport
from mentor_lab.lesson_catalog import LessonCatalog
from mentor_lab.lesson_doctor import LessonDoctor
from mentor_lab.orchestrator import LiveLessonOrchestrator
from mentor_lab.plan_coach import PlanCoach
from mentor_lab.readiness import ReadinessDoctorPro
from mentor_lab.runbooks import RunbookCatalog
from mentor_lab.session_contract import PORTAL_APP_PATH, PORTAL_REPOSITORY, SessionContractValidator
from mentor_lab.session_experience import SessionManager
from mentor_lab.teaching import TeachingSessionBuilder

def _handle_list(args: argparse.Namespace) -> int:
    _ = args
    print("Available labs:")
    for lab in _registry().list():
        print(f"- {lab.name:12} [{lab.status}] {lab.title}")
    return 0


def _handle_info(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1

    print(lab.title)
    print("")
    print(lab.description)
    print("")
    print("Student interface:")
    print(f"  python3 mentor-lab.py up {lab.name}")
    print(f"  python3 mentor-lab.py status {lab.name}")
    print(f"  python3 mentor-lab.py psql {lab.name}")
    print(f"  python3 mentor-lab.py reset {lab.name}")
    print("")
    print("macOS:")
    print("  1. Install Docker Desktop.")
    print(f"  2. Run: python3 mentor-lab.py up {lab.name}")
    print(f"  3. Run: python3 mentor-lab.py psql {lab.name}")
    print("")
    print("Windows:")
    print("  1. Install Docker Desktop with WSL 2 backend enabled.")
    print("  2. Open PowerShell in the repository folder.")
    print(f"  3. Run: py mentor-lab.py up {lab.name}")
    print(f"  4. Run: py mentor-lab.py psql {lab.name}")
    print("")
    print(
        "The psql command runs inside the container, so students do not need "
        "a local PostgreSQL client."
    )
    return 0


def _handle_doctor(args: argparse.Namespace) -> int:
    if args.full:
        print(FullDoctorReport().render(), end="")
        return 0
    print("Required tools:")
    print("- Python 3.9+")
    print("- Docker Desktop")
    print("- Docker Compose v2")
    print("")
    print("Run `docker compose version` to verify Docker Compose.")
    print("Run `python3 mentor-lab.py up greenplum` to start on macOS.")
    print("Run `py mentor-lab.py up greenplum` to start on Windows.")
    return 0


def _handle_readiness(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    try:
        print(ReadinessDoctorPro().render(lab.name, args.platform), end="")
    except KeyError as exc:
        print(str(exc))
        return 1
    return 0


def _handle_lesson(args: argparse.Namespace) -> int:
    try:
        lesson = LessonCatalog.default().get(args.lesson_code)
        steps = [lesson.step(args.step)] if args.step else lesson.steps
    except KeyError as exc:
        print(str(exc))
        return 1

    print(f"{lesson.title} ({lesson.code})")
    print("")
    for step in steps:
        print(f"Step {step.number}: {step.title}")
        print(f"Type: {step.kind}")
        print(f"Duration: {step.duration_minutes} min")
        print(f"Goal: {step.goal}")
        print(f"Mentor: {step.mentor_action}")
        print(f"Student: {step.student_action}")
        print(f"Expected outcome: {step.expected_outcome}")
        print("")
    return 0


def _handle_runbook(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    try:
        runbook = RunbookCatalog.default().get(lab.name, args.route)
    except KeyError as exc:
        print(str(exc))
        return 1
    print(runbook.render(), end="")
    return 0


def _handle_session_start(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    output = Path(args.output) if args.output else None
    session_dir = SessionManager().start(lab.name, args.student, output)
    session_file = session_dir / "session.json"
    portal_command = (
        f"cd {PORTAL_APP_PATH} && MENTOR_LAB_SESSION={session_file} npm run dev"
    )
    print(f"Academy Experience v5 session started at {session_dir}")
    print(f"Nuxt portal repo: {PORTAL_REPOSITORY}")
    print(f"Clone: git clone {PORTAL_REPOSITORY}.git")
    print(f"Run: {portal_command}")
    print(f"Report: python3 mentor-lab.py session {lab.name} report --session {session_dir}")
    return 0


def _handle_session_event(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    try:
        timeline = SessionManager().record_event(
            Path(args.session),
            event_type=args.type,
            note=args.note,
        )
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    print(f"Session event recorded in {timeline}")
    return 0


def _handle_session_report(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    manager = SessionManager()
    session_dir = Path(args.session)
    output = Path(args.output) if args.output else None
    try:
        rendered = manager.report(session_dir, output=output)
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    if output is not None:
        print(f"Session report written to {output}")
    else:
        print(rendered, end="")
    return 0


def _handle_session_validate(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    result = SessionContractValidator().validate_file(Path(args.session))
    print(result.render(), end="")
    return 0 if result.valid else 1


def _handle_lesson_doctor(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    doctor = LessonDoctor(_project_root())
    try:
        report = doctor.build(lab.name)
    except KeyError as exc:
        print(str(exc))
        return 1
    rendered = report.render()
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Lesson Doctor report written to {output}")
    else:
        print(rendered, end="")
    return 0 if report.passed else 1


def _handle_teach(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    try:
        session = TeachingSessionBuilder.default().build(
            lab.name,
            args.route,
            stage_number=args.stage,
        )
    except (KeyError, ValueError) as exc:
        print(str(exc))
        return 1
    print(session.render(), end="")
    return 0


def _handle_orchestrate(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    try:
        stage = LiveLessonOrchestrator.default().build(
            lab.name,
            route=args.route,
            stage_number=args.stage,
            mode=args.mode,
        )
    except (KeyError, ValueError) as exc:
        print(str(exc))
        return 1
    print(stage.render(), end="")
    return 0


def _handle_hint(args: argparse.Namespace) -> int:
    try:
        hints = LessonCatalog.default().hints(args.lesson_code, args.topic)
    except KeyError as exc:
        print(str(exc))
        return 1

    if args.level:
        print(f"Hint {args.level}: {hints[args.level - 1]}")
        return 0

    for index, hint in enumerate(hints, start=1):
        print(f"Hint {index}: {hint}")
    return 0


def _handle_analyze_plan(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    analyzer = ExplainPlanAnalyzer()
    try:
        if args.sample:
            plan = analyzer.sample_plan(args.query)
        else:
            plan = _sql_client(lab).text(f"EXPLAIN {analyzer.query_sql(args.query)}")
    except (KeyError, RuntimeError) as exc:
        print(str(exc))
        return 1

    print(analyzer.render(analyzer.analyze(plan)))
    return 0


def _handle_coach_plan(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    analyzer = ExplainPlanAnalyzer()
    try:
        if args.sample:
            plan = analyzer.sample_plan(args.query)
        else:
            plan = _sql_client(lab).text(f"EXPLAIN {analyzer.query_sql(args.query)}")
        report = PlanCoach(analyzer).coach(lab.name, args.query, plan)
    except (KeyError, RuntimeError) as exc:
        print(str(exc))
        return 1
    print(report.render(), end="")
    return 0
