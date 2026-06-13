import subprocess
import sys


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "mentor-lab.py", *args],
        check=False,
        text=True,
        capture_output=True,
    )


def test_orchestrator_renders_mode_aware_stage_with_decision_gate():
    result = run_cli(
        "orchestrate",
        "greenplum",
        "--route",
        "simple",
        "--stage",
        "1",
        "--mode",
        "recovery",
    )

    assert result.returncode == 0
    assert "Live Lesson Orchestrator" in result.stdout
    assert "Mode: recovery" in result.stdout
    assert "Decision gate" in result.stdout
    assert "Next action" in result.stdout
    assert "timer" in result.stdout.lower()


def test_observe_start_and_report_create_evidence_trail(tmp_path):
    checklist = tmp_path / "observe-checklist.md"
    report = tmp_path / "observe-report.md"
    commands = tmp_path / "commands.log"
    commands.write_text(
        "\n".join(
            [
                "python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join --sample",
                "SELECT gp_segment_id, count(*) FROM lesson01.fact_sales_bad GROUP BY 1;",
                "python3 mentor-lab.py misconception greenplum diagnose --text 'motion always bad'",
            ]
        ),
        encoding="utf-8",
    )

    start = run_cli("observe", "greenplum", "start", "--output", str(checklist))
    observe_report = run_cli(
        "observe",
        "greenplum",
        "report",
        "--commands",
        str(commands),
        "--output",
        str(report),
    )

    assert start.returncode == 0
    assert checklist.exists()
    checklist_text = checklist.read_text(encoding="utf-8")
    assert "Live Lab Observation" in checklist_text
    assert "gp_segment_id" in checklist_text
    assert observe_report.returncode == 0
    assert report.exists()
    report_text = report.read_text(encoding="utf-8")
    assert "Observation Report" in report_text
    assert "EXPLAIN evidence: yes" in report_text
    assert "Segment evidence: yes" in report_text
    assert "Misconception check: yes" in report_text


def test_coach_plan_explains_mpp_plan_and_next_sql():
    result = run_cli(
        "coach-plan",
        "greenplum",
        "--query",
        "bad_customer_join",
        "--sample",
    )

    assert result.returncode == 0
    assert "Query Plan Coach" in result.stdout
    assert "Redistribute Motion" in result.stdout
    assert "Root cause hypothesis" in result.stdout
    assert "Next SQL to run" in result.stdout
    assert "gp_segment_id" in result.stdout


def test_readiness_pro_gives_platform_specific_actions():
    macos = run_cli("readiness", "greenplum", "--platform", "macos")
    windows = run_cli("readiness", "greenplum", "--platform", "windows")
    linux = run_cli("readiness", "greenplum", "--platform", "linux")

    assert macos.returncode == 0
    assert "Readiness Doctor Pro" in macos.stdout
    assert "Docker Desktop" in macos.stdout
    assert "Colima" in macos.stdout
    assert windows.returncode == 0
    assert "WSL 2" in windows.stdout
    assert "PowerShell" in windows.stdout
    assert linux.returncode == 0
    assert "Docker Engine" in linux.stdout
    assert "docker compose" in linux.stdout


def test_calibration_and_replay_commands_create_professional_feedback(tmp_path):
    calibration = run_cli("calibration", "greenplum", "show", "senior")
    submission = tmp_path / "submission.md"
    submission.write_text(
        "Redistribute Motion Hash Join gp_segment_id Physical cause distribution key "
        "join key Change DISTRIBUTED BY Validation EXPLAIN ANALYZE Residual risk "
        "Broadcast Motion. partition key equals distribution key.",
        encoding="utf-8",
    )
    replay = tmp_path / "replay.md"

    replay_result = run_cli(
        "replay",
        "greenplum",
        "--student",
        "Иван",
        "--submission",
        str(submission),
        "--pre",
        "40",
        "--post",
        "85",
        "--output",
        str(replay),
    )

    assert calibration.returncode == 0
    assert "Senior-level submission" in calibration.stdout
    assert "evidence" in calibration.stdout.lower()
    assert replay_result.returncode == 0
    assert replay.exists()
    replay_text = replay.read_text(encoding="utf-8")
    assert "Lesson Replay Pack" in replay_text
    assert "Debrief" in replay_text
    assert "Что принести на Lesson 02" in replay_text


def test_scenario_pack_v2_contains_extra_production_incidents():
    scenarios = run_cli("scenario", "greenplum", "list")
    mutable = run_cli("scenario", "greenplum", "show", "aoco-mutable-dimension")
    coordinator = run_cli("scenario", "greenplum", "show", "coordinator-result-set")

    assert scenarios.returncode == 0
    assert "aoco-mutable-dimension" in scenarios.stdout
    assert "coordinator-result-set" in scenarios.stdout
    assert mutable.returncode == 0
    assert "AOCO" in mutable.stdout
    assert "mutable dimension" in mutable.stdout
    assert coordinator.returncode == 0
    assert "coordinator" in coordinator.stdout.lower()
    assert "Gather Motion" in coordinator.stdout
