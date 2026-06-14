"""Thin argparse facade for mentor-lab commands."""

from __future__ import annotations

import argparse

from mentor_lab.cli_parser_foundation import register_foundation_commands
from mentor_lab.cli_parser_operations import register_operations_commands
from mentor_lab.cli_parser_practice import register_practice_commands
from mentor_lab.cli_parser_self_service import register_self_service_commands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mentor-lab",
        description=(
            "Self-service CLI for data engineering mentorship labs. "
            "Works on macOS and Windows with Docker Desktop."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")
    register_foundation_commands(subparsers)
    register_self_service_commands(subparsers)
    register_practice_commands(subparsers)
    register_operations_commands(subparsers)
    return parser
