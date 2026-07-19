"""Automated checks for the Greenplum lesson lab."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Protocol


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class CheckResult:
    code: str
    title: str
    status: CheckStatus
    detail: str
    remediation: str


class SqlClient(Protocol):
    def scalar(self, sql: str) -> str:
        ...

    def text(self, sql: str) -> str:
        ...


class GreenplumCheckSuite:
    """Runs lesson-01 checks against a Greenplum SQL client."""

    def __init__(self, sql_client: SqlClient) -> None:
        self._sql = sql_client

    @staticmethod
    def documented_check_codes() -> List[str]:
        return [
            "greenplum_connection",
            "lesson_schema",
            "seed_data",
            "bad_distribution_skew",
            "good_distribution_balance",
            "motion_plan",
        ]

    @staticmethod
    def documented_success_results() -> List[CheckResult]:
        return [
            CheckResult(
                code,
                code.replace("_", " ").title(),
                CheckStatus.PASS,
                "Documented dry-run success.",
                "",
            )
            for code in GreenplumCheckSuite.documented_check_codes()
        ]

    def run(self) -> List[CheckResult]:
        results = [
            self._check_connection(),
            self._check_schema(),
            self._check_seed_data(),
            self._check_bad_skew(),
            self._check_good_balance(),
            self._check_motion_plan(),
        ]
        return results

    def _check_connection(self) -> CheckResult:
        value = self._sql.scalar("SELECT 1")
        return _result(
            "greenplum_connection",
            "Greenplum connection",
            value.strip() == "1",
            f"SELECT 1 returned {value!r}.",
            "Start the lab with `python3 mentor-lab.py up greenplum` "
            "(alias of greenplum-625, port 15436).",
        )

    def _check_schema(self) -> CheckResult:
        value = self._sql.scalar("SCHEMA_EXISTS")
        return _result(
            "lesson_schema",
            "lesson01 schema exists",
            value.strip() == "1",
            f"lesson01 schema count is {value}.",
            "Run `python3 mentor-lab.py seed greenplum --profile lesson01` "
            "(or `--profile academy`).",
        )

    def _check_seed_data(self) -> CheckResult:
        rows = int(float(self._sql.scalar("BAD_FACT_ROWS").strip()))
        return _result(
            "seed_data",
            "Seed data loaded",
            rows >= 50000,
            f"fact_sales_bad has {rows} rows.",
            "Run `python3 mentor-lab.py seed greenplum --profile lesson01`.",
        )

    def _check_bad_skew(self) -> CheckResult:
        max_percent = float(self._sql.scalar("BAD_SKEW_MAX_PERCENT").strip())
        return _result(
            "bad_distribution_skew",
            "Bad table demonstrates skew",
            max_percent >= 80.0,
            f"Max segment share is {max_percent:.2f}%.",
            "Inspect gp_segment_id and use a low-cardinality status distribution for the incident.",
        )

    def _check_good_balance(self) -> CheckResult:
        spread = float(self._sql.scalar("GOOD_SKEW_SPREAD_PERCENT").strip())
        return _result(
            "good_distribution_balance",
            "Corrected table is balanced",
            spread <= 5.0,
            f"Good table segment spread is {spread:.2f} percentage points.",
            "Rebuild fact_sales_good with DISTRIBUTED BY(customer_id).",
        )

    def _check_motion_plan(self) -> CheckResult:
        plan = self._sql.text("BAD_JOIN_EXPLAIN")
        has_motion = "Redistribute Motion" in plan
        return _result(
            "motion_plan",
            "Bad join plan shows Redistribute Motion",
            has_motion,
            "Redistribute Motion found." if has_motion else "Redistribute Motion missing.",
            "Run EXPLAIN for the bad join, find Redistribute Motion, and compare it with the corrected table.",
        )


class Greenplum625CheckSuite:
    """Checks for the Lesson 03 Greenplum 6.25 optimization lab."""

    def __init__(self, sql_client: SqlClient) -> None:
        self._sql = sql_client

    @staticmethod
    def documented_check_codes() -> List[str]:
        return [
            "greenplum625_connection",
            "greenplum625_database",
            "greenplum625_version",
            "lesson03_schema",
            "lesson03_fact_rows",
            "optimizer_guc_available",
            "orca_plan_marker",
        ]

    @staticmethod
    def documented_success_results() -> List[CheckResult]:
        return [
            CheckResult(
                code,
                code.replace("_", " ").title(),
                CheckStatus.PASS,
                "Documented dry-run success.",
                "",
            )
            for code in Greenplum625CheckSuite.documented_check_codes()
        ]

    def run(self) -> List[CheckResult]:
        return [
            self._check_connection(),
            self._check_database(),
            self._check_version(),
            self._check_schema(),
            self._check_fact_rows(),
            self._check_optimizer_guc(),
            self._check_orca_plan(),
        ]

    def _check_connection(self) -> CheckResult:
        value = self._sql.scalar("SELECT 1")
        return _result(
            "greenplum625_connection",
            "Greenplum 6.25 connection",
            value.strip() == "1",
            f"SELECT 1 returned {value!r}.",
            "Start the lab with `python3 mentor-lab.py up greenplum-625`.",
        )

    def _check_database(self) -> CheckResult:
        value = self._sql.scalar("SELECT current_database()")
        return _result(
            "greenplum625_database",
            "Connected to mentor database",
            value.strip() == "mentor",
            f"current_database()={value!r}",
            "Lab default_database must be mentor; rerun seed/check so CLI creates it.",
        )

    def _check_version(self) -> CheckResult:
        version = self._sql.scalar("SELECT version()")
        ok = "Greenplum Database 6.25" in version
        return _result(
            "greenplum625_version",
            "Greenplum 6.25 version",
            ok,
            version.split(" on ")[0] if version else "empty version",
            "Use image andruche/greenplum:6.25.3-slim-arm64 (or amd64).",
        )

    def _check_schema(self) -> CheckResult:
        value = self._sql.scalar(
            "SELECT count(*) FROM information_schema.schemata WHERE schema_name = 'lesson03'"
        )
        return _result(
            "lesson03_schema",
            "lesson03 schema exists",
            value.strip() == "1",
            f"lesson03 schema count is {value}.",
            "Run `python3 mentor-lab.py seed greenplum-625 --profile lesson03`.",
        )

    def _check_fact_rows(self) -> CheckResult:
        try:
            rows = int(float(self._sql.scalar("SELECT count(*) FROM lesson03.fact_sales").strip()))
        except RuntimeError:
            rows = 0
        return _result(
            "lesson03_fact_rows",
            "Lesson 03 fact rows loaded",
            rows >= 100000,
            f"lesson03.fact_sales has {rows} rows.",
            "Run `python3 mentor-lab.py seed greenplum-625 --profile lesson03`.",
        )

    def _check_optimizer_guc(self) -> CheckResult:
        value = self._sql.scalar("SHOW optimizer")
        ok = value.strip().lower() in {"on", "off"}
        return _result(
            "optimizer_guc_available",
            "optimizer GUC available",
            ok,
            f"optimizer={value!r}",
            "Confirm GPORCA build: SHOW optimizer should return on/off.",
        )

    def _check_orca_plan(self) -> CheckResult:
        try:
            # One psql invocation so SET applies to EXPLAIN in the same session.
            plan = self._sql.text(
                "SET optimizer = on; "
                "EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case LIMIT 5"
            )
        except RuntimeError as exc:
            return _result(
                "orca_plan_marker",
                "ORCA plan explailable",
                False,
                str(exc),
                "Seed lesson03 data, then rerun check.",
            )
        marker = (
            "Optimizer: Pivotal Optimizer" in plan
            or "Optimizer status" in plan
            or "Motion" in plan
            or "Dynamic Seq Scan" in plan
        )
        return _result(
            "orca_plan_marker",
            "ORCA/Legacy plan readable",
            marker,
            "Plan contains optimizer/Motion markers." if marker else "No recognizable plan markers.",
            "Run examples/lesson03-optimizer-legacy-vs-orca.sql in psql (one session).",
        )


class SharedAcademyCheckSuite:
    """Infra + Lessons 01–03 readiness on the shared Greenplum 6.25 stand."""

    def __init__(self, sql_client: SqlClient) -> None:
        self._sql = sql_client
        self._lesson01 = GreenplumCheckSuite(sql_client)
        self._lesson03 = Greenplum625CheckSuite(sql_client)

    @staticmethod
    def documented_check_codes() -> List[str]:
        return [
            "greenplum625_connection",
            "greenplum625_database",
            "greenplum625_version",
            "lesson_schema",
            "seed_data",
            "bad_distribution_skew",
            "good_distribution_balance",
            "motion_plan",
            "lesson02_schema",
            "lesson03_schema",
            "lesson03_fact_rows",
            "optimizer_guc_available",
            "orca_plan_marker",
        ]

    @staticmethod
    def documented_success_results() -> List[CheckResult]:
        return [
            CheckResult(
                code,
                code.replace("_", " ").title(),
                CheckStatus.PASS,
                "Documented dry-run success.",
                "",
            )
            for code in SharedAcademyCheckSuite.documented_check_codes()
        ]

    def run(self) -> List[CheckResult]:
        lesson01_by_code = {item.code: item for item in self._lesson01.run()}
        lesson03_by_code = {item.code: item for item in self._lesson03.run()}
        return [
            lesson03_by_code["greenplum625_connection"],
            lesson03_by_code["greenplum625_database"],
            lesson03_by_code["greenplum625_version"],
            lesson01_by_code["lesson_schema"],
            lesson01_by_code["seed_data"],
            lesson01_by_code["bad_distribution_skew"],
            lesson01_by_code["good_distribution_balance"],
            lesson01_by_code["motion_plan"],
            self._check_lesson02_schema(),
            lesson03_by_code["lesson03_schema"],
            lesson03_by_code["lesson03_fact_rows"],
            lesson03_by_code["optimizer_guc_available"],
            lesson03_by_code["orca_plan_marker"],
        ]

    def _check_lesson02_schema(self) -> CheckResult:
        value = self._sql.scalar(
            "SELECT count(*) FROM information_schema.schemata "
            "WHERE schema_name = 'lesson02'"
        )
        return _result(
            "lesson02_schema",
            "lesson02 schema exists",
            value.strip() == "1",
            f"lesson02 schema count is {value}.",
            "Run `python3 mentor-lab.py seed greenplum --profile lesson02` "
            "(or `--profile academy`).",
        )


def _result(
    code: str,
    title: str,
    passed: bool,
    detail: str,
    remediation: str,
) -> CheckResult:
    return CheckResult(
        code=code,
        title=title,
        status=CheckStatus.PASS if passed else CheckStatus.FAIL,
        detail=detail,
        remediation="" if passed else remediation,
    )
