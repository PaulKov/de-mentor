import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from mentor_lab.cli import main


ROOT = Path(__file__).resolve().parents[1]


def invoke(args):
    stdout = StringIO()
    try:
        with redirect_stdout(stdout):
            exit_code = main(args)
    except SystemExit as exc:
        exit_code = int(exc.code)
    return exit_code, stdout.getvalue()


def create_session(tmp_path):
    session_dir = tmp_path / "ivan-session"
    exit_code, output = invoke(
        [
            "session",
            "greenplum",
            "start",
            "--student",
            "Иван",
            "--output",
            str(session_dir),
        ]
    )
    assert exit_code == 0, output
    return session_dir


def test_session_state_contains_academy_control_plane(tmp_path):
    session_dir = create_session(tmp_path)

    state = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))

    control_plane = state["control_plane"]
    assert control_plane["version"] == "academy-control-plane/v1"
    assert control_plane["mentor_mode"]["default_route"] == "simple"
    assert "python3 mentor-lab.py runbook greenplum simple" in control_plane["mentor_mode"]["runbook_commands"]
    assert control_plane["mentor_mode"]["slide_deck"] == "artifacts/greenplum-theory.pptx"
    assert control_plane["student_mode"]["workbook"] == "docs/lessons/01-greenplum/student-workbook.md"
    assert control_plane["student_mode"]["homework"] == "docs/lessons/01-greenplum/homework.md"
    assert control_plane["next_lesson"]["code"] == "02-greenplum-partitioning"

    environment_guide = control_plane["mentor_mode"]["stage_guides"][0]
    assert environment_guide["stage_code"] == "environment"
    assert environment_guide["slides"] == "1-4"
    assert "паспорт кластера" in environment_guide["mentor_script"]
    assert "python3 mentor-lab.py check greenplum --dry-run" in environment_guide["show_commands"]
    assert environment_guide["question"]
    assert environment_guide["expected_answer"]
    assert environment_guide["verification"]
    assert environment_guide["workbook_ref"] == "docs/lessons/01-greenplum/student-workbook.md"
    assert environment_guide["homework_ref"] == "docs/lessons/01-greenplum/homework.md"

    portal_actions = control_plane["portal_actions"]
    assert "mentor-lab.py portal greenplum start" in portal_actions["start_command"]
    assert "mentor-lab.py portal greenplum export" in portal_actions["export_command"]
    assert "mentor-lab.py portal greenplum open" in portal_actions["open_command"]


def test_portal_start_prints_cross_repo_launch_plan(tmp_path):
    session_dir = create_session(tmp_path)
    portal_dir = tmp_path / "de-mentor-portal"

    exit_code, output = invoke(
        [
            "portal",
            "greenplum",
            "start",
            "--session",
            str(session_dir),
            "--portal-dir",
            str(portal_dir),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert "Portal start plan" in output
    assert str(session_dir / "session.json") in output
    assert "npm ci" in output
    assert "npm run dev" in output
    assert "MENTOR_LAB_SESSION=" in output
    assert "http://127.0.0.1:3000" in output


def test_portal_export_writes_session_json_and_env_file(tmp_path):
    session_dir = create_session(tmp_path)
    portal_dir = tmp_path / "de-mentor-portal"

    exit_code, output = invoke(
        [
            "portal",
            "greenplum",
            "export",
            "--session",
            str(session_dir),
            "--portal-dir",
            str(portal_dir),
        ]
    )

    assert exit_code == 0
    assert "Portal session exported" in output

    exported_session = portal_dir / "public" / "session.json"
    env_file = portal_dir / ".env"
    assert exported_session.exists()
    assert env_file.exists()

    source_state = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    exported_state = json.loads(exported_session.read_text(encoding="utf-8"))
    assert exported_state["control_plane"] == source_state["control_plane"]
    assert f"MENTOR_LAB_SESSION={session_dir / 'session.json'}" in env_file.read_text(encoding="utf-8")


def test_portal_open_supports_dry_run_without_side_effects():
    exit_code, output = invoke(
        [
            "portal",
            "greenplum",
            "open",
            "--url",
            "http://127.0.0.1:3000",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert "Would open portal: http://127.0.0.1:3000" in output


def test_academy_control_plane_is_documented():
    docs = [
        ROOT / "README.md",
        ROOT / "docs/lessons/01-greenplum/README.md",
        ROOT / "docs/lessons/01-greenplum/mentor-guide.md",
        ROOT / "docs/lessons/01-greenplum/student-workbook.md",
    ]
    markers = [
        "Academy Control Plane",
        "mentor-lab.py portal greenplum start",
        "mentor-lab.py portal greenplum export",
        "mentor-lab.py portal greenplum open",
    ]

    for path in docs:
        content = path.read_text(encoding="utf-8")
        for marker in markers:
            assert marker in content, f"{marker} missing from {path}"
