"""Glossary term catalog for Lesson 03 — single source for tips, anchors, slides.

Used by:
- front-matter full glossary (начало презентации);
- inline «теория → детали» blocks next to Stage 2/3;
- clickable term chips with hover tooltips.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


def _term(
    *,
    key: str,
    label: str,
    tip: str,
    front_anchor: str,
    title: str,
    subtitle: str,
    body: str = "",
    cards: Optional[List[List[str]]] = None,
    slide_type: str = "panel",
) -> Dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "tip": tip,
        "front_anchor": front_anchor,
        "title": title,
        "subtitle": subtitle,
        "body": body,
        "cards": cards,
        "type": slide_type,
    }


TERMS: Dict[str, Dict[str, Any]] = {
    "guc": _term(
        key="guc",
        label="GUC",
        tip="Параметр сервера (SHOW/SET). Пример: optimizer, statement_mem.",
        front_anchor="glossary",
        title="GUC — параметр конфигурации",
        subtitle="Grand Unified Configuration.",
        body=(
            "GUC — настройка сервера Greenplum/Postgres.\n"
            "Смотреть: SHOW name; менять в сессии: SET name = value.\n\n"
            "На уроке критичны:\n"
            "• optimizer = on|off  → GPORCA или Legacy\n"
            "• statement_mem      → память операторов (spill)\n\n"
            "Перед before/after всегда фиксируйте один и тот же набор GUC."
        ),
    ),
    "qd_qe": _term(
        key="qd_qe",
        label="QD / QE",
        tip="QD = master (план + координация). QE = процесс на сегменте.",
        front_anchor="glossary",
        title="QD и QE",
        subtitle="Кто строит план и кто исполняет slice.",
        body=(
            "QD (Query Dispatcher) — на master: парсит SQL, выбирает план, "
            "режет его на slices и собирает результат.\n\n"
            "QE (Query Executor) — на каждом сегменте: исполняет свой кусок плана.\n\n"
            "Между QE разных сегментов данные едут через Motion."
        ),
    ),
    "motion": _term(
        key="motion",
        label="Motion",
        tip="Пересылка строк по сети: Redistribute / Broadcast / Gather.",
        front_anchor="glossary-2",
        title="Motion — цена сети в MPP",
        subtitle="Три основных вида обмена строками.",
        body=(
            "Motion — оператор, который двигает строки между сегментами (или на master).\n\n"
            "• Redistribute — перетасовать по hash-ключу (дорого на широком потоке).\n"
            "• Broadcast — отправить копию маленькой таблицы всем сегментам.\n"
            "• Gather — собрать результат на QD/master.\n\n"
            "Цель тюнинга: делать Motion на уже узком наборе строк."
        ),
    ),
    "orca": _term(
        key="orca",
        label="ORCA / GPORCA",
        tip="Pivotal Optimizer (Cascades). GUC: optimizer=on.",
        front_anchor="glossary",
        title="GPORCA (ORCA)",
        subtitle="Современный cost-based optimizer Greenplum.",
        body=(
            "GPORCA — оптимизатор на базе Cascades/memo.\n"
            "Включается: SET optimizer = on;\n"
            "В EXPLAIN: Optimizer: Pivotal Optimizer (GPORCA).\n\n"
            "Обычно сильнее Legacy на star-join и сложных OLAP.\n"
            "Не аксиома «всегда быстрее» — сравнивайте shape и runtime."
        ),
    ),
    "selectivity": _term(
        key="selectivity",
        label="Selectivity",
        tip="Доля строк после фильтра (0…1). rows ≈ N · sel.",
        front_anchor="glossary-3",
        title="Selectivity — доля строк после фильтра",
        subtitle="Главное число, из которого планировщик получает rows ≈ N · sel.",
        body=(
            "Selectivity — доля строк после предиката (0 < sel ≤ 1).\n"
            "Оценка: rows_est ≈ N · sel.\n\n"
            "Пример: N=100 000, segment='enterprise', sel=0.31 → rows_est ≈ 31 000.\n\n"
            "От rows_est зависят join order, Nested Loop vs Hash, Broadcast vs Redistribute.\n"
            "Ошибка в sel → плохой план даже при свежем ANALYZE."
        ),
    ),
    "n_distinct": _term(
        key="n_distinct",
        label="n_distinct",
        tip="Сколько разных значений в колонке (NDV). База для sel ≈ 1/NDV.",
        front_anchor="glossary-4",
        title="n_distinct — сколько разных значений",
        subtitle="NDV (number of distinct values).",
        body=(
            "n_distinct в pg_stats — оценка NDV (числа различных значений).\n"
            "• > 0 — абсолютный NDV (segment ≈ 4)\n"
            "• < 0 — доля от строк (−1.0 ≈ почти уникально / PK)\n\n"
            "Равенство без MCV: sel ≈ 1 / NDV.\n"
            "Пример: region NDV=10, region='NW' вне MCV → sel≈0.10 → ~10k из 100k.\n\n"
            "GROUP BY: планировщик roughly считает «групп ≈ NDV»."
        ),
    ),
    "mcv": _term(
        key="mcv",
        label="MCV",
        tip="Most Common Values + частоты (MCF). Точнее равномерной оценки 1/NDV.",
        front_anchor="glossary-5",
        title="MCV: список самых частых значений",
        subtitle="Сначала смысл. Формулы — на advanced-слайде рядом.",
        body=(
            "Планировщик угадывает rows для WHERE segment = 'enterprise' —\n"
            "от этого зависят join и Motion.\n\n"
            "Грубо: «4 значения → по 25%». В жизни: enterprise ~31%, test ~6%.\n\n"
            "MCV = Most Common Values — самые частые значения колонки;\n"
            "рядом MCF — доля строк каждого значения.\n"
            "• значение из MCV → берём его реальную долю;\n"
            "• редкое вне MCV → делим остаток поровну.\n\n"
            "Устаревший/пустой MCV → врёт rows → NLJ вместо Hash, лишний Broadcast.\n"
            "Формулы — на следующем (advanced) слайде."
        ),
    ),
    "mcv_adv": _term(
        key="mcv_adv",
        label="MCV (формулы)",
        tip="most_common_vals/freqs в pg_stats; sel из MCF или хвоста.",
        front_anchor="glossary-5b",
        title="MCV: как читать pg_stats и считать sel",
        subtitle="Язык каталога и формулы.",
        body=(
            "pg_stats:\n"
            "  most_common_vals (MCV) · most_common_freqs (MCF), Σ freqs ≤ 1\n\n"
            "Стенд dim_customer.segment:\n"
            "  MCV ≈ {enterprise, mid, smb, test}\n"
            "  MCF ≈ {0.31, 0.31, 0.31, 0.06} · n_distinct=4 → hist=NULL\n\n"
            "∈ MCV:  segment='enterprise' → sel = 0.31  (не 1/4)\n"
            "∉ MCV и NDV > |MCV|:\n"
            "  sel ≈ (1 − Σ MCF) / (NDV − |MCV|)"
        ),
    ),
    "histogram": _term(
        key="histogram",
        label="Histogram",
        tip="Корзины равного числа строк; для range (BETWEEN, >, <).",
        front_anchor="glossary-7",
        title="Histogram: equi-depth корзины",
        subtitle="Смысл корзин до формул histfrac.",
        body=(
            "MCV: «сколько строк с точным значением?»\n"
            "Histogram: «сколько строк в диапазоне?» (amount > 50, BETWEEN …).\n\n"
            "Как строится:\n"
            "1) Сортируем значения колонки.\n"
            "2) Режем на равные кучи по числу строк (= корзины).\n"
            "3) Границы — точки разрезов.\n\n"
            "Пример: 100 строк, amount 1…100, 4 корзины.\n"
            "  границы ≈ 1 · 25 · 50 · 75 · 100\n"
            "  A: 1…25 (~25 строк)  B: 25…50  C: 50…75  D: 75…100\n\n"
            "amount > 50 ≈ правая половина → ~50% строк.\n"
            "Корзины равны по числу строк, не по ширине шкалы."
        ),
    ),
    "histogram_adv": _term(
        key="histogram_adv",
        label="Histogram (формулы)",
        tip="histogram_bounds, histfrac, связь с MCV в pg_stats.",
        front_anchor="glossary-8",
        title="Histogram: bounds, histfrac, связь с MCV",
        subtitle="Тот же смысл — в терминах pg_stats.",
        body=(
            "pg_stats.histogram_bounds — массив границ equi-depth корзин.\n"
            "Число границ ≈ default_statistics_target + 1 "
            "(target=100 → часто ≈101).\n\n"
            "Значения из MCV в histogram обычно не входят.\n\n"
            "Range → histfrac → selectivity → rows_est ≈ N · sel.\n\n"
            "Если NDV мал и всё в MCV — histogram_bounds = NULL "
            "(на стенде так у segment)."
        ),
    ),
    "star_join": _term(
        key="star_join",
        label="Star-join",
        tip="Fact в центре + dims по FK. Порядок join бьёт по Motion.",
        front_anchor="glossary-9",
        title="Star-join и snowflake",
        subtitle="Схемы «звезда» / «снежинка».",
        body=(
            "Fact — события/меры (продажи). Dimension — справочник (клиент, продукт).\n\n"
            "Star-join: fact в центре + несколько dim по FK.\n"
            "Snowflake: dim → sub-dim (ещё joins).\n\n"
            "В Greenplum порядок dims решает Broadcast/Redistribute cost — "
            "здесь ORCA обычно сильнее Legacy."
        ),
    ),
}


def term_chip(key: str, *, prefer_inline: bool = True) -> Dict[str, str]:
    """Chip descriptor for a slide's ``terms`` list."""
    term = TERMS[key]
    anchor = f"detail-{key}" if prefer_inline else term["front_anchor"]
    return {
        "key": key,
        "label": term["label"],
        "tip": term["tip"],
        "anchor": anchor,
    }


