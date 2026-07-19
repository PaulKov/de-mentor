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
LESSON_PACK = ROOT / "lessons" / "lesson-03"
LESSON_ROOT = LESSON_PACK / "docs"
HOMEWORK_ROOT = LESSON_PACK / "homework"
HOMEWORK_SEED = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-homework-seed.sql"
)
CLASS_DEMO = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-class-demo.sql"
)
SQL_EXAMPLE = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-olap-decomposition-tuning.sql"
)
REFERENCE_REWRITE = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "solutions"
    / "lesson03-reference-rewrite.sql"
)
OPTIMIZER_SQL = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-optimizer-legacy-vs-orca.sql"
)
CARDINALITY_SQL = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "examples"
    / "lesson03-cardinality-histogram-demo.sql"
)
TEMP_LIFECYCLE_SQL = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "examples"
    / "lesson03-temp-on-commit-lifecycle.sql"
)
STATS_ANALYZE_SQL = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "examples"
    / "lesson03-stats-analyze-lifecycle.sql"
)
E2E_CASE_SQL = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-e2e-case-metrics.sql"
)
STORAGE_SQL = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-storage-heap-ao-aoco.sql"
)
NLJ_CASE_SQL = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-nlj-cte-temp-case.sql"
)
ORCA_CE_SQL = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-orca-ce-trap.sql"
)
LEGACY_CE_SQL = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-legacy-ce-trap.sql"
)
PRINCIPAL_SQL = (
    ROOT / "labs" / "greenplum-625" / "examples" / "lesson03-principal-scd2-locus.sql"
)
SECRET18_SQL = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "examples"
    / "lesson03-secret18-not-in-broadcast.sql"
)
SECRET14_SQL = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "examples"
    / "lesson03-secret14-window-partition-skew.sql"
)
SECRET29_SQL = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "examples"
    / "lesson03-secret29-values-params-broadcast.sql"
)
SECRET42_SQL = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "examples"
    / "lesson03-secret42-distinct-by-segment.sql"
)
SECRET41_SQL = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "examples"
    / "lesson03-secret41-autostats-partitions.sql"
)
SECRET38_SQL = (
    ROOT
    / "labs"
    / "greenplum-625"
    / "examples"
    / "lesson03-secret38-median-gather-qd.sql"
)
FULL_PPTX = ROOT / "lessons" / "lesson-03" / "artifacts" / "greenplum-query-tuning-theory.pptx"
CORE_ONLY_PPTX = ROOT / "lessons" / "lesson-03" / "artifacts" / "greenplum-query-tuning-core.pptx"
APPENDIX_PPTX = (
    ROOT / "lessons" / "lesson-03" / "artifacts" / "greenplum-query-tuning-appendix.pptx"
)
CORE_PPTX = FULL_PPTX  # Google Slides / primary deck = core+appendix
GOOGLE_SLIDES_URL = (
    "https://docs.google.com/presentation/d/"
    "1pBIOaqt9WkubsHqCN_p5kxtAhCLjPs6rxFGH9s-_o3c/edit?usp=sharing"
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
    assert "labs/greenplum-625/examples/lesson03-homework-seed.sql" in route.sql_examples
    assert "labs/greenplum-625/examples/lesson03-class-demo.sql" in route.sql_examples
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
        LESSON_PACK / "README.md",
        LESSON_ROOT / "README.md",
        LESSON_ROOT / "mentor-guide.md",
        LESSON_ROOT / "student-workbook.md",
        LESSON_ROOT / "cheat-sheet.md",
        LESSON_ROOT / "runbooks" / "simple-path.md",
        LESSON_ROOT / "runbooks" / "deep-dive-path.md",
        LESSON_ROOT / "runbooks" / "student-prep.md",
        HOMEWORK_ROOT / "assignment.md",
        HOMEWORK_ROOT / "plan.md",
        HOMEWORK_ROOT / "rubric.md",
        HOMEWORK_ROOT / "templates" / "evidence.md",
        HOMEWORK_ROOT / "templates" / "reconcile.sql",
        LESSON_ROOT / "deep-dives" / "pg-statistic-internals.md",
        LESSON_ROOT / "deep-dives" / "storage-physical-layout.md",
        LESSON_ROOT / "deep-dives" / "temp-tables-and-spill.md",
        LESSON_ROOT / "deep-dives" / "optimizer-legacy-vs-orca.md",
        LESSON_ROOT / "deep-dives" / "principal-scd2-locus-redistribute.md",
        LESSON_ROOT / "deep-dives" / "secret18-not-in-broadcast.md",
        LESSON_ROOT / "deep-dives" / "secret14-window-partition-skew.md",
        LESSON_ROOT / "deep-dives" / "secret29-values-params-broadcast.md",
        LESSON_ROOT / "deep-dives" / "secret42-distinct-by-segment.md",
        LESSON_ROOT / "deep-dives" / "secret41-autostats-partitions.md",
        LESSON_ROOT / "deep-dives" / "secret38-median-gather-qd.md",
    ]

    missing = [path.relative_to(ROOT).as_posix() for path in expected_docs if not path.exists()]
    assert missing == []

    joined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in expected_docs if path.suffix == ".md"
    )
    for marker in [
        "EXPLAIN",
        "pg_statistic",
        "TEMP",
        "AOCO",
        "GPORCA",
        "greenplum-625",
        "mentor",
        "lesson03-homework-seed.sql",
        "homework",
        "Principal",
        "EXCEPT ALL",
        "Hard gates",
    ]:
        assert marker in joined_docs

    homework = (HOMEWORK_ROOT / "assignment.md").read_text(encoding="utf-8")
    assert "≥2 TEMP" not in homework
    assert "0 до 3" in homework or "0–3" in homework
    assert "lesson03-class-demo.sql" in homework
    rubric = (HOMEWORK_ROOT / "rubric.md").read_text(encoding="utf-8")
    assert "Environment" in rubric
    assert "не** scored" in rubric or "не scored" in rubric.lower()

    seed = HOMEWORK_SEED.read_text(encoding="utf-8")
    for marker in [
        "Database: mentor",
        "CREATE SCHEMA IF NOT EXISTS lesson03",
        "CREATE TABLE lesson03.fact_sales",
        "appendonly = true",
        "orientation = column",
        "v_heavy_olap_monolith",
        "v_star_join_orca_case",
    ]:
        assert marker in seed
    assert "CREATE TEMP TABLE" not in seed

    demo = CLASS_DEMO.read_text(encoding="utf-8")
    for marker in [
        "lesson03-homework-seed.sql",
        "DROP TABLE IF EXISTS tmp_lesson03_sales_feb",
        "CREATE TEMP TABLE tmp_lesson03_sales_feb",
        "ANALYZE tmp_lesson03_sales_feb",
        "optimizer",
    ]:
        assert marker in demo

    shim = SQL_EXAMPLE.read_text(encoding="utf-8")
    assert "lesson03-class-demo.sql" in shim
    assert REFERENCE_REWRITE.exists()
    assert "CREATE TEMP TABLE" in REFERENCE_REWRITE.read_text(encoding="utf-8")

    evidence_tmpl = HOMEWORK_ROOT / "templates" / "evidence.md"
    reconcile_tmpl = HOMEWORK_ROOT / "templates" / "reconcile.sql"
    assert evidence_tmpl.exists()
    assert reconcile_tmpl.exists()
    assert reconcile_tmpl.read_text(encoding="utf-8").lower().count("except all") >= 2

    optimizer_sql = OPTIMIZER_SQL.read_text(encoding="utf-8")
    assert "SET optimizer = on" in optimizer_sql
    assert "SET optimizer = off" in optimizer_sql

    cardinality_sql = CARDINALITY_SQL.read_text(encoding="utf-8")
    for marker in [
        "histogram_bounds",
        "most_common_freqs",
        "SET optimizer = on",
        "SET optimizer = off",
        "SET STATISTICS",
        "date_trunc",
        "NOT IN",
    ]:
        assert marker in cardinality_sql

    temp_sql = TEMP_LIFECYCLE_SQL.read_text(encoding="utf-8")
    for marker in [
        "ON COMMIT PRESERVE ROWS",
        "ON COMMIT DELETE ROWS",
        "ON COMMIT DROP",
        "pg_my_temp_schema",
        "relpersistence",
    ]:
        assert marker in temp_sql

    stats_sql = STATS_ANALYZE_SQL.read_text(encoding="utf-8")
    for marker in [
        "gp_autostats_mode",
        "last_analyze",
        "last_autoanalyze",
        "n_mod_since_analyze",
        "gp_stats_missing",
    ]:
        assert marker in stats_sql

    stats_deep = (LESSON_ROOT / "deep-dives" / "pg-statistic-internals.md").read_text(
        encoding="utf-8"
    )
    for marker in [
        "DEFAULT_EQ_SEL",
        "CalcScaleFactorCumulativeConj",
        "GetCumulativeNDVs",
        "density_bucket",
        "clauselist_selectivity",
        "gp_autostats_mode",
        "last_analyze",
        "last_autoanalyze",
    ]:
        assert marker in stats_deep

    temp_deep = (LESSON_ROOT / "deep-dives" / "temp-tables-and-spill.md").read_text(
        encoding="utf-8"
    )
    for marker in [
        "ON COMMIT",
        "PRESERVE ROWS",
        "DELETE ROWS",
        "pg_my_temp_schema",
        "сессия",
    ]:
        assert marker in temp_deep

    orca_deep = (
        LESSON_ROOT / "deep-dives" / "optimizer-legacy-vs-orca.md"
    ).read_text(encoding="utf-8")
    for marker in ["Florian Waas", "SIGMOD", "2010", "Greenplum 5"]:
        assert marker in orca_deep

    storage_deep = (
        LESSON_ROOT / "deep-dives" / "storage-physical-layout.md"
    ).read_text(encoding="utf-8")
    for marker in [
        "pg_appendonly",
        "PageHeaderData",
        "appendoptimized",
        "orientation=column",
        "visimaprelid",
    ]:
        assert marker in storage_deep

    e2e_sql = E2E_CASE_SQL.read_text(encoding="utf-8")
    for marker in [
        "EXPLAIN ANALYZE",
        "EXCEPT ALL",
        "CREATE TEMP TABLE",
        "ANALYZE",
        "Equivalence",
    ]:
        assert marker in e2e_sql

    storage_sql = STORAGE_SQL.read_text(encoding="utf-8")
    for marker in ["appendonly", "orientation", "pg_appendonly", "Heap"]:
        assert marker in storage_sql

    assert (ROOT / "lessons/lesson-03/artifacts/case/metrics.md").exists()

    assert "lesson03-orca-ce-trap.sql" in NLJ_CASE_SQL.read_text(encoding="utf-8")

    orca_sql = ORCA_CE_SQL.read_text(encoding="utf-8")
    for marker in [
        "cte_orders",
        "cte_enriched",
        "Nested Loop",
        "Hash Join",
        "tmp_orca_enriched",
        "SET optimizer = on",
        "DISTRIBUTED REPLICATED",
    ]:
        assert marker in orca_sql

    legacy_sql = LEGACY_CE_SQL.read_text(encoding="utf-8")
    for marker in [
        "SET optimizer = off",
        "enable_nestloop",
        "EXISTS",
        "Nested Loop Semi",
        "tmp_leg_enriched",
        "Hash Join",
    ]:
        assert marker in legacy_sql
    assert (ROOT / "lessons/lesson-03/artifacts/case/ce-traps-metrics.md").exists()

    principal_sql = PRINCIPAL_SQL.read_text(encoding="utf-8")
    for marker in [
        "DISTRIBUTED BY (biz_key, version_id)",
        "DISTRIBUTED BY (biz_key)",
        "max(version_id)",
        "Redistribute",
        "t_join_int8",
        "::bigint",
    ]:
        assert marker in principal_sql
    principal_deep = (
        LESSON_ROOT / "deep-dives" / "principal-scd2-locus-redistribute.md"
    ).read_text(encoding="utf-8")
    for marker in ["hash(biz_key", "locus", "int8", "Hash Key"]:
        assert marker in principal_deep
    assert (ROOT / "lessons/lesson-03/artifacts/case/principal-scd2-locus-metrics.md").exists()

    secret18 = SECRET18_SQL.read_text(encoding="utf-8")
    for marker in ["NOT IN", "NOT EXISTS", "Broadcast", "Hash Anti", "LEFT JOIN"]:
        assert marker in secret18
    secret14 = SECRET14_SQL.read_text(encoding="utf-8")
    for marker in ["PARTITION BY", "invalid_id", "WindowAgg", "Redistribute", "row_number"]:
        assert marker in secret14
    secret29 = SECRET29_SQL.read_text(encoding="utf-8")
    for marker in ["VALUES", "data_batch", "DISTRIBUTED RANDOMLY", "Broadcast", "ANY"]:
        assert marker in secret29
    for name in (
        "secret18-not-in-broadcast.md",
        "secret14-window-partition-skew.md",
        "secret29-values-params-broadcast.md",
    ):
        body = (LESSON_ROOT / "deep-dives" / name).read_text(encoding="utf-8")
        assert "cloudberry" in body or "gpdb-archive" in body
        assert "Как исправлять" in body
    assert (ROOT / "lessons/lesson-03/artifacts/case/secret18-not-in-broadcast-metrics.md").exists()
    assert (ROOT / "lessons/lesson-03/artifacts/case/secret14-window-partition-skew-metrics.md").exists()
    assert (ROOT / "lessons/lesson-03/artifacts/case/secret29-values-params-broadcast-metrics.md").exists()

    secret42 = SECRET42_SQL.read_text(encoding="utf-8")
    for marker in ["count(DISTINCT", "gp_segment_id", "DISTRIBUTED BY (id)", "mapped"]:
        assert marker in secret42
    secret41 = SECRET41_SQL.read_text(encoding="utf-8")
    for marker in ["gp_autostats_mode", "on_no_stats", "PARTITION BY RANGE", "pg_statistic"]:
        assert marker in secret41
    secret38 = SECRET38_SQL.read_text(encoding="utf-8")
    for marker in ["percentile_disc", "WITHIN GROUP", "Gather", "gp_segment_id"]:
        assert marker in secret38
    for name in (
        "secret42-distinct-by-segment.md",
        "secret41-autostats-partitions.md",
        "secret38-median-gather-qd.md",
    ):
        body = (LESSON_ROOT / "deep-dives" / name).read_text(encoding="utf-8")
        assert "gpdb-archive" in body
        assert "Как исправлять" in body
    assert (ROOT / "lessons/lesson-03/artifacts/case/secret42-distinct-by-segment-metrics.md").exists()
    assert (ROOT / "lessons/lesson-03/artifacts/case/secret41-autostats-partitions-metrics.md").exists()
    assert (ROOT / "lessons/lesson-03/artifacts/case/secret38-median-gather-qd-metrics.md").exists()


