import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_BLOB_BASE = "https://github.com/PaulKov/de-mentor/blob/master/"
GPDB_BLOB_BASE = (
    "https://github.com/PaulKov/gpdb/blob/"
    "482967c1b49028cf072c15935462f75bc3e4b045/"
)


def _without_fenced_code(content: str) -> str:
    return re.sub(r"```.*?```", "", content, flags=re.DOTALL)


PUBLIC_DOC_ROOTS = [
    ROOT / "README.md",
    ROOT / "decks/greenplum-theory",
    ROOT / "docs/lessons/01-greenplum",
    ROOT / "labs/greenplum",
]


def _public_markdown_docs() -> list[Path]:
    docs = []
    for root in PUBLIC_DOC_ROOTS:
        if root.is_file():
            docs.append(root)
        elif root.exists():
            docs.extend(root.rglob("*.md"))
    return sorted(set(docs))


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
        "docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md",
        "docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md",
        "docs/lessons/01-greenplum/query-tuning-lab.md",
        "docs/lessons/01-greenplum/academy-loop.md",
        "docs/lessons/01-greenplum/runbooks/simple-path.md",
        "docs/lessons/01-greenplum/runbooks/deep-dive-path.md",
        "docs/lessons/01-greenplum/runbooks/homework-plan.md",
        "docs/lessons/01-greenplum/runbooks/student-prep.md",
        "labs/greenplum/examples/cluster-inspection.sql",
        "labs/greenplum/examples/cluster-monitoring.sql",
        "labs/greenplum/examples/partitioning-strategies.sql",
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


def test_dev_draft_docs_are_not_tracked_as_public_materials():
    dev_docs = list((ROOT / "docs/superpowers").rglob("*.md"))
    assert dev_docs == []


def test_public_markdown_uses_russian_service_labels():
    blacklist = [
        "Expected answer",
        "Cross-links",
        "Source anchors",
        "Presenter Notes",
        "Acceptance Criteria",
        "Data Profiles",
        "Strong Answer Signals",
        "Deliverables",
        "Expected Submission",
        "What It Automates",
        "What Makes It Professional",
        "Student Route",
        "Mentor Route",
        "Evidence Contract",
        "Requirements",
        "Quick start",
        "Simple Path",
        "Deep-Dive Path",
    ]

    offenders = []
    for path in _public_markdown_docs():
        prose = _without_fenced_code(path.read_text(encoding="utf-8"))
        for marker in blacklist:
            if marker in prose:
                offenders.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")

    assert offenders == []


def test_core_lesson_docs_have_russian_titles_and_terms():
    expected = {
        "docs/lessons/01-greenplum/architecture.md": [
            "# Карта Архитектуры Greenplum",
            "## Ментальная Модель MPP",
            "## Что Смотреть В EXPLAIN",
        ],
        "docs/lessons/01-greenplum/capstone.md": [
            "# Финальная Задача: Daily Marketplace Revenue Mart",
            "## Сценарий",
            "## Что Сдать",
        ],
        "docs/lessons/01-greenplum/rubric.md": [
            "# Матрица Оценки И Навыков",
            "## Уровни Оценки",
            "## Вопросы Ментора",
        ],
        "docs/lessons/01-greenplum/incidents/skewed-distribution.md": [
            "# Инцидент: Перекошенное Распределение",
            "## Симптомы",
            "## Критерии Приемки",
        ],
    }

    for relative_path, markers in expected.items():
        content = (ROOT / relative_path).read_text(encoding="utf-8")
        for marker in markers:
            assert marker in content


