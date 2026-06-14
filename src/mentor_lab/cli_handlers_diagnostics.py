"""Diagnostics, scenario and knowledge-assist CLI handlers."""

from __future__ import annotations

from pathlib import Path

from mentor_lab.adaptive_review import AdaptiveReviewer
from mentor_lab.calibration import CalibrationCatalog
from mentor_lab.cli_context import _lab_or_none, _project_root, _sql_client
from mentor_lab.control_room import MentorControlRoom
from mentor_lab.diagnostics import DiagnosticsCatalog
from mentor_lab.explain_analyzer import ExplainPlanAnalyzer
from mentor_lab.misconceptions import MisconceptionCatalog
from mentor_lab.plan_visualizer import PlanVisualizer
from mentor_lab.scenario_dsl import ScenarioDslCatalog
from mentor_lab.scenario_engine import ScenarioRandomizer
from mentor_lab.seed_profiles import SeedProfileCatalog
from mentor_lab.solutions import SolutionCatalog

def _handle_misconception(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    catalog = MisconceptionCatalog.default()
    try:
        if args.misconception_command == "list":
            for card in catalog.list(lab.name):
                print(f"- {card.code}: {card.title}")
            return 0
        if args.misconception_command == "show":
            if not args.code:
                print("Use: mentor-lab misconception <lab> show <code>")
                return 1
            print(catalog.get(lab.name, args.code).render(), end="")
            return 0
        text = args.text or ""
        if not text:
            print("Use --text for misconception diagnosis.")
            return 1
        print(catalog.diagnose(lab.name, text).render(), end="")
    except KeyError as exc:
        print(str(exc))
        return 1
    return 0


def _handle_visualize_plan(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    analyzer = ExplainPlanAnalyzer()
    try:
        plan = (
            analyzer.sample_plan(args.query)
            if args.sample
            else _sql_client(lab).text(f"EXPLAIN {analyzer.query_sql(args.query)}")
        )
    except (KeyError, RuntimeError) as exc:
        print(str(exc))
        return 1

    analysis = analyzer.analyze(plan)
    visualizer = PlanVisualizer()
    if args.format == "html":
        if not args.output:
            print("Use --output when --format html is selected.")
            return 1
        written = visualizer.write_html(Path(args.output), analysis)
        print(f"Plan visualization written to {written}")
        return 0

    mermaid = visualizer.to_mermaid(analysis)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(mermaid, encoding="utf-8")
        print(f"Plan visualization written to {output}")
        return 0
    print(mermaid, end="")
    return 0


def _handle_diagnostics(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    catalog = DiagnosticsCatalog.default()
    try:
        if args.diagnostics_command == "list":
            for probe in catalog.list(lab.name):
                print(f"- {probe.code}: {probe.title}")
            return 0
        if not args.probe_code:
            print("Use: mentor-lab diagnostics <lab> show|run <probe_code>")
            return 1
        probe = catalog.get(lab.name, args.probe_code)
    except KeyError as exc:
        print(str(exc))
        return 1

    if args.diagnostics_command == "show" or args.dry_run:
        print(probe.render(), end="")
        return 0
    try:
        print(_sql_client(lab).text(probe.sql), end="")
    except RuntimeError as exc:
        print(f"Diagnostic execution failed: {exc}")
        return 1
    return 0


def _handle_scenario(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    catalog = ScenarioDslCatalog.default()
    try:
        if args.scenario_command == "list":
            for scenario in catalog.list(lab.name):
                print(f"- {scenario.code}: {scenario.title} [{scenario.difficulty}]")
            return 0
        if args.scenario_command == "show":
            if not args.scenario_code:
                print("Use: mentor-lab scenario <lab> show <scenario_code>")
                return 1
            print(catalog.get(lab.name, args.scenario_code).render(), end="")
            return 0
        start = ScenarioRandomizer.default().start(
            lab.name, difficulty=args.difficulty, seed=args.seed
        )
    except KeyError as exc:
        print(str(exc))
        return 1

    print(start.render(), end="")
    if args.dry_run:
        return 0
    try:
        profile = SeedProfileCatalog.default(_project_root()).get(
            lab.name, start.scenario.seed_profile
        )
    except KeyError as exc:
        print(str(exc))
        return 1
    return _sql_client(lab).run_file(profile.container_path)


def _handle_adaptive_review(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    path = Path(args.submission)
    if not path.exists():
        print(f"Submission file does not exist: {path}")
        return 1
    print(AdaptiveReviewer.default().review(path).render(), end="")
    return 0


def _handle_control_room(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    output = Path(args.output) if args.output else Path("artifacts") / f"{lab.name}-control-room.html"
    written = MentorControlRoom().write(output, lab.name)
    print(f"Control room written to {written}")
    return 0


def _handle_solutions(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    catalog = SolutionCatalog.default()
    try:
        if args.solutions_command == "list":
            for solution in catalog.list(lab.name):
                print(f"- {solution.code}: {solution.title}")
            return 0
        if not args.solution_code:
            print("Use: mentor-lab solutions <lab> show <solution_code>")
            return 1
        print(catalog.get(lab.name, args.solution_code).render(), end="")
    except KeyError as exc:
        print(str(exc))
        return 1
    return 0


def _handle_calibration(args: argparse.Namespace) -> int:
    lab = _lab_or_none(args.lab_name)
    if lab is None:
        return 1
    catalog = CalibrationCatalog.default()
    try:
        if args.calibration_command == "list":
            for example in catalog.list(lab.name):
                print(f"- {example.level}: {example.title} [{example.score_band}]")
            return 0
        if not args.level:
            print("Use: mentor-lab calibration <lab> show <level>")
            return 1
        print(catalog.get(lab.name, args.level).render(), end="")
    except KeyError as exc:
        print(str(exc))
        return 1
    return 0
