import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from zipfile import ZipFile

from mentor_lab.cli import main
from mentor_lab.lesson_catalog import LessonCatalog
from mentor_lab.lesson_routes import resolve_learning_route
from mentor_lab.runbooks import RunbookCatalog


ROOT = Path(__file__).resolve().parents[1]
LESSON_ROOT = ROOT / "docs" / "lessons" / "03-greenplum-query-tuning"
SQL_EXAMPLE = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-olap-decomposition-tuning.sql"
)
OPTIMIZER_SQL = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-optimizer-legacy-vs-orca.sql"
)
GOOGLE_SLIDES_URL = (
    "https://docs.google.com/presentation/d/"
    "1e5vpqatw6ccgeZF0PWLLWMzIqkb4SODE-IwKxrSyqB8/edit?usp=sharing"
)


def invoke(args):
    stdout = StringIO()
    try:
        with redirect_stdout(stdout):
            exit_code = main(args)
    except SystemExit as exc:
        exit_code = int(exc.code)
    return exit_code, stdout.getvalue()


def test_lesson_03_route_uses_greenplum_625_lab():
    route = resolve_learning_route("greenplum-query-tuning")
    assert route.physical_lab_name == "greenplum-625"
    assert route.google_slides_url == GOOGLE_SLIDES_URL
    assert "labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql" in route.sql_examples


def test_lesson_03_catalog_exposes_query_tuning_curriculum():
    lesson = LessonCatalog.default().get("greenplum-query-tuning")

    assert lesson.code == "lesson-03"
    assert lesson.title == "Декомпозиция и тюнинг тяжёлых запросов в MPP"
    assert [step.title for step in lesson.steps] == [
        "Стенд GP 6.25 и стадии оптимизации",
        "Legacy vs GPORCA",
        "Чтение сложного EXPLAIN слоями",
        "Статистика до pg_statistic",
        "Физическое хранение Heap/AO/AOCO",
        "TEMP-декомпозиция, spill и homework",
    ]
    assert "Motion" in LessonCatalog.default().hints("lesson-03", "plan-reading")[0]
    assert "pg_stats" in LessonCatalog.default().hints("lesson-03", "statistics")[0]


def test_lesson_03_documents_and_sql_lab_exist_with_contract_markers():
    expected_docs = [
        LESSON_ROOT / "README.md",
        LESSON_ROOT / "mentor-guide.md",
        LESSON_ROOT / "student-workbook.md",
        LESSON_ROOT / "homework.md",
        LESSON_ROOT / "rubric.md",
        LESSON_ROOT / "cheat-sheet.md",
        LESSON_ROOT / "runbooks" / "simple-path.md",
        LESSON_ROOT / "runbooks" / "deep-dive-path.md",
        LESSON_ROOT / "runbooks" / "homework-plan.md",
        LESSON_ROOT / "runbooks" / "student-prep.md",
        LESSON_ROOT / "deep-dives" / "pg-statistic-internals.md",
        LESSON_ROOT / "deep-dives" / "storage-physical-layout.md",
        LESSON_ROOT / "deep-dives" / "temp-tables-and-spill.md",
        LESSON_ROOT / "deep-dives" / "optimizer-legacy-vs-orca.md",
    ]

    missing = [path.relative_to(ROOT).as_posix() for path in expected_docs if not path.exists()]
    assert missing == []

    joined_docs = "\n".join(path.read_text(encoding="utf-8") for path in expected_docs)
    for marker in [
        "EXPLAIN",
        "pg_statistic",
        "TEMP",
        "AOCO",
        "GPORCA",
        "greenplum-625",
        "mentor",
        "lesson03-olap-decomposition-tuning.sql",
        "homework",
        "Principal",
    ]:
        assert marker in joined_docs

    sql = SQL_EXAMPLE.read_text(encoding="utf-8")
    for marker in [
        "Database: mentor",
        "CREATE SCHEMA IF NOT EXISTS lesson03",
        "CREATE TABLE lesson03.fact_sales",
        "appendonly = true",
        "orientation = column",
        "v_heavy_olap_monolith",
        "v_star_join_orca_case",
        "CREATE TEMP TABLE tmp_lesson03_sales_feb",
        "ANALYZE tmp_lesson03_sales_feb",
        "optimizer",
    ]:
        assert marker in sql

    optimizer_sql = OPTIMIZER_SQL.read_text(encoding="utf-8")
    assert "SET optimizer = on" in optimizer_sql
    assert "SET optimizer = off" in optimizer_sql


