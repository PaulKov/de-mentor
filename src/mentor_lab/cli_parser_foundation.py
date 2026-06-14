"""Argparse registrations for core lesson commands."""

from __future__ import annotations

import argparse

from mentor_lab.cli_handlers_foundation import (
    _handle_analyze_plan,
    _handle_coach_plan,
    _handle_doctor,
    _handle_hint,
    _handle_info,
    _handle_lesson,
    _handle_lesson_doctor,
    _handle_list,
    _handle_orchestrate,
    _handle_readiness,
    _handle_runbook,
    _handle_session_event,
    _handle_session_report,
    _handle_session_start,
    _handle_session_validate,
    _handle_teach,
)
from mentor_lab.orchestrator import LiveLessonOrchestrator


def register_foundation_commands(subparsers: argparse._SubParsersAction) -> None:
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
    doctor_parser.add_argument("--full", action="store_true")
    doctor_parser.set_defaults(handler=_handle_doctor)

    readiness_parser = subparsers.add_parser(
        "readiness",
        help="Print platform-specific readiness guidance for a lab.",
    )
    readiness_parser.add_argument("lab_name")
    readiness_parser.add_argument(
        "--platform",
        choices=["macos", "windows", "linux"],
        default="macos",
    )
    readiness_parser.set_defaults(handler=_handle_readiness)

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

    session_parser = subparsers.add_parser(
        "session",
        help="Create and update an Academy Experience v5 lesson session.",
    )
    session_parser.add_argument("lab_name")
    session_subparsers = session_parser.add_subparsers(dest="session_command")
    session_start = session_subparsers.add_parser(
        "start",
        help="Create session state for the Nuxt portal.",
    )
    session_start.add_argument("--student", required=True)
    session_start.add_argument("--output")
    session_start.set_defaults(handler=_handle_session_start)
    session_event = session_subparsers.add_parser(
        "event",
        help="Record a live lesson event.",
    )
    session_event.add_argument("--session", required=True)
    session_event.add_argument("--type", required=True)
    session_event.add_argument("--note", required=True)
    session_event.set_defaults(handler=_handle_session_event)
    session_report = session_subparsers.add_parser(
        "report",
        help="Render a session report.",
    )
    session_report.add_argument("--session", required=True)
    session_report.add_argument("--output")
    session_report.set_defaults(handler=_handle_session_report)
    session_validate = session_subparsers.add_parser(
        "validate",
        help="Validate a session JSON file against the published contract.",
    )
    session_validate.add_argument("--session", required=True)
    session_validate.set_defaults(handler=_handle_session_validate)

    lesson_doctor_parser = subparsers.add_parser(
        "lesson-doctor",
        help="Check lesson artifacts before a live class.",
    )
    lesson_doctor_parser.add_argument("lab_name")
    lesson_doctor_parser.add_argument("--output")
    lesson_doctor_parser.set_defaults(handler=_handle_lesson_doctor)

    teach_parser = subparsers.add_parser(
        "teach",
        help="Run a one-button mentor facilitation view for a lesson route.",
    )
    teach_parser.add_argument("lab_name")
    teach_parser.add_argument("route", choices=["prep", "simple", "deep", "homework"])
    teach_parser.add_argument("--stage", type=int)
    teach_parser.set_defaults(handler=_handle_teach)

    orchestrate_parser = subparsers.add_parser(
        "orchestrate",
        help="Render a mode-aware live lesson orchestration stage.",
    )
    orchestrate_parser.add_argument("lab_name")
    orchestrate_parser.add_argument("--route", choices=["simple", "deep"], default="simple")
    orchestrate_parser.add_argument("--stage", type=int, default=1)
    orchestrate_parser.add_argument(
        "--mode",
        choices=LiveLessonOrchestrator.modes(),
        default="simple",
    )
    orchestrate_parser.set_defaults(handler=_handle_orchestrate)

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

    coach_plan_parser = subparsers.add_parser(
        "coach-plan",
        help="Explain a Greenplum EXPLAIN plan as a mentor coach.",
    )
    coach_plan_parser.add_argument("lab_name")
    coach_plan_parser.add_argument("--query", default="bad_customer_join")
    coach_plan_parser.add_argument("--sample", action="store_true")
    coach_plan_parser.set_defaults(handler=_handle_coach_plan)
