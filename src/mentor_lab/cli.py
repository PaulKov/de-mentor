"""Cross-platform CLI for mentorship lab stands.

The CLI intentionally uses only the Python standard library. A student can run
it from the repository checkout without installing Python packages:

    python3 mentor-lab.py up greenplum
    py mentor-lab.py up greenplum
"""

import argparse
from pathlib import Path
from typing import Callable, Optional, Sequence

from mentor_lab.assessment import AssessmentCatalog
from mentor_lab.adaptive_review import AdaptiveReviewer
from mentor_lab.certificates import CertificateWriter
from mentor_lab.checks import CheckStatus, GreenplumCheckSuite
from mentor_lab.challenges import ChallengeCatalog
from mentor_lab.cockpit import MentorCockpit
from mentor_lab.control_room import MentorControlRoom
from mentor_lab.diagnostics import DiagnosticsCatalog
from mentor_lab.docker_compose import DockerComposeRunner
from mentor_lab.domain import LabDefinition, UnknownLabError
from mentor_lab.explain_analyzer import ExplainPlanAnalyzer
from mentor_lab.evidence import EvidenceCollector
from mentor_lab.grading import GradeCalculator
from mentor_lab.homework_review import HomeworkReviewer
from mentor_lab.lesson_catalog import LessonCatalog, normalize_lesson_code
from mentor_lab.learning_loop import LearningLoopBuilder
from mentor_lab.plan_visualizer import PlanVisualizer
from mentor_lab.portal import StudentPortal
from mentor_lab.query_tuning import QueryTuningCatalog
from mentor_lab.reports import MentorReport
from mentor_lab.registry import create_default_registry
from mentor_lab.runbooks import RunbookCatalog
from mentor_lab.scenario_dsl import ScenarioDslCatalog
from mentor_lab.scenario_engine import ScenarioRandomizer
from mentor_lab.seed_profiles import SeedProfileCatalog
from mentor_lab.sql_client import GreenplumSqlClient
from mentor_lab.solutions import SolutionCatalog
from mentor_lab.submissions import SubmissionReviewer, SubmissionTemplate
from mentor_lab.teaching import TeachingSessionBuilder
from mentor_lab.telemetry import TelemetryReport


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    return args.handler(args)