def detail_slide(key: str, *, context: str) -> Dict[str, Any]:
    """Clone term content as an inline detail slide next to theory."""
    term = TERMS[key]
    out: Dict[str, Any] = {
        "anchor": f"detail-{key}",
        "kicker": f"Детали · {context}",
        "title": term["title"],
        "subtitle": f"{term['subtitle']}  ·  «↗ В общий словарь» / «Аа Словарь».",
        "type": term["type"],
        "terms": [
            {
                "key": key,
                "label": f"↗ В общий словарь",
                "tip": term["tip"],
                "anchor": term["front_anchor"],
            }
        ],
    }
    if term["type"] == "panel":
        out["body"] = term["body"]
    else:
        out["cards"] = deepcopy(term["cards"] or [])
    return out


def front_glossary_slides() -> List[Dict[str, Any]]:
    """Full glossary at deck start (architecture + stats terms)."""
    return [
        {
            "anchor": "glossary",
            "kicker": "Словарь · 1/9",
            "title": "Архитектура исполнения запроса",
            "subtitle": "Клик по термину на слайдах урока → сюда или в локальные «Детали».",
            "type": "cards",
            "cards": [
                ["GUC", TERMS["guc"]["tip"], "green"],
                ["QD / QE", TERMS["qd_qe"]["tip"], "blue"],
                ["Motion", TERMS["motion"]["tip"], "amber"],
                ["ORCA / Legacy", TERMS["orca"]["tip"] + " Legacy: optimizer=off.", "green"],
            ],
            "terms": [
                term_chip("guc", prefer_inline=False),
                term_chip("qd_qe", prefer_inline=False),
                term_chip("motion", prefer_inline=False),
                term_chip("orca", prefer_inline=False),
            ],
        },
        {
            "anchor": "glossary-2",
            "kicker": "Словарь · 2/9",
            "title": "Motion и физическое хранение",
            "subtitle": "Motion двигает строки по сети. Storage решает IO scan.",
            "type": "cards",
            "cards": [
                ["Motion", TERMS["motion"]["tip"], "green"],
                [
                    "AO / AOCO",
                    "Append-Only row / column. AOCO читает нужные колонки.",
                    "blue",
                ],
                [
                    "Heap / DXL",
                    "Heap — 8KB pages. DXL — IR между ORCA и executor.",
                    "amber",
                ],
                [
                    "Spill",
                    "Нехватка statement_mem → файлы pgsql_tmp на сегменте.",
                    "red",
                ],
            ],
            "terms": [term_chip("motion", prefer_inline=False)],
        },
        _front_from_term("selectivity", "3/9"),
        _front_from_term("n_distinct", "4/9"),
        _front_from_term("mcv", "5/9 · смысл"),
        _front_from_term("mcv_adv", "6/9 · формулы"),
        _front_from_term("histogram", "7/9 · смысл"),
        _front_from_term("histogram_adv", "8/9 · формулы"),
        _front_from_term("star_join", "9/9 · смысл"),
    ]


