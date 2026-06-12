from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_professional_lesson_artifacts_exist():
    expected = [
        "docs/lessons/01-greenplum/case-study.md",
        "docs/lessons/01-greenplum/architecture.md",
        "docs/lessons/01-greenplum/rubric.md",
        "docs/lessons/01-greenplum/capstone.md",
        "docs/lessons/01-greenplum/incidents/skewed-distribution.md",
        "docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md",
        "docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md",
        "docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md",
        "docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md",
        "docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md",
        "docs/lessons/01-greenplum/query-tuning-lab.md",
        "docs/lessons/01-greenplum/academy-loop.md",
        "docs/lessons/01-greenplum/runbooks/simple-path.md",
        "docs/lessons/01-greenplum/runbooks/deep-dive-path.md",
        "docs/lessons/01-greenplum/runbooks/homework-plan.md",
        "docs/lessons/01-greenplum/runbooks/student-prep.md",
        "labs/greenplum/examples/storage-and-partitioning.sql",
        "decks/greenplum-theory/README.md",
        "decks/greenplum-theory/facilitator-guide.md",
    ]

    missing = [path for path in expected if not (ROOT / path).exists()]

    assert missing == []


def test_user_facing_docs_have_no_placeholders():
    docs = list((ROOT / "docs/lessons/01-greenplum").rglob("*.md"))

    offenders = []
    for path in docs:
        content = path.read_text(encoding="utf-8")
        if "TODO" in content or "TBD" in content:
            offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == []


def test_presentation_facilitator_guide_has_timing_and_system_taxonomy():
    guide = (ROOT / "decks/greenplum-theory/facilitator-guide.md").read_text(
        encoding="utf-8"
    )

    assert "00:00-02:00" in guide
    assert "57:00-60:00" in guide
    assert "simple path" in guide.lower()
    assert "deep-dive path" in guide.lower()
    assert "SMP" in guide
    assert "MPP" in guide
    assert "EPP" in guide
    assert "QD/QE deep dive" in guide
    assert "Heap, AO row, AOCO column" in guide
    assert "Greenplum vs sharded PostgreSQL" in guide
    assert "partitioning intro" in guide
    assert "Что сказать емко" in guide


def test_runbooks_have_commands_questions_checks_and_cross_links():
    runbook_paths = [
        ROOT / "docs/lessons/01-greenplum/runbooks/simple-path.md",
        ROOT / "docs/lessons/01-greenplum/runbooks/deep-dive-path.md",
        ROOT / "docs/lessons/01-greenplum/runbooks/homework-plan.md",
    ]

    for path in runbook_paths:
        content = path.read_text(encoding="utf-8")
        assert "## Stage" in content
        assert "Команды" in content
        assert "Что спрашиваем" in content
        assert "Expected answer" in content
        assert "Как проверяем" in content
        assert "student-workbook.md" in content
        assert "homework.md" in content
        assert "storage-and-partitioning.sql" in content


def test_workbook_homework_and_mentor_guide_are_cross_linked():
    workbook = (ROOT / "docs/lessons/01-greenplum/student-workbook.md").read_text(
        encoding="utf-8"
    )
    homework = (ROOT / "docs/lessons/01-greenplum/homework.md").read_text(
        encoding="utf-8"
    )
    mentor = (ROOT / "docs/lessons/01-greenplum/mentor-guide.md").read_text(
        encoding="utf-8"
    )

    assert "homework.md" in workbook
    assert "runbooks/homework-plan.md" in workbook
    assert "storage-and-partitioning.sql" in workbook
    assert "Greenplum vs sharded PostgreSQL" in workbook
    assert "QD" in workbook and "QE" in workbook and "gang" in workbook and "slice" in workbook
    assert "appendoptimized=true" in workbook
    assert "orientation=column" in workbook
    assert "PARTITION BY RANGE" in workbook
    assert "Lesson 02: Partitioning, statistics and incremental loads in MPP" in homework
    assert "runbooks/simple-path.md" in mentor
    assert "runbooks/deep-dive-path.md" in mentor


def test_student_prep_runbook_has_cross_platform_environment_contract():
    prep = (ROOT / "docs/lessons/01-greenplum/runbooks/student-prep.md").read_text(
        encoding="utf-8"
    )
    workbook = (ROOT / "docs/lessons/01-greenplum/student-workbook.md").read_text(
        encoding="utf-8"
    )

    assert "macOS" in prep
    assert "Windows" in prep
    assert "Linux" in prep
    assert "Docker Desktop" in prep
    assert "WSL 2" in prep
    assert "Docker Engine" in prep
    assert "python3 mentor-lab.py doctor" in prep
    assert "py mentor-lab.py doctor" in prep
    assert "docker compose version" in prep
    assert "15432" in prep
    assert "student-prep.md" in workbook


