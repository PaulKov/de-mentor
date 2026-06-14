"""Operational and post-lesson CLI handlers."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence

from mentor_lab.certificates import CertificateWriter
from mentor_lab.challenges import ChallengeCatalog
from mentor_lab.checks import CheckStatus, GreenplumCheckSuite
from mentor_lab.ci_smoke import CiSmokePlanBuilder
from mentor_lab.cli_context import (
    _lab_or_none,
    _normalize_lesson_arg,
    _project_root,
    _runner,
    _sql_client,
)
from mentor_lab.dataset_generator import DatasetGenerator, DatasetSpec
from mentor_lab.debrief import DebriefGenerator
from mentor_lab.docker_compose import DockerComposeRunner
from mentor_lab.domain import LabDefinition
from mentor_lab.grading import GradeCalculator
from mentor_lab.learning_loop import LearningLoopBuilder
from mentor_lab.lesson_catalog import LessonCatalog
from mentor_lab.replay import LessonReplayBuilder
from mentor_lab.reports import MentorReport
from mentor_lab.scenario_dsl import ScenarioDslCatalog
from mentor_lab.seed_profiles import SeedProfileCatalog
from mentor_lab.telemetry import TelemetryReport

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


def _handle_dataset(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    generator = DatasetGenerator()
    try:
        if args.dataset_command == "manifest":
            print(generator.manifest(lab.name), end="")
            return 0
        generated = generator.generate(
            DatasetSpec(
                lab_name=lab.name,
                scale=args.scale,
                seed=args.seed,
                skew=args.skew,
                late_facts=args.late_facts,
                wide_rows=args.wide_rows,
            )
        )
    except KeyError as exc:
        print(str(exc))
        return 1

    if args.output:
        written = generated.write(Path(args.output))
        print(f"Dataset SQL written to {written}")
        return 0
    print(generated.sql, end="")
    return 0


def _handle_ci_smoke(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    try:
        plan = CiSmokePlanBuilder().build(lab.name)
    except KeyError as exc:
        print(str(exc))
        return 1
    rendered = plan.render()
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"CI smoke plan written to {output}")
        return 0
    print(rendered, end="")
    return 0


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


def _handle_debrief(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    submission_path = Path(args.submission)
    if not submission_path.exists():
        print(f"Submission file does not exist: {submission_path}")
        return 1
    debrief = DebriefGenerator.default().generate(
        lab.name,
        student_name=args.student,
        submission_path=submission_path,
        pre_score=args.pre,
        post_score=args.post,
    ).render()
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(debrief, encoding="utf-8")
        print(f"Debrief written to {output}")
        return 0
    print(debrief, end="")
    return 0


def _handle_replay(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    submission_path = Path(args.submission)
    if not submission_path.exists():
        print(f"Submission file does not exist: {submission_path}")
        return 1
    try:
        replay = LessonReplayBuilder.default().build(
            lab_name=lab.name,
            student_name=args.student,
            submission_path=submission_path,
            pre_score=args.pre,
            post_score=args.post,
        )
    except (KeyError, ValueError) as exc:
        print(str(exc))
        return 1
    if args.output:
        written = replay.write(Path(args.output))
        print(f"Lesson replay pack written to {written}")
        return 0
    print(replay.render(), end="")
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
