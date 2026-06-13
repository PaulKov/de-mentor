"""Pre-flight checks for professional lesson delivery."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from mentor_lab.session_experience import ACADEMY_VERSION, PORTAL_FRAMEWORK


@dataclass(frozen=True)
class LessonDoctorCheck:
    """A single lesson readiness check."""

    title: str
    path: Path
    required_markers: tuple[str, ...] = ()

    def evaluate(self, project_root: Path) -> "LessonDoctorResult":
        absolute = project_root / self.path
        if not absolute.exists():
            return LessonDoctorResult(self.title, self.path, "FAIL", "Файл не найден.")
        if self.required_markers:
            content = absolute.read_text(encoding="utf-8")
            missing = [marker for marker in self.required_markers if marker not in content]
            if missing:
                return LessonDoctorResult(
                    self.title,
                    self.path,
                    "FAIL",
                    "Нет маркеров: " + ", ".join(missing),
                )
        return LessonDoctorResult(self.title, self.path, "PASS", "Готово.")


@dataclass(frozen=True)
class LessonDoctorResult:
    """Rendered result of a readiness check."""

    title: str
    path: Path
    status: str
    detail: str


@dataclass(frozen=True)
class LessonDoctorReport:
    """Full report for a lab lesson."""

    lab_name: str
    results: List[LessonDoctorResult]

    @property
    def passed(self) -> bool:
        return all(result.status == "PASS" for result in self.results)

    def render(self) -> str:
        title = self.lab_name.title()
        lines = [
            f"# Lesson Doctor: {title}",
            "",
            f"- Версия: {ACADEMY_VERSION}",
            f"- Портал: {PORTAL_FRAMEWORK}",
            "- Назначение: проверить, что урок можно проводить без ручной охоты за артефактами.",
            "",
            "## Проверки",
            "",
        ]
        for result in self.results:
            lines.append(
                f"- {result.status} {result.title}: `{result.path.as_posix()}` — {result.detail}"
            )
        lines.extend(
            [
                "",
                "## Команды Перед Уроком",
                "",
                "```bash",
                "python3 mentor-lab.py check greenplum --dry-run",
                "python3 mentor-lab.py session greenplum start --student <name> --output artifacts/sessions/<name>",
                "MENTOR_LAB_SESSION=artifacts/sessions/<name>/session.json npm --prefix apps/academy-portal run dev",
                "python3 mentor-lab.py autograde-sql greenplum --submission labs/greenplum/examples/student-solution-example.sql --output artifacts/sql-autograde.md",
                "python3 mentor-lab.py ci-smoke greenplum --dry-run",
                "```",
                "",
                "## Что Проверить Глазами",
                "",
                "- Nuxt portal открывается и показывает current stage;",
                "- copy-command кнопки копируют команды;",
                "- skill graph совпадает с маршрутом урока;",
                "- workbook, homework и runbook кликабельно ведут в репозиторий;",
                "- SQL examples соответствуют Docker Greenplum стенду.",
                "",
            ]
        )
        return "\n".join(lines)


class LessonDoctor:
    """Builds deterministic pre-flight checks for lesson materials."""

    _SUPPORTED_LABS = {"greenplum"}

    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root

    def build(self, lab_name: str) -> LessonDoctorReport:
        normalized = lab_name.lower()
        if normalized not in self._SUPPORTED_LABS:
            raise KeyError(f"Unknown lesson doctor lab: {lab_name}")
        return LessonDoctorReport(
            lab_name=normalized,
            results=[
                check.evaluate(self._project_root)
                for check in _greenplum_checks()
            ],
        )

    def write(self, lab_name: str, output: Path) -> LessonDoctorReport:
        report = self.build(lab_name)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report.render(), encoding="utf-8")
        return report


def _greenplum_checks() -> Iterable[LessonDoctorCheck]:
    return [
        LessonDoctorCheck(
            "Презентация",
            Path("artifacts/greenplum-theory.pptx"),
        ),
        LessonDoctorCheck(
            "Workbook",
            Path("docs/lessons/01-greenplum/student-workbook.md"),
            ("homework.md", "partitioning-strategies.sql", "QD", "QE"),
        ),
        LessonDoctorCheck(
            "Mentor guide",
            Path("docs/lessons/01-greenplum/mentor-guide.md"),
            ("runbooks/simple-path.md", "runbooks/deep-dive-path.md"),
        ),
        LessonDoctorCheck(
            "Simple runbook",
            Path("docs/lessons/01-greenplum/runbooks/simple-path.md"),
            ("Команды", "Что спрашиваем", "Как проверяем"),
        ),
        LessonDoctorCheck(
            "Storage SQL",
            Path("labs/greenplum/examples/storage-and-partitioning.sql"),
            ("appendoptimized=true", "orientation=column", "PARTITION BY RANGE"),
        ),
        LessonDoctorCheck(
            "Partitioning SQL",
            Path("labs/greenplum/examples/partitioning-strategies.sql"),
            ("PARTITION BY RANGE", "PARTITION BY LIST", "PARTITION BY HASH"),
        ),
        LessonDoctorCheck(
            "Sample submission",
            Path("labs/greenplum/examples/student-solution-example.sql"),
            ("EXPLAIN ANALYZE", "gp_segment_id", "DISTRIBUTED BY"),
        ),
        LessonDoctorCheck(
            "CI smoke workflow",
            Path(".github/workflows/greenplum-smoke.yml"),
            ("Greenplum Live Smoke", "autograde-sql", "student-solution-example.sql"),
        ),
        LessonDoctorCheck(
            "Nuxt portal package",
            Path("apps/academy-portal/package.json"),
            ("nuxt", "vue"),
        ),
        LessonDoctorCheck(
            "Nuxt portal screen",
            Path("apps/academy-portal/app.vue"),
            ("Academy Experience v5", "current stage", "copy-command", "skill graph"),
        ),
    ]
