"""Self-service Academy CLI handlers."""

from __future__ import annotations

from pathlib import Path

from mentor_lab.academy_self_service import AcademySelfService, AcademyStartOptions
from mentor_lab.cli_context import _lab_or_none, _runner
from mentor_lab.student_self_service import StudentSelfServiceGuide


def _handle_academy(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
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
    )
    result = AcademySelfService(_runner()).start(lab, options)
    print(result.render(), end="")
    return result.exit_code


def _handle_student(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    guide = StudentSelfServiceGuide()
    if args.student_command == "bootstrap":
        print(guide.bootstrap(lab, args.platform), end="")
        return 0
    if args.student_command == "homework":
        print(guide.homework(lab), end="")
        return 0
    print("Use: mentor-lab student <lab> bootstrap|homework")
    return 1
