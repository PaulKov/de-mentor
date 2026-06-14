import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from mentor_lab.cli import main
from mentor_lab.lesson_catalog import LessonCatalog
from mentor_lab.runbooks import RunbookCatalog


ROOT = Path(__file__).resolve().parents[1]
LESSON_ROOT = ROOT / "docs" / "lessons" / "02-greenplum-partitioning"
SQL_EXAMPLE = ROOT / "labs" / "greenplum" / "examples" / "lesson02-partitioning-statistics-loads.sql"


def invoke(args):
    stdout = StringIO()
    try:
        with redirect_stdout(stdout):
            exit_code = main(args)
    except SystemExit as exc:
        exit_code = int(exc.code)
    return exit_code, stdout.getvalue()


def test_lesson_02_catalog_exposes_partitioning_curriculum():
    lesson = LessonCatalog.default().get("greenplum-partitioning")

    assert lesson.code == "lesson-02"
    assert lesson.title == "Partitioning, statistics and incremental loads in MPP"
    assert [step.title for step in lesson.steps] == [
        "Replay evidence from Lesson 01",
        "Partition pruning and retention",
        "Statistics after incremental load",
        "Late-arriving facts and idempotency",
        "AOCO partitions and maintenance",
        "Homework handoff and next lesson",
    ]
    assert "partition pruning" in LessonCatalog.default().hints("lesson-02", "partition-pruning")[0]
    assert "ANALYZE" in LessonCatalog.default().hints("lesson-02", "statistics")[0]


def test_lesson_02_documents_and_sql_lab_exist_with_contract_markers():
    expected_docs = [
        LESSON_ROOT / "README.md",
        LESSON_ROOT / "mentor-guide.md",
        LESSON_ROOT / "student-workbook.md",
        LESSON_ROOT / "homework.md",
        LESSON_ROOT / "rubric.md",
        LESSON_ROOT / "runbooks" / "simple-path.md",
        LESSON_ROOT / "runbooks" / "deep-dive-path.md",
        LESSON_ROOT / "runbooks" / "homework-plan.md",
        LESSON_ROOT / "cheat-sheet.md",
    ]

    missing = [path.relative_to(ROOT).as_posix() for path in expected_docs if not path.exists()]
    assert missing == []

    joined_docs = "\n".join(path.read_text(encoding="utf-8") for path in expected_docs)
    for marker in [
        "partition pruning",
        "late-arriving facts",
        "incremental load",
        "ANALYZE",
        "AOCO",
        "pg_partition_tree",
        "gp_toolkit.gp_partitions",
        "lesson02-partitioning-statistics-loads.sql",
        "docs/lessons/02-greenplum-partitioning/homework.md",
    ]:
        assert marker in joined_docs

    sql = SQL_EXAMPLE.read_text(encoding="utf-8")
    for marker in [
        "CREATE SCHEMA IF NOT EXISTS lesson02",
        "CREATE TABLE lesson02.fact_sales_partitioned",
        "WITH (appendoptimized=true, orientation=column",
        "PARTITION BY RANGE (sale_date)",
        "CREATE TABLE lesson02.fact_sales_stage",
        "late-arriving",
        "ANALYZE lesson02.fact_sales_partitioned",
        "pg_partition_tree",
        "gp_toolkit.gp_partitions",
        "EXPLAIN",
    ]:
        assert marker in sql


def test_lesson_02_runbook_cli_routes_are_available():
    for route in ["simple", "deep", "homework"]:
        exit_code, output = invoke(["runbook", "greenplum-partitioning", route])

        assert exit_code == 0, output
        assert "Lesson 02" in output
        assert "lesson02-partitioning-statistics-loads.sql" in output
        assert "docs/lessons/02-greenplum-partitioning/student-workbook.md" in output
        assert "docs/lessons/02-greenplum-partitioning/homework.md" in output


def test_lesson_02_student_self_service_uses_same_greenplum_stand():
    exit_code, bootstrap = invoke(
        ["student", "greenplum-partitioning", "bootstrap", "--platform", "windows"]
    )

    assert exit_code == 0, bootstrap
    assert "Student bootstrap: greenplum-partitioning" in bootstrap
    assert "py mentor-lab.py readiness greenplum --platform windows" in bootstrap
    assert "py mentor-lab.py runbook greenplum-partitioning simple" in bootstrap
    assert "docs/lessons/02-greenplum-partitioning/student-workbook.md" in bootstrap

    exit_code, homework = invoke(["student", "greenplum-partitioning", "homework"])

    assert exit_code == 0, homework
    assert "Student homework: greenplum-partitioning" in homework
    assert "docs/lessons/02-greenplum-partitioning/homework.md" in homework
    assert "python3 mentor-lab.py runbook greenplum-partitioning homework" in homework
    assert "python3 mentor-lab.py check greenplum" in homework


def test_lesson_02_academy_dry_run_separates_lesson_route_from_physical_lab():
    exit_code, output = invoke(
        [
            "academy",
            "greenplum-partitioning",
            "start",
            "--student",
            "Иван",
            "--route",
            "deep",
            "--dry-run",
        ]
    )

    assert exit_code == 0, output
    assert "Lab: greenplum" in output
    assert "Lesson route: greenplum-partitioning" in output
    assert "python3 mentor-lab.py up greenplum" in output
    assert "python3 mentor-lab.py runbook greenplum-partitioning deep" in output
    assert "python3 mentor-lab.py student greenplum-partitioning homework" in output


def test_lesson_02_session_control_plane_points_to_lesson_02_materials(tmp_path):
    session_dir = tmp_path / "lesson02-session"
    exit_code, output = invoke(
        [
            "session",
            "greenplum-partitioning",
            "start",
            "--student",
            "Иван",
            "--output",
            str(session_dir),
        ]
    )

    assert exit_code == 0, output

    state = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    control_plane = state["control_plane"]

    assert control_plane["mentor_mode"]["slide_deck"] == "artifacts/greenplum-theory.pptx"
    assert (ROOT / control_plane["mentor_mode"]["slide_deck"]).exists()
    assert "python3 mentor-lab.py runbook greenplum-partitioning simple" in control_plane["mentor_mode"]["runbook_commands"]
    assert control_plane["student_mode"]["workbook"] == "docs/lessons/02-greenplum-partitioning/student-workbook.md"
    assert control_plane["student_mode"]["homework"] == "docs/lessons/02-greenplum-partitioning/homework.md"
    assert "labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql" in {
        artifact["path"] for artifact in control_plane["artifacts"]
    }
    assert control_plane["next_lesson"]["code"] == "03-greenplum-query-tuning"
    assert control_plane["mentor_mode"]["stage_guides"][0]["stage_code"] == "replay"
    assert "ANALYZE" in control_plane["mentor_mode"]["stage_guides"][2]["show_commands"][0]


def test_lesson_02_cli_lesson_view_is_printable():
    exit_code, output = invoke(["lesson", "lesson-02"])

    assert exit_code == 0, output
    assert "Partitioning, statistics and incremental loads in MPP" in output
    assert "Partition pruning and retention" in output
    assert "Late-arriving facts and idempotency" in output