# Keys that also have inline «теория → детали» duplicates in the core journey.
_INLINE_DETAIL_KEYS = frozenset(
    {
        "qd_qe",
        "motion",
        "orca",
        "guc",
        "selectivity",
        "n_distinct",
        "mcv",
        "mcv_adv",
        "histogram",
        "histogram_adv",
    }
)


def _front_from_term(key: str, num: str) -> Dict[str, Any]:
    term = TERMS[key]
    terms: List[Dict[str, str]] = [
        {
            "key": key,
            "label": term["label"],
            "tip": term["tip"],
            "anchor": term["front_anchor"],
        }
    ]
    if key in _INLINE_DETAIL_KEYS:
        terms.append(
            {
                "key": key,
                "label": "↗ У теории",
                "tip": "Тот же разбор рядом с этапом плана/статистики.",
                "anchor": f"detail-{key}",
            }
        )
    return {
        "anchor": term["front_anchor"],
        "kicker": f"Словарь · {num}",
        "title": term["title"],
        "subtitle": term["subtitle"],
        "type": "panel",
        "body": term["body"],
        "terms": terms,
    }


def plan_inline_details() -> List[Dict[str, Any]]:
    """Детали рядом с Этапом 2 (чтение плана)."""
    return [
        {
            "kicker": "План · Словарь рядом",
            "title": "Термины плана — сначала смысл",
            "subtitle": "Дальше — короткие карточки-детали. Наведите на чип термина на соседних слайдах.",
            "type": "cards",
            "cards": [
                ["QD / QE", TERMS["qd_qe"]["tip"], "green"],
                ["Motion", TERMS["motion"]["tip"], "blue"],
                ["ORCA", TERMS["orca"]["tip"], "amber"],
                ["GUC", TERMS["guc"]["tip"], "red"],
            ],
            "terms": [
                term_chip("qd_qe"),
                term_chip("motion"),
                term_chip("orca"),
                term_chip("guc"),
            ],
        },
        detail_slide("qd_qe", context="план"),
        detail_slide("motion", context="план"),
        detail_slide("orca", context="план"),
        detail_slide("guc", context="план"),
    ]