def console() -> None:
    raise SystemExit(main())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mentor-lab",
        description=(
            "Self-service CLI for data engineering mentorship labs. "
            "Works on macOS and Windows with Docker Desktop."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser(
        "list",
        help="List ready and planned learning labs.",
    )
    list_parser.set_defaults(handler=_handle_list)

    info_parser = subparsers.add_parser(
        "info",
        help="Show student-friendly instructions for a lab.",
    )
    info_parser.add_argument("lab_name")
    info_parser.set_defaults(handler=_handle_info)

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Print environment checks and the next action.",
    )
    doctor_parser.set_defaults(handler=_handle_doctor)

    lesson_parser = subparsers.add_parser(
        "lesson",
        help="Print an interactive lesson runner view.",
    )
    lesson_parser.add_argument("lesson_code")
    lesson_parser.add_argument("--step", type=int)
    lesson_parser.set_defaults(handler=_handle_lesson)

    runbook_parser = subparsers.add_parser(
        "runbook",
        help="Print a mentor runbook route with slides, commands, questions, and checks.",
    )
    runbook_parser.add_argument("lab_name")
    runbook_parser.add_argument("route", choices=["prep", "simple", "deep", "homework"])
    runbook_parser.set_defaults(handler=_handle_runbook)

    teach_parser = subparsers.add_parser(
        "teach",
        help="Run a one-button mentor facilitation view for a lesson route.",
    )
    teach_parser.add_argument("lab_name")
    teach_parser.add_argument("route", choices=["prep", "simple", "deep", "homework"])
    teach_parser.add_argument("--stage", type=int)
    teach_parser.set_defaults(handler=_handle_teach)

    hint_parser = subparsers.add_parser(
        "hint",
        help="Show progressive hints for a lesson topic.",
    )
    hint_parser.add_argument("lesson_code")
    hint_parser.add_argument("topic")
    hint_parser.add_argument("--level", type=int, choices=[1, 2, 3])
    hint_parser.set_defaults(handler=_handle_hint)

    analyze_parser = subparsers.add_parser(
        "analyze-plan",
        help="Analyze a Greenplum EXPLAIN plan for Motion, joins, and risks.",
    )
    analyze_parser.add_argument("lab_name")
    analyze_parser.add_argument("--query", default="bad_customer_join")
    analyze_parser.add_argument("--sample", action="store_true")
    analyze_parser.set_defaults(handler=_handle_analyze_plan)

    assessment_parser = subparsers.add_parser(
        "assessment",
        help="Print or score a pre/post lesson assessment.",
    )
    assessment_parser.add_argument("lab_name")
    assessment_parser.add_argument("mode", choices=["pre", "post"])
    assessment_parser.add_argument("--answers")
    assessment_parser.set_defaults(handler=_handle_assessment)

    submit_parser = subparsers.add_parser(
        "submit",
        help="Create a student submission template.",
    )
    submit_parser.add_argument("lab_name")
    submit_parser.add_argument("assignment")
    submit_parser.add_argument("--output")
    submit_parser.set_defaults(handler=_handle_submit)

    review_parser = subparsers.add_parser(
        "review",
        help="Review a student submission for required evidence.",
    )
    review_parser.add_argument("lab_name")
    review_parser.add_argument("--submission", required=True)
    review_parser.set_defaults(handler=_handle_review)

    evidence_parser = subparsers.add_parser(
        "evidence",
        help="Create a submission-ready evidence pack for a scenario task.",
    )
    evidence_parser.add_argument("lab_name")
    evidence_parser.add_argument("evidence_command", choices=["collect"])
    evidence_parser.add_argument("task_code")
    evidence_parser.add_argument("--output")
    evidence_parser.set_defaults(handler=_handle_evidence)

    homework_parser = subparsers.add_parser(
        "homework",
        help="Check a homework submission against the Greenplum evidence contract.",
    )
    homework_parser.add_argument("lab_name")
    homework_parser.add_argument("homework_command", choices=["check"])
    homework_parser.add_argument("--submission", required=True)
    homework_parser.add_argument("--output")
    homework_parser.set_defaults(handler=_handle_homework)

    tuning_parser = subparsers.add_parser(
        "tuning",
        help="List or show query tuning lab tasks.",
    )
    tuning_parser.add_argument("lab_name")
    tuning_parser.add_argument("tuning_command", choices=["list", "show"])
    tuning_parser.add_argument("task_code", nargs="?")
    tuning_parser.set_defaults(handler=_handle_tuning)

    cockpit_parser = subparsers.add_parser(
        "cockpit",
        help="Generate a local mentor cockpit HTML page.",
    )
    cockpit_parser.add_argument("lab_name")
    cockpit_parser.add_argument("--output")
    cockpit_parser.set_defaults(handler=_handle_cockpit)

    portal_parser = subparsers.add_parser(
        "portal",
        help="Generate a local student portal HTML page.",
    )
    portal_parser.add_argument("lab_name")
    portal_parser.add_argument("--output")
    portal_parser.set_defaults(handler=_handle_portal)

    visualize_parser = subparsers.add_parser(
        "visualize-plan",
        help="Render a Greenplum EXPLAIN plan as Mermaid or static HTML.",
    )
    visualize_parser.add_argument("lab_name")
    visualize_parser.add_argument("--query", default="bad_customer_join")
    visualize_parser.add_argument("--sample", action="store_true")
    visualize_parser.add_argument("--format", choices=["mermaid", "html"], default="mermaid")
    visualize_parser.add_argument("--output")
    visualize_parser.set_defaults(handler=_handle_visualize_plan)

    diagnostics_parser = subparsers.add_parser(
        "diagnostics",
        help="List, show, or run runtime diagnostic probes.",
    )
    diagnostics_parser.add_argument("lab_name")
    diagnostics_parser.add_argument("diagnostics_command", choices=["list", "show", "run"])
    diagnostics_parser.add_argument("probe_code", nargs="?")
    diagnostics_parser.add_argument("--dry-run", action="store_true")
    diagnostics_parser.set_defaults(handler=_handle_diagnostics)

    scenario_parser = subparsers.add_parser(
        "scenario",
        help="List or start randomized academy scenarios.",
    )
    scenario_parser.add_argument("lab_name")
    scenario_parser.add_argument("scenario_command", choices=["list", "show", "start"])
    scenario_parser.add_argument("scenario_code", nargs="?")
    scenario_parser.add_argument("--difficulty", default="medium")
    scenario_parser.add_argument("--seed", type=int, default=42)
    scenario_parser.add_argument("--dry-run", action="store_true")
    scenario_parser.set_defaults(handler=_handle_scenario)

    adaptive_parser = subparsers.add_parser(
        "adaptive-review",
        help="Score a submission with the adaptive evidence rubric.",
    )
    adaptive_parser.add_argument("lab_name")
    adaptive_parser.add_argument("--submission", required=True)
    adaptive_parser.set_defaults(handler=_handle_adaptive_review)

    control_room_parser = subparsers.add_parser(
        "control-room",
        help="Generate a local mentor control room HTML page.",
    )
    control_room_parser.add_argument("lab_name")
    control_room_parser.add_argument("--output")
    control_room_parser.set_defaults(handler=_handle_control_room)

    solutions_parser = subparsers.add_parser(
        "solutions",
        help="List or show golden and anti-solutions.",
    )
    solutions_parser.add_argument("lab_name")
    solutions_parser.add_argument("solutions_command", choices=["list", "show"])
    solutions_parser.add_argument("solution_code", nargs="?")
    solutions_parser.set_defaults(handler=_handle_solutions)

    telemetry_parser = subparsers.add_parser(
        "telemetry",
        help="Generate a lesson telemetry summary.",
    )
    telemetry_parser.add_argument("lab_name")
    telemetry_parser.add_argument("--pre", type=int, required=True)
    telemetry_parser.add_argument("--post", type=int, required=True)
    telemetry_parser.add_argument("--review", type=int, required=True)
    telemetry_parser.add_argument("--output")
    telemetry_parser.set_defaults(handler=_handle_telemetry)

    learning_loop_parser = subparsers.add_parser(
        "learning-loop",
        help="Generate a skill map, evidence feedback, and spaced follow-up plan.",
    )
    learning_loop_parser.add_argument("lab_name")
    learning_loop_parser.add_argument("--pre", type=int, required=True)
    learning_loop_parser.add_argument("--post", type=int, required=True)
    learning_loop_parser.add_argument("--submission")
    learning_loop_parser.add_argument(
        "--review",
        type=int,
        help="Manual evidence score when a submission file is not available.",
    )
    learning_loop_parser.add_argument("--output")
    learning_loop_parser.set_defaults(handler=_handle_learning_loop)

    challenge_parser = subparsers.add_parser(
        "challenge",
        help="Start a timed challenge.",
    )
    challenge_parser.add_argument("lab_name")
    challenge_parser.add_argument("challenge_command", choices=["start"])
    challenge_parser.add_argument("--difficulty", default="hard")
    challenge_parser.add_argument("--minutes", type=int, default=15)
    challenge_parser.add_argument("--seed", type=int, default=7)
    challenge_parser.add_argument("--output")
    challenge_parser.set_defaults(handler=_handle_challenge)

    dsl_parser = subparsers.add_parser(
        "dsl",
        help="List or show engine-neutral scenario DSL definitions.",
    )
    dsl_parser.add_argument("lab_name")
    dsl_parser.add_argument("dsl_command", choices=["list", "show"])
    dsl_parser.add_argument("scenario_code", nargs="?")
    dsl_parser.set_defaults(handler=_handle_dsl)

    check_parser = subparsers.add_parser(
        "check",
        help="Run automated lab checks.",
    )
    check_parser.add_argument("lab_name")
    check_parser.add_argument("--dry-run", action="store_true")
    check_parser.set_defaults(handler=_handle_check)

    grade_parser = subparsers.add_parser(
        "grade",
        help="Grade a lesson using automated checks.",
    )
    grade_parser.add_argument("lesson_code")
    grade_parser.add_argument("--dry-run", action="store_true")
    grade_parser.set_defaults(handler=_handle_grade)

    seed_parser = subparsers.add_parser(
        "seed",
        help="Apply a repeatable data profile to a lab.",
    )
    seed_parser.add_argument("lab_name")
    seed_parser.add_argument("--profile", default="skewed")
    seed_parser.add_argument("--dry-run", action="store_true")
    seed_parser.set_defaults(handler=_handle_seed)

    incident_parser = subparsers.add_parser(
        "incident",
        help="List or start incident-mode exercises.",
    )
    incident_subparsers = incident_parser.add_subparsers(dest="incident_command")
    incident_list = incident_subparsers.add_parser("list", help="List incidents.")
    incident_list.add_argument("lesson_code", nargs="?")
    incident_list.set_defaults(handler=_handle_incident_list)
    incident_start = incident_subparsers.add_parser("start", help="Start an incident.")
    incident_start.add_argument("incident_args", nargs="+", metavar="incident_code")
    incident_start.set_defaults(handler=_handle_incident_start)

    report_parser = subparsers.add_parser(
        "report",
        help="Generate a mentor markdown report.",
    )
    report_parser.add_argument("lesson_code")
    report_parser.add_argument("--output")
    report_parser.add_argument("--dry-run", action="store_true")
    report_parser.set_defaults(handler=_handle_report)

    certificate_parser = subparsers.add_parser(
        "certificate",
        help="Generate a lesson completion artifact.",
    )
    certificate_parser.add_argument("lab_name")
    certificate_parser.add_argument("--output")
    certificate_parser.add_argument("--dry-run", action="store_true")
    certificate_parser.set_defaults(handler=_handle_certificate)

    _add_lab_command(
        subparsers,
        "up",
        "Start a lab stand.",
        lambda runner, lab: runner.build_up_command(lab),
    )
    _add_lab_command(
        subparsers,
        "down",
        "Stop a lab stand without deleting volumes.",
        lambda runner, lab: runner.build_down_command(lab),
    )
    _add_lab_command(
        subparsers,
        "reset",
        "Stop a lab stand and delete its volumes for a clean retry.",
        lambda runner, lab: runner.build_reset_command(lab),
    )
    _add_lab_command(
        subparsers,
        "status",
        "Show Docker Compose status for a lab.",
        lambda runner, lab: runner.build_status_command(lab),
    )
    _add_lab_command(
        subparsers,
        "psql",
        "Open psql inside the lab container.",
        lambda runner, lab: runner.build_psql_command(lab),
    )
    _add_lab_command(
        subparsers,
        "config",
        "Render Docker Compose config for troubleshooting.",
        lambda runner, lab: runner.build_config_command(lab),
    )

    logs_parser = subparsers.add_parser("logs", help="Show lab container logs.")
    logs_parser.add_argument("lab_name")
    logs_parser.add_argument("--follow", action="store_true")
    logs_parser.add_argument("--dry-run", action="store_true")
    logs_parser.set_defaults(handler=_handle_logs)

    return parser


