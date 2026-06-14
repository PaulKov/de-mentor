"""Validation for the Academy Session JSON contract."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List


CONTRACT_VERSION = "academy-session/v1"
CONTRACT_SCHEMA_PATH = Path("contracts/academy-session/v1/session.schema.json")
PORTAL_REPOSITORY = "https://github.com/PaulKov/de-mentor-portal"
PORTAL_APP_PATH = "de-mentor-portal"
PORTAL_FRAMEWORK = "Vue 3 + Nuxt 3 + Vite"


@dataclass(frozen=True)
class ContractValidationResult:
    """Result of validating a session payload."""

    errors: List[str]

    @property
    def valid(self) -> bool:
        return not self.errors

    def render(self) -> str:
        if self.valid:
            return f"Session contract valid: {CONTRACT_VERSION}\n"
        lines = [f"Session contract invalid: {CONTRACT_VERSION}"]
        lines.extend(f"- {error}" for error in self.errors)
        return "\n".join(lines) + "\n"


class SessionContractValidator:
    """Small dependency-free validator for `academy-session/v1`.

    The repository publishes a JSON Schema for humans and external tools, while
    this validator keeps the CLI zero-dependency for students.
    """

    def validate_file(self, path: Path) -> ContractValidationResult:
        session_path = path / "session.json" if path.is_dir() else path
        if not session_path.exists():
            return ContractValidationResult([f"session file does not exist: {session_path}"])
        try:
            payload = json.loads(session_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return ContractValidationResult([f"invalid JSON: {exc}"])
        return self.validate_payload(payload)

    def validate_payload(self, payload: Dict[str, Any]) -> ContractValidationResult:
        errors: List[str] = []
        _require_keys(
            payload,
            [
                "contract_version",
                "academy_version",
                "lab_name",
                "student_name",
                "created_at",
                "current_stage",
                "stages",
                "skill_graph",
                "commands",
                "events",
                "portal",
            ],
            "session",
            errors,
        )
        if payload.get("contract_version") != CONTRACT_VERSION:
            errors.append(
                f"contract_version must be {CONTRACT_VERSION}, got {payload.get('contract_version')!r}"
            )

        stages = payload.get("stages")
        if not isinstance(stages, list) or not stages:
            errors.append("stages must be a non-empty list")
        else:
            for index, stage in enumerate(stages):
                _validate_stage(stage, f"stages[{index}]", errors)

        current_stage = payload.get("current_stage")
        _validate_stage(current_stage, "current_stage", errors)
        if isinstance(current_stage, dict) and isinstance(stages, list):
            stage_codes = {
                stage.get("code")
                for stage in stages
                if isinstance(stage, dict)
            }
            if current_stage.get("code") not in stage_codes:
                errors.append("current_stage.code must exist in stages[].code")

        _validate_string_list(payload.get("commands"), "commands", errors)
        _validate_skill_graph(payload.get("skill_graph"), errors)
        _validate_events(payload.get("events"), errors)
        if "control_plane" in payload:
            _validate_control_plane(payload.get("control_plane"), errors)
        _validate_portal(payload.get("portal"), errors)
        return ContractValidationResult(errors)


def _require_keys(
    payload: Any,
    keys: Iterable[str],
    label: str,
    errors: List[str],
) -> None:
    if not isinstance(payload, dict):
        errors.append(f"{label} must be an object")
        return
    for key in keys:
        if key not in payload:
            errors.append(f"{label}.{key} is required")


def _validate_stage(payload: Any, label: str, errors: List[str]) -> None:
    _require_keys(
        payload,
        ["code", "title", "timebox", "mentor_focus", "student_action", "command"],
        label,
        errors,
    )
    if not isinstance(payload, dict):
        return
    for key in ["code", "title", "timebox", "mentor_focus", "student_action", "command"]:
        if key in payload and not isinstance(payload[key], str):
            errors.append(f"{label}.{key} must be a string")


def _validate_string_list(payload: Any, label: str, errors: List[str]) -> None:
    if not isinstance(payload, list):
        errors.append(f"{label} must be a list")
        return
    for index, item in enumerate(payload):
        if not isinstance(item, str):
            errors.append(f"{label}[{index}] must be a string")


def _validate_skill_graph(payload: Any, errors: List[str]) -> None:
    if not isinstance(payload, list):
        errors.append("skill_graph must be a list")
        return
    for index, item in enumerate(payload):
        _require_keys(item, ["code", "title", "level", "evidence"], f"skill_graph[{index}]", errors)


def _validate_events(payload: Any, errors: List[str]) -> None:
    if not isinstance(payload, list):
        errors.append("events must be a list")
        return
    for index, item in enumerate(payload):
        _require_keys(item, ["event_type", "note", "created_at"], f"events[{index}]", errors)


def _validate_portal(payload: Any, errors: List[str]) -> None:
    _require_keys(
        payload,
        ["framework", "repository", "app_path", "session_env", "dev_command"],
        "portal",
        errors,
    )
    if not isinstance(payload, dict):
        return
    expected = {
        "framework": PORTAL_FRAMEWORK,
        "repository": PORTAL_REPOSITORY,
        "app_path": PORTAL_APP_PATH,
        "session_env": "MENTOR_LAB_SESSION",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"portal.{key} must be {value!r}")


def _validate_control_plane(payload: Any, errors: List[str]) -> None:
    _require_keys(
        payload,
        [
            "version",
            "mentor_mode",
            "student_mode",
            "portal_actions",
            "artifacts",
            "next_lesson",
        ],
        "control_plane",
        errors,
    )
    if not isinstance(payload, dict):
        return
    if payload.get("version") != "academy-control-plane/v1":
        errors.append("control_plane.version must be 'academy-control-plane/v1'")
    mentor_mode = payload.get("mentor_mode")
    _require_keys(
        mentor_mode,
        ["default_route", "runbook_commands", "slide_deck", "stage_guides"],
        "control_plane.mentor_mode",
        errors,
    )
    if isinstance(mentor_mode, dict):
        _validate_string_list(
            mentor_mode.get("runbook_commands"),
            "control_plane.mentor_mode.runbook_commands",
            errors,
        )
        stage_guides = mentor_mode.get("stage_guides")
        if not isinstance(stage_guides, list) or not stage_guides:
            errors.append("control_plane.mentor_mode.stage_guides must be a non-empty list")
        elif isinstance(stage_guides, list):
            for index, guide in enumerate(stage_guides):
                _require_keys(
                    guide,
                    [
                        "stage_code",
                        "slides",
                        "mentor_script",
                        "show_commands",
                        "question",
                        "expected_answer",
                        "verification",
                        "workbook_ref",
                        "homework_ref",
                    ],
                    f"control_plane.mentor_mode.stage_guides[{index}]",
                    errors,
                )
                if isinstance(guide, dict):
                    _validate_string_list(
                        guide.get("show_commands"),
                        f"control_plane.mentor_mode.stage_guides[{index}].show_commands",
                        errors,
                    )

    student_mode = payload.get("student_mode")
    _require_keys(
        student_mode,
        ["prep_runbook", "workbook", "homework", "self_check_commands"],
        "control_plane.student_mode",
        errors,
    )
    if isinstance(student_mode, dict):
        _validate_string_list(
            student_mode.get("self_check_commands"),
            "control_plane.student_mode.self_check_commands",
            errors,
        )
    _require_keys(
        payload.get("portal_actions"),
        ["start_command", "export_command", "open_command"],
        "control_plane.portal_actions",
        errors,
    )
    if not isinstance(payload.get("artifacts"), list):
        errors.append("control_plane.artifacts must be a list")
    _require_keys(
        payload.get("next_lesson"),
        ["code", "title", "path"],
        "control_plane.next_lesson",
        errors,
    )
