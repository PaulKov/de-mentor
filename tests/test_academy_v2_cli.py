import subprocess
import sys


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "mentor-lab.py", *args],
        check=False,
        text=True,
        capture_output=True,
    )


def test_portal_command_writes_student_html(tmp_path):
    output = tmp_path / "portal.html"

    result = run_cli("portal", "greenplum", "--output", str(output))

    assert result.returncode == 0
    assert output.exists()
    assert "Student Portal" in output.read_text(encoding="utf-8")


def test_control_room_command_writes_mentor_html(tmp_path):
    output = tmp_path / "control-room.html"

    result = run_cli("control-room", "greenplum", "--output", str(output))

    assert result.returncode == 0
    assert output.exists()
    assert "Mentor Control Room" in output.read_text(encoding="utf-8")


def test_visualize_plan_prints_mermaid_sample():
    result = run_cli(
        "visualize-plan",
        "greenplum",
        "--query",
        "product_join",
        "--sample",
        "--format",
        "mermaid",
    )

    assert result.returncode == 0
    assert "flowchart TD" in result.stdout
    assert "Broadcast Motion" in result.stdout


def test_visualize_plan_writes_html_sample(tmp_path):
    output = tmp_path / "plan.html"

    result = run_cli(
        "visualize-plan",
        "greenplum",
        "--query",
        "bad_customer_join",
        "--sample",
        "--format",
        "html",
        "--output",
        str(output),
    )

    assert result.returncode == 0
    assert output.exists()
    assert "Greenplum EXPLAIN Visualizer" in output.read_text(encoding="utf-8")


def test_diagnostics_show_supports_dry_run_sql():
    result = run_cli("diagnostics", "greenplum", "show", "segment-skew")

    assert result.returncode == 0
    assert "gp_segment_id" in result.stdout


def test_scenario_start_can_dry_run_with_seed():
    result = run_cli(
        "scenario",
        "greenplum",
        "start",
        "--difficulty",
        "medium",
        "--seed",
        "42",
        "--dry-run",
    )

    assert result.returncode == 0
    assert "Scenario:" in result.stdout
    assert "Seed profile:" in result.stdout


def test_adaptive_review_command_scores_submission(tmp_path):
    submission = tmp_path / "submission.md"
    submission.write_text(
        "Redistribute Motion Hash Join gp_segment_id distribution key join key "
        "Physical cause Validation Residual risk",
        encoding="utf-8",
    )

    result = run_cli("adaptive-review", "greenplum", "--submission", str(submission))

    assert result.returncode == 0
    assert "Adaptive review" in result.stdout


def test_solution_and_challenge_commands_are_available():
    solution = run_cli("solutions", "greenplum", "show", "redistribute-join")
    challenge = run_cli(
        "challenge",
        "greenplum",
        "start",
        "--difficulty",
        "hard",
        "--minutes",
        "15",
        "--seed",
        "7",
    )

    assert solution.returncode == 0
    assert "Golden solution" in solution.stdout
    assert challenge.returncode == 0
    assert "Timed challenge" in challenge.stdout


def test_telemetry_and_dsl_commands_are_available():
    telemetry = run_cli("telemetry", "greenplum", "--pre", "40", "--post", "85", "--review", "70")
    dsl = run_cli("dsl", "greenplum", "show", "redistribute-join")

    assert telemetry.returncode == 0
    assert "Growth: +45" in telemetry.stdout
    assert dsl.returncode == 0
    assert "plan_contains" in dsl.stdout


def test_learning_loop_command_generates_student_follow_up_report(tmp_path):
    submission = tmp_path / "query-tuning.md"
    output = tmp_path / "learning-loop.md"
    submission.write_text(
        "Redistribute Motion Hash Join gp_segment_id Physical cause distribution key "
        "join key Change DISTRIBUTED BY Validation EXPLAIN ANALYZE Residual risk "
        "Broadcast Motion",
        encoding="utf-8",
    )

    result = run_cli(
        "learning-loop",
        "greenplum",
        "--pre",
        "40",
        "--post",
        "85",
        "--submission",
        str(submission),
        "--output",
        str(output),
    )

    assert result.returncode == 0
    assert "Learning loop report written" in result.stdout
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "Рост: +45" in content
    assert "Карта Навыков" in content
    assert "+1 день" in content


def test_teach_evidence_and_homework_commands_are_available(tmp_path):
    teach = run_cli("teach", "greenplum", "simple", "--stage", "1")

    evidence_output = tmp_path / "redistribute-evidence.md"
    evidence = run_cli(
        "evidence",
        "greenplum",
        "collect",
        "redistribute-join",
        "--output",
        str(evidence_output),
    )

    homework_submission = tmp_path / "homework.md"
    homework_submission.write_text(
        "Fact tables: fact_orders. Dimension tables: dim_customers. "
        "Fact grain: one row per order item. "
        "Distribution strategy: DISTRIBUTED BY (customer_id), join pattern, cardinality. "
        "Partition strategy: PARTITION BY RANGE (sale_date), partition key is not distribution key. "
        "Storage strategy: AOCO appendoptimized=true orientation=column; heap for dimensions. "
        "Catalog evidence: pg_partition_tree gp_toolkit.gp_partitions leaf_partitions. "
        "Quality checks: EXPLAIN ANALYZE gp_segment_id before/after validation. "
        "Risks: stale statistics Broadcast Motion residual risk. "
        "Questions for Lesson 02: partition pruning statistics incremental loads.",
        encoding="utf-8",
    )
    homework = run_cli(
        "homework",
        "greenplum",
        "check",
        "--submission",
        str(homework_submission),
    )

    assert teach.returncode == 0
    assert "Teach Mode" in teach.stdout
    assert "Evidence checkpoint" in teach.stdout
    assert evidence.returncode == 0
    assert "Evidence pack written" in evidence.stdout
    assert evidence_output.exists()
    assert "Redistribute Motion" in evidence_output.read_text(encoding="utf-8")
    assert homework.returncode == 0
    assert "Homework review" in homework.stdout
    assert "Accepted: yes" in homework.stdout


def test_homework_command_returns_non_zero_for_incomplete_submission(tmp_path):
    homework_submission = tmp_path / "homework.md"
    homework_submission.write_text("I understood everything.", encoding="utf-8")

    result = run_cli(
        "homework",
        "greenplum",
        "check",
        "--submission",
        str(homework_submission),
    )

    assert result.returncode == 1
    assert "Accepted: no" in result.stdout
    assert "EXPLAIN/gp_segment_id evidence" in result.stdout
