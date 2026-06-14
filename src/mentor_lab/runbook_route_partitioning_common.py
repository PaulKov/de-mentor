"""Shared factory helpers for Lesson 02 runbooks."""

from mentor_lab.lesson_routes import LESSON_02_ROUTE


def lesson02_runbook_paths() -> dict[str, object]:
    """Return common paths injected into every Lesson 02 runbook."""

    return {
        "deck_path": LESSON_02_ROUTE.deck_path,
        "workbook_path": LESSON_02_ROUTE.workbook_path,
        "homework_path": LESSON_02_ROUTE.homework_path,
        "sql_examples": list(LESSON_02_ROUTE.sql_examples),
    }