def _add_lab_command(
    subparsers: argparse._SubParsersAction,
    command_name: str,
    help_text: str,
    command_builder: Callable[[DockerComposeRunner, LabDefinition], Sequence[str]],
) -> None:
    command_parser = subparsers.add_parser(command_name, help=help_text)
    command_parser.add_argument("lab_name")
    command_parser.add_argument("--dry-run", action="store_true")
    command_parser.set_defaults(
        handler=lambda args: _handle_lab_command(args, command_builder)
    )


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
    _ = args
    print("Required tools:")
    print("- Python 3.9+")
    print("- Docker Desktop")
    print("- Docker Compose v2")
    print("")
    print("Run `docker compose version` to verify Docker Compose.")
    print("Run `python3 mentor-lab.py up greenplum` to start on macOS.")
    print("Run `py mentor-lab.py up greenplum` to start on Windows.")
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


def _handle_assessment(args: argparse.Namespace) -> int:
    try:
        assessment = AssessmentCatalog.default().get(args.lab_name, args.mode)
    except KeyError as exc:
        print(str(exc))
        return 1

    print(assessment.render(), end="")
    if args.answers:
        answers = [answer.strip() for answer in args.answers.split(",")]
        print(f"Score: {assessment.score(answers)}/100")
    return 0


def _handle_submit(args: argparse.Namespace) -> int:
    _ = _lab_or_none(args.lab_name)
    if _ is None:
        return 1
    output = Path(args.output) if args.output else Path("submissions") / f"{args.assignment}.md"
    try:
        written = SubmissionTemplate.default().write(output, args.assignment)
    except KeyError as exc:
        print(str(exc))
        return 1
    print(f"Submission template written to {written}")
    return 0