def test_storage_and_partitioning_sql_contains_runnable_demo_contracts():
    sql = (ROOT / "labs/greenplum/examples/storage-and-partitioning.sql").read_text(
        encoding="utf-8"
    )

    assert "storage_heap_demo" in sql
    assert "storage_ao_row_demo" in sql
    assert "storage_aoco_demo" in sql
    assert "appendoptimized=true" in sql
    assert "orientation=row" in sql
    assert "orientation=column" in sql
    assert "PARTITION BY RANGE (sale_date)" in sql
    assert "gp_default_storage_options" in sql


def test_master_segment_deep_dive_has_diagrams_and_source_anchors():
    guide = (ROOT / "docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md").read_text(
        encoding="utf-8"
    )

    assert "```mermaid" in guide
    assert "Query Dispatcher" in guide
    assert "Query Executor" in guide
    assert "TupleChunks" in guide
    assert "gpfdist" in guide
    assert "X-GP-PROTO" in guide
    assert "AOCO" in guide
    assert "cdbdisp_query.c" in guide
    assert "nodeMotion.c" in guide


def test_qd_qe_gang_slices_deep_dive_is_canonical_and_teachable():
    deep_dive = (
        ROOT
        / "docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md"
    ).read_text(encoding="utf-8")
    workbook = (ROOT / "docs/lessons/01-greenplum/student-workbook.md").read_text(
        encoding="utf-8"
    )
    runbook = (
        ROOT / "docs/lessons/01-greenplum/runbooks/deep-dive-path.md"
    ).read_text(encoding="utf-8")
    lesson_readme = (ROOT / "docs/lessons/01-greenplum/README.md").read_text(
        encoding="utf-8"
    )

    expected_terms = [
        "QD  = Query Dispatcher на master",
        "QE  = Query Executor на segment",
        "Slice = кусок distributed execution plan",
        "Gang = группа QE-процессов",
        "Motion = граница между slice",
        "QD — это backend-процесс на master/coordinator",
        "QE — это worker/backend-процесс на segment instance",
        "slice — это не процесс",
        "Gang — это уже физическое исполнение slice",
        "Redistribute Motion 48:48",
        "Gather Motion 48:1",
        "gp_max_slices",
        "co-located plan",
        "distribution keys",
        "join keys",
        "статистику",
        "skew",
    ]
    expected_sections = [
        "## 1. QD",
        "## 2. QE",
        "## 3. Slice",
        "## 4. Gang",
        "## Как они работают вместе",
        "## Как это видно в EXPLAIN",
        "## Почему это важно для производительности",
        "## Самая полезная ментальная модель",
    ]

    for marker in [*expected_terms, *expected_sections]:
        assert marker in deep_dive

    assert "```mermaid" in deep_dive
    assert "https://docs-cn.greenplum.org/v6/admin_guide/query/topics/parallel-proc.html" in deep_dive
    assert "https://knowledge.broadcom.com/external/article/430557/understanding-and-managing-gpmaxslices.html" in deep_dive
    assert "qd-qe-gang-slices-explained.md" in workbook
    assert "qd-qe-gang-slices-explained.md" in runbook
    assert "qd-qe-gang-slices-explained.md" in lesson_readme


def test_advanced_deep_dives_cover_plan_reading_joins_and_mpp_taxonomy():
    plan = (ROOT / "docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md").read_text(
        encoding="utf-8"
    )
    joins = (ROOT / "docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md").read_text(
        encoding="utf-8"
    )
    taxonomy = (ROOT / "docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md").read_text(
        encoding="utf-8"
    )

    assert "plan-reading ladder" in plan
    assert "slice" in plan
    assert "Motion" in plan
    assert "Rows out" in plan
    assert "Hash Join" in joins
    assert "Broadcast Motion" in joins
    assert "Redistribute Motion" in joins
    assert "co-located join" in joins
    assert "nodeHashjoin.c" in joins
    assert "joinpath.c" in joins
    assert "CdbPathLocus" in joins
    assert "SMP" in taxonomy
    assert "MPP" in taxonomy
    assert "EPP" in taxonomy
    assert "lakehouse" in taxonomy
    assert "trade-off matrix" in taxonomy
