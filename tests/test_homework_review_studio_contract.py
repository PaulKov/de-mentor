import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from mentor_lab.cli import main
from mentor_lab.session_contract import SessionContractValidator


ROOT = Path(__file__).resolve().parents[1]


def invoke(args: list[str]) -> tuple[int, str]:
    stdout = StringIO()
    try:
        with redirect_stdout(stdout):
            exit_code = main(args)
    except SystemExit as exc:
        exit_code = int(exc.code)
    return exit_code, stdout.getvalue()


def test_session_start_can_create_lesson_01_homework_walkthrough_without_submission(tmp_path):
    session_dir = tmp_path / "ivan-review"

    exit_code, output = invoke(
        [
            "session",
            "greenplum",
            "start",
            "--homework-review",
            "lesson-01",
            "--student",
            "Иван",
            "--output",
            str(session_dir),
        ]
    )

    assert exit_code == 0, output
    state = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    review = state["homework_review"]

    assert review["lesson_code"] == "lesson-01"
    assert review["title"] == "Lesson 01 Homework Walkthrough"
    assert review["submission_status"] == "not_submitted"
    assert review["submission_path"] == ""
    assert review["score"] == 0
    assert review["accepted"] is False
    assert len(review["rubric_items"]) >= 8
    assert len(review["live_checklist"]) >= 5
    assert len(review["sql_snippets"]) >= 4
    assert review["mentor_conclusion"]["summary"].startswith("Домашка не была сдана")
    assert review["next_lesson_plan"]["lesson_code"] == "lesson-02"
    assert "partition pruning" in review["next_lesson_plan"]["focus"].lower()

    validation = SessionContractValidator().validate_file(session_dir / "session.json")
    assert validation.valid, validation.render()


def test_session_start_embeds_homework_review_score_from_submission(tmp_path):
    submission = tmp_path / "homework.md"
    submission.write_text(
        """
# Homework

fact, dimension, grain
distribution distributed by join pattern cardinality
partition partition by partition key distribution key
storage aoco appendoptimized orientation=column
pg_partition_tree gp_toolkit.gp_partitions leaf_partitions
explain gp_segment_id validation
risk stale statistics broadcast motion residual risk
lesson 02 partition pruning statistics incremental loads
""",
        encoding="utf-8",
    )
    session_dir = tmp_path / "scored-review"

    exit_code, output = invoke(
        [
            "session",
            "greenplum",
            "start",
            "--homework-review",
            "lesson-01",
            "--submission",
            str(submission),
            "--student",
            "Иван",
            "--output",
            str(session_dir),
        ]
    )

    assert exit_code == 0, output
    state = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    review = state["homework_review"]

    assert review["submission_status"] == "submitted"
    assert review["submission_path"] == str(submission)
    assert review["score"] == 100
    assert review["accepted"] is True
    assert review["missing_evidence"] == []
    assert all(item["score"] == 100 for item in review["rubric_items"])
    assert any("EXPLAIN" in snippet["command"] for snippet in review["sql_snippets"])
    assert review["mentor_conclusion"]["decision"] == "ready_for_lesson_02"


def test_session_contract_schema_documents_optional_homework_review():
    schema = json.loads(
        (ROOT / "contracts" / "academy-session" / "v1" / "session.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert "homework_review" in schema["properties"]
    review_def = schema["$defs"]["homeworkReview"]
    assert "lesson_code" in review_def["required"]
    assert "rubric_items" in review_def["required"]
    assert "sql_snippets" in review_def["required"]
    assert "next_lesson_plan" in review_def["required"]
