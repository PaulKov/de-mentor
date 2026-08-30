"""High-level self-service workflow for Spark students.

The workflow composes existing Docker and Spark command builders instead of
duplicating container paths or shell strings.  It is intentionally injectable:
tests can provide a fake runner, while the CLI uses the real subprocess runner.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol, Sequence

from mentor_lab.docker_compose import Command, DockerComposeRunner
from mentor_lab.domain import LabDefinition
from mentor_lab.homework_review import HomeworkReview
from mentor_lab.homework_review_lesson04 import Lesson04HomeworkReviewer
from mentor_lab.lesson_routes import LearningRoute
from mentor_lab.spark_lab import SparkLabCommands


class HomeworkPackReviewer(Protocol):
    """Minimal review dependency required by the student workflow."""

    def review(self, submission: Path) -> HomeworkReview:
        """Review one directory-based homework submission."""


@dataclass(frozen=True)
class WorkflowStep:
    """One executable and human-readable workflow step."""

    code: str
    description: str
    command: Command


@dataclass(frozen=True)
class WorkflowResult:
    """Stable CLI result for a start or test workflow."""

    title: str
    exit_code: int
    lines: tuple[str, ...]

    def render(self) -> str:
        """Render a compact terminal report."""

        return "\n".join((f"# {self.title}", "", *self.lines, ""))


@dataclass(frozen=True)
class SubmissionScaffoldResult:
    """Result of creating the two-file Lesson 04 homework scaffold."""

    exit_code: int
    destination: Path
    written_files: tuple[Path, ...]
    message: str

    def render(self) -> str:
        """Render paths relative to the scaffold destination when possible."""

        lines = [self.message, f"Submission: {self.destination}"]
        lines.extend(f"- {path.name}" for path in self.written_files)
        return "\n".join(lines) + "\n"


class SparkStudentWorkflow:
    """Orchestrate a ready-to-use Spark course environment and homework pack."""

    _PIPELINE_TEMPLATE = Path("labs/spark/examples/lesson04_core_pipeline.py")
    _EVIDENCE_TEMPLATE = Path("lessons/lesson-04/homework/templates/evidence.md")

    def __init__(
        self,
        project_root: Path,
        lab: LabDefinition,
        route: LearningRoute,
        runner: DockerComposeRunner,
        *,
        spark_commands: SparkLabCommands | None = None,
        reviewer: HomeworkPackReviewer | None = None,
    ) -> None:
        if lab.runtime != "spark" or route.lesson_code != "lesson-04":
            raise ValueError("Spark student workflow supports only the Lesson 04 route.")
        self._project_root = project_root.resolve()
        self._lab = lab
        self._route = route
        self._runner = runner
        self._spark_commands = spark_commands or SparkLabCommands(
            self._project_root,
            lab,
            runner,
        )
        self._reviewer = reviewer or Lesson04HomeworkReviewer()

    def start_steps(self, profile: str, with_notebook: bool) -> tuple[WorkflowStep, ...]:
        """Build the deterministic start plan without executing it."""

        profiles = ("notebook",) if with_notebook else ()
        return (
            WorkflowStep(
                "compose",
                "Start Spark services and wait for health checks",
                self._runner.build_up_command(
                    self._lab,
                    profiles=profiles,
                    build=with_notebook,
                    wait=True,
                ),
            ),
            WorkflowStep(
                "seed",
                f"Generate deterministic '{profile}' lesson data",
                self._spark_commands.build_seed_command(profile),
            ),
            WorkflowStep(
                "smoke",
                "Run the live Spark readiness application",
                self._spark_commands.build_check_command(),
            ),
        )

    def start(
        self,
        profile: str,
        *,
        with_notebook: bool = True,
        dry_run: bool = False,
    ) -> WorkflowResult:
        """Start and validate the complete student environment."""

        steps = self.start_steps(profile, with_notebook)
        lines: list[str] = []
        for index, step in enumerate(steps, start=1):
            lines.extend(
                (
                    f"[{index}/{len(steps)}] {step.description}",
                    f"$ {self._runner.format_command(step.command)}",
                )
            )
            if dry_run:
                lines.append("DRY-RUN")
                continue
            exit_code = self._runner.run(step.command)
            if exit_code != 0:
                lines.append(f"FAIL {step.code}: exit code {exit_code}")
                return WorkflowResult("Spark student environment", exit_code, tuple(lines))
            lines.append(f"PASS {step.code}")

        lines.extend(self._next_steps(with_notebook))
        return WorkflowResult("Spark student environment", 0, tuple(lines))

    def initialize_submission(
        self,
        destination: Path | None = None,
        *,
        force: bool = False,
    ) -> SubmissionScaffoldResult:
        """Create pipeline.py and evidence.md without accidental overwrites."""

        target = self._resolve_path(destination or Path(self._route.submission_path))
        templates = {
            target / "pipeline.py": self._project_root / self._PIPELINE_TEMPLATE,
            target / "evidence.md": self._project_root / self._EVIDENCE_TEMPLATE,
        }
        existing = tuple(path for path in templates if path.exists())
        if existing and not force:
            return SubmissionScaffoldResult(
                exit_code=1,
                destination=target,
                written_files=(),
                message=(
                    "Scaffold not changed: target files already exist. "
                    "Use --force only when replacement is intentional."
                ),
            )

        missing_templates = tuple(source for source in templates.values() if not source.is_file())
        if missing_templates:
            names = ", ".join(str(path) for path in missing_templates)
            return SubmissionScaffoldResult(
                exit_code=1,
                destination=target,
                written_files=(),
                message=f"Scaffold templates are missing: {names}",
            )

        target.mkdir(parents=True, exist_ok=True)
        for output, source in templates.items():
            shutil.copyfile(source, output)
        return SubmissionScaffoldResult(
            exit_code=0,
            destination=target,
            written_files=tuple(templates),
            message="Lesson 04 submission scaffold is ready.",
        )

    def test_submission(
        self,
        submission: Path | None = None,
        *,
        skip_live: bool = False,
    ) -> WorkflowResult:
        """Run the live Spark smoke gate and mechanical homework review."""

        target = self._resolve_path(submission or Path(self._route.submission_path))
        lines: list[str] = []
        if not skip_live:
            command = self._spark_commands.build_check_command()
            lines.extend(
                (
                    "[1/2] Run live Spark readiness",
                    f"$ {self._runner.format_command(command)}",
                )
            )
            exit_code = self._runner.run(command)
            if exit_code != 0:
                lines.append(f"FAIL live-spark: exit code {exit_code}")
                return WorkflowResult("Spark homework test", exit_code, tuple(lines))
            lines.append("PASS live-spark")
        else:
            lines.append("[1/2] SKIP live Spark readiness (--skip-live)")

        review = self._reviewer.review(target)
        lines.extend(("[2/2] Mechanical evidence review", review.render().rstrip()))
        return WorkflowResult(
            "Spark homework test",
            0 if review.accepted else 1,
            tuple(lines),
        )

    def _resolve_path(self, path: Path) -> Path:
        return path if path.is_absolute() else self._project_root / path

    @staticmethod
    def _next_steps(with_notebook: bool) -> Iterable[str]:
        lines = [
            "Ready: Spark master UI http://localhost:18080",
            "Run: python3 mentor-lab.py student spark-foundations init",
            "Test: python3 mentor-lab.py student spark-foundations test",
        ]
        if with_notebook:
            lines.insert(1, "Ready: JupyterLab http://localhost:18888 (token: de-mentor)")
        return lines
