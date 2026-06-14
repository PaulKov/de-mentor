from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from mentor_lab.cli import main
from mentor_lab.lesson_release_manifest import LessonReleaseManifestLoader


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "lessons" / "02-greenplum-partitioning" / "lesson.yaml"
GOOGLE_SLIDES_URL = (
    "https://docs.google.com/presentation/d/"
    "17Ae88PoniaFU34egsFPwC0PndAOoXMze4qV1pIKQkaI/edit?usp=sharing"
)


def invoke(args: list[str]) -> tuple[int, str]:
    stdout = StringIO()
    try:
        with redirect_stdout(stdout):
            exit_code = main(args)
    except SystemExit as exc:
        exit_code = int(exc.code)
    return exit_code, stdout.getvalue()


def test_lesson_release_manifest_loads_lesson_02_contract():
    manifest = LessonReleaseManifestLoader(ROOT).load("greenplum-partitioning")

    assert manifest.route == "greenplum-partitioning"
    assert manifest.lesson_code == "lesson-02"
    assert manifest.physical_lab == "greenplum"
    assert manifest.deck_path == "artifacts/greenplum-partitioning-theory.pptx"
    assert manifest.google_slides_url == GOOGLE_SLIDES_URL
    assert manifest.expected_owner_email == "pavelkov007@gmail.com"
    assert manifest.expected_slide_count == 18
    assert manifest.drive_folder == (
        "lessons/Greenplum/"
        "Lesson 02 - Partitioning, statistics and incremental loads"
    )
    assert "docs/lessons/02-greenplum-partitioning/student-workbook.md" in manifest.docs
    assert "labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql" in manifest.sql_examples
    assert "python3 mentor-lab.py runbook greenplum-partitioning simple" in manifest.safe_cli_commands


def test_lesson_release_verify_cli_outputs_preflight_report():
    exit_code, output = invoke(["lesson-release", "greenplum-partitioning", "verify"])

    assert exit_code == 0, output
    assert "# Lesson Release Report: greenplum-partitioning" in output
    assert "Status: READY_WITH_WARNINGS" in output
    assert "PASS manifest" in output
    assert "PASS pptx_artifact" in output
    assert "PASS session_control_plane" in output
    assert "WARN google_slides_live" in output
    assert "python3 mentor-lab.py slides publish greenplum-partitioning --dry-run" in output
    assert "Что Дать Ученику" in output


def test_lesson_release_report_command_writes_markdown(tmp_path):
    output_path = tmp_path / "lesson02-release.md"

    exit_code, output = invoke(
        [
            "lesson-release",
            "greenplum-partitioning",
            "report",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0, output
    assert f"Lesson release report written to {output_path}" in output
    report = output_path.read_text(encoding="utf-8")
    assert "Lesson Release Report: greenplum-partitioning" in report
    assert "docs/lessons/02-greenplum-partitioning/homework.md" in report


def test_lesson_release_publish_slides_dry_run_uses_personal_drive_guard():
    exit_code, output = invoke(
        [
            "lesson-release",
            "greenplum-partitioning",
            "publish-slides",
            "--dry-run",
            "--confirm-account",
            "pavelkov007@gmail.com",
        ]
    )

    assert exit_code == 0, output
    assert "Slides publish dry-run" in output
    assert "Account: pavelkov007@gmail.com" in output
    assert "lessons/Greenplum/Lesson 02 - Partitioning" in output


def test_lesson_release_live_google_verify_requires_credentials():
    exit_code, output = invoke(
        [
            "lesson-release",
            "greenplum-partitioning",
            "verify",
            "--live-google-slides",
            "--confirm-account",
            "pavelkov007@gmail.com",
        ]
    )

    assert exit_code == 1
    assert "--oauth-client-json is required with --live-google-slides" in output


def test_lesson_release_manifest_never_mentions_work_google_account():
    content = MANIFEST.read_text(encoding="utf-8")

    assert "pavel.a.kovalev@1win.pro" not in content


def test_release_pipeline_is_documented_in_readme_and_lesson_index():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    lesson_index = (
        ROOT / "docs" / "lessons" / "02-greenplum-partitioning" / "README.md"
    ).read_text(encoding="utf-8")

    for content in [readme, lesson_index]:
        assert "mentor-lab.py lesson-release greenplum-partitioning verify" in content
        assert "mentor-lab.py lesson-release greenplum-partitioning report" in content
        assert "mentor-lab.py lesson-release greenplum-partitioning publish-slides" in content
        assert "docs/lessons/02-greenplum-partitioning/lesson.yaml" in content