def test_presentation_facilitator_guide_has_timing_and_system_taxonomy():
    guide = (ROOT / "decks/greenplum-theory/facilitator-guide.md").read_text(
        encoding="utf-8"
    )

    assert "00:00-02:00" in guide
    assert "57:00-60:00" in guide
    assert "упрощенный маршрут" in guide.lower()
    assert "расширенный маршрут" in guide.lower()
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
        assert "## Этап" in content
        assert "Команды" in content
        assert "Что спрашиваем" in content
        assert "Ожидаемый ответ" in content
        assert "Как проверяем" in content
        assert "student-workbook.md" in content
        assert "homework.md" in content
        assert "storage-and-partitioning.sql" in content
        assert "partitioning-strategies.sql" in content


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
    assert "partitioning-strategies.sql" in workbook
    assert "deep-dives/partitioning-strategies.md" in workbook
    assert "Greenplum vs sharded PostgreSQL" in workbook
    assert "QD" in workbook and "QE" in workbook and "gang" in workbook and "slice" in workbook
    assert "appendoptimized=true" in workbook
    assert "orientation=column" in workbook
    assert "PARTITION BY RANGE" in workbook
    assert "Lesson 02: Partitioning, statistics and incremental loads in MPP" in homework
    assert "runbooks/simple-path.md" in mentor
    assert "runbooks/deep-dive-path.md" in mentor


def test_workbook_has_end_of_lesson_student_handoff_pack():
    workbook = (ROOT / "docs/lessons/01-greenplum/student-workbook.md").read_text(
        encoding="utf-8"
    )

    assert "## Что Отправить Ученику После Урока" in workbook

    required_links = [
        f"{REPO_BLOB_BASE}docs/lessons/01-greenplum/runbooks/student-prep.md",
        f"{REPO_BLOB_BASE}labs/greenplum/README.md",
        f"{REPO_BLOB_BASE}docs/lessons/01-greenplum/student-workbook.md",
        f"{REPO_BLOB_BASE}docs/lessons/01-greenplum/homework.md",
        f"{REPO_BLOB_BASE}docs/lessons/01-greenplum/runbooks/homework-plan.md",
        f"{REPO_BLOB_BASE}labs/greenplum/examples/cluster-inspection.sql",
        f"{REPO_BLOB_BASE}labs/greenplum/examples/cluster-monitoring.sql",
        f"{REPO_BLOB_BASE}labs/greenplum/examples/storage-and-partitioning.sql",
        f"{REPO_BLOB_BASE}labs/greenplum/examples/partitioning-strategies.sql",
    ]
    required_commands = [
        "python3 mentor-lab.py doctor",
        "python3 mentor-lab.py up greenplum",
        "python3 mentor-lab.py check greenplum",
        "python3 mentor-lab.py psql greenplum",
        "py mentor-lab.py doctor",
        "py mentor-lab.py up greenplum",
        "py mentor-lab.py check greenplum",
        "py mentor-lab.py psql greenplum",
        "python3 mentor-lab.py portal greenplum --version v2",
        "python3 mentor-lab.py evidence greenplum collect redistribute-join",
        "python3 mentor-lab.py misconception greenplum diagnose",
        "python3 mentor-lab.py homework greenplum check",
        "python3 mentor-lab.py debrief greenplum",
        "python3 mentor-lab.py learning-loop greenplum",
    ]

    for marker in [*required_links, *required_commands]:
        assert marker in workbook


def test_learning_loop_is_documented_as_end_of_lesson_artifact():
    docs = [
        ROOT / "README.md",
        ROOT / "docs/lessons/01-greenplum/README.md",
        ROOT / "docs/lessons/01-greenplum/academy-loop.md",
        ROOT / "docs/lessons/01-greenplum/academy-v2.md",
        ROOT / "docs/lessons/01-greenplum/mentor-guide.md",
        ROOT / "docs/lessons/01-greenplum/student-workbook.md",
    ]

    for path in docs:
        content = path.read_text(encoding="utf-8")
        assert "mentor-lab.py learning-loop greenplum" in content
        assert "Learning Loop" in content


def test_mentor_automation_commands_are_documented():
    overview_docs = [
        ROOT / "README.md",
        ROOT / "docs/lessons/01-greenplum/README.md",
        ROOT / "docs/lessons/01-greenplum/academy-loop.md",
        ROOT / "docs/lessons/01-greenplum/academy-v2.md",
        ROOT / "docs/lessons/01-greenplum/mentor-guide.md",
        ROOT / "docs/lessons/01-greenplum/student-workbook.md",
        ROOT / "docs/lessons/01-greenplum/cheat-sheet.md",
    ]
    expected_commands = [
        "mentor-lab.py teach greenplum simple",
        "mentor-lab.py portal greenplum --version v2",
        "mentor-lab.py evidence greenplum collect redistribute-join",
        "mentor-lab.py misconception greenplum diagnose",
        "mentor-lab.py homework greenplum check",
        "mentor-lab.py debrief greenplum",
    ]

    for path in overview_docs:
        content = path.read_text(encoding="utf-8")
        for command in expected_commands:
            assert command in content

    homework = (ROOT / "docs/lessons/01-greenplum/homework.md").read_text(
        encoding="utf-8"
    )
    assert "mentor-lab.py homework greenplum check" in homework


