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
            "Start the lab with `python3 mentor-lab.py up greenplum`.",
        )

    def _check_schema(self) -> CheckResult:
        value = self._sql.scalar("SCHEMA_EXISTS")
        return _result(
            "lesson_schema",
            "lesson01 schema exists",
            value.strip() == "1",
            f"lesson01 schema count is {value}.",
            "Reset and initialize the lab so the lesson01 schema is created.",
        )

    def _check_seed_data(self) -> CheckResult:
        rows = int(float(self._sql.scalar("BAD_FACT_ROWS").strip()))
        return _result(
            "seed_data",
            "Seed data loaded",
            rows >= 50000,
            f"fact_sales_bad has {rows} rows.",
            "Run `python3 mentor-lab.py seed greenplum --profile skewed`.",
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
