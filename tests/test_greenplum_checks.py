from mentor_lab.checks import CheckStatus, GreenplumCheckSuite


class FakeSqlClient:
    def __init__(self, responses):
        self.responses = responses
        self.queries = []

    def scalar(self, sql):
        self.queries.append(sql)
        return self.responses[sql]

    def text(self, sql):
        self.queries.append(sql)
        return self.responses[sql]


def test_greenplum_check_suite_passes_for_expected_lab_state():
    suite = GreenplumCheckSuite(
        FakeSqlClient(
            {
                "SELECT 1": "1",
                "SCHEMA_EXISTS": "1",
                "BAD_FACT_ROWS": "50000",
                "BAD_SKEW_MAX_PERCENT": "99.00",
                "GOOD_SKEW_SPREAD_PERCENT": "0.20",
                "BAD_JOIN_EXPLAIN": "Redistribute Motion 2:2\nGather Motion 2:1",
            }
        )
    )

    results = suite.run()

    assert {result.status for result in results} == {CheckStatus.PASS}
    assert [result.code for result in results] == [
        "greenplum_connection",
        "lesson_schema",
        "seed_data",
        "bad_distribution_skew",
        "good_distribution_balance",
        "motion_plan",
    ]


def test_greenplum_check_suite_reports_actionable_failures():
    suite = GreenplumCheckSuite(
        FakeSqlClient(
            {
                "SELECT 1": "1",
                "SCHEMA_EXISTS": "0",
                "BAD_FACT_ROWS": "100",
                "BAD_SKEW_MAX_PERCENT": "50.00",
                "GOOD_SKEW_SPREAD_PERCENT": "40.00",
                "BAD_JOIN_EXPLAIN": "Gather Motion 2:1",
            }
        )
    )

    results = suite.run()
    failures = [result for result in results if result.status == CheckStatus.FAIL]

    assert len(failures) == 5
    assert failures[0].code == "lesson_schema"
    assert "lesson01" in failures[0].remediation
    assert any("Redistribute Motion" in result.remediation for result in failures)