def test_academy_pro_v3_commands_and_lesson02_scaffold_are_documented():
    overview_docs = [
        ROOT / "README.md",
        ROOT / "docs/lessons/01-greenplum/README.md",
        ROOT / "docs/lessons/01-greenplum/academy-loop.md",
        ROOT / "docs/lessons/01-greenplum/academy-v2.md",
        ROOT / "docs/lessons/01-greenplum/mentor-guide.md",
        ROOT / "docs/lessons/01-greenplum/student-workbook.md",
        ROOT / "docs/lessons/01-greenplum/cheat-sheet.md",
    ]
    expected_commands = [
        "mentor-lab.py readiness greenplum --platform macos",
        "mentor-lab.py orchestrate greenplum --route simple --stage 1 --mode recovery",
        "mentor-lab.py observe greenplum start",
        "mentor-lab.py coach-plan greenplum --query bad_customer_join --sample",
        "mentor-lab.py calibration greenplum show senior",
        "mentor-lab.py replay greenplum",
    ]

    for path in overview_docs:
        content = path.read_text(encoding="utf-8")
        for command in expected_commands:
            assert command in content

    lesson02_files = [
        ROOT / "docs/lessons/02-greenplum-partitioning/README.md",
        ROOT / "docs/lessons/02-greenplum-partitioning/runbooks/simple-path.md",
        ROOT / "docs/lessons/02-greenplum-partitioning/student-workbook.md",
    ]
    for path in lesson02_files:
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Lesson 02" in content
        assert "partition" in content.lower()
        assert "statistics" in content.lower()
        assert "incremental loads" in content.lower()


def test_academy_enterprise_v4_autograder_dataset_and_ci_are_documented():
    overview_docs = [
        ROOT / "README.md",
        ROOT / "docs/lessons/01-greenplum/README.md",
        ROOT / "docs/lessons/01-greenplum/academy-loop.md",
        ROOT / "docs/lessons/01-greenplum/academy-v2.md",
        ROOT / "docs/lessons/01-greenplum/mentor-guide.md",
        ROOT / "docs/lessons/01-greenplum/student-workbook.md",
        ROOT / "docs/lessons/01-greenplum/cheat-sheet.md",
    ]
    expected_commands = [
        "mentor-lab.py autograde-sql greenplum --submission",
        "mentor-lab.py dataset greenplum generate",
        "mentor-lab.py ci-smoke greenplum --dry-run",
    ]

    for path in overview_docs:
        content = path.read_text(encoding="utf-8")
        for command in expected_commands:
            assert command in content

    workflow = ROOT / ".github/workflows/greenplum-smoke.yml"
    sample_sql = ROOT / "labs/greenplum/examples/student-solution-example.sql"
    assert workflow.exists()
    assert sample_sql.exists()
    assert "Greenplum Live Smoke" in workflow.read_text(encoding="utf-8")
    sample = sample_sql.read_text(encoding="utf-8")
    assert "DISTRIBUTED BY" in sample
    assert "PARTITION BY RANGE" in sample
    assert "EXPLAIN ANALYZE" in sample
    assert "gp_segment_id" in sample


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


