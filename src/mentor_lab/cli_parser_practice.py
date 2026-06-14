"""Argparse registrations for practice and diagnostic commands."""

from __future__ import annotations

import argparse

from mentor_lab.cli_handlers_diagnostics import (
    _handle_adaptive_review,
    _handle_calibration,
    _handle_control_room,
    _handle_diagnostics,
    _handle_misconception,
    _handle_scenario,
    _handle_solutions,
    _handle_visualize_plan,
)
from mentor_lab.cli_handlers_practice import (
    _handle_assessment,
    _handle_autograde_sql,
    _handle_cockpit,
    _handle_evidence,
    _handle_homework,
    _handle_observe,
    _handle_portal,
    _handle_review,
    _handle_submit,
    _handle_tuning,
)
from mentor_lab.session_contract import PORTAL_APP_PATH


def register_practice_commands(subparsers: argparse._SubParsersAction) -> None:
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

    autograde_parser = subparsers.add_parser(
        "autograde-sql",
        help="Grade a submitted SQL file with the Greenplum evidence contract.",
    )
    autograde_parser.add_argument("lab_name")
    autograde_parser.add_argument("--submission", required=True)
    autograde_parser.add_argument("--live", action="store_true")
    autograde_parser.add_argument("--output")
    autograde_parser.set_defaults(handler=_handle_autograde_sql)

    evidence_parser = subparsers.add_parser(
        "evidence",
        help="Create a submission-ready evidence pack for a scenario task.",
    )
    evidence_parser.add_argument("lab_name")
    evidence_parser.add_argument("evidence_command", choices=["collect"])
    evidence_parser.add_argument("task_code")
    evidence_parser.add_argument("--output")
    evidence_parser.set_defaults(handler=_handle_evidence)

    observe_parser = subparsers.add_parser(
        "observe",
        help="Create live observation checklists and evidence trail reports.",
    )
    observe_parser.add_argument("lab_name")
    observe_parser.add_argument("observe_command", choices=["start", "report"])
    observe_parser.add_argument("--commands")
    observe_parser.add_argument("--output")
    observe_parser.set_defaults(handler=_handle_observe)

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
    portal_parser.add_argument(
        "portal_command",
        nargs="?",
        choices=["static", "start", "export", "open"],
        default="static",
    )
    portal_parser.add_argument("--version", choices=["v1", "v2"], default="v1")
    portal_parser.add_argument("--output")
    portal_parser.add_argument("--session")
    portal_parser.add_argument("--portal-dir", default=PORTAL_APP_PATH)
    portal_parser.add_argument("--host", default="127.0.0.1")
    portal_parser.add_argument("--port", type=int, default=3000)
    portal_parser.add_argument("--url", default="http://127.0.0.1:3000")
    portal_parser.add_argument("--dry-run", action="store_true")
    portal_parser.set_defaults(handler=_handle_portal)

    misconception_parser = subparsers.add_parser(
        "misconception",
        help="List, show, or diagnose common Greenplum misconceptions.",
    )
    misconception_parser.add_argument("lab_name")
    misconception_parser.add_argument(
        "misconception_command",
        choices=["list", "show", "diagnose"],
    )
    misconception_parser.add_argument("code", nargs="?")
    misconception_parser.add_argument("--text")
    misconception_parser.set_defaults(handler=_handle_misconception)

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

    calibration_parser = subparsers.add_parser(
        "calibration",
        help="List or show gold submission calibration examples.",
    )
    calibration_parser.add_argument("lab_name")
    calibration_parser.add_argument("calibration_command", choices=["list", "show"])
    calibration_parser.add_argument("level", nargs="?")
    calibration_parser.set_defaults(handler=_handle_calibration)
