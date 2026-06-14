"""Release manifest loading for lesson productization."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mentor_lab.lesson_routes import resolve_learning_route


@dataclass(frozen=True)
class LessonReleaseManifest:
    """Declarative release contract for one lesson route."""

    source_path: Path
    route: str
    lesson_code: str
    physical_lab: str
    title: str
    deck_path: str
    google_slides_url: str
    expected_owner_email: str
    expected_slide_count: int
    drive_folder: str
    portal_repo: str
    docs: tuple[str, ...]
    runbooks: tuple[str, ...]
    sql_examples: tuple[str, ...]
    student_handoff: tuple[str, ...]
    safe_cli_commands: tuple[str, ...]

    @property
    def all_local_artifacts(self) -> tuple[str, ...]:
        return (
            self.deck_path,
            *self.docs,
            *self.runbooks,
            *self.sql_examples,
        )


class LessonReleaseManifestLoader:
    """Loads simple lesson YAML manifests without external dependencies."""

    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root

    def load(self, route_name: str) -> LessonReleaseManifest:
        route = resolve_learning_route(route_name)
        source_path = self._project_root / route.docs_root / "lesson.yaml"
        if not source_path.exists():
            raise FileNotFoundError(f"Lesson release manifest not found: {source_path}")
        payload = _parse_simple_yaml(source_path.read_text(encoding="utf-8"))
        return LessonReleaseManifest(
            source_path=source_path,
            route=_required(payload, "route"),
            lesson_code=_required(payload, "lesson_code"),
            physical_lab=_required(payload, "physical_lab"),
            title=_required(payload, "title"),
            deck_path=_required(payload, "deck_path"),
            google_slides_url=_required(payload, "google_slides_url"),
            expected_owner_email=_required(payload, "expected_owner_email"),
            expected_slide_count=int(_required(payload, "expected_slide_count")),
            drive_folder=_required(payload, "drive_folder"),
            portal_repo=_required(payload, "portal_repo"),
            docs=_required_list(payload, "docs"),
            runbooks=_required_list(payload, "runbooks"),
            sql_examples=_required_list(payload, "sql_examples"),
            student_handoff=_required_list(payload, "student_handoff"),
            safe_cli_commands=_required_list(payload, "safe_cli_commands"),
        )


def _parse_simple_yaml(content: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                raise ValueError(f"List item without a key: {line}")
            parsed[current_list_key].append(_clean_value(line[4:]))
            continue
        if line.startswith(" "):
            raise ValueError(f"Unsupported nested YAML line: {line}")
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Expected key: value line, got: {line}")
        key = key.strip()
        value = value.strip()
        if value:
            parsed[key] = _clean_value(value)
            current_list_key = None
        else:
            parsed[key] = []
            current_list_key = key
    return parsed


def _clean_value(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in "'\"":
        return stripped[1:-1]
    return stripped


def _required(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Missing required manifest field: {key}")
    return value


def _required_list(payload: dict[str, Any], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Missing required manifest list: {key}")
    if not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"Manifest list contains empty values: {key}")
    return tuple(value)