def test_partitioning_strategy_materials_are_complete_and_cross_linked():
    sql = (ROOT / "labs/greenplum/examples/partitioning-strategies.sql").read_text(
        encoding="utf-8"
    )
    deep_dive = (
        ROOT / "docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md"
    ).read_text(encoding="utf-8")
    workbook = (ROOT / "docs/lessons/01-greenplum/student-workbook.md").read_text(
        encoding="utf-8"
    )
    simple = (
        ROOT / "docs/lessons/01-greenplum/runbooks/simple-path.md"
    ).read_text(encoding="utf-8")
    deep = (
        ROOT / "docs/lessons/01-greenplum/runbooks/deep-dive-path.md"
    ).read_text(encoding="utf-8")

    expected_markers = [
        "PARTITION BY RANGE",
        "PARTITION BY LIST",
        "PARTITION BY HASH",
        "DEFAULT",
        "pg_partition_tree",
        "gp_toolkit.gp_partitions",
        "leaf_partitions",
        "partition key не равен distribution key",
        "out-of-range INSERT",
        "ATTACH PARTITION",
        "DETACH PARTITION",
    ]

    for content in [sql, deep_dive, workbook, simple, deep]:
        for marker in expected_markers:
            assert marker in content

    assert "RANGE / LIST / HASH" in deep_dive
    assert "no default partitioning" in deep_dive
    assert "partitioning-strategies.sql" in workbook
    assert "partitioning-strategies.sql" in simple
    assert "partitioning-strategies.sql" in deep


def test_greenplum_lab_cluster_passport_is_documented_and_runnable():
    readme = (ROOT / "labs/greenplum/README.md").read_text(encoding="utf-8")
    sql = (ROOT / "labs/greenplum/examples/cluster-inspection.sql").read_text(
        encoding="utf-8"
    )
    workbook = (ROOT / "docs/lessons/01-greenplum/student-workbook.md").read_text(
        encoding="utf-8"
    )
    runbook = (
        ROOT / "docs/lessons/01-greenplum/runbooks/simple-path.md"
    ).read_text(encoding="utf-8")

    expected_markers = [
        "woblerr/greenplum:7.1.0",
        "1 coordinator/master",
        "2 primary segments",
        "0 mirror segments",
        "1 segment host",
        "15432:5432",
        "CPU/RAM limits",
        "Docker Desktop/Engine",
        "greenplum-data",
        "gp_segment_configuration",
        "gp_toolkit.gp_disk_free",
        "cluster-inspection.sql",
    ]

    for marker in expected_markers:
        assert marker in readme

    for marker in [
        "gp_segment_configuration",
        "pg_settings",
        "gp_toolkit.gp_disk_free",
        "pg_database_size",
        "gp_vmem_protect_limit",
        "statement_mem",
        "work_mem",
        "shared_buffers",
    ]:
        assert marker in sql

    assert "cluster-inspection.sql" in workbook
    assert "cluster-inspection.sql" in runbook


def test_greenplum_cluster_monitoring_sql_is_documented_and_teachable():
    sql = (ROOT / "labs/greenplum/examples/cluster-monitoring.sql").read_text(
        encoding="utf-8"
    )
    lab_readme = (ROOT / "labs/greenplum/README.md").read_text(encoding="utf-8")
    workbook = (ROOT / "docs/lessons/01-greenplum/student-workbook.md").read_text(
        encoding="utf-8"
    )
    runbook = (
        ROOT / "docs/lessons/01-greenplum/runbooks/simple-path.md"
    ).read_text(encoding="utf-8")

    expected_sql_markers = [
        "gp_segment_configuration",
        "gp_toolkit.gp_disk_free",
        "gp_toolkit.gp_resgroup_status_per_segment",
        "gp_toolkit.gp_skew_coefficients",
        "gp_toolkit.gp_skew_idle_fractions",
        "gp_segment_id",
        "gp_dist_random",
        "gp_execution_segment",
        "gpstate -s",
        "role <> preferred_role",
        "status <> 'u'",
        "mode <> 's'",
        "STRING_AGG(content::text, ',' ORDER BY content)",
        "max_to_avg_ratio",
        "max_to_min_ratio",
    ]

    for marker in expected_sql_markers:
        assert marker in sql

    for content in [lab_readme, workbook, runbook]:
        assert "cluster-monitoring.sql" in content
        assert "gp_segment_configuration" in content
        assert "gp_segment_id" in content
        assert "gpstate -s" in content


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


