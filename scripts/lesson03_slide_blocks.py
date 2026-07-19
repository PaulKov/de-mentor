"""Reusable section / case title slides for Lesson 03 deck structure."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def stage_gate(
    *,
    anchor: str,
    num: str,
    title: str,
    subtitle: str,
    cards: List[List[str]],
) -> Dict[str, Any]:
    """Full-bleed stage intro: student sees where they are in the journey."""
    return {
        "anchor": anchor,
        "kicker": f"Этап {num}",
        "title": title,
        "subtitle": subtitle,
        "type": "cards",
        "cards": cards,
    }


def case_title(
    *,
    anchor: str,
    num: str,
    title: str,
    subtitle: str,
    problem: str,
    plan_signal: str,
    fix: str,
    lab: str,
) -> Dict[str, Any]:
    """Dedicated title slide before each optimization case."""
    return {
        "anchor": anchor,
        "kicker": f"Кейс {num}",
        "title": title,
        "subtitle": subtitle,
        "type": "cards",
        "cards": [
            ["Проблема", problem, "red"],
            ["Сигнал в плане", plan_signal, "amber"],
            ["Как чинить", fix, "green"],
            ["Стенд", lab, "blue"],
        ],
    }


def retitle(spec: Dict[str, Any], *, kicker: str, title: Optional[str] = None, subtitle: Optional[str] = None) -> Dict[str, Any]:
    out = dict(spec)
    out["kicker"] = kicker
    if title is not None:
        out["title"] = title
    if subtitle is not None:
        out["subtitle"] = subtitle
    return out
