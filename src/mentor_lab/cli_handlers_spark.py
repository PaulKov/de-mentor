"""Spark-specific CLI handlers kept outside SQL operational handlers."""

from __future__ import annotations

from pathlib import Path

from mentor_lab.cli_context import _lab_or_none, _project_root, _runner
from mentor_lab.domain import LabDefinition
from mentor_lab.spark_lab import SparkLabCommands


def run_spark_check(lab: LabDefinition, dry_run: bool) -> int:
    """Run or describe the Spark readiness application."""

    runner = _runner()
    commands = SparkLabCommands(_project_root(), lab, runner)
    command = commands.build_check_command()
    if dry_run:
        print("Checks that would run:")
        for code in commands.documented_check_codes():
            print(f"- {code}")
        print("Command:")
        print(runner.format_command(command))
        return 0
    return runner.run(command)


def run_spark_seed(lab: LabDefinition, profile: str, dry_run: bool) -> int:
    """Generate a deterministic Spark lesson dataset."""

    runner = _runner()
    commands = SparkLabCommands(_project_root(), lab, runner)
    try:
        command = commands.build_seed_command(profile)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        print(str(exc))
        return 1
    if dry_run:
        print(runner.format_command(command))
        return 0
    return runner.run(command)


def handle_spark_submit(args) -> int:
    """Submit one repository-local PySpark application."""

    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    if lab.runtime != "spark":
        print(f"Lab '{lab.name}' does not support PySpark application submission.")
        return 1

    script_path = Path(args.script)
    if not script_path.is_absolute():
        script_path = _project_root() / script_path
    dry_run = args.dry_run or "--dry-run" in args.script_args
    script_args = tuple(
        arg for arg in args.script_args if arg not in {"--", "--dry-run"}
    )
    runner = _runner()
    try:
        command = SparkLabCommands(_project_root(), lab, runner).build_submit_command(
            script_path,
            script_args,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(str(exc))
        return 1

    if dry_run:
        print(runner.format_command(command))
        return 0
    return runner.run(command)