def test_greenplum_source_anchors_use_remote_fork_links():
    docs = [
        ROOT / "docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md",
        ROOT / "docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)

    expected_sources = [
        "src/backend/cdb/dispatcher/cdbdisp_query.c",
        "src/backend/cdb/cdbsrlz.c",
        "src/include/executor/execdesc.h",
        "src/backend/executor/execMain.c",
        "src/backend/executor/nodeMotion.c",
        "src/backend/cdb/motion/tupser.c",
        "src/include/cdb/ml_ipc.h",
        "src/backend/cdb/motion/ic_udpifc.c",
        "src/include/commands/copy.h",
        "src/bin/gpfdist/gpfdist.c",
        "src/backend/access/external/url_curl.c",
        "src/backend/cdb/cdbpath.c",
        "src/backend/optimizer/path/joinpath.c",
        "src/backend/optimizer/util/pathnode.c",
        "src/backend/cdb/cdbpathtoplan.c",
        "src/backend/executor/nodeHashjoin.c",
        "src/backend/executor/nodeNestloop.c",
        "src/backend/executor/nodeMergejoin.c",
    ]

    assert "/tmp/gpdb-source" not in combined
    for source_path in expected_sources:
        assert f"{GPDB_BLOB_BASE}{source_path}" in combined


def test_lesson_cross_links_are_clickable_repo_links():
    docs = [
        ROOT / "decks/greenplum-theory/README.md",
        ROOT / "decks/greenplum-theory/facilitator-guide.md",
        ROOT / "docs/lessons/01-greenplum/README.md",
        ROOT / "docs/lessons/01-greenplum/mentor-guide.md",
        ROOT / "docs/lessons/01-greenplum/student-workbook.md",
        ROOT / "docs/lessons/01-greenplum/homework.md",
        ROOT / "docs/lessons/01-greenplum/runbooks/simple-path.md",
        ROOT / "docs/lessons/01-greenplum/runbooks/deep-dive-path.md",
        ROOT / "docs/lessons/01-greenplum/runbooks/homework-plan.md",
        ROOT / "docs/lessons/01-greenplum/runbooks/student-prep.md",
        ROOT / "docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md",
        ROOT / "docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md",
        ROOT / "labs/greenplum/README.md",
    ]
    path_like_span = re.compile(
        r"(\.\./|docs/lessons/|labs/greenplum/|decks/greenplum|"
        r"artifacts/greenplum|\.md$|\.sql$|\.pptx$)"
    )

    offenders = []
    for path in docs:
        prose = _without_fenced_code(path.read_text(encoding="utf-8"))
        for inline_code in re.findall(r"`([^`]+)`", prose):
            if inline_code.startswith(r"\i /mentor-lab/examples/"):
                continue
            if path_like_span.search(inline_code):
                offenders.append(f"{path.relative_to(ROOT).as_posix()}: `{inline_code}`")

    assert offenders == []

    relative_link_targets = []
    for path in docs:
        prose = _without_fenced_code(path.read_text(encoding="utf-8"))
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", prose):
            if target.startswith("../") or target.startswith("./"):
                relative_link_targets.append(
                    f"{path.relative_to(ROOT).as_posix()}: {target}"
                )

    assert relative_link_targets == []

    workbook = (ROOT / "docs/lessons/01-greenplum/student-workbook.md").read_text(
        encoding="utf-8"
    )
    runbook = (
        ROOT / "docs/lessons/01-greenplum/runbooks/simple-path.md"
    ).read_text(encoding="utf-8")
    for url in [
        f"{REPO_BLOB_BASE}docs/lessons/01-greenplum/runbooks/student-prep.md",
        f"{REPO_BLOB_BASE}docs/lessons/01-greenplum/homework.md",
        f"{REPO_BLOB_BASE}labs/greenplum/README.md",
        f"{REPO_BLOB_BASE}labs/greenplum/examples/cluster-inspection.sql",
        f"{REPO_BLOB_BASE}labs/greenplum/examples/cluster-monitoring.sql",
        f"{REPO_BLOB_BASE}labs/greenplum/examples/storage-and-partitioning.sql",
        f"{REPO_BLOB_BASE}labs/greenplum/examples/partitioning-strategies.sql",
    ]:
        assert url in workbook
    assert f"{REPO_BLOB_BASE}artifacts/greenplum-theory.pptx" in runbook


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
