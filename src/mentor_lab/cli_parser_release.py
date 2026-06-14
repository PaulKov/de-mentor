"""Argparse registrations for lesson release pipeline commands."""

from __future__ import annotations

import argparse

from mentor_lab.cli_handlers_release import _handle_lesson_release


def register_release_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "lesson-release",
        help="Verify, report, and publish lesson release artifacts.",
    )
    parser.add_argument("lab_name")
    release_subparsers = parser.add_subparsers(dest="release_command")

    verify = release_subparsers.add_parser(
        "verify",
        help="Run lesson release preflight checks.",
    )
    _add_verify_arguments(verify, output_required=False)
    verify.set_defaults(handler=_handle_lesson_release)

    report = release_subparsers.add_parser(
        "report",
        help="Write a markdown lesson release report.",
    )
    _add_verify_arguments(report, output_required=True)
    report.set_defaults(handler=_handle_lesson_release)

    publish = release_subparsers.add_parser(
        "publish-slides",
        help="Publish or dry-run Google Slides for the lesson.",
    )
    publish.add_argument("--dry-run", action="store_true")
    publish.add_argument("--confirm-account", required=True)
    publish.add_argument("--oauth-client-json")
    publish.add_argument("--refresh-token-env", default="google_personal_refresh_token")
    publish.set_defaults(handler=_handle_lesson_release)


def _add_verify_arguments(
    parser: argparse.ArgumentParser,
    *,
    output_required: bool,
) -> None:
    parser.add_argument("--output", required=output_required)
    parser.add_argument("--live-google-slides", action="store_true")
    parser.add_argument("--confirm-account")
    parser.add_argument("--oauth-client-json")
    parser.add_argument("--refresh-token-env", default="google_personal_refresh_token")