def _handle_review(args: argparse.Namespace) -> int:
    _ = _lab_or_none(args.lab_name)
    if _ is None:
        return 1
    path = Path(args.submission)
    if not path.exists():
        print(f"Submission file does not exist: {path}")
        return 1
    print(SubmissionReviewer.default().review(path).render(), end="")
    return 0


def _handle_evidence(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    try:
        packet = EvidenceCollector.default().collect(lab.name, args.task_code)
    except KeyError as exc:
        print(str(exc))
        return 1

    if args.output:
        output = Path(args.output)
    else:
        output = Path("submissions") / f"{args.task_code}.md"
    written = packet.write(output)
    print(f"Evidence pack written to {written}")
    return 0


def _handle_homework(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    path = Path(args.submission)
    if not path.exists():
        print(f"Homework submission file does not exist: {path}")
        return 1

    review = HomeworkReviewer.default().review(path)
    rendered = review.render()
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Homework review written to {output}")
    else:
        print(rendered, end="")
    return 0 if review.accepted else 1


def _handle_tuning(args: argparse.Namespace) -> int:
    try:
        catalog = QueryTuningCatalog.default()
        if args.tuning_command == "list":
            for task in catalog.list(args.lab_name):
                print(f"- {task.code}: {task.title}")
            return 0
        if not args.task_code:
            print("Use: mentor-lab tuning <lab> show <task_code>")
            return 1
        task = catalog.get(args.lab_name, args.task_code)
    except KeyError as exc:
        print(str(exc))
        return 1
    print(task.title)
    print(f"Symptom: {task.symptom}")
    print(f"Investigation: {task.investigation}")
    print("Success criteria:")
    for item in task.success_criteria:
        print(f"- {item}")
    return 0


def _handle_cockpit(args: argparse.Namespace) -> int:
    _ = _lab_or_none(args.lab_name)
    if _ is None:
        return 1
    output = Path(args.output) if args.output else Path("artifacts") / f"{args.lab_name}-cockpit.html"
    written = MentorCockpit().write(output, args.lab_name)
    print(f"Cockpit written to {written}")
    return 0


def _handle_portal(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    output = Path(args.output) if args.output else Path("artifacts") / f"{lab.name}-student-portal.html"
    written = StudentPortal().write(output, lab.name)
    print(f"Student portal written to {written}")
    return 0


def _handle_visualize_plan(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    analyzer = ExplainPlanAnalyzer()
    try:
        plan = (
            analyzer.sample_plan(args.query)
            if args.sample
            else _sql_client(lab).text(f"EXPLAIN {analyzer.query_sql(args.query)}")
        )
    except (KeyError, RuntimeError) as exc:
        print(str(exc))
        return 1

    analysis = analyzer.analyze(plan)
    visualizer = PlanVisualizer()
    if args.format == "html":
        if not args.output:
            print("Use --output when --format html is selected.")
            return 1
        written = visualizer.write_html(Path(args.output), analysis)
        print(f"Plan visualization written to {written}")
        return 0

    mermaid = visualizer.to_mermaid(analysis)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(mermaid, encoding="utf-8")
        print(f"Plan visualization written to {output}")
        return 0
    print(mermaid, end="")
    return 0


def _handle_diagnostics(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    catalog = DiagnosticsCatalog.default()
    try:
        if args.diagnostics_command == "list":
            for probe in catalog.list(lab.name):
                print(f"- {probe.code}: {probe.title}")
            return 0
        if not args.probe_code:
            print("Use: mentor-lab diagnostics <lab> show|run <probe_code>")
            return 1
        probe = catalog.get(lab.name, args.probe_code)
    except KeyError as exc:
        print(str(exc))
        return 1

    if args.diagnostics_command == "show" or args.dry_run:
        print(probe.render(), end="")
        return 0
    try:
        print(_sql_client(lab).text(probe.sql), end="")
    except RuntimeError as exc:
        print(f"Diagnostic execution failed: {exc}")
        return 1
    return 0


def _handle_scenario(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    catalog = ScenarioDslCatalog.default()
    try:
        if args.scenario_command == "list":
            for scenario in catalog.list(lab.name):
                print(f"- {scenario.code}: {scenario.title} [{scenario.difficulty}]")
            return 0
        if args.scenario_command == "show":
            if not args.scenario_code:
                print("Use: mentor-lab scenario <lab> show <scenario_code>")
                return 1
            print(catalog.get(lab.name, args.scenario_code).render(), end="")
            return 0
        start = ScenarioRandomizer.default().start(
            lab.name, difficulty=args.difficulty, seed=args.seed
        )
    except KeyError as exc:
        print(str(exc))
        return 1

    print(start.render(), end="")
    if args.dry_run:
        return 0
    try:
        profile = SeedProfileCatalog.default(_project_root()).get(
            lab.name, start.scenario.seed_profile
        )
    except KeyError as exc:
        print(str(exc))
        return 1
    return _sql_client(lab).run_file(profile.container_path)


def _handle_adaptive_review(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    path = Path(args.submission)
    if not path.exists():
        print(f"Submission file does not exist: {path}")
        return 1
    print(AdaptiveReviewer.default().review(path).render(), end="")
    return 0


def _handle_control_room(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    output = Path(args.output) if args.output else Path("artifacts") / f"{lab.name}-control-room.html"
    written = MentorControlRoom().write(output, lab.name)
    print(f"Control room written to {written}")
    return 0


def _handle_solutions(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    catalog = SolutionCatalog.default()
    try:
        if args.solutions_command == "list":
            for solution in catalog.list(lab.name):
                print(f"- {solution.code}: {solution.title}")
            return 0
        if not args.solution_code:
            print("Use: mentor-lab solutions <lab> show <solution_code>")
            return 1
        print(catalog.get(lab.name, args.solution_code).render(), end="")
    except KeyError as exc:
        print(str(exc))
        return 1
    return 0


def _handle_telemetry(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    report = TelemetryReport(
        pre_score=args.pre,
        post_score=args.post,
        review_score=args.review,
    ).render()
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(f"Telemetry report written to {output}")
        return 0
    print(report, end="")
    return 0


def _handle_learning_loop(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1

    submission_path = Path(args.submission) if args.submission else None
    if submission_path is not None and not submission_path.exists():
        print(f"Submission file does not exist: {submission_path}")
        return 1

    try:
        report = LearningLoopBuilder.default().build(
            lab_name=lab.name,
            pre_score=args.pre,
            post_score=args.post,
            submission_path=submission_path,
            review_score=args.review,
        ).render()
    except (KeyError, ValueError) as exc:
        print(str(exc))
        return 1

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(f"Learning loop report written to {output}")
        return 0
    print(report, end="")
    return 0


def _handle_challenge(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    try:
        challenge = ChallengeCatalog.default().start(
            lab.name,
            difficulty=args.difficulty,
            minutes=args.minutes,
            seed=args.seed,
        )
    except KeyError as exc:
        print(str(exc))
        return 1
    rendered = challenge.render()
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Timed challenge written to {output}")
        return 0
    print(rendered, end="")
    return 0


def _handle_dsl(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    catalog = ScenarioDslCatalog.default()
    try:
        if args.dsl_command == "list":
            for scenario in catalog.list(lab.name):
                print(f"- {scenario.code}: {scenario.title} [{scenario.difficulty}]")
            return 0
        if not args.scenario_code:
            print("Use: mentor-lab dsl <lab> show <scenario_code>")
            return 1
        print(catalog.get(lab.name, args.scenario_code).render(), end="")
    except KeyError as exc:
        print(str(exc))
        return 1
    return 0


def _handle_check(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    if args.dry_run:
        print("Checks that would run:")
        for code in GreenplumCheckSuite.documented_check_codes():
            print(f"- {code}")
        return 0

    try:
        checks = GreenplumCheckSuite(_sql_client(lab)).run()
    except RuntimeError as exc:
        print(f"Check execution failed: {exc}")
        return 1

    for check in checks:
        print(f"{check.status.value} {check.code}: {check.detail}")
        if check.remediation:
            print(f"  remediation: {check.remediation}")
    return 0 if all(check.status == CheckStatus.PASS for check in checks) else 1


def _handle_grade(args: argparse.Namespace) -> int:
    if args.dry_run:
        print("Score requires a running Greenplum lab.")
        print("Checks:")
        for code in GreenplumCheckSuite.documented_check_codes():
            print(f"- {code}")
        return 0

    lab = _lab_or_none("greenplum")
    if lab is None:
        return 1
    try:
        checks = GreenplumCheckSuite(_sql_client(lab)).run()
    except RuntimeError as exc:
        print(f"Grade execution failed: {exc}")
        return 1

    grade = GradeCalculator.default().calculate(_normalize_lesson_arg(args.lesson_code), checks)
    print(f"Score: {grade.score}/100")
    print(f"Level: {grade.level}")
    print("Skill matrix:")
    for skill, score in grade.skill_scores.items():
        print(f"- {skill}: {score}")
    if grade.next_actions:
        print("Next actions:")
        for action in grade.next_actions:
            print(f"- {action}")
    return 0


def _handle_seed(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    try:
        profile = SeedProfileCatalog.default(_project_root()).get(lab.name, args.profile)
    except KeyError as exc:
        print(str(exc))
        return 1

    client = _sql_client(lab)
    command = client.build_file_command(profile.container_path)
    if args.dry_run:
        print(client.format_command(command))
        return 0
    return client.run_file(profile.container_path)


def _handle_incident_list(args: argparse.Namespace) -> int:
    catalog = LessonCatalog.default()
    if args.lesson_code:
        try:
            lesson = catalog.get(args.lesson_code)
        except KeyError as exc:
            print(str(exc))
            return 1
        print(f"Incidents for {lesson.title} ({lesson.code}):")
    for incident in catalog.incidents():
        print(f"- {incident.code}: {incident.title}")
    return 0


def _handle_incident_start(args: argparse.Namespace) -> int:
    catalog = LessonCatalog.default()
    incident_args = args.incident_args
    if len(incident_args) == 1:
        incident_code = incident_args[0]
    elif len(incident_args) == 2:
        try:
            catalog.get(incident_args[0])
        except KeyError as exc:
            print(str(exc))
            return 1
        incident_code = incident_args[1]
    else:
        print("Use: mentor-lab incident start [lesson_code] incident_code")
        return 1

    try:
        incident = catalog.incident(incident_code)
    except KeyError as exc:
        print(str(exc))
        return 1
    print(incident.title)
    print("")
    print(f"Symptoms: {incident.symptoms}")
    print(f"Mission: {incident.mission}")
    print("")
    print("Acceptance criteria:")
    for item in incident.acceptance_criteria:
        print(f"- {item}")
    print("")
    print("Suggested setup:")
    print("  python3 mentor-lab.py seed greenplum --profile skewed")
    print("  python3 mentor-lab.py check greenplum")
    return 0


def _handle_report(args: argparse.Namespace) -> int:
    report_path = Path(args.output) if args.output else MentorReport.default_path(
        _normalize_lesson_arg(args.lesson_code)
    )
    if args.dry_run:
        print(f"Report would be written to {report_path}")
        return 0

    lab = _lab_or_none("greenplum")
    if lab is None:
        return 1
    try:
        checks = GreenplumCheckSuite(_sql_client(lab)).run()
    except RuntimeError as exc:
        print(f"Report execution failed: {exc}")
        return 1

    lesson_code = _normalize_lesson_arg(args.lesson_code)
    grade = GradeCalculator.default().calculate(lesson_code, checks)
    written = MentorReport().write(report_path, lesson_code, checks, grade)
    print(f"Report written to {written}")
    return 0


def _handle_certificate(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    output = Path(args.output) if args.output else Path("artifacts") / f"{args.lab_name}-certificate.md"
    lesson_code = "lesson-01" if args.lab_name == "greenplum" else args.lab_name

    if args.dry_run:
        grade = GradeCalculator.default().calculate(
            lesson_code,
            GreenplumCheckSuite.documented_success_results(),
        )
    else:
        try:
            checks = GreenplumCheckSuite(_sql_client(lab)).run()
        except RuntimeError as exc:
            print(f"Certificate execution failed: {exc}")
            return 1
        grade = GradeCalculator.default().calculate(lesson_code, checks)

    written = CertificateWriter().write(output, args.lab_name, grade)
    print(f"Certificate written to {written}")
    return 0


def _handle_lab_command(
    args: argparse.Namespace,
    command_builder: Callable[[DockerComposeRunner, LabDefinition], Sequence[str]],
) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1

    runner = _runner()
    command = command_builder(runner, lab)
    if args.dry_run:
        print(runner.format_command(command))
        return 0
    return runner.run(command)


def _handle_logs(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1

    runner = _runner()
    command = runner.build_logs_command(lab, args.follow)
    if args.dry_run:
        print(runner.format_command(command))
        return 0
    return runner.run(command)


def _lab_or_none(name: str) -> Optional[LabDefinition]:
    try:
        return _registry().get(name)
    except UnknownLabError as exc:
        print(str(exc))
        return None


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _registry():
    return create_default_registry(_project_root())


def _runner() -> DockerComposeRunner:
    return DockerComposeRunner(_project_root())


def _sql_client(lab: LabDefinition) -> GreenplumSqlClient:
    return GreenplumSqlClient(_project_root(), lab)


def _normalize_lesson_arg(value: str) -> str:
    return normalize_lesson_code(value)
