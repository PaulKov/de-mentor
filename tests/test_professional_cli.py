from contextlib import redirect_stdout
from io import StringIO

from mentor_lab.cli import main


def invoke(args):
    stdout = StringIO()
    with redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, stdout.getvalue()


def test_lesson_command_prints_interactive_runner_steps():
    exit_code, output = invoke(["lesson", "01", "--step", "3"])

    assert exit_code == 0
    assert "Step 3" in output
    assert "distribution" in output.lower()
    assert "Expected outcome" in output


def test_lesson_command_accepts_greenplum_alias():
    exit_code, output = invoke(["lesson", "greenplum", "--step", "3"])

    assert exit_code == 0
    assert "Step 3" in output
    assert "Greenplum MPP Foundations" in output


def test_hint_command_prints_progressive_hints():
    exit_code, output = invoke(["hint", "lesson-01", "skew"])

    assert exit_code == 0
    assert "Hint 1" in output
    assert "Hint 3" in output
    assert "DISTRIBUTED BY" in output


def test_hint_command_accepts_human_aliases():
    exit_code, output = invoke(["hint", "greenplum", "skew-investigation"])

    assert exit_code == 0
    assert "Hint 1" in output
    assert "gp_segment_id" in output


def test_hint_command_supports_adaptive_levels():
    exit_code, output = invoke(["hint", "greenplum", "physical-joins", "--level", "2"])

    assert exit_code == 0
    assert "Hint 2" in output
    assert "Broadcast Motion" in output
    assert "Hint 1" not in output


def test_advanced_hint_commands_are_available():
    plan_exit, plan_output = invoke(["hint", "greenplum", "plan-reading"])
    join_exit, join_output = invoke(["hint", "greenplum", "physical-joins"])
    systems_exit, systems_output = invoke(["hint", "greenplum", "mpp-systems"])

    assert plan_exit == 0
    assert "Motion" in plan_output
    assert join_exit == 0
    assert "Broadcast Motion" in join_output
    assert systems_exit == 0
    assert "EPP" in systems_output


def test_academy_loop_commands_are_available_without_database(tmp_path):
    submission = tmp_path / "submission.md"
    cockpit = tmp_path / "cockpit.html"
    certificate = tmp_path / "certificate.md"

    analyze_exit, analyze_output = invoke(["analyze-plan", "greenplum", "--query", "bad_customer_join", "--sample"])
    pre_exit, pre_output = invoke(["assessment", "greenplum", "pre"])
    submit_exit, submit_output = invoke(["submit", "greenplum", "advanced-joins", "--output", str(submission)])
    review_exit, review_output = invoke(["review", "greenplum", "--submission", str(submission)])
    tuning_exit, tuning_output = invoke(["tuning", "greenplum", "list"])
    cockpit_exit, cockpit_output = invoke(["cockpit", "greenplum", "--output", str(cockpit)])
    cert_exit, cert_output = invoke(["certificate", "greenplum", "--output", str(certificate), "--dry-run"])

    assert analyze_exit == 0
    assert "EXPLAIN Analysis" in analyze_output
    assert pre_exit == 0
    assert "Pre-assessment" in pre_output
    assert submit_exit == 0
    assert submission.exists()
    assert "Submission template written" in submit_output
    assert review_exit == 0
    assert "Submission review" in review_output
    assert tuning_exit == 0
    assert "missing-statistics" in tuning_output
    assert cockpit_exit == 0
    assert cockpit.exists()
    assert "Cockpit written" in cockpit_output
    assert cert_exit == 0
    assert certificate.exists()
    assert "Certificate written" in cert_output


def test_incident_list_and_start_are_available_without_database():
    list_exit, list_output = invoke(["incident", "list"])
    start_exit, start_output = invoke(["incident", "start", "skewed-distribution"])

    assert list_exit == 0
    assert "skewed-distribution" in list_output
    assert start_exit == 0
    assert "Marketplace revenue report became slow" in start_output
    assert "Acceptance criteria" in start_output


def test_incident_commands_accept_lesson_and_incident_aliases():
    list_exit, list_output = invoke(["incident", "list", "greenplum"])
    start_exit, start_output = invoke(["incident", "start", "greenplum", "skew-investigation"])

    assert list_exit == 0
    assert "Greenplum MPP Foundations" in list_output
    assert start_exit == 0
    assert "Marketplace revenue report became slow" in start_output


def test_hidden_incidents_are_available():
    list_exit, list_output = invoke(["incident", "list", "greenplum"])
    start_exit, start_output = invoke(["incident", "start", "greenplum", "slow-product-analytics"])

    assert list_exit == 0
    assert "slow-product-analytics" in list_output
    assert "broken-daily-mart" in list_output
    assert start_exit == 0
    assert "Hidden incident" in start_output


def test_seed_dry_run_points_to_container_seed_file():
    exit_code, output = invoke(["seed", "greenplum", "--profile", "enterprise", "--dry-run"])

    assert exit_code == 0
    assert "docker compose -f" in output
    assert "/mentor-lab/seed/enterprise.sql" in output


def test_grade_dry_run_uses_documented_checks():
    exit_code, output = invoke(["grade", "lesson-01", "--dry-run"])

    assert exit_code == 0
    assert "greenplum_connection" in output
    assert "motion_plan" in output
    assert "Score requires a running Greenplum lab" in output


def test_grade_dry_run_accepts_greenplum_alias():
    exit_code, output = invoke(["grade", "greenplum", "--dry-run"])

    assert exit_code == 0
    assert "Score requires a running Greenplum lab" in output
