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


def test_session_start_creates_state_for_nuxt_portal(tmp_path):
    session_dir = tmp_path / "ivan-greenplum-session"

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

    assert exit_code == 0
    assert "Academy Experience v5 session started" in output
    assert "Nuxt portal" in output
    assert "npm --prefix apps/academy-portal run dev" in output

    session_json = session_dir / "session.json"
    timeline = session_dir / "timeline.md"
    skill_graph = session_dir / "skill-graph.md"
    mentor_cockpit = session_dir / "mentor-cockpit.md"
    student_handoff = session_dir / "student-handoff.md"

    for path in [session_json, timeline, skill_graph, mentor_cockpit, student_handoff]:
        assert path.exists(), path

    state = json.loads(session_json.read_text(encoding="utf-8"))
    assert state["academy_version"] == "Academy Experience v5"
    assert state["lab_name"] == "greenplum"
    assert state["student_name"] == "Иван"
    assert state["current_stage"]["code"] == "environment"
    assert state["portal"]["framework"] == "Vue 3 + Nuxt 3 + Vite"
    assert "mentor-lab.py autograde-sql greenplum" in "\n".join(state["commands"])
    assert "mentor-lab.py dataset greenplum generate" in "\n".join(state["commands"])

    timeline_text = timeline.read_text(encoding="utf-8")
    assert "## Лента Сессии" in timeline_text
    assert "environment" in timeline_text
    assert "Иван" in timeline_text

    skill_graph_text = skill_graph.read_text(encoding="utf-8")
    assert "## Skill Graph" in skill_graph_text
    assert "QD/QE/gang/slice" in skill_graph_text
    assert "EXPLAIN и Motion" in skill_graph_text


def test_session_event_and_report_update_existing_session(tmp_path):
    session_dir = tmp_path / "session"
    report_path = tmp_path / "session-report.md"

    start_exit, _ = invoke(
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
    event_exit, event_output = invoke(
        [
            "session",
            "greenplum",
            "event",
            "--session",
            str(session_dir),
            "--type",
            "misconception",
            "--note",
            "partition key спутан с distribution key",
        ]
    )
    report_exit, report_output = invoke(
        [
            "session",
            "greenplum",
            "report",
            "--session",
            str(session_dir),
            "--output",
            str(report_path),
        ]
    )

    assert start_exit == 0
    assert event_exit == 0
    assert "Session event recorded" in event_output
    assert report_exit == 0
    assert "Session report written" in report_output
    assert report_path.exists()

    state = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    assert state["events"][-1]["event_type"] == "misconception"
    assert state["events"][-1]["note"] == "partition key спутан с distribution key"

    timeline = (session_dir / "timeline.md").read_text(encoding="utf-8")
    assert "misconception" in timeline
    assert "partition key спутан с distribution key" in timeline

    report = report_path.read_text(encoding="utf-8")
    assert "# Session Report: Greenplum" in report
    assert "Иван" in report
    assert "Academy Experience v5" in report
    assert "Skill Graph" in report
    assert "Next actions" in report
    assert "partition key спутан с distribution key" in report


def test_lesson_doctor_checks_materials_and_portal_contract(tmp_path):
    output_path = tmp_path / "lesson-doctor.md"

    exit_code, output = invoke(
        [
            "lesson-doctor",
            "greenplum",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert "Lesson Doctor report written" in output
    assert output_path.exists()

    report = output_path.read_text(encoding="utf-8")
    assert "# Lesson Doctor: Greenplum" in report
    assert "Academy Experience v5" in report
    assert "PASS" in report
    assert "apps/academy-portal" in report
    assert "Vue 3 + Nuxt 3 + Vite" in report
    assert "python3 mentor-lab.py check greenplum --dry-run" in report
    assert "python3 mentor-lab.py autograde-sql greenplum --submission" in report
    assert "python3 mentor-lab.py ci-smoke greenplum --dry-run" in report
    assert "python3 mentor-lab.py session greenplum start" in report


def test_academy_portal_is_nuxt3_vite_application():
    package_json = ROOT / "apps/academy-portal/package.json"
    nuxt_config = ROOT / "apps/academy-portal/nuxt.config.ts"
    app_vue = ROOT / "apps/academy-portal/app.vue"
    composable = ROOT / "apps/academy-portal/composables/useSessionState.ts"
    sample_session = ROOT / "apps/academy-portal/public/session.sample.json"
    readme = ROOT / "apps/academy-portal/README.md"

    for path in [package_json, nuxt_config, app_vue, composable, sample_session, readme]:
        assert path.exists(), path

    package = json.loads(package_json.read_text(encoding="utf-8"))
    assert package["scripts"]["dev"] == "nuxt dev"
    assert package["scripts"]["build"] == "nuxt build"
    assert package["scripts"]["generate"] == "nuxt generate"
    assert "nuxt" in package["dependencies"]
    assert "vue" in package["dependencies"]

    assert "defineNuxtConfig" in nuxt_config.read_text(encoding="utf-8")

    app = app_vue.read_text(encoding="utf-8")
    expected_markers = [
        "Academy Experience v5",
        "current stage",
        "copy-command",
        "skill graph",
        "mentor-lab.py autograde-sql",
        "mentor-lab.py dataset",
        "mentor-lab.py session greenplum report",
    ]
    for marker in expected_markers:
        assert marker in app

    composable_text = composable.read_text(encoding="utf-8")
    assert "useState" in composable_text
    assert "session.json" in composable_text
    assert "session.sample.json" in composable_text

    sample = json.loads(sample_session.read_text(encoding="utf-8"))
    assert sample["academy_version"] == "Academy Experience v5"
    assert sample["portal"]["framework"] == "Vue 3 + Nuxt 3 + Vite"
    assert sample["current_stage"]["code"] == "environment"


def test_academy_experience_v5_is_documented_in_public_guides():
    docs = [
        ROOT / "README.md",
        ROOT / "docs/lessons/01-greenplum/README.md",
        ROOT / "docs/lessons/01-greenplum/academy-loop.md",
        ROOT / "docs/lessons/01-greenplum/academy-v2.md",
        ROOT / "docs/lessons/01-greenplum/mentor-guide.md",
        ROOT / "docs/lessons/01-greenplum/student-workbook.md",
        ROOT / "docs/lessons/01-greenplum/cheat-sheet.md",
    ]
    expected = [
        "Academy Experience v5",
        "mentor-lab.py session greenplum start",
        "mentor-lab.py session greenplum report",
        "mentor-lab.py lesson-doctor greenplum",
        "apps/academy-portal",
        "npm --prefix apps/academy-portal run dev",
        "Vue 3 + Nuxt 3 + Vite",
    ]

    for path in docs:
        content = path.read_text(encoding="utf-8")
        for marker in expected:
            assert marker in content
