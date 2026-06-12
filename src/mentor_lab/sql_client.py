"""SQL execution helpers for Greenplum running in Docker Compose."""

import shlex
import subprocess
from pathlib import Path
from typing import Sequence

from mentor_lab.domain import LabDefinition


class GreenplumSqlClient:
    """Executes SQL in the Greenplum container as gpadmin."""

    _ENV_SCRIPT = ". /usr/local/greenplum-db/greenplum_path.sh"

    _ALIASES = {
        "SCHEMA_EXISTS": (
            "SELECT count(*) FROM information_schema.schemata "
            "WHERE schema_name = 'lesson01'"
        ),
        "BAD_FACT_ROWS": "SELECT count(*) FROM lesson01.fact_sales_bad",
        "BAD_SKEW_MAX_PERCENT": (
            "SELECT max(rows_percent) FROM lesson01.v_fact_sales_bad_segment_distribution"
        ),
        "GOOD_SKEW_SPREAD_PERCENT": (
            "SELECT max(rows_percent) - min(rows_percent) "
            "FROM lesson01.v_fact_sales_good_segment_distribution"
        ),
        "BAD_JOIN_EXPLAIN": (
            "EXPLAIN SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue "
            "FROM lesson01.fact_sales_bad AS f "
            "JOIN lesson01.dim_customers AS c USING (customer_id) "
            "GROUP BY c.region ORDER BY revenue DESC"
        ),
    }

    def __init__(self, project_root: Path, lab: LabDefinition) -> None:
        self._project_root = project_root
        self._lab = lab

    def scalar(self, sql: str) -> str:
        return self._execute(self._resolve(sql), ["-At"])

    def text(self, sql: str) -> str:
        return self._execute(self._resolve(sql), [])

    def build_file_command(self, container_path: str) -> Sequence[str]:
        shell = (
            f"{self._ENV_SCRIPT} && "
            f"psql -U {shlex.quote(self._lab.default_user)} "
            f"-d {shlex.quote(self._lab.default_database)} "
            f"-v ON_ERROR_STOP=1 -f {shlex.quote(container_path)}"
        )
        return self._compose_exec_prefix() + ["bash", "-lc", shell]

    def run_file(self, container_path: str) -> int:
        completed = subprocess.run(self.build_file_command(container_path), check=False)
        return completed.returncode

    def format_command(self, command: Sequence[str]) -> str:
        return shlex.join(command)

    def _execute(self, sql: str, psql_flags: Sequence[str]) -> str:
        command = self._build_sql_command(sql, psql_flags)
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            message = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(message)
        return completed.stdout.strip()

    def _build_sql_command(self, sql: str, psql_flags: Sequence[str]) -> Sequence[str]:
        flags = " ".join(psql_flags)
        shell = (
            f"{self._ENV_SCRIPT} && "
            f"psql {flags} -U {shlex.quote(self._lab.default_user)} "
            f"-d {shlex.quote(self._lab.default_database)} "
            f"-c {shlex.quote(sql)}"
        )
        return self._compose_exec_prefix() + ["bash", "-lc", shell]

    def _compose_exec_prefix(self) -> Sequence[str]:
        return [
            "docker",
            "compose",
            "-f",
            str(self._lab.compose_path(self._project_root)),
            "exec",
            "-T",
            "-u",
            self._lab.default_user,
            self._lab.service_name,
        ]

    def _resolve(self, sql: str) -> str:
        return self._ALIASES.get(sql, sql)

