import subprocess
import sys

from mentor_lab.dataset_generator import DatasetGenerator, DatasetSpec
from mentor_lab.sql_autograder import SqlSubmissionGrader


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "mentor-lab.py", *args],
        check=False,
        text=True,
        capture_output=True,
    )


def test_sql_submission_grader_scores_real_greenplum_evidence():
    submission = """
CREATE TABLE lesson01.fact_orders_student (
    order_id bigint,
    customer_id bigint,
    sale_date date,
    amount numeric(12, 2)
)
WITH (appendoptimized=true, orientation=column, compresstype=zstd)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date)
(
    START (DATE '2026-01-01') END (DATE '2026-04-01') EVERY (INTERVAL '1 month')
);

EXPLAIN ANALYZE
SELECT customer_id, sum(amount)
FROM lesson01.fact_orders_student
GROUP BY customer_id;

SELECT gp_segment_id, count(*)
FROM lesson01.fact_orders_student
GROUP BY gp_segment_id;

ANALYZE lesson01.fact_orders_student;
-- validation before/after: compare EXPLAIN ANALYZE and segment spread
"""

    grade = SqlSubmissionGrader.default().grade_text("greenplum", submission)

    assert grade.score >= 85
    assert grade.accepted
    assert grade.passed_codes == [
        "distributed_by",
        "partition_by_range",
        "aoco_storage",
        "explain_analyze",
        "segment_evidence",
        "statistics_refresh",
        "validation_before_after",
    ]
    assert "Real SQL Autograde" in grade.render()


def test_autograde_sql_cli_writes_report(tmp_path):
    submission = tmp_path / "submission.sql"
    report = tmp_path / "grade.md"
    submission.write_text(
        "CREATE TABLE lesson01.fact_student (customer_id bigint, sale_date date) "
        "WITH (appendoptimized=true, orientation=column) "
        "DISTRIBUTED BY (customer_id) PARTITION BY RANGE (sale_date) "
        "(START (DATE '2026-01-01') END (DATE '2026-02-01') EVERY (INTERVAL '1 day')); "
        "EXPLAIN ANALYZE SELECT * FROM lesson01.fact_student; "
        "SELECT gp_segment_id, count(*) FROM lesson01.fact_student GROUP BY 1; "
        "ANALYZE lesson01.fact_student; validation before/after",
        encoding="utf-8",
    )

    result = run_cli(
        "autograde-sql",
        "greenplum",
        "--submission",
        str(submission),
        "--output",
        str(report),
    )

    assert result.returncode == 0
    assert "SQL autograde report written" in result.stdout
    assert report.exists()
    content = report.read_text(encoding="utf-8")
    assert "Score:" in content
    assert "Accepted: yes" in content
    assert "distributed_by" in content


def test_dataset_generator_produces_deterministic_greenplum_seed_sql():
    first = DatasetGenerator().generate(
        DatasetSpec(lab_name="greenplum", scale="small", seed=42, skew="high", late_facts=True, wide_rows=True)
    )
    second = DatasetGenerator().generate(
        DatasetSpec(lab_name="greenplum", scale="small", seed=42, skew="high", late_facts=True, wide_rows=True)
    )

    assert first.sql == second.sql
    assert "Dataset Generator Pro" in first.sql
    assert "SELECT setseed(0.42);" in first.sql
    assert "generate_series(1, 5000)" in first.sql
    assert "lesson01.generated_fact_sales" in first.sql
    assert "late arriving facts" in first.sql
    assert "wide_payload" in first.sql
    assert "DISTRIBUTED BY (customer_id)" in first.sql


def test_dataset_cli_manifest_and_generate(tmp_path):
    output = tmp_path / "generated.sql"

    manifest = run_cli("dataset", "greenplum", "manifest")
    generated = run_cli(
        "dataset",
        "greenplum",
        "generate",
        "--scale",
        "small",
        "--seed",
        "42",
        "--skew",
        "high",
        "--late-facts",
        "--wide-rows",
        "--output",
        str(output),
    )

    assert manifest.returncode == 0
    assert "Dataset Generator Pro" in manifest.stdout
    assert "small: 5000 fact rows" in manifest.stdout
    assert generated.returncode == 0
    assert "Dataset SQL written" in generated.stdout
    assert output.exists()
    assert "generated_fact_sales" in output.read_text(encoding="utf-8")


def test_ci_smoke_cli_and_workflow_are_available():
    dry_run = run_cli("ci-smoke", "greenplum", "--dry-run")

    assert dry_run.returncode == 0
    assert "Greenplum Live Smoke Plan" in dry_run.stdout
    assert "python3 mentor-lab.py up greenplum" in dry_run.stdout
    assert "python3 mentor-lab.py autograde-sql greenplum" in dry_run.stdout

    workflow = ".github/workflows/greenplum-smoke.yml"
    with open(workflow, encoding="utf-8") as handle:
        content = handle.read()
    assert "Greenplum Live Smoke" in content
    assert "mentor-lab.py check greenplum" in content
    assert "mentor-lab.py dataset greenplum generate" in content
    assert "mentor-lab.py autograde-sql greenplum" in content
