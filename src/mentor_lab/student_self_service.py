"""Student-facing self-service command guides."""

from __future__ import annotations

from dataclasses import dataclass

from mentor_lab.domain import LabDefinition
from mentor_lab.lesson_routes import LearningRoute


@dataclass(frozen=True)
class StudentPlatformProfile:
    """Command prefix and setup hints for one student OS."""

    label: str
    python_command: str
    setup_notes: tuple[str, ...]


class StudentSelfServiceGuide:
    """Renders bootstrap and homework instructions without side effects."""

    _PROFILES = {
        "macos": StudentPlatformProfile(
            label="macOS",
            python_command="python3",
            setup_notes=("Docker Desktop", "Terminal", "Git", "Python 3.9+"),
        ),
        "windows": StudentPlatformProfile(
            label="Windows",
            python_command="py",
            setup_notes=("Docker Desktop", "WSL 2", "PowerShell", "Git", "Python 3.9+"),
        ),
        "linux": StudentPlatformProfile(
            label="Linux",
            python_command="python3",
            setup_notes=("Docker Engine", "Docker Compose plugin", "Git", "Python 3.9+"),
        ),
    }

    def bootstrap(self, lab: LabDefinition, route: LearningRoute, platform: str) -> str:
        profile = self._PROFILES[platform]
        prefix = profile.python_command
        lines = [
            f"Student bootstrap: {route.name}",
            f"Physical lab: {lab.name}",
            f"Platform: {profile.label}",
            "",
            "Prepare:",
        ]
        lines.extend(f"- {note}" for note in profile.setup_notes)
        commands = [
            "",
            "Commands:",
            f"  {prefix} mentor-lab.py doctor --full",
            f"  {prefix} mentor-lab.py readiness {lab.name} --platform {platform}",
            f"  {prefix} mentor-lab.py up {lab.name}",
        ]
        if lab.name in {"greenplum", "greenplum-625"}:
            commands.append(
                f"  {prefix} mentor-lab.py seed {lab.name} --profile academy"
            )
            commands.append(
                f"  # Shared GP 6.25 stand @ :15436; DB mentor; schemas lesson01/02/03"
            )
        elif lab.runtime == "spark":
            commands.append(
                f"  {prefix} mentor-lab.py seed {lab.name} --profile lesson04"
            )
            commands.append(
                "  # Spark master UI @ :18080; driver UI @ :4040 while a job is running"
            )
        commands.extend(
            [
                f"  {prefix} mentor-lab.py check {lab.name}",
                f"  {prefix} mentor-lab.py runbook {route.name} simple",
                (
                    f"  {prefix} mentor-lab.py session {route.name} start "
                    "--student <your-name>"
                    if lab.runtime == "spark"
                    else f"  {prefix} mentor-lab.py academy {route.name} start --student <your-name>"
                ),
                "",
                "Lesson pack:",
                f"  {route.lesson_root}/README.md",
                f"  {route.prep_runbook_path}",
                f"  {route.workbook_path}",
                f"  {route.homework_path}",
                f"  {lab.docs_path}",
            ]
        )
        lines.extend(commands)
        return "\n".join(lines) + "\n"

    def homework(self, lab: LabDefinition, route: LearningRoute) -> str:
        read_extra: list[str] = []
        if route.lesson_code == "lesson-04":
            bring = (
                "  pipeline.py, evidence.md, explain(formatted), quality checks, "
                "Spark UI observations and a production decision."
            )
            read_extra = [f"  {route.homework_dir}/templates/evidence.md"]
        elif route.lesson_code == "lesson-03":
            bring = (
                "  Senior core: rewrite.sql (0–3 stages), evidence.md (e2e + decision), "
                "reconcile.sql (two-way EXCEPT ALL), residual risks. "
                "Principal extension (matrix/FS/policy) optional."
            )
            read_extra = [
                f"  {route.homework_dir}/templates/evidence.md",
                f"  {route.homework_dir}/templates/reconcile.sql",
            ]
        elif route.lesson_code == "lesson-02":
            bring = (
                "  DDL, EXPLAIN evidence, partition catalog checks, "
                "statistics policy, validation."
            )
        else:
            bring = (
                "  facts/dimensions/grain, distribution, partitioning, storage, "
                "catalog evidence, EXPLAIN, risks, Lesson 02 questions."
            )

        lines = [
            f"Student homework: {route.name}",
            f"Physical lab: {lab.name}",
            f"Runtime: {lab.runtime}",
            f"Database: {lab.default_database or '(n/a)'}",
            f"Lesson pack: {route.lesson_root}/",
            f"Submission: {route.submission_path}",
            "",
            "Read:",
            f"  {route.lesson_root}/README.md",
            f"  {route.homework_path}",
            f"  {route.homework_plan_path}",
            f"  {route.rubric_path}",
            f"  {route.workbook_path}",
            *read_extra,
            "",
            "Self-check commands:",
            f"  python3 mentor-lab.py runbook {route.name} homework",
            f"  python3 mentor-lab.py check {lab.name}",
            (
                f"  python3 mentor-lab.py homework {lab.name} check "
                f"--submission {route.submission_path}"
            ),
            (
                f"  python3 mentor-lab.py grade {lab.name} --dry-run"
                if lab.runtime == "sql"
                else "  # Spark homework is checked from the submission pack"
            ),
            "",
            f"Bring to {_lesson_label(route.next_lesson.code)}:",
            bring,
        ]
        return "\n".join(lines) + "\n"


def _lesson_label(code: str) -> str:
    if code.startswith("02-"):
        return "Lesson 02"
    if code.startswith("03-"):
        return "Lesson 03"
    if code.startswith("04-"):
        return "Lesson 04"
    if code.startswith("05-"):
        return "Lesson 05"
    return code
