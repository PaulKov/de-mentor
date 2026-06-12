from mentor_lab.explain_analyzer import ExplainPlanAnalyzer


SAMPLE_PLAN = """
Gather Motion 2:1  (slice1; segments: 2)
  -> Finalize HashAggregate
        -> Redistribute Motion 2:2  (slice2; segments: 2)
              Hash Key: dim_customers.region
              -> Hash Join
                    Hash Cond: (fact_sales_bad.customer_id = dim_customers.customer_id)
                    -> Redistribute Motion 2:2  (slice3; segments: 2)
                          Hash Key: fact_sales_bad.customer_id
                          -> Seq Scan on fact_sales_bad
                    -> Hash
                          -> Broadcast Motion 2:2  (slice4; segments: 2)
                                -> Seq Scan on dim_customers
"""


def test_explain_analyzer_extracts_motion_join_slices_and_risks():
    analysis = ExplainPlanAnalyzer().analyze(SAMPLE_PLAN)

    assert analysis.motion_counts["Redistribute Motion"] == 2
    assert analysis.motion_counts["Broadcast Motion"] == 1
    assert analysis.motion_counts["Gather Motion"] == 1
    assert analysis.join_algorithms == ["Hash Join"]
    assert analysis.slices == ["slice1", "slice2", "slice3", "slice4"]
    assert "fact_sales_bad.customer_id" in analysis.hash_keys
    assert "Network movement: Redistribute Motion appears 2 time(s)." in analysis.findings
    assert "Broadcast Motion requires a genuinely small input." in analysis.risks


def test_explain_analyzer_renders_student_friendly_report():
    analysis = ExplainPlanAnalyzer().analyze(SAMPLE_PLAN)
    report = ExplainPlanAnalyzer().render(analysis)

    assert "# EXPLAIN Analysis" in report
    assert "Join algorithms" in report
    assert "Redistribute Motion" in report
    assert "Questions to answer" in report