def test_lesson_03_runbook_cli_routes_are_available():
    for route in ["simple", "deep", "homework"]:
        exit_code, output = invoke(["runbook", "greenplum-query-tuning", route])

        assert exit_code == 0, output
        assert "тюнинг" in output or "Урок 03" in output
        assert "lesson03-olap-decomposition-tuning.sql" in output
        assert "greenplum-625" in output


def test_lesson_03_runbook_slide_references_fit_the_standalone_deck():
    deck_path = ROOT / "artifacts" / "greenplum-query-tuning-theory.pptx"
    assert deck_path.exists()
    assert deck_path.stat().st_size > 50_000

    with ZipFile(deck_path) as pptx:
        slides = [
            name
            for name in pptx.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
    assert len(slides) == 65

    catalog = RunbookCatalog.default()
    simple = catalog.get("greenplum-query-tuning", "simple")
    assert simple.stages[0].slides


def test_lesson_03_deck_source_has_russian_and_optimizer_markers():
    deck_dir = ROOT / "decks" / "greenplum-query-tuning-theory"
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(deck_dir.rglob("*.md")) + sorted(deck_dir.rglob("*.mjs"))
    )
    assert "#F7F7F4" in source
    assert "Декомпозиция и тюнинг тяжёлых запросов в MPP" in source
    assert "GPORCA" in source
    assert "Legacy" in source
    assert "Grand Unified Configuration" in source
    assert "Star-join" in source or "star-join" in source
    assert "equi-depth" in source or "histogram_bounds" in source
    assert (ROOT / "artifacts/lesson03-plan-screens/stats-histogram-structure.png").exists()
    assert "greenplum-625" in source
    assert "pg_statistic" in source
    assert (ROOT / "artifacts/lesson03-plan-screens/explain-orca.png").exists()
    assert (ROOT / "artifacts/lesson03-plan-screens/explain-legacy.png").exists()
    assert (ROOT / "artifacts/lesson03-plan-screens/temp-relfilenode-fs.png").exists()
    assert (ROOT / "artifacts/lesson03-plan-screens/spill-pgsql_tmp-growth.png").exists()
    assert "pgsql_tmp_Sort" in source or "external merge" in source


def test_lesson_03_session_control_plane_points_to_lesson_03_materials(tmp_path):
    session_dir = tmp_path / "lesson03-session"
    exit_code, output = invoke(
        [
            "session",
            "greenplum-query-tuning",
            "start",
            "--student",
            "Иван",
            "--output",
            str(session_dir),
        ]
    )
    assert exit_code == 0, output
    control_plane = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))[
        "control_plane"
    ]
    assert control_plane["mentor_mode"]["slide_deck"] == "artifacts/greenplum-query-tuning-theory.pptx"
    assert control_plane["mentor_mode"]["google_slides"] == GOOGLE_SLIDES_URL
    assert "labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql" in {
        item["path"] for item in control_plane["artifacts"] if item["kind"] == "sql"
    }
    assert control_plane["next_lesson"]["code"] == "04-greenplum-wlm-diagnostics"
    assert control_plane["mentor_mode"]["stage_guides"][0]["stage_code"] == "lab-optimizer"


def test_lesson_03_cli_lesson_view_is_printable():
    exit_code, output = invoke(["lesson", "lesson-03"])
    assert exit_code == 0, output
    assert "Декомпозиция" in output or "тюнинг" in output
    assert "GPORCA" in output or "Legacy" in output or "6.25" in output