def stats_inline_details_after_map() -> List[Dict[str, Any]]:
    """Selectivity + n_distinct сразу после карты статистики."""
    return [
        {
            "kicker": "Статистика · Словарь рядом",
            "title": "Сначала термины, потом формулы урока",
            "subtitle": "Чипы на слайдах: наведение = коротко, клик = этот разбор.",
            "type": "cards",
            "cards": [
                ["Selectivity", TERMS["selectivity"]["tip"], "green"],
                ["n_distinct", TERMS["n_distinct"]["tip"], "blue"],
                ["MCV", TERMS["mcv"]["tip"], "amber"],
                ["Histogram", TERMS["histogram"]["tip"], "red"],
            ],
            "terms": [
                term_chip("selectivity"),
                term_chip("n_distinct"),
                term_chip("mcv"),
                term_chip("histogram"),
            ],
        },
        detail_slide("selectivity", context="статистика"),
        detail_slide("n_distinct", context="статистика"),
    ]


def stats_inline_details_after_equality() -> List[Dict[str, Any]]:
    return [
        detail_slide("mcv", context="equality"),
        detail_slide("mcv_adv", context="equality"),
    ]


def stats_inline_details_after_range() -> List[Dict[str, Any]]:
    return [
        detail_slide("histogram", context="range"),
        detail_slide("histogram_adv", context="range"),
    ]
