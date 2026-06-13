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
    assert "Nuxt portal repo" in output
    assert "https://github.com/PaulKov/de-mentor-portal" in output

    session_json = session_dir / "session.json"
    timeline = session_dir / "timeline.md"
    skill_graph = session_dir / "skill-graph.md"
    mentor_cockpit = session_dir / "mentor-cockpit.md"
    student_handoff = session_dir / "student-handoff.md"

    for path in [session_json, timeline, skill_graph, mentor_cockpit, student_handoff]:
        assert path.exists(), path

    state = json.loads(session_json.read_text(encoding="utf-8"))
    assert state["contract_version"] == "academy-session/v1"
    assert state["academy_version"] == "Academy Experience v5"
    assert state["lab_name"] == "greenplum"
    assert state["student_name"] == "Иван"
    assert state["current_stage"]["code"] == "environment"
    assert state["portal"]["framework"] == "Vue 3 + Nuxt 3 + Vite"
    assert state["portal"]["repository"] == "https://github.com/PaulKov/de-mentor-portal"
    assert state["portal"]["app_path"] == "de-mentor-portal"
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

    handoff = student_handoff.read_text(encoding="utf-8")
    assert "git clone https://github.com/PaulKov/de-mentor-portal.git" in handoff
    assert "MENTOR_LAB_SESSION=" in handoff
    assert "npm run dev" in handoff


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


def test_session_validate_checks_academy_session_contract(tmp_path):
    session_dir = tmp_path / "session"
    broken_session = tmp_path / "broken-session.json"

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
    validate_exit, validate_output = invoke(
        [
            "session",
            "greenplum",
            "validate",
            "--session",
            str(session_dir / "session.json"),
        ]
    )

    payload = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    payload.pop("lab_name")
    broken_session.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    broken_exit, broken_output = invoke(
        [
            "session",
            "greenplum",
            "validate",
            "--session",
            str(broken_session),
        ]
    )

    assert start_exit == 0
    assert validate_exit == 0
    assert "Session contract valid: academy-session/v1" in validate_output
    assert broken_exit == 1
    assert "lab_name" in broken_output


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
    assert "Session contract" in report
    assert "de-mentor-portal" in report
    assert "Vue 3 + Nuxt 3 + Vite" in report
    assert "python3 mentor-lab.py check greenplum --dry-run" in report
    assert "python3 mentor-lab.py autograde-sql greenplum --submission" in report
    assert "python3 mentor-lab.py ci-smoke greenplum --dry-run" in report
    assert "python3 mentor-lab.py session greenplum start" in report


def test_academy_session_contract_is_versioned_and_sampled():
    schema_path = ROOT / "contracts/academy-session/v1/session.schema.json"
    sample_path = ROOT / "contracts/academy-session/v1/session.sample.json"
    readme_path = ROOT / "contracts/academy-session/v1/README.md"

    for path in [schema_path, sample_path, readme_path]:
        assert path.exists(), path

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    sample = json.loads(sample_path.read_text(encoding="utf-8"))

    assert schema["$id"] == (
        "https://github.com/PaulKov/de-mentor/blob/master/"
        "contracts/academy-session/v1/session.schema.json"
    )
    assert schema["properties"]["contract_version"]["const"] == "academy-session/v1"
    assert "portal" in schema["required"]
    assert "skill_graph" in schema["required"]
    assert sample["contract_version"] == "academy-session/v1"
    assert sample["portal"]["repository"] == "https://github.com/PaulKov/de-mentor-portal"


def test_academy_portal_is_split_out_of_core_repo():
    assert not (ROOT / "apps/academy-portal").exists()


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
        "https://github.com/PaulKov/de-mentor-portal",
        "git clone https://github.com/PaulKov/de-mentor-portal.git",
        "MENTOR_LAB_SESSION=",
        "npm run dev",
        "Vue 3 + Nuxt 3 + Vite",
    ]

    for path in docs:
        content = path.read_text(encoding="utf-8")
        for marker in expected:
            assert marker in content
        assert "npm --prefix apps/academy-portal run dev" not in content
