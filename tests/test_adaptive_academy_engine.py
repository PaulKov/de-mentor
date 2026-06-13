from mentor_lab.debrief import DebriefGenerator
from mentor_lab.misconceptions import MisconceptionCatalog
from mentor_lab.portal import StudentPortal


def test_misconception_catalog_diagnoses_partition_distribution_confusion():
    response = (
        "Я выберу partition key как distribution key, потому что оба отвечают "
        "за распределение данных и pruning."
    )

    diagnosis = MisconceptionCatalog.default().diagnose("greenplum", response)
    rendered = diagnosis.render()

    assert diagnosis.matches
    assert diagnosis.matches[0].code == "partition-equals-distribution"
    assert "partition key != distribution key" in rendered
    assert "мини-эксперимент" in rendered
    assert "follow-up" in rendered


def test_misconception_catalog_renders_show_card_for_master_data_path():
    card = MisconceptionCatalog.default().get("greenplum", "master-reads-all-data")

    rendered = card.render()

    assert "master читает все данные" in rendered
    assert "QD" in rendered
    assert "QE" in rendered
    assert "Gather Motion" in rendered
    assert "mentor-lab.py teach greenplum simple" in rendered


def test_student_portal_v2_has_progress_hints_and_submission_export():
    html = StudentPortal().render("greenplum", version="v2")

    assert "Greenplum Student Portal v2" in html
    assert "data-progress" in html
    assert "Evidence checklist" in html
    assert "Misconception hints" in html
    assert "Export submission" in html
    assert "mentor-lab.py misconception greenplum diagnose" in html
    assert "mentor-lab.py evidence greenplum collect redistribute-join" in html
    assert "mentor-lab.py homework greenplum check" in html


def test_debrief_generator_combines_review_misconceptions_and_next_steps(tmp_path):
    submission = tmp_path / "query-tuning.md"
    submission.write_text(
        "Symptom: slow query. Plan evidence: Redistribute Motion and Hash Join. "
        "Segment evidence: gp_segment_id skew. Physical cause: distribution key "
        "differs from join key. Change: recreate fact DISTRIBUTED BY customer_id. "
        "Validation: EXPLAIN ANALYZE improved. Residual risk: Broadcast Motion. "
        "I initially thought partition key equals distribution key.",
        encoding="utf-8",
    )

    debrief = DebriefGenerator.default().generate(
        lab_name="greenplum",
        student_name="Иван",
        submission_path=submission,
        pre_score=40,
        post_score=85,
    )
    rendered = debrief.render()

    assert "# Debrief: Иван / Greenplum" in rendered
    assert "Score:" in rendered
    assert "Рост: +45" in rendered
    assert "Misconceptions" in rendered
    assert "partition key != distribution key" in rendered
    assert "Что отправить ученику" in rendered
    assert "Private mentor notes" in rendered
