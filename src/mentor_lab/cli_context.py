"""Shared CLI dependency factory helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from mentor_lab.docker_compose import DockerComposeRunner
from mentor_lab.domain import LabDefinition, UnknownLabError
from mentor_lab.lesson_catalog import normalize_lesson_code
from mentor_lab.lesson_routes import LearningRoute, UnknownLearningRouteError, resolve_learning_route
from mentor_lab.registry import create_default_registry
from mentor_lab.sql_client import GreenplumSqlClient

def _lab_or_none(name: str) -> Optional[LabDefinition]:
    try:
        return _registry().get(name)
    except UnknownLabError as exc:
        print(str(exc))
        return None


def _learning_route_or_none(name: str) -> Optional[LearningRoute]:
    try:
        return resolve_learning_route(name)
    except UnknownLearningRouteError as exc:
        print(str(exc))
        return None


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _registry():
    return create_default_registry(_project_root())


def _runner() -> DockerComposeRunner:
    return DockerComposeRunner(_project_root())


def _sql_client(lab: LabDefinition) -> GreenplumSqlClient:
    return GreenplumSqlClient(_project_root(), lab)


def _normalize_lesson_arg(value: str) -> str:
    return normalize_lesson_code(value)
