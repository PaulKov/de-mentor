"""Argparse registrations for self-service Academy commands."""

from __future__ import annotations

import argparse

from mentor_lab.cli_handlers_self_service import _handle_academy, _handle_student
from mentor_lab.session_contract import PORTAL_APP_PATH


def register_self_service_commands(subparsers: argparse._SubParsersAction) -> None:
    academy_parser = subparsers.add_parser(
        "academy",
        help="Run one-command mentor/student Academy workflows.",
    )
    academy_parser.add_argument("lab_name")
    academy_subparsers = academy_parser.add_subparsers(dest="academy_command")
    academy_start = academy_subparsers.add_parser(
        "start",
        help="Create session state, prepare portal state, and optionally start the lab.",
    )
    academy_start.add_argument("--student", required=True)
    academy_start.add_argument("--session-dir", default="artifacts/sessions/academy")
    academy_start.add_argument("--portal-dir", default=PORTAL_APP_PATH)
    academy_start.add_argument("--route", choices=["simple", "deep"], default="simple")
    academy_start.add_argument(
        "--platform",
        choices=["macos", "windows", "linux"],
        default="macos",
    )
    academy_start.add_argument("--host", default="127.0.0.1")
    academy_start.add_argument("--port", type=int, default=3000)
    academy_start.add_argument("--dry-run", action="store_true")
    academy_start.add_argument("--skip-lab", action="store_true")
    academy_start.set_defaults(handler=_handle_academy)

    student_parser = subparsers.add_parser(
        "student",
        help="Print student self-service setup and homework routes.",
    )
    student_parser.add_argument("lab_name")
    student_subparsers = student_parser.add_subparsers(dest="student_command")
    student_bootstrap = student_subparsers.add_parser(
        "bootstrap",
        help="Print cross-platform setup commands for a student.",
    )
    student_bootstrap.add_argument(
        "--platform",
        choices=["macos", "windows", "linux"],
        default="macos",
    )
    student_bootstrap.set_defaults(handler=_handle_student)
    student_homework = student_subparsers.add_parser(
        "homework",
        help="Print homework route, self-check commands, and Lesson 02 handoff.",
    )
    student_homework.set_defaults(handler=_handle_student)
    student_start = student_subparsers.add_parser(
        "start",
        help="Start Spark, Jupyter, lesson data, and smoke checks in one command.",
    )
    student_start.add_argument(
        "--profile",
        choices=["tiny", "lesson04", "class", "deep"],
        default="lesson04",
    )
    student_start.add_argument(
        "--no-notebook",
        action="store_false",
        dest="with_notebook",
        help="Start only the Spark services, without the Jupyter profile.",
    )
    student_start.add_argument("--dry-run", action="store_true")
    student_start.set_defaults(handler=_handle_student, with_notebook=True)
    student_init = student_subparsers.add_parser(
        "init",
        help="Create the Lesson 04 pipeline.py and evidence.md submission scaffold.",
    )
    student_init.add_argument("--output")
    student_init.add_argument(
        "--force",
        action="store_true",
        help="Replace existing scaffold files intentionally.",
    )
    student_init.set_defaults(handler=_handle_student)
    student_test = student_subparsers.add_parser(
        "test",
        help="Run live Spark readiness and mechanical homework evidence gates.",
    )
    student_test.add_argument("--submission")
    student_test.add_argument(
        "--skip-live",
        action="store_true",
        help="Run only the deterministic static evidence review.",
    )
    student_test.set_defaults(handler=_handle_student)
