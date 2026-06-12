from pathlib import Path

from mentor_lab.checks import CheckResult, CheckStatus
from mentor_lab.grading import GradeCalculator
from mentor_lab.reports import MentorReport


def test_grade_calculator_maps_checks_to_skill_matrix():
    checks = [
        CheckResult("greenplum_connection", "Connection", CheckStatus.PASS, "", ""),
        CheckResult("lesson_schema", "Schema", CheckStatus.PASS, "", ""),
        CheckResult("seed_data", "Seed", CheckStatus.PASS, "", ""),
        CheckResult("bad_distribution_skew", "Skew", CheckStatus.FAIL, "50%", "Inspect gp_segment_id"),
        CheckResult("good_distribution_balance", "Balance", CheckStatus.PASS, "", ""),
        CheckResult("motion_plan", "Motion", CheckStatus.FAIL, "Missing", "Run EXPLAIN"),
    ]

    grade = GradeCalculator.default().calculate("lesson-01", checks)

    assert grade.score == 55
    assert grade.level == "Developing"
    assert grade.skill_scores["MPP diagnostics"] == 0
    assert grade.skill_scores["EXPLAIN literacy"] == 0
    assert "Inspect gp_segment_id" in grade.next_actions


def test_mentor_report_writes_markdown_with_rubric_and_next_actions(tmp_path):
    checks = [
        CheckResult("greenplum_connection", "Connection", CheckStatus.PASS, "ok", ""),
        CheckResult("motion_plan", "Motion", CheckStatus.FAIL, "Missing", "Run EXPLAIN"),
    ]
    grade = GradeCalculator.default().calculate("lesson-01", checks)
    report_path = tmp_path / "lesson-01-report.md"

    MentorReport().write(report_path, "lesson-01", checks, grade)

    content = report_path.read_text(encoding="utf-8")
    assert "# Mentor Report: lesson-01" in content
    assert "Score:" in content
    assert "Motion" in content
    assert "Run EXPLAIN" in content


def test_report_default_path_is_inside_reports_directory():
    path = MentorReport.default_path("lesson-01")

    assert path == Path("reports/lesson-01-report.md")
