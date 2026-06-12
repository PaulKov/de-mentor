"""Docker Compose command builder and executor."""

import shlex
import subprocess
from pathlib import Path
from typing import Callable, List, Optional, Sequence

from mentor_lab.domain import LabDefinition

Command = List[str]
CommandExecutor = Callable[[Sequence[str]], int]


class DockerComposeRunner:
    """Build and run Docker Compose commands for a lab definition."""

    _GREENPLUM_ENV_SCRIPT = ". /usr/local/greenplum-db/greenplum_path.sh"

    def __init__(
        self,
        project_root: Path,
        executor: Optional[CommandExecutor] = None,
    ) -> None:
        self._project_root = project_root
        self._executor = executor or self._run_subprocess

    def build_up_command(self, lab: LabDefinition) -> Command:
        return self._compose_prefix(lab) + ["up", "-d"]

    def build_down_command(self, lab: LabDefinition) -> Command:
        return self._compose_prefix(lab) + ["down", "--remove-orphans"]

    def build_reset_command(self, lab: LabDefinition) -> Command:
        return self._compose_prefix(lab) + [
            "down",
            "--volumes",
            "--remove-orphans",
        ]

    def build_status_command(self, lab: LabDefinition) -> Command:
        return self._compose_prefix(lab) + ["ps"]

    def build_logs_command(self, lab: LabDefinition, follow: bool) -> Command:
        command = self._compose_prefix(lab) + ["logs"]
        if follow:
            command.append("-f")
        command.append(lab.service_name)
        return command

    def build_psql_command(self, lab: LabDefinition) -> Command:
        return self._compose_prefix(lab) + [
            "exec",
            "-u",
            lab.default_user,
            lab.service_name,
            "bash",
            "-lc",
            self._build_psql_shell_command(lab),
        ]

    def build_config_command(self, lab: LabDefinition) -> Command:
        return self._compose_prefix(lab) + ["config"]

    def build_healthcheck_probe_command(self, lab: LabDefinition) -> Command:
        return [
            "su",
            "-",
            lab.default_user,
            "-c",
            self._build_psql_shell_command(lab, ["-c", "SELECT 1"]),
        ]

    def run(self, command: Sequence[str]) -> int:
        return self._executor(command)

    def format_command(self, command: Sequence[str]) -> str:
        return shlex.join(command)

    def _compose_prefix(self, lab: LabDefinition) -> Command:
        return [
            "docker",
            "compose",
            "-f",
            str(lab.compose_path(self._project_root)),
        ]

    def _build_psql_shell_command(
        self,
        lab: LabDefinition,
        extra_args: Optional[Sequence[str]] = None,
    ) -> str:
        args = [
            "psql",
            "-U",
            lab.default_user,
            "-d",
            lab.default_database,
        ]
        if extra_args:
            args.extend(extra_args)
        return f"{self._GREENPLUM_ENV_SCRIPT} && {shlex.join(args)}"

    @staticmethod
    def _run_subprocess(command: Sequence[str]) -> int:
        completed = subprocess.run(command, check=False)
        return completed.returncode
