from mentor_lab.learning_loop import LearningLoopBuilder


def test_learning_loop_builds_skill_map_from_assessment_and_evidence(tmp_path):
    submission = tmp_path / "query-tuning.md"
    submission.write_text(
        "\n".join(
            [
                "Redistribute Motion",
                "Hash Join",
                "gp_segment_id",
                "Physical cause: wrong distribution key for join key",
                "Change: DISTRIBUTED BY (customer_id)",
                "Validation: EXPLAIN ANALYZE before and after",
                "Residual risk: Broadcast Motion can be acceptable for tiny dimensions",
            ]
        ),
        encoding="utf-8",
    )

    report = LearningLoopBuilder.default().build(
        lab_name="greenplum",
        pre_score=40,
        post_score=85,
        submission_path=submission,
    )

    rendered = report.render()

    assert report.growth == 45
    assert report.review_score == 100
    assert "# Learning Loop: Greenplum" in rendered
    assert "Рост: +45" in rendered
    assert "## Карта Навыков" in rendered
    assert "MPP mental model" in rendered
    assert "Distribution design" in rendered
    assert "EXPLAIN literacy" in rendered
    assert "Evidence quality" in rendered
    assert "+1 день" in rendered
    assert "+3 дня" in rendered
    assert "+7 дней" in rendered
    assert "submissions/query-tuning.md" in rendered


def test_learning_loop_handles_missing_evidence_without_submission():
    report = LearningLoopBuilder.default().build(
        lab_name="greenplum",
        pre_score=55,
        post_score=70,
        review_score=50,
    )

    rendered = report.render()

    assert report.growth == 15
    assert report.review_score == 50
    assert "evidence-файл не передан" in rendered
    assert "повторить с ментором" in rendered
