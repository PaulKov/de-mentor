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
