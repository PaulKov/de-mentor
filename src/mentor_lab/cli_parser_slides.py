"""Argparse registrations for Google Slides publishing commands."""

from __future__ import annotations

import argparse

from mentor_lab.cli_handlers_slides import _handle_slides_publish, _handle_slides_verify


def register_slides_commands(subparsers: argparse._SubParsersAction) -> None:
    slides_parser = subparsers.add_parser(
        "slides",
        help="Publish and verify Google Slides lesson decks.",
    )
    slides_subparsers = slides_parser.add_subparsers(dest="slides_command")

    publish_parser = slides_subparsers.add_parser(
        "publish",
        help="Organize or upload a lesson deck in Google Slides.",
    )
    _add_common_arguments(publish_parser)
    publish_parser.add_argument("--dry-run", action="store_true")
    publish_parser.set_defaults(handler=_handle_slides_publish)

    verify_parser = slides_subparsers.add_parser(
        "verify",
        help="Verify Google Slides account, folder, sharing, and slide count.",
    )
    _add_common_arguments(verify_parser)
    verify_parser.set_defaults(handler=_handle_slides_verify)


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("lab_name")
    parser.add_argument("--confirm-account", required=True)
    parser.add_argument("--oauth-client-json")
    parser.add_argument(
        "--refresh-token-env",
        default="google_personal_refresh_token",
    )
