"""Front matter for Lesson 03: clickable TOC + teaching glossary at deck start."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from lesson03_glossary_catalog import front_glossary_slides

GLOSSARY_SLIDES: List[Dict[str, Any]] = front_glossary_slides()


def how_to_watch_slide() -> Dict[str, Any]:
    """First navigation contract: modes + what the large slide count means."""
    return {
        "anchor": "nav-guide",
        "kicker": "Навигация · обязательно",
        "title": "Как смотреть эту презентацию",
        "subtitle": (
            "В Google много слайдов = урок + справочник + порталы возврата. "
            "Не листать подряд. Выберите режим."
        ),
        "type": "cards",
        "cards": [
            [
                "Core 60 · ~30 LIVE",
                "Проблема → план → sel lite → TEMP → proof. "
                "Словарь и «Детали» — только по чипу «Термины».",
                "green",
            ],
            [
                "Core 90 · ~45 LIVE",
                "Core 60 + MCV/hist (смысл) + storage decision + 2 кейса "
                "(01 и 03 или 08). Остальное — homework.",
                "blue",
            ],
            [
                "Full · справочник",
                "Все этапы + 9 кейсов + Appendix. Порталы «Аа Словарь» / "
                "«→ Appendix» — служебные, не часть лекции.",
                "amber",
            ],
            [
                "Кнопки",
                "☰ Меню = оглавление. Аа Словарь = портал с ← Вернуться. "
                "Синие «Термины» = tip + разбор рядом.",
                "red",
            ],
        ],
        "jumps": [
            {"label": "→ Начать Core 60 (Проблема)", "anchor": "stage-problem"},
            {"label": "→ Словарь (по желанию)", "anchor": "glossary"},
            {"label": "→ Оглавление этапов", "anchor": "toc"},
        ],
    }


def toc_slides() -> List[Dict[str, Any]]:
    """TOC aligned with student journey: theory → practice → cases."""
    return [
        {
            "anchor": "toc",
            "kicker": "Оглавление · 1/2",
            "title": "Путь ученика",
            "subtitle": (
                "Сначала режим на слайде «Как смотреть». "
                "Дальше клик по этапу. Словарь live не листать."
            ),
            "type": "toc",
            "entries": [
                {
                    "num": "0",
                    "title": "Как смотреть (режимы)",
                    "hint": "Core 60 / 90 / Full · что не листать",
                    "anchor": "nav-guide",
                    "color": "red",
                },
                {
                    "num": "01",
                    "title": "Словарь (по клику)",
                    "hint": "Self-service · не обязателен в Core 60",
                    "anchor": "glossary",
                    "color": "green",
                },
                {
                    "num": "02",
                    "title": "Этап 1 · Проблема",
                    "hint": "Старт Core 60 / 90",
                    "anchor": "stage-problem",
                    "color": "red",
                },
                {
                    "num": "03",
                    "title": "Этап 2 · Как читать план",
                    "hint": "Motion · ORCA · детали по чипу",
                    "anchor": "stage-plan",
                    "color": "blue",
                },
                {
                    "num": "04",
                    "title": "Этап 3 · Статистика",
                    "hint": "sel · MCV · hist",
                    "anchor": "stage-stats",
                    "color": "amber",
                },
                {
                    "num": "05",
                    "title": "Этап 4–5 · Storage → Практика",
                    "hint": "Decision → TEMP → metrics",
                    "anchor": "stage-storage",
                    "color": "green",
                },
            ],
        },
        {
            "anchor": "toc-2",
            "kicker": "Оглавление · 2/2",
            "title": "Кейсы · закрепление · Appendix",
            "subtitle": (
                "Core 60: кейсы SKIP. Core 90: два кейса. "
                "Full: все 01–09 + Appendix."
            ),
            "type": "toc",
            "entries": [
                {
                    "num": "06",
                    "title": "Этап 5 · Практика OLAP",
                    "hint": "TEMP · after plan · proof",
                    "anchor": "stage-practice",
                    "color": "blue",
                },
                {
                    "num": "07",
                    "title": "Этап 6 · Кейсы",
                    "hint": "01–09 · live только выбранные",
                    "anchor": "cases",
                    "color": "red",
                },
                {
                    "num": "08",
                    "title": "Кейс 01 · ORCA CE",
                    "hint": "Рекомендуемый live в Core 90",
                    "anchor": "case-orca-ce",
                    "color": "amber",
                },
                {
                    "num": "09",
                    "title": "Этап 7 · Итог",
                    "hint": "Checklist · маршруты",
                    "anchor": "stage-wrap",
                    "color": "green",
                },
                {
                    "num": "10",
                    "title": "Appendix",
                    "hint": "Справочник · не для Core 60",
                    "anchor": "appendix",
                    "color": "amber",
                },
                {
                    "num": "↑",
                    "title": "Как смотреть / оглавление",
                    "hint": "Режимы · этапы 1–5",
                    "anchor": "nav-guide",
                    "color": "green",
                },
            ],
        },
    ]


def tag_section_anchors(slides: List[Dict[str, Any]]) -> None:
    return


def prepend_front_matter(body_slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Title → how-to-watch → TOC → Glossary → rest of body."""
    guide = how_to_watch_slide()
    if not body_slides:
        return [guide, *toc_slides(), *GLOSSARY_SLIDES]
    title, *rest = body_slides
    title = dict(title)
    title["anchor"] = "title"
    title["subtitle"] = (
        "Сначала «Как смотреть» (Core 60 / 90 / Full). "
        "Большое число слайдов ≠ всё читать вслух."
    )
    if title.get("type") == "cards" and title.get("cards"):
        cards = []
        for name, body, color in title["cards"]:
            if name in {"Не цель", "Сначала", "Путь"}:
                cards.append(
                    [
                        "Путь",
                        "Режим → проблема → план → stats → TEMP → proof. "
                        "Словарь/кейсы — по режиму.",
                        "amber",
                    ]
                )
            else:
                cards.append([name, body, color])
        title["cards"] = cards
    tag_section_anchors(rest)
    return [title, guide, *toc_slides(), *GLOSSARY_SLIDES, *rest]


APPENDIX_POINTER = {
    "anchor": "appendix-map",
    "kicker": "Appendix · старт",
    "title": "Справочник (не для 60‑мин lite)",
    "subtitle": "Словарь — в начале и рядом с теорией. Сюда — deep reference.",
    "type": "cards",
    "cards": [
        ["Словарь", "Полный в начале + блоки «Детали» у Этапов 2–3.", "green"],
        ["Термины", "Чип на слайде: наведение = tip, клик = разбор.", "blue"],
        ["Здесь", "History ORCA, формулы CE, ON COMMIT, полные EXPLAIN.", "amber"],
        ["Вернуться", "Портал «→ Appendix» / «Аа Словарь» с ← Вернуться.", "green"],
    ],
    "jumps": [
        {"label": "→ Формулы CE (Legacy vs ORCA)", "anchor": "appendix-ce-summary"},
        {"label": "→ Spill / pgsql_tmp", "anchor": "appendix-spill"},
        {"label": "→ История двух оптимизаторов", "anchor": "appendix-history"},
    ],
}
