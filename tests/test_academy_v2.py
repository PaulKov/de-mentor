from pathlib import Path

from mentor_lab.adaptive_review import AdaptiveReviewer
from mentor_lab.challenges import ChallengeCatalog
from mentor_lab.control_room import MentorControlRoom
from mentor_lab.diagnostics import DiagnosticsCatalog
from mentor_lab.explain_analyzer import ExplainPlanAnalyzer
from mentor_lab.plan_visualizer import PlanVisualizer
from mentor_lab.portal import StudentPortal
from mentor_lab.scenario_dsl import ScenarioDslCatalog
from mentor_lab.scenario_engine import ScenarioRandomizer
from mentor_lab.solutions import SolutionCatalog
from mentor_lab.telemetry import TelemetryReport


def test_visualizer_renders_motion_graph():
    analyzer = ExplainPlanAnalyzer()
    analysis = analyzer.analyze(analyzer.sample_plan("product_join"))

    mermaid = PlanVisualizer().to_mermaid(analysis)

    assert "flowchart TD" in mermaid
    assert "Broadcast Motion" in mermaid
    assert "Redistribute Motion" in mermaid
    assert "Gather Motion" in mermaid
    assert "Interconnect" in mermaid


def test_visualizer_writes_static_html(tmp_path: Path):
    analyzer = ExplainPlanAnalyzer()
    analysis = analyzer.analyze(analyzer.sample_plan("bad_customer_join"))

    output = PlanVisualizer().write_html(tmp_path / "plan.html", analysis)

    html = output.read_text(encoding="utf-8")
    assert "Greenplum EXPLAIN Visualizer" in html
    assert "Redistribute Motion" in html
    assert "mermaid" in html


def test_diagnostics_catalog_exposes_greenplum_probes():
    probes = DiagnosticsCatalog.default().list("greenplum")

    assert {probe.code for probe in probes} >= {
        "segment-skew",
        "active-queries",
        "table-statistics",
        "spill-risk",
    }
    assert all(probe.sql.strip().endswith(";") for probe in probes)


def test_scenario_dsl_exposes_engine_neutral_contract():
    scenario = ScenarioDslCatalog.default().get("greenplum", "redistribute-join")

    rendered = scenario.render()

    assert scenario.engine == "greenplum"
    assert "skills:" in rendered
    assert "checks:" in rendered
    assert "plan_contains" in rendered


def test_scenario_randomizer_is_deterministic_by_seed():
    randomizer = ScenarioRandomizer.default()

    first = randomizer.pick("greenplum", difficulty="medium", seed=42)
    second = randomizer.pick("greenplum", difficulty="medium", seed=42)

    assert first == second
    assert first.seed_profile
    assert first.acceptance_criteria
    assert first.difficulty == "medium"


def test_adaptive_reviewer_scores_reasoning_quality(tmp_path: Path):
    submission = tmp_path / "submission.md"
    submission.write_text(
        "Symptom: slow query\n"
        "Plan evidence: Redistribute Motion and Hash Join\n"
        "Segment evidence: gp_segment_id skew\n"
        "Physical cause: distribution key differs from join key\n"
        "Change: recreate fact DISTRIBUTED BY customer_id\n"
        "Validation: EXPLAIN ANALYZE improved and skew fixed\n"
        "Residual risk: product joins may need Broadcast Motion\n",
        encoding="utf-8",
    )

    review = AdaptiveReviewer.default().review(submission)

    assert review.score >= 90
    assert "EXPLAIN evidence" in review.skill_scores
    assert "Root cause reasoning" in review.skill_scores
    assert not review.missing
    assert "Recommended next task" in review.render()


def test_student_portal_and_control_room_artifacts_are_written(tmp_path: Path):
    portal_path = StudentPortal().write(tmp_path / "student.html", "greenplum")
    room_path = MentorControlRoom().write(tmp_path / "mentor.html", "greenplum")

    portal_html = portal_path.read_text(encoding="utf-8")
    room_html = room_path.read_text(encoding="utf-8")
    assert "Greenplum Student Portal" in portal_html
    assert "mentor-lab.py visualize-plan" in portal_html
    assert "mentor-lab.py evidence" in portal_html
    assert "mentor-lab.py homework" in portal_html
    assert "mentor-lab.py misconception" in portal_html
    assert "mentor-lab.py debrief" in portal_html
    assert "mentor-lab.py readiness" in portal_html
    assert "mentor-lab.py coach-plan" in portal_html
    assert "mentor-lab.py replay" in portal_html
    assert "mentor-lab.py dataset" in portal_html
    assert "mentor-lab.py autograde-sql" in portal_html
    assert "mentor-lab.py ci-smoke" in portal_html
    assert "Greenplum Mentor Control Room" in room_html
    assert "Timed challenge" in room_html
    assert "mentor-lab.py teach" in room_html
    assert "mentor-lab.py evidence" in room_html
    assert "mentor-lab.py homework" in room_html
    assert "mentor-lab.py misconception" in room_html
    assert "mentor-lab.py debrief" in room_html
    assert "mentor-lab.py learning-loop" in room_html
    assert "mentor-lab.py orchestrate" in room_html
    assert "mentor-lab.py observe" in room_html
    assert "mentor-lab.py calibration" in room_html
    assert "mentor-lab.py replay" in room_html
    assert "mentor-lab.py dataset" in room_html
    assert "mentor-lab.py autograde-sql" in room_html
    assert "mentor-lab.py ci-smoke" in room_html


def test_solution_catalog_contains_golden_and_anti_solution():
    solution = SolutionCatalog.default().get("greenplum", "redistribute-join")

    rendered = solution.render()

    assert "DISTRIBUTED BY" in solution.golden
    assert "Golden solution" in rendered
    assert "Anti-solution" in rendered


def test_telemetry_report_recommends_next_focus():
    report = TelemetryReport(pre_score=40, post_score=85, review_score=70)

    rendered = report.render()

    assert "Growth: +45" in rendered
    assert "Recommended next focus" in rendered
    assert "Broadcast vs Redistribute" in rendered


def test_timed_challenge_has_deadline_and_evidence_contract():
    challenge = ChallengeCatalog.default().start(
        "greenplum", difficulty="hard", minutes=15, seed=7
    )

    rendered = challenge.render()

    assert challenge.deadline_iso
    assert "Timed challenge" in rendered
    assert "Evidence contract" in rendered
    assert "15 min" in rendered
