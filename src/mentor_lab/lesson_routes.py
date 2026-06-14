"""Learning route metadata that separates lessons from deployable labs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class NextLesson:
    """Short pointer to the next curriculum step."""

    code: str
    title: str
    path: str


@dataclass(frozen=True)
class LearningRoute:
    """User-facing lesson route mapped to a physical lab stand."""

    name: str
    lesson_code: str
    physical_lab_name: str
    title: str
    docs_root: str
    deck_path: str
    sql_examples: tuple[str, ...]
    next_lesson: NextLesson

    @property
    def workbook_path(self) -> str:
        return f"{self.docs_root}/student-workbook.md"

    @property
    def homework_path(self) -> str:
        return f"{self.docs_root}/homework.md"

    @property
    def prep_runbook_path(self) -> str:
        return f"{self.docs_root}/runbooks/student-prep.md"


class UnknownLearningRouteError(KeyError):
    """Raised when a user asks for an unknown lesson route."""

    def __init__(self, requested_name: str, available_names: Iterable[str]) -> None:
        available = ", ".join(available_names)
        self.message = (
            f"Unknown learning route '{requested_name}'. Available routes: {available}."
        )
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


LESSON_01_ROUTE = LearningRoute(
    name="greenplum",
    lesson_code="lesson-01",
    physical_lab_name="greenplum",
    title="Greenplum MPP foundations",
    docs_root="docs/lessons/01-greenplum",
    deck_path="artifacts/greenplum-theory.pptx",
    sql_examples=(
        "labs/greenplum/examples/storage-and-partitioning.sql",
        "labs/greenplum/examples/partitioning-strategies.sql",
        "labs/greenplum/examples/cluster-monitoring.sql",
    ),
    next_lesson=NextLesson(
        code="02-greenplum-partitioning",
        title="Partitioning, statistics and incremental loads in MPP",
        path="docs/lessons/02-greenplum-partitioning/README.md",
    ),
)

LESSON_02_ROUTE = LearningRoute(
    name="greenplum-partitioning",
    lesson_code="lesson-02",
    physical_lab_name="greenplum",
    title="Partitioning, statistics and incremental loads in MPP",
    docs_root="docs/lessons/02-greenplum-partitioning",
    deck_path="artifacts/greenplum-partitioning-theory.pptx",
    sql_examples=(
        "labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql",
        "labs/greenplum/examples/partitioning-strategies.sql",
        "labs/greenplum/examples/cluster-monitoring.sql",
    ),
    next_lesson=NextLesson(
        code="03-greenplum-query-tuning",
        title="Query tuning, workload management and production diagnostics",
        path="docs/lessons/03-greenplum-query-tuning/README.md",
    ),
)

_ROUTES = {
    LESSON_01_ROUTE.name: LESSON_01_ROUTE,
    LESSON_02_ROUTE.name: LESSON_02_ROUTE,
}

_ALIASES = {
    "gp": "greenplum",
    "greenplum-01": "greenplum",
    "lesson-01": "greenplum",
    "1": "greenplum",
    "02": "greenplum-partitioning",
    "2": "greenplum-partitioning",
    "lesson-02": "greenplum-partitioning",
    "greenplum-02": "greenplum-partitioning",
    "partitioning": "greenplum-partitioning",
    "gp-partitioning": "greenplum-partitioning",
}


def resolve_learning_route(name: str) -> LearningRoute:
    """Return a lesson route by canonical name or alias."""

    normalized = name.strip().lower()
    canonical = _ALIASES.get(normalized, normalized)
    try:
        return _ROUTES[canonical]
    except KeyError as exc:
        raise UnknownLearningRouteError(name, sorted(_ROUTES)) from exc


def learning_route_names() -> tuple[str, ...]:
    """Return canonical route names for user-facing errors."""

    return tuple(sorted(_ROUTES))
