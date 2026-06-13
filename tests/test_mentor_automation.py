from mentor_lab.evidence import EvidenceCollector
from mentor_lab.homework_review import HomeworkReviewer
from mentor_lab.teaching import TeachingSessionBuilder


def test_teach_mode_renders_stage_with_commands_questions_and_evidence_prompt():
    session = TeachingSessionBuilder.default().build(
        lab_name="greenplum",
        route="simple",
        stage_number=1,
    )

    rendered = session.render()

    assert "# Teach Mode: Simple path" in rendered
    assert "Stage 1/" in rendered
    assert "Слайды:" in rendered
    assert "Что сказать:" in rendered
    assert "Команды сейчас:" in rendered
    assert "Что спросить:" in rendered
    assert "Ожидаемый ответ:" in rendered
    assert "Evidence checkpoint" in rendered
    assert "python3 mentor-lab.py evidence greenplum collect" in rendered


def test_evidence_collector_builds_submission_ready_markdown():
    packet = EvidenceCollector.default().collect(
        lab_name="greenplum",
        task_code="redistribute-join",
    )

    rendered = packet.render()

    assert "# Evidence Pack: redistribute-join" in rendered
    assert "Redistribute Motion" in rendered
    assert "gp_segment_id" in rendered
    assert "EXPLAIN" in rendered
    assert "Validation" in rendered
    assert "python3 mentor-lab.py adaptive-review greenplum" in rendered
    assert "python3 mentor-lab.py learning-loop greenplum" in rendered


def test_homework_reviewer_accepts_complete_architecture_submission():
    submission = """
# Homework

Fact tables: fact_orders, fact_payments.
Dimension tables: dim_customers, dim_products.
Fact grain: one row per order item.
Distribution strategy: DISTRIBUTED BY (customer_id), because the main join
pattern goes through customer_id and cardinality is high enough.
Partition strategy: PARTITION BY RANGE (sale_date). The partition key is not
the distribution key; pruning follows the date filter.
Storage strategy: AOCO column table with appendoptimized=true and
orientation=column for analytical scans; heap stays acceptable for small
dimensions.
Catalog evidence: pg_partition_tree, gp_toolkit.gp_partitions, leaf_partitions.
Quality checks: EXPLAIN ANALYZE, gp_segment_id skew check, before/after
validation.
Risks: stale statistics, Broadcast Motion on growing dimensions, residual risk.
Questions for Lesson 02: partition pruning, statistics after load,
incremental loads.
"""

    review = HomeworkReviewer.default().review_text(submission)

    assert review.accepted is True
    assert review.score >= 90
    assert review.missing == []
    assert "Distribution design" in review.skill_scores
    assert "Lesson 02 readiness" in review.render()


def test_homework_reviewer_rejects_submission_without_physical_evidence():
    submission = """
# Homework

I will create facts and dimensions. Greenplum is fast, so it should work.
"""

    review = HomeworkReviewer.default().review_text(submission)

    assert review.accepted is False
    assert review.score < 60
    assert "Distribution design" in review.missing
    assert "EXPLAIN/gp_segment_id evidence" in review.missing