def test_lesson_03_runbook_cli_routes_are_available():
    for route in ["simple", "deep", "homework"]:
        exit_code, output = invoke(["runbook", "greenplum-query-tuning", route])

        assert exit_code == 0, output
        assert "тюнинг" in output or "Урок 03" in output
        assert "lesson03-homework-seed.sql" in output or "lesson03-class-demo.sql" in output
        assert "greenplum-625" in output


def test_lesson_03_homework_mechanical_checker_accepts_valid_pack(tmp_path):
    pack = tmp_path / "lesson03-query-tuning"
    pack.mkdir()
    (pack / "rewrite.sql").write_text(
        """
SET optimizer = on;
DROP TABLE IF EXISTS tmp_l03_a;
CREATE TEMP TABLE tmp_l03_a AS
SELECT customer_id, amount FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01'
DISTRIBUTED BY (customer_id);
ANALYZE tmp_l03_a;
SELECT region, sum(amount) FROM tmp_l03_a t
JOIN lesson03.dim_customer c USING (customer_id)
GROUP BY 1;
""",
        encoding="utf-8",
    )
    (pack / "reconcile.sql").write_text(
        (HOMEWORK_ROOT / "templates" / "reconcile.sql").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (pack / "evidence.md").write_text(
        (HOMEWORK_ROOT / "templates" / "evidence.md").read_text(encoding="utf-8")
        .replace("Grain:", "Grain: region×category")
        .replace("Optimizer for rewrite proof (`SET optimizer = …`):",
                 "Optimizer for rewrite proof (`SET optimizer = …`): on; DB mentor")
        .replace("Production decision: **merge / do not merge / needs larger-scale validation** — why:",
                 "Production decision: **do not merge** — total pipeline slower; TEMP boundary explored")
        .replace("## I. Residual risks\n\n(Beyond the verified snapshot — does **not** replace H.)\n\n1.\n2.",
                 "## I. Residual risks\n\n(Beyond the verified snapshot — does **not** replace H.)\n\n1. NDV drift after load\n2. ORCA fallback on larger scale\n"),
        encoding="utf-8",
    )

    exit_code, output = invoke(
        [
            "homework",
            "greenplum-625",
            "check",
            "--submission",
            str(pack),
        ]
    )
    assert exit_code == 0, output
    assert "Accepted: yes" in output
    assert "mechanical" in output.lower()


def test_lesson_03_homework_mechanical_checker_rejects_class_demo_copy(tmp_path):
    pack = tmp_path / "bad"
    pack.mkdir()
    (pack / "rewrite.sql").write_text(
        """
SET optimizer = on;
DROP TABLE IF EXISTS tmp_lesson03_sales_shaped;
DROP TABLE IF EXISTS tmp_lesson03_sales_feb;
CREATE TEMP TABLE tmp_lesson03_sales_feb AS
SELECT 1 AS customer_id DISTRIBUTED BY (customer_id);
ANALYZE tmp_lesson03_sales_feb;
CREATE TEMP TABLE tmp_lesson03_sales_shaped AS
SELECT 1 AS region DISTRIBUTED BY (region);
ANALYZE tmp_lesson03_sales_shaped;
""",
        encoding="utf-8",
    )
    (pack / "reconcile.sql").write_text(
        "SELECT * FROM a EXCEPT ALL SELECT * FROM b;\n"
        "SELECT * FROM b EXCEPT ALL SELECT * FROM a;\n",
        encoding="utf-8",
    )
    (pack / "evidence.md").write_text(
        (HOMEWORK_ROOT / "templates" / "evidence.md").read_text(encoding="utf-8")
        .replace("Grain:", "Grain: x; mentor")
        .replace(
            "Production decision: **merge / do not merge / needs larger-scale validation** — why:",
            "Production decision: **merge** — total pipeline time improved",
        )
        .replace(
            "## I. Residual risks\n\n(Beyond the verified snapshot — does **not** replace H.)\n\n1.\n2.",
            "## I. Residual risks\n\n1. freshness\n2. skew\n",
        ),
        encoding="utf-8",
    )
    exit_code, output = invoke(
        ["homework", "greenplum-625", "check", "--submission", str(pack)]
    )
    assert exit_code == 1, output
    assert "no_class_demo_copy" in output


def _pptx_slide_count(path: Path) -> int:
    with ZipFile(path) as pptx:
        return sum(
            1
            for name in pptx.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        )


def test_lesson_03_panel_and_code_bodies_fit_google_line_budget():
    """Guard against text/SQL overflowing panels after Google Slides inflation."""
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from build_lesson03_pptx import (
        GOOGLE_LINE_FACTOR,
        PANEL_WRAP_COLS,
        CODE_WRAP_COLS,
        _content_bottom_for,
        _effective_code_lines,
        _fit_font_size,
        inch,
    )
    from lesson03_core_slide_specs import CORE_SLIDES

    overflows = []
    for spec in CORE_SLIDES:
        bottom = _content_bottom_for(spec)
        top = inch(2.02)
        panel_h = bottom - top
        kind = spec.get("type")
        if kind == "panel":
            body = spec.get("body") or ""
            lines = _effective_code_lines(body, cols=PANEL_WRAP_COLS)
            box_h = (panel_h / 914400) - 0.32
            size = _fit_font_size(
                lines, box_h, candidates=(14, 13, 12, 11, 10, 9, 8)
            )
            if lines * size * GOOGLE_LINE_FACTOR > box_h * 72:
                overflows.append(("panel", spec.get("title"), lines, size))
        elif kind == "code":
            code = spec.get("code") or ""
            lines = _effective_code_lines(code, cols=CODE_WRAP_COLS)
            text_h = (panel_h / 914400) - 0.48
            from build_lesson03_pptx import CODE_LINE_FACTOR

            size = _fit_font_size(
                lines,
                text_h,
                candidates=(12, 11, 10, 9, 8, 7),
                line_factor=CODE_LINE_FACTOR,
            )
            if lines * size * CODE_LINE_FACTOR > text_h * 72:
                overflows.append(("code", spec.get("title"), lines, size))
    assert not overflows, f"content overflows under Google budget: {overflows[:8]}"


def test_lesson_03_runbook_slide_references_fit_the_standalone_deck():
    assert FULL_PPTX.exists()
    assert FULL_PPTX.stat().st_size > 50_000
    assert _pptx_slide_count(FULL_PPTX) == 439  # core + divider + appendix + portals

    assert CORE_ONLY_PPTX.exists()
    assert _pptx_slide_count(CORE_ONLY_PPTX) == 213

    assert APPENDIX_PPTX.exists()
    assert APPENDIX_PPTX.stat().st_size > 50_000
    assert _pptx_slide_count(APPENDIX_PPTX) >= 115

    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from lesson03_core_slide_specs import CORE_SLIDES as _core_specs
    assert _core_specs[1].get("anchor") == "nav-guide"
    assert "презентац" in (_core_specs[1].get("title") or "").lower()
    assert _core_specs[2]["type"] == "toc"
    assert "Словарь" in _core_specs[4]["kicker"]
    assert not any("колод" in ((s.get("title") or "") + (s.get("subtitle") or "") + (s.get("body") or "")).lower() for s in _core_specs)
    assert any("Selectivity" in s.get("title", "") for s in _core_specs)
    assert any("n_distinct" in s.get("title", "") for s in _core_specs)
    assert any("частых значений" in s.get("title", "") for s in _core_specs)
    assert any("pg_stats" in s.get("title", "") and "MCV" in s.get("title", "") for s in _core_specs)
    assert any("смысл" in s.get("kicker", "") for s in _core_specs)
    assert any("формулы" in s.get("kicker", "") for s in _core_specs)
    assert any("equi-depth" in s.get("title", "").lower() for s in _core_specs)
    assert not any("чайника" in (s.get("kicker") or "") for s in _core_specs)
    assert not any("хит-парад" in ((s.get("title") or "") + (s.get("body") or "") + (s.get("subtitle") or "")) for s in _core_specs)
    assert any("1 · 25 · 50" in (s.get("body") or "") for s in _core_specs)
    assert any("0.75" in (s.get("body") or "") for s in _core_specs)
    assert any(s.get("type") == "panel" for s in _core_specs)
    assert any(s.get("jumps") for s in _core_specs)
    from build_lesson03_pptx import attach_nav_portals
    expanded, portals = attach_nav_portals(list(_core_specs))
    assert portals, "glossary return portals required"
    assert all(expanded[p].get("_return_to") == origin for origin, p in portals.items())

    assert any(
        any(j.get("anchor") == "appendix-orca-and" for j in (s.get("jumps") or []))
        for s in _core_specs
    )

    assert any(s.get("anchor") == "stage-problem" for s in _core_specs)
    assert any(s.get("anchor") == "cases" for s in _core_specs)
    assert any(s.get("title", "").startswith("ORCA недооценил") for s in _core_specs)
    assert not any("эрудит" in s.get("title", "").lower() for s in _core_specs)

    catalog = RunbookCatalog.default()
    simple = catalog.get("greenplum-query-tuning", "simple")
    assert simple.stages[0].slides
    assert "Incident" in simple.stages[0].title or "incident" in simple.description.lower()


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
    assert "Incident" in source
    assert "appendoptimized" in source
    assert "Grand Unified Configuration" in source  # appendix glossary
    assert "Star-join" in source or "star-join" in source
    assert "equi-depth" in source or "histogram_bounds" in source
    assert (ROOT / "lessons/lesson-03/artifacts/plan-screens/stats-histogram-structure.png").exists()
    assert "greenplum-625" in source
    assert "pg_statistic" in source
    assert (ROOT / "lessons/lesson-03/artifacts/plan-screens/explain-orca.png").exists()
    assert (ROOT / "lessons/lesson-03/artifacts/plan-screens/explain-legacy.png").exists()
    assert (ROOT / "lessons/lesson-03/artifacts/plan-screens/temp-relfilenode-fs.png").exists()
    assert (ROOT / "lessons/lesson-03/artifacts/plan-screens/spill-pgsql_tmp-growth.png").exists()
    assert "pgsql_tmp_Sort" in source or "external merge" in source
    assert "metrics" in source.lower()


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
    assert control_plane["mentor_mode"]["slide_deck"] == "lessons/lesson-03/artifacts/greenplum-query-tuning-theory.pptx"
    assert control_plane["mentor_mode"]["google_slides"] == GOOGLE_SLIDES_URL
    sql_paths = {
        item["path"] for item in control_plane["artifacts"] if item["kind"] == "sql"
    }
    assert "labs/greenplum-625/examples/lesson03-homework-seed.sql" in sql_paths
    assert "labs/greenplum-625/examples/lesson03-class-demo.sql" in sql_paths

    assert control_plane["next_lesson"]["code"] == "04-greenplum-wlm-diagnostics"
    assert control_plane["mentor_mode"]["stage_guides"][0]["stage_code"] == "lab-optimizer"


def test_lesson_03_cli_lesson_view_is_printable():
    exit_code, output = invoke(["lesson", "lesson-03"])
    assert exit_code == 0, output
    assert "Декомпозиция" in output or "тюнинг" in output
    assert "GPORCA" in output or "Legacy" in output or "6.25" in output
