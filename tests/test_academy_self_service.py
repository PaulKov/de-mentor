from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from mentor_lab.academy_self_service import AcademySelfService, AcademyStartOptions
from mentor_lab.cli import main
from mentor_lab.registry import create_default_registry


ROOT = Path(__file__).resolve().parents[1]


def invoke(args):
    stdout = StringIO()
    try:
        with redirect_stdout(stdout):
            exit_code = main(args)
    except SystemExit as exc:
        exit_code = int(exc.code)
    return exit_code, stdout.getvalue()


def test_academy_start_dry_run_prints_one_command_lesson_plan(tmp_path):
    session_dir = tmp_path / "session"
    portal_dir = tmp_path / "portal"

    exit_code, output = invoke(
        [
            "academy",
            "greenplum",
            "start",
            "--student",
            "Иван",
            "--session-dir",
            str(session_dir),
            "--portal-dir",
            str(portal_dir),
            "--route",
            "simple",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert "Academy self-service start plan" in output
    assert "Student: Иван" in output
    assert "Route: simple" in output
    assert "python3 mentor-lab.py doctor --full" in output
    assert "python3 mentor-lab.py up greenplum" in output
    assert "python3 mentor-lab.py session greenplum start --student Иван" in output
    assert "python3 mentor-lab.py portal greenplum export" in output
    assert "cd " in output and "npm run dev" in output
    assert "--host 127.0.0.1 --port 3000" in output
    assert "python3 mentor-lab.py runbook greenplum simple" in output
    assert not session_dir.exists()
    assert not portal_dir.exists()


def test_academy_start_skip_lab_creates_session_and_exports_portal_state(tmp_path):
    session_dir = tmp_path / "session"
    portal_dir = tmp_path / "portal"

    exit_code, output = invoke(
        [
            "academy",
            "greenplum",
            "start",
            "--student",
            "Иван",
            "--session-dir",
            str(session_dir),
            "--portal-dir",
            str(portal_dir),
            "--skip-lab",
        ]
    )

    assert exit_code == 0
    assert "Academy session prepared" in output
    assert "Lab start skipped" in output
    assert (session_dir / "session.json").exists()
    assert (portal_dir / "public" / "session.json").exists()
    assert (portal_dir / ".env").exists()


def test_academy_self_service_returns_lab_start_failure(tmp_path):
    class FailingRunner:
        def build_up_command(self, lab):
            return ["docker", "compose", "up", "-d"]

        def format_command(self, command):
            return " ".join(command)

        def run(self, command):
            return 42

    lab = create_default_registry(ROOT).get("greenplum")
    result = AcademySelfService(FailingRunner()).start(
        lab,
        AcademyStartOptions(
            student="Иван",
            session_dir=tmp_path / "session",
            portal_dir=tmp_path / "portal",
        ),
    )

    assert result.exit_code == 42
    assert "Lab start failed with exit code 42" in result.render()


def test_student_bootstrap_prints_platform_specific_setup():
    exit_code, output = invoke(
        [
            "student",
            "greenplum",
            "bootstrap",
            "--platform",
            "windows",
        ]
    )

    assert exit_code == 0
    assert "Student bootstrap: greenplum" in output
    assert "Windows" in output
    assert "Docker Desktop" in output
    assert "WSL 2" in output
    assert "py mentor-lab.py doctor --full" in output
    assert "py mentor-lab.py academy greenplum start --student" in output
    assert "runbooks/student-prep.md" in output


def test_student_homework_prints_self_check_route():
    exit_code, output = invoke(["student", "greenplum", "homework"])

    assert exit_code == 0
    assert "Student homework: greenplum" in output
    assert "docs/lessons/01-greenplum/homework.md" in output
    assert "docs/lessons/01-greenplum/runbooks/homework-plan.md" in output
    assert "python3 mentor-lab.py runbook greenplum homework" in output
    assert "python3 mentor-lab.py check greenplum" in output
    assert "Lesson 02" in output


def test_doctor_full_prints_core_portal_and_quality_guard_checks():
    exit_code, output = invoke(["doctor", "--full"])

    assert exit_code == 0
    assert "Full environment doctor" in output
    assert "Core repo" in output
    assert "Portal repo" in output
    assert "Docker Compose" in output
    assert "Quality guard" in output
    assert "python3 -m pytest tests/test_quality_guards.py -q" in output
    assert "npm run check" in output


def test_release_notes_document_self_service_release():
    release_notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")

    assert "Academy Self-Service v1" in release_notes
    assert "mentor-lab.py academy greenplum start" in release_notes
    assert "mentor-lab.py student greenplum bootstrap" in release_notes
    assert "doctor --full" in release_notes
