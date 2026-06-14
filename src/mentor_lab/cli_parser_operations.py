"""Argparse registrations for operational commands."""

from __future__ import annotations

import argparse
from typing import Callable, Sequence

from mentor_lab.cli_handlers_operations import (
    _handle_certificate,
    _handle_challenge,
    _handle_check,
    _handle_ci_smoke,
    _handle_dataset,
    _handle_debrief,
    _handle_dsl,
    _handle_grade,
    _handle_incident_list,
    _handle_incident_start,
    _handle_lab_command,
    _handle_learning_loop,
    _handle_logs,
    _handle_report,
    _handle_replay,
    _handle_seed,
    _handle_telemetry,
)
from mentor_lab.docker_compose import DockerComposeRunner
from mentor_lab.domain import LabDefinition


def register_operations_commands(subparsers: argparse._SubParsersAction) -> None:
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

    dataset_parser = subparsers.add_parser(
        "dataset",
        help="Generate deterministic Greenplum datasets for live practice.",
    )
    dataset_parser.add_argument("lab_name")
    dataset_parser.add_argument("dataset_command", choices=["manifest", "generate"])
    dataset_parser.add_argument("--scale", choices=["small", "medium", "large"], default="small")
    dataset_parser.add_argument("--seed", type=int, default=42)
    dataset_parser.add_argument("--skew", choices=["none", "medium", "high"], default="medium")
    dataset_parser.add_argument("--late-facts", action="store_true")
    dataset_parser.add_argument("--wide-rows", action="store_true")
    dataset_parser.add_argument("--output")
    dataset_parser.set_defaults(handler=_handle_dataset)

    ci_smoke_parser = subparsers.add_parser(
        "ci-smoke",
        help="Render a live Greenplum smoke plan for local CI and GitHub Actions.",
    )
    ci_smoke_parser.add_argument("lab_name")
    ci_smoke_parser.add_argument("--dry-run", action="store_true")
    ci_smoke_parser.add_argument("--output")
    ci_smoke_parser.set_defaults(handler=_handle_ci_smoke)

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

    debrief_parser = subparsers.add_parser(
        "debrief",
        help="Generate a student-facing post-lesson debrief and mentor notes.",
    )
    debrief_parser.add_argument("lab_name")
    debrief_parser.add_argument("--student", required=True)
    debrief_parser.add_argument("--submission", required=True)
    debrief_parser.add_argument("--pre", type=int)
    debrief_parser.add_argument("--post", type=int)
    debrief_parser.add_argument("--output")
    debrief_parser.set_defaults(handler=_handle_debrief)

    replay_parser = subparsers.add_parser(
        "replay",
        help="Generate a post-lesson replay pack with debrief and next prep.",
    )
    replay_parser.add_argument("lab_name")
    replay_parser.add_argument("--student", required=True)
    replay_parser.add_argument("--submission", required=True)
    replay_parser.add_argument("--pre", type=int, required=True)
    replay_parser.add_argument("--post", type=int, required=True)
    replay_parser.add_argument("--output")
    replay_parser.set_defaults(handler=_handle_replay)

    certificate_parser = subparsers.add_parser(
        "certificate",
        help="Generate a lesson completion artifact.",
    )
    certificate_parser.add_argument("lab_name")
    certificate_parser.add_argument("--output")
    certificate_parser.add_argument("--dry-run", action="store_true")
    certificate_parser.set_defaults(handler=_handle_certificate)

    add_lab_command(
        subparsers,
        "up",
        "Start a lab stand.",
        lambda runner, lab: runner.build_up_command(lab),
    )
    add_lab_command(
        subparsers,
        "down",
        "Stop a lab stand without deleting volumes.",
        lambda runner, lab: runner.build_down_command(lab),
    )
    add_lab_command(
        subparsers,
        "reset",
        "Stop a lab stand and delete its volumes for a clean retry.",
        lambda runner, lab: runner.build_reset_command(lab),
    )
    add_lab_command(
        subparsers,
        "status",
        "Show Docker Compose status for a lab.",
        lambda runner, lab: runner.build_status_command(lab),
    )
    add_lab_command(
        subparsers,
        "psql",
        "Open psql inside the lab container.",
        lambda runner, lab: runner.build_psql_command(lab),
    )
    add_lab_command(
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


def add_lab_command(
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
