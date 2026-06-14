"""Typed Academy Experience session payload model."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mentor_lab.control_plane import ControlPlaneBuilder
from mentor_lab.session_contract import (
    CONTRACT_VERSION,
    PORTAL_APP_PATH,
    PORTAL_FRAMEWORK,
    PORTAL_REPOSITORY,
)


ACADEMY_VERSION = "Academy Experience v5"


@dataclass(frozen=True)
class SessionStage:
    """A visible lesson stage for the live portal and mentor timeline."""

    code: str
    title: str
    timebox: str
    mentor_focus: str
    student_action: str
    command: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "code": self.code,
            "title": self.title,
            "timebox": self.timebox,
            "mentor_focus": self.mentor_focus,
            "student_action": self.student_action,
            "command": self.command,
        }


@dataclass(frozen=True)
class SkillNode:
    """A single observable skill in the lesson skill graph."""

    code: str
    title: str
    level: str
    evidence: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "code": self.code,
            "title": self.title,
            "level": self.level,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class SessionEvent:
    """A timestamped event recorded during the lesson."""

    event_type: str
    note: str
    created_at: str

    @classmethod
    def create(cls, event_type: str, note: str) -> "SessionEvent":
        return cls(
            event_type=event_type,
            note=note,
            created_at=_timestamp(),
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "event_type": self.event_type,
            "note": self.note,
            "created_at": self.created_at,
        }


@dataclass
class AcademySession:
    """Serializable state shared by CLI artifacts and the Nuxt portal."""

    lab_name: str
    student_name: str
    created_at: str
    stages: List[SessionStage]
    skill_graph: List[SkillNode]
    commands: List[str]
    events: List[SessionEvent] = field(default_factory=list)
    current_stage_code: str = "environment"
    control_plane: Dict[str, Any] = field(default_factory=dict)

    @property
    def current_stage(self) -> SessionStage:
        for stage in self.stages:
            if stage.code == self.current_stage_code:
                return stage
        return self.stages[0]

    def to_dict(self) -> Dict[str, Any]:
        dev_command = (
            f"MENTOR_LAB_SESSION=/absolute/path/to/session.json "
            "npm run dev"
        )
        return {
            "contract_version": CONTRACT_VERSION,
            "academy_version": ACADEMY_VERSION,
            "lab_name": self.lab_name,
            "student_name": self.student_name,
            "created_at": self.created_at,
            "current_stage": self.current_stage.to_dict(),
            "stages": [stage.to_dict() for stage in self.stages],
            "skill_graph": [node.to_dict() for node in self.skill_graph],
            "commands": self.commands,
            "events": [event.to_dict() for event in self.events],
            "control_plane": self.control_plane
            or ControlPlaneBuilder().build(self.lab_name).to_dict(),
            "portal": {
                "framework": PORTAL_FRAMEWORK,
                "repository": PORTAL_REPOSITORY,
                "app_path": PORTAL_APP_PATH,
                "session_env": "MENTOR_LAB_SESSION",
                "dev_command": dev_command,
            },
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "AcademySession":
        return cls(
            lab_name=payload["lab_name"],
            student_name=payload["student_name"],
            created_at=payload["created_at"],
            current_stage_code=payload["current_stage"]["code"],
            stages=[
                SessionStage(
                    code=item["code"],
                    title=item["title"],
                    timebox=item["timebox"],
                    mentor_focus=item["mentor_focus"],
                    student_action=item["student_action"],
                    command=item["command"],
                )
                for item in payload["stages"]
            ],
            skill_graph=[
                SkillNode(
                    code=item["code"],
                    title=item["title"],
                    level=item["level"],
                    evidence=item["evidence"],
                )
                for item in payload["skill_graph"]
            ],
            commands=list(payload["commands"]),
            events=[
                SessionEvent(
                    event_type=item["event_type"],
                    note=item["note"],
                    created_at=item["created_at"],
                )
                for item in payload.get("events", [])
            ],
            control_plane=dict(payload.get("control_plane", {})),
        )


def _timestamp() -> str:
    return datetime.now().replace(microsecond=0).isoformat()
