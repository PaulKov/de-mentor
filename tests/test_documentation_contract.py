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
        "docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md",
        "docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md",
        "docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md",
        "docs/lessons/01-greenplum/query-tuning-lab.md",
        "docs/lessons/01-greenplum/academy-loop.md",
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
    assert "SMP" in guide
    assert "MPP" in guide
    assert "EPP" in guide
    assert "QD/QE deep dive" in guide
    assert "Heap, AO row, AOCO column" in guide
    assert "Что сказать емко" in guide


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
