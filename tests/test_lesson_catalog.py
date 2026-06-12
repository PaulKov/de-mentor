from mentor_lab.lesson_catalog import LessonCatalog


def test_lesson_catalog_contains_professional_greenplum_flow():
    lesson = LessonCatalog.default().get("lesson-01")

    assert lesson.title == "Greenplum MPP Foundations"
    assert len(lesson.steps) >= 8
    assert lesson.steps[0].kind == "theory"
    assert any(step.kind == "incident" for step in lesson.steps)
    assert any(step.kind == "capstone" for step in lesson.steps)


def test_lesson_step_lookup_is_human_indexed():
    lesson = LessonCatalog.default().get("lesson-01")

    step = lesson.step(3)

    assert step.number == 3
    assert "distribution" in step.title.lower()


def test_greenplum_alias_resolves_to_first_lesson():
    lesson = LessonCatalog.default().get("greenplum")

    assert lesson.code == "lesson-01"


def test_hint_catalog_returns_progressive_hints():
    hints = LessonCatalog.default().hints("lesson-01", "skew")

    assert len(hints) == 3
    assert "gp_segment_id" in hints[0]
    assert "low-cardinality" in hints[1]
    assert "DISTRIBUTED BY" in hints[2]


def test_hint_catalog_accepts_human_topic_alias():
    hints = LessonCatalog.default().hints("greenplum", "skew-investigation")

    assert "gp_segment_id" in hints[0]


def test_advanced_hint_topics_cover_plan_joins_and_mpp_systems():
    catalog = LessonCatalog.default()

    plan_hints = catalog.hints("greenplum", "plan-reading")
    join_hints = catalog.hints("greenplum", "physical-joins")
    systems_hints = catalog.hints("greenplum", "mpp-systems")

    assert "Motion" in plan_hints[0]
    assert "Rows out" in plan_hints[1]
    assert "co-located" in join_hints[0]
    assert "Broadcast Motion" in join_hints[1]
    assert "SMP" in systems_hints[0]
    assert "EPP" in systems_hints[2]


def test_incident_catalog_contains_acceptance_criteria():
    incident = LessonCatalog.default().incident("skewed-distribution")

    assert incident.title == "Marketplace revenue report became slow"
    assert "Redistribute Motion" in incident.symptoms
    assert len(incident.acceptance_criteria) >= 4


def test_incident_catalog_accepts_human_alias():
    incident = LessonCatalog.default().incident("skew-investigation")

    assert incident.code == "skewed-distribution"
