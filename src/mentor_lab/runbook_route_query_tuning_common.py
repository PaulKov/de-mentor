"""Shared factory helpers for Lesson 03 runbooks."""

from mentor_lab.lesson_routes import LESSON_03_ROUTE


def lesson03_runbook_paths() -> dict[str, object]:
    """Return common paths injected into every Lesson 03 runbook."""

    return {
        "deck_path": LESSON_03_ROUTE.deck_path,
        "google_slides_url": LESSON_03_ROUTE.google_slides_url,
        "workbook_path": LESSON_03_ROUTE.workbook_path,
        "homework_path": LESSON_03_ROUTE.homework_path,
        "sql_examples": list(LESSON_03_ROUTE.sql_examples),
    }
