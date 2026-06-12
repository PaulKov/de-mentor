from mentor_lab.assessment import AssessmentCatalog
from mentor_lab.certificates import CertificateWriter
from mentor_lab.cockpit import MentorCockpit
from mentor_lab.grading import Grade
from mentor_lab.query_tuning import QueryTuningCatalog
from mentor_lab.submissions import SubmissionReviewer, SubmissionTemplate


def test_assessment_catalog_scores_pre_and_post_answers():
    catalog = AssessmentCatalog.default()

    pre = catalog.get("greenplum", "pre")
    post = catalog.get("greenplum", "post")

    assert len(pre.questions) >= 5
    assert pre.score(["B", "C", "A", "B", "C"]) >= 60
    assert post.score(post.answer_key) == 100
    assert "Motion" in post.questions[0].prompt


def test_submission_template_and_reviewer_create_evidence_loop(tmp_path):
    template_path = tmp_path / "advanced-joins.md"

    written = SubmissionTemplate.default().write(template_path, "advanced-joins")

    assert written == template_path
    content = template_path.read_text(encoding="utf-8")
    assert "EXPLAIN evidence" in content
    assert "Redistribute Motion" in content

    template_path.write_text(
        "Redistribute Motion\nBroadcast Motion\nHash Join\n"
        "gp_segment_id\nRCA: distribution key does not match join key\n",
        encoding="utf-8",
    )
    review = SubmissionReviewer.default().review(template_path)

    assert review.score >= 80
    assert "EXPLAIN literacy" in review.skill_hits
    assert review.missing_evidence == []


def test_query_tuning_catalog_contains_realistic_tasks():
    catalog = QueryTuningCatalog.default()
    codes = [task.code for task in catalog.list("greenplum")]

    assert "missing-statistics" in codes
    assert "bad-partitioning" in codes
    assert "large-gather" in codes
    assert "storage-model-choice" in codes
    assert "Redistribute Motion" in catalog.get("greenplum", "redistribute-join").symptom


def test_mentor_cockpit_writes_self_service_html(tmp_path):
    output = tmp_path / "cockpit.html"

    MentorCockpit().write(output, "greenplum")

    html = output.read_text(encoding="utf-8")
    assert "Mentor Cockpit" in html
    assert "EXPLAIN Analyzer" in html
    assert "Hidden incidents" in html
    assert "mentor-lab.py check greenplum" in html


def test_certificate_writer_creates_completion_artifact(tmp_path):
    output = tmp_path / "certificate.md"
    grade = Grade(
        lesson_code="lesson-01",
        score=92,
        level="Production-ready",
        skill_scores={"EXPLAIN literacy": 25, "Distribution design": 25},
        next_actions=[],
    )

    CertificateWriter().write(output, "greenplum", grade)

    content = output.read_text(encoding="utf-8")
    assert "# Greenplum Lesson Completion" in content
    assert "Production-ready" in content
    assert "EXPLAIN literacy" in content
    assert "Next recommended challenge" in content
