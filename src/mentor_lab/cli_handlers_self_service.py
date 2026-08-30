"""Self-service Academy CLI handlers."""

from __future__ import annotations

import argparse
from pathlib import Path

from mentor_lab.academy_self_service import AcademySelfService, AcademyStartOptions
from mentor_lab.cli_context import (
    _lab_or_none,
    _learning_route_or_none,
    _project_root,
    _runner,
)
from mentor_lab.spark_student_workflow import SparkStudentWorkflow
from mentor_lab.student_self_service import StudentSelfServiceGuide


def _handle_academy(args: argparse.Namespace) -> int:
    route = _learning_route_or_none(args.lab_name)
    if route is None:
        return 1
    lab = _lab_or_none(route.physical_lab_name)
    if lab is None:
        return 1
    if args.academy_command != "start":
        print("Use: mentor-lab academy <lab> start --student <name>")
        return 1

    options = AcademyStartOptions(
        student=args.student,
        session_dir=Path(args.session_dir),
        portal_dir=Path(args.portal_dir),
        route=args.route,
        platform=args.platform,
        host=args.host,
        port=args.port,
        dry_run=args.dry_run,
        skip_lab=args.skip_lab,
        lesson_route=route,
    )
    result = AcademySelfService(_runner()).start(lab, options)
    print(result.render(), end="")
    return result.exit_code


def _handle_student(args: argparse.Namespace) -> int:
    route = _learning_route_or_none(args.lab_name)
    if route is None:
        return 1
    lab = _lab_or_none(route.physical_lab_name)
    if lab is None:
        return 1
    guide = StudentSelfServiceGuide()
    if args.student_command == "bootstrap":
        print(guide.bootstrap(lab, route, args.platform), end="")
        return 0
    if args.student_command == "homework":
        print(guide.homework(lab, route), end="")
        return 0
    if args.student_command in {"start", "init", "test"}:
        if lab.runtime != "spark" or route.lesson_code != "lesson-04":
            print(
                "The start/init/test student workflow is available for "
                "spark-foundations (Lesson 04)."
            )
            return 1
        workflow = SparkStudentWorkflow(_project_root(), lab, route, _runner())
        if args.student_command == "start":
            try:
                result = workflow.start(
                    args.profile,
                    with_notebook=args.with_notebook,
                    dry_run=args.dry_run,
                )
            except (KeyError, ValueError, FileNotFoundError) as exc:
                print(str(exc))
                return 1
            print(result.render(), end="")
            return result.exit_code
        if args.student_command == "init":
            destination = Path(args.output) if args.output else None
            result = workflow.initialize_submission(destination, force=args.force)
            print(result.render(), end="")
            return result.exit_code
        submission = Path(args.submission) if args.submission else None
        result = workflow.test_submission(submission, skip_live=args.skip_live)
        print(result.render(), end="")
        return result.exit_code
    print("Use: mentor-lab student <lab> bootstrap|homework|start|init|test")
    return 1
