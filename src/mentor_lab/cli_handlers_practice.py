"""Submission, homework, cockpit and portal CLI handlers."""

from __future__ import annotations

from pathlib import Path

from mentor_lab.assessment import AssessmentCatalog
from mentor_lab.cli_context import _lab_or_none, _learning_route_or_none, _sql_client
from mentor_lab.cockpit import MentorCockpit
from mentor_lab.evidence import EvidenceCollector
from mentor_lab.homework_review import HomeworkReviewer
from mentor_lab.observation import ObservationBuilder
from mentor_lab.portal import StudentPortal
from mentor_lab.portal_launcher import PortalLauncher
from mentor_lab.query_tuning import QueryTuningCatalog
from mentor_lab.sql_autograder import SqlSubmissionGrader, build_transactional_sql
from mentor_lab.submissions import SubmissionReviewer, SubmissionTemplate

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


def _handle_autograde_sql(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    submission_path = Path(args.submission)
    if not submission_path.exists():
        print(f"Submission file does not exist: {submission_path}")
        return 1
    submission_text = submission_path.read_text(encoding="utf-8")
    live_output = ""
    if args.live:
        try:
            live_output = _sql_client(lab).text(build_transactional_sql(submission_text))
        except RuntimeError as exc:
            print(f"Live SQL execution failed: {exc}")
            return 1

    try:
        result = SqlSubmissionGrader.default().grade_text(
            lab.name,
            submission_text,
            live_output=live_output,
        )
    except KeyError as exc:
        print(str(exc))
        return 1

    rendered = result.render()
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"SQL autograde report written to {output}")
    else:
        print(rendered, end="")
    return 0 if result.accepted else 1


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


def _handle_observe(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    builder = ObservationBuilder()
    if args.observe_command == "start":
        output = Path(args.output) if args.output else Path("artifacts") / f"{lab.name}-observe-checklist.md"
        written = builder.start(lab.name).write(output)
        print(f"Observation checklist written to {written}")
        return 0

    if not args.commands:
        print("Use --commands with `mentor-lab observe <lab> report`.")
        return 1
    commands_path = Path(args.commands)
    if not commands_path.exists():
        print(f"Commands log does not exist: {commands_path}")
        return 1
    output = Path(args.output) if args.output else Path("artifacts") / f"{lab.name}-observation-report.md"
    written = builder.report(lab.name, commands_path).write(output)
    print(f"Observation report written to {written}")
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
    route = _learning_route_or_none(args.lab_name)
    if route is None:
        return 1
    lab = _lab_or_none(route.physical_lab_name)
    if lab is None:
        return 1
    if args.portal_command == "start":
        return _handle_portal_start(args)
    if args.portal_command == "export":
        return _handle_portal_export(args)
    if args.portal_command == "open":
        return _handle_portal_open(args)

    suffix = "student-portal-v2" if args.version == "v2" else "student-portal"
    output = Path(args.output) if args.output else Path("artifacts") / f"{route.name}-{suffix}.html"
    try:
        written = StudentPortal().write(output, lab.name, version=args.version)
    except ValueError as exc:
        print(str(exc))
        return 1
    print(f"Student portal written to {written}")
    return 0


def _handle_portal_start(args: argparse.Namespace) -> int:
    if not args.session:
        print("Use --session with `mentor-lab.py portal <lab> start`.")
        return 1
    launcher = PortalLauncher()
    try:
        plan = launcher.build_start_plan(
            Path(args.session),
            Path(args.portal_dir),
            host=args.host,
            port=args.port,
        )
        if not args.dry_run:
            env_file = launcher.write_env_file(plan.portal_dir, plan.session_file)
            print(f"Portal .env written to {env_file}")
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    print(plan.render(), end="")
    return 0


def _handle_portal_export(args: argparse.Namespace) -> int:
    if not args.session:
        print("Use --session with `mentor-lab.py portal <lab> export`.")
        return 1
    try:
        result = PortalLauncher().export_session(Path(args.session), Path(args.portal_dir))
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    print(f"Portal session exported to {result.session_file}")
    print(f"Portal env written to {result.env_file}")
    return 0


def _handle_portal_open(args: argparse.Namespace) -> int:
    if args.dry_run:
        print(f"Would open portal: {args.url}")
        return 0
    opened = PortalLauncher().open_url(args.url)
    print(f"Portal open requested: {args.url}")
    return 0 if opened else 1
