#!/usr/bin/env python3
"""Build Lesson 03 PPTX and regenerate declarative slide sources.

Usage:
    python3 scripts/build_lesson03_pptx.py
"""

from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Pt


ROOT = Path(__file__).resolve().parents[1]
DECK_DIR = ROOT / "decks" / "greenplum-query-tuning-theory"
SLIDES_DIR = DECK_DIR / "slides"
PPTX_PATH = ROOT / "artifacts" / "greenplum-query-tuning-theory.pptx"

W, H = 12192000, 6858000  # 13.333" x 7.5" in EMUs
C = {
    "bg": RGBColor(0xF7, 0xF7, 0xF4),
    "panel": RGBColor(0xFF, 0xFF, 0xFF),
    "text": RGBColor(0x20, 0x21, 0x23),
    "muted": RGBColor(0x6E, 0x6E, 0x68),
    "green": RGBColor(0x10, 0xA3, 0x7F),
    "blue": RGBColor(0x2F, 0x6F, 0xED),
    "amber": RGBColor(0xB7, 0x79, 0x1F),
    "red": RGBColor(0xB4, 0x23, 0x18),
    "line": RGBColor(0xD8, 0xD7, 0xD0),
}
HEX = {
    "green": "#10A37F",
    "blue": "#2F6FED",
    "amber": "#B7791F",
    "red": "#B42318",
}


def inch(value: float) -> int:
    return int(value * 914400)


SLIDES = [
    {
        "kicker": "Урок 03",
        "title": "Декомпозиция и тюнинг тяжёлых запросов в MPP",
        "subtitle": "Greenplum 6.25: планы, GPORCA vs Legacy, статистика, storage, TEMP.",
        "type": "cards",
        "cards": [
            ["Цель", "Понять оптимизацию Greenplum по косточкам и доказывать rewrite планом.", "green"],
            ["Стенд", "labs/greenplum-625 (GP 6.25.3): seed, check, ORCA/Legacy demo.", "blue"],
            ["Итог", "Ученик выбирает optimizer и physical stage осознанно, не по привычке.", "green"],
        ],
    },
    {
        "kicker": "Lab",
        "title": "Self-service стенд Урока 03 — Greenplum 6.25",
        "subtitle": "Отдельный lab greenplum-625, чтобы демо ORCA/Legacy было воспроизводимо.",
        "type": "code",
        "code": (
            "python3 mentor-lab.py up greenplum-625\n"
            "python3 mentor-lab.py check greenplum-625\n"
            "python3 mentor-lab.py seed greenplum-625 --profile lesson03\n"
            "python3 mentor-lab.py psql greenplum-625\n\n"
            "# x86_64:\n"
            "GREENPLUM_625_IMAGE=andruche/greenplum:6.25.3-slim-amd64 \\\n"
            "  python3 mentor-lab.py up greenplum-625"
        ),
    },
    {
        "kicker": "Mental model",
        "title": "Тяжёлый OLAP = данные + сеть + оценки + выбор оптимизатора",
        "subtitle": "SQL — вход; план — контракт на CPU, IO и interconnect.",
        "type": "two",
        "left": [
            "Что дорого",
            "Лишний Motion, плохой join order, stale stats, spill, широкая projection.",
            "red",
        ],
        "right": [
            "Рычаги",
            "optimizer on/off, ANALYZE, TEMP stages, DISTRIBUTED BY, Heap/AO/AOCO.",
            "green",
        ],
    },
    {
        "kicker": "Pipeline",
        "title": "Как Greenplum оптимизирует запрос: стадии",
        "subtitle": "QD строит план; QE исполняют slices. Ошибка на стадии optimize = дорогая сеть.",
        "type": "flow",
        "flow": [
            ["Parse", "SQL → parse tree.", "green"],
            ["Rewrite", "views/rules → query tree.", "blue"],
            ["Optimize", "Legacy или GPORCA → plan.", "amber"],
            ["Dispatch", "QD → gangs/slices.", "green"],
            ["Execute", "QE + Motion + gather.", "blue"],
        ],
    },
    {
        "kicker": "Optimize stage",
        "title": "Стадия Optimize — развилка Legacy vs GPORCA",
        "subtitle": "GUC optimizer управляет, кто строит распределённый plan.",
        "type": "code",
        "code": (
            "SHOW optimizer;              -- on | off\n"
            "SET optimizer = on;           -- GPORCA (Pivotal Optimizer)\n"
            "SET optimizer = off;          -- legacy Postgres-based planner\n\n"
            "-- В EXPLAIN ищите маркер оптимизатора:\n"
            "-- Settings: ... optimizer=on\n"
            "-- Optimizer status: PQO version ..."
        ),
    },
    {
        "kicker": "Legacy",
        "title": "Legacy Postgres planner: как думает",
        "subtitle": "Динамическое программирование / жадные эвристики вокруг path trees PostgreSQL + GP Motion hooks.",
        "type": "cards",
        "cards": [
            ["Корни", "path/joinpath, costsize, selfuncs + cdbpath Motion.", "green"],
            ["Сильная сторона", "Простые/средние запросы, предсказуемый fallback.", "blue"],
            ["Слабость", "Взрыв пространства при многих joins; слабее глобальный reorder.", "amber"],
            ["Практика", "Часто хорош на 2–3 joins и локальных agg.", "green"],
        ],
    },
    {
        "kicker": "GPORCA",
        "title": "GPORCA: memo, transformations, cost-based search",
        "subtitle": "Cascades-style optimizer: исследование эквивалентных планов в memo-структуре.",
        "type": "cards",
        "cards": [
            ["Memo", "Groups альтернативных выражений одного logical result.", "green"],
            ["Xforms", "Join reorder, aggregate pull-up/push-down, distribution enforcers.", "blue"],
            ["Cost", "Учитывает Motion/distribution как first-class cost.", "amber"],
            ["Сильная сторона", "Сложные star/snowflake, много joins, CTE-heavy SQL.", "green"],
        ],
    },
    {
        "kicker": "Compare",
        "title": "Где ORCA обычно выигрывает, а где Legacy",
        "subtitle": "Не религия: измеряйте EXPLAIN/EXPLAIN ANALYZE на вашем workload.",
        "type": "two",
        "left": [
            "ORCA лучше",
            "Много joins, сложный star, partition-heavy, когда нужен глубокий reorder и distribution-aware cost.",
            "green",
        ],
        "right": [
            "Legacy лучше / безопаснее",
            "Простые запросы; ORCA fallback/features gaps; отладка «странного» ORCA plan; иногда ниже planning time.",
            "amber",
        ],
    },
    {
        "kicker": "Demo SQL",
        "title": "Демо на стенде: один SQL — два оптимизатора",
        "subtitle": "lesson03.v_star_join_orca_case специально перегружен joins.",
        "type": "code",
        "code": (
            "\\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql\n\n"
            "SET optimizer = on;\n"
            "EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case\n"
            "ORDER BY revenue DESC LIMIT 20;\n\n"
            "SET optimizer = off;\n"
            "EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case\n"
            "ORDER BY revenue DESC LIMIT 20;"
        ),
    },
    {
        "kicker": "ORCA+ / Legacy−",
        "title": "Кейс: ORCA эффективен, Legacy проседает",
        "subtitle": "Многоjoin star: Legacy залипает в плохом порядке → лишний Redistribute.",
        "type": "cards",
        "cards": [
            ["Симптом", "Большой Redistribute до фильтров/agg; странный join order.", "red"],
            ["ORCA", "Находит порядок с меньшей shuffle cost через memo search.", "green"],
            ["Evidence", "Сравнить Settings/Optimizer status и Motion bytes/rows.", "blue"],
            ["Не путать", "Выигрыш ORCA ≠ повод не делать TEMP/ANALYZE.", "amber"],
        ],
    },
    {
        "kicker": "Legacy+ / ORCA−",
        "title": "Кейс: Legacy достаточен, ORCA избыточен",
        "subtitle": "Простой aggregate по dimension: planning overhead ORCA не окупается.",
        "type": "code",
        "code": (
            "SET optimizer = off;\n"
            "EXPLAIN SELECT region, count(*)\n"
            "FROM lesson03.dim_customer\n"
            "GROUP BY region;\n\n"
            "-- Здесь оба плана близки; смотрите planning time\n"
            "-- и стабильность, а не «модный» optimizer=on."
        ),
    },
    {
        "kicker": "Pros/Cons",
        "title": "Плюсы и минусы: Legacy planner",
        "subtitle": "Честный trade-off для Senior review.",
        "type": "two",
        "left": [
            "Плюсы",
            "Проще ментальная модель; быстрый planning на простых SQL; зрелый fallback; легче объяснить path tree.",
            "green",
        ],
        "right": [
            "Минусы",
            "Слабее на many-join; меньше глобальных transform; чаще локально-оптимальный join order.",
            "red",
        ],
    },
    {
        "kicker": "Pros/Cons",
        "title": "Плюсы и минусы: GPORCA",
        "subtitle": "Мощный search space имеет цену.",
        "type": "two",
        "left": [
            "Плюсы",
            "Глубокий join reorder; distribution-aware costing; сильнее на сложном OLAP/CTE.",
            "green",
        ],
        "right": [
            "Минусы",
            "Дороже planning; feature gaps → fallback; сложнее debug; иногда неожиданный plan shape.",
            "red",
        ],
    },
    {
        "kicker": "Fallback",
        "title": "ORCA fallback и minidump — обязательная грамотность",
        "subtitle": "Если ORCA не может оптимизировать, Greenplum уходит в Legacy.",
        "type": "cards",
        "cards": [
            ["Признак", "В EXPLAIN: Optimizer status / fallback reason.", "amber"],
            ["GUC", "optimizer_minidump=onerror для диагностики.", "blue"],
            ["Практика", "Не «чините SQL вслепую» — сначала читайте reason.", "green"],
            ["Prod", "Фиксируйте optimizer setting в session/role policy.", "green"],
        ],
    },
    {
        "kicker": "Case",
        "title": "Сквозной case: месячный OLAP по продажам и клиентам",
        "subtitle": "Монолит для layered EXPLAIN + сравнения optimizer.",
        "type": "code",
        "code": (
            "-- lesson03.v_heavy_olap_monolith\n"
            "SELECT c.region, d.category,\n"
            "       sum(f.amount) AS revenue,\n"
            "       rank() OVER (PARTITION BY c.region ORDER BY sum(f.amount) DESC)\n"
            "FROM lesson03.fact_sales f\n"
            "JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id\n"
            "JOIN lesson03.dim_product  d ON d.product_id  = f.product_id\n"
            "WHERE f.sale_date >= DATE '2026-02-01'\n"
            "  AND f.sale_date <  DATE '2026-03-01'\n"
            "  AND c.segment <> 'test'\n"
            "GROUP BY c.region, d.category;"
        ),
    },
    {
        "kicker": "Decomposition",
        "title": "Декомпозиция: сужаем → соединяем → считаем → доказываем",
        "subtitle": "Каждый этап должен уменьшать cardinality или убирать Motion.",
        "type": "flow",
        "flow": [
            ["Filter", "Окно и anti-test.", "green"],
            ["Shape", "TEMP grain.", "blue"],
            ["Join", "Узкий set.", "amber"],
            ["Agg", "Локально где можно.", "green"],
            ["Prove", "EXPLAIN до/после.", "blue"],
        ],
    },
    {
        "kicker": "EXPLAIN",
        "title": "Сложный план: слои Senior readout",
        "subtitle": "0) Optimizer. 1) Motion. 2) Join order. 3) Estimates. 4) Scan/storage.",
        "type": "cards",
        "cards": [
            ["Optimizer", "on/off, fallback, PQO version.", "green"],
            ["Motion", "Redistribute/Broadcast/Gather и ключ.", "blue"],
            ["Estimates", "rows vs actual; selectivity traps.", "amber"],
            ["Scan", "partition pruning / AOCO projection.", "green"],
        ],
    },
    {
        "kicker": "Estimates",
        "title": "Если rows врут — тюнинг SQL почти бессмысленен",
        "subtitle": "Плохая selectivity ломает и Legacy, и ORCA — но по-разному.",
        "type": "code",
        "code": (
            "EXPLAIN ANALYZE\n"
            "SELECT ...;\n\n"
            "-- Ищем:\n"
            "--   rows vs actual rows\n"
            "--   расхождение x10–x100 на join input\n"
            "-- Затем: pg_stats / ANALYZE, и только потом rewrite."
        ),
    },
    {
        "kicker": "Motion",
        "title": "Платим сетью: цель — перенести Motion на меньший set",
        "subtitle": "ORCA может выбрать другой enforcer; TEMP фиксирует ваш контракт.",
        "type": "two",
        "left": ["До", "Redistribute широкого fact; Broadcast раздутой dim.", "red"],
        "right": ["После", "TEMP окна + ANALYZE → меньше shuffle bytes.", "green"],
    },
    {
        "kicker": "Statistics",
        "title": "Оптимизатор питается MCV, histogram, n_distinct",
        "subtitle": "И Legacy, и ORCA читают pg_statistic; мусор на входе = мусор в plan.",
        "type": "cards",
        "cards": [
            ["n_distinct", "Кардинальность; ломается на skew.", "green"],
            ["MCV", "Частые значения для equality/IN.", "blue"],
            ["Histogram", "Range predicates.", "amber"],
            ["correlation", "Physical order vs logical.", "green"],
        ],
    },
    {
        "kicker": "Catalog",
        "title": "pg_stats → pg_statistic → слоты на диске",
        "subtitle": "Читаем статистику как plan: сначала human view, затем raw slots.",
        "type": "code",
        "code": (
            "SELECT attname, n_distinct, most_common_vals, histogram_bounds\n"
            "FROM pg_stats\n"
            "WHERE schemaname='lesson03' AND tablename='fact_sales';\n\n"
            "SELECT staattnum, stakind1, stanumbers1, stavalues1\n"
            "FROM pg_statistic\n"
            "WHERE starelid='lesson03.fact_sales'::regclass;"
        ),
    },
    {
        "kicker": "Engine",
        "title": "ANALYZE path в коде Greenplum 6.25",
        "subtitle": "sample → compute_stats → catalog heap tuple (возможно TOAST).",
        "type": "cards",
        "cards": [
            ["analyze.c", "Sampling и расчёт MCV/histogram.", "green"],
            ["selfuncs.c", "Selectivity functions для costing.", "blue"],
            ["pg_statistic", "Источник истины planner/ORCA metadata.", "amber"],
            ["QD/QE", "План на QD; данные и файлы на segments.", "green"],
        ],
    },
    {
        "kicker": "Storage",
        "title": "Heap / AO / AOCO на GP 6.25",
        "subtitle": "В 6.x синтаксис: appendonly=true (не appendoptimized).",
        "type": "cards",
        "cards": [
            ["Heap", "Dims, updates, staging.", "green"],
            ["AO row", "Bulk append row-oriented.", "blue"],
            ["AOCO", "Scan-heavy fact + projection.", "amber"],
            ["Не лечит", "Плохой optimizer choice / Motion / skew.", "red"],
        ],
    },
    {
        "kicker": "AOCO GP6",
        "title": "Физическая раскладка AOCO и типы данных",
        "subtitle": "Column files + compression; text/numeric varlena; широкий payload не читается зря.",
        "type": "code",
        "code": (
            "CREATE TABLE lesson03.fact_sales (...)\n"
            "WITH (\n"
            "  appendonly=true,\n"
            "  orientation=column,\n"
            "  compresstype=zstd,\n"
            "  compresslevel=1\n"
            ")\n"
            "DISTRIBUTED BY (customer_id)\n"
            "PARTITION BY RANGE (sale_date) (...);"
        ),
    },
    {
        "kicker": "TEMP",
        "title": "TEMP — physical stage с ANALYZE и distribution",
        "subtitle": "Фиксируем промежуточный контракт, который optimizer пересчитывает заново.",
        "type": "cards",
        "cards": [
            ["Зачем", "Новый grain + новый plan.", "green"],
            ["ANALYZE", "Обязателен после наполнения.", "blue"],
            ["Distribution", "Под следующий join key.", "amber"],
            ["Риск", "TEMP без фильтра увеличивает стоимость.", "red"],
        ],
    },
    {
        "kicker": "TEMP internals",
        "title": "pg_temp, файлы сегментов, spill ≠ TEMP TABLE",
        "subtitle": "Явная TEMP relation и hash/sort spill files — разные механизмы.",
        "type": "cards",
        "cards": [
            ["Namespace", "pg_temp_NNN session-local.", "green"],
            ["Файлы", "Temporary relfilenode на segments.", "blue"],
            ["Spill", "work_mem miss → temp files исполнителей.", "amber"],
            ["GPDB", "QD координирует, данные на QE.", "green"],
        ],
    },
    {
        "kicker": "Rewrite",
        "title": "Паттерн rewrite + проверка optimizer",
        "subtitle": "Before/after при фиксированном SET optimizer.",
        "type": "code",
        "code": (
            "SET optimizer = on;  -- зафиксировали\n"
            "CREATE TEMP TABLE tmp_sales_feb AS\n"
            "SELECT customer_id, product_id, amount\n"
            "FROM lesson03.fact_sales\n"
            "WHERE sale_date >= DATE '2026-02-01'\n"
            "  AND sale_date <  DATE '2026-03-01'\n"
            "DISTRIBUTED BY (customer_id);\n"
            "ANALYZE tmp_sales_feb;\n"
            "EXPLAIN ..."
        ),
    },
    {
        "kicker": "Simple path",
        "title": "60 минут на GP 6.25",
        "subtitle": "Case → optimizer → EXPLAIN → stats → TEMP → proof.",
        "type": "flow",
        "flow": [
            ["Up/seed", "greenplum-625", "green"],
            ["ORCA", "on vs off", "blue"],
            ["Plan", "слои", "amber"],
            ["TEMP", "rewrite", "green"],
            ["Proof", "evidence", "blue"],
        ],
    },
    {
        "kicker": "Deep route",
        "title": "Deep-dive Principal: internals end-to-end",
        "subtitle": "ORCA memo/xforms, pg_statistic slots, AOCO files, TEMP spill, design review.",
        "type": "cards",
        "cards": [
            ["ORCA", "fallback, minidump, join_order GUCs.", "green"],
            ["Stats files", "stakind/stavalues/TOAST.", "blue"],
            ["Storage", "appendonly column layout.", "amber"],
            ["RFC", "rewrite + optimizer policy.", "green"],
        ],
    },
    {
        "kicker": "Summary",
        "title": "Что унести с Урока 03",
        "subtitle": "Оптимизация Greenplum — это pipeline + два optimizer + физика данных.",
        "type": "cards",
        "cards": [
            ["Стадии", "parse → rewrite → optimize → dispatch → execute.", "green"],
            ["Выбор", "ORCA vs Legacy измерять, не верить.", "blue"],
            ["Физика", "stats/storage/TEMP — вход оптимизатора.", "amber"],
        ],
    },
]


def _set_run(paragraph, text, *, size=18, bold=False, color=None, font="Calibri"):
    paragraph.text = text
    paragraph.font.size = Pt(size)
    paragraph.font.bold = bold
    paragraph.font.name = font
    paragraph.font.color.rgb = color or C["text"]


def _add_rect(slide, x, y, w, h, fill):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    return shape


def _add_round(slide, x, y, w, h, fill):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = C["line"]
    shape.adjustments[0] = 0.08
    return shape


def _add_text(slide, x, y, w, h, text, *, size=18, bold=False, color=None, align=PP_ALIGN.LEFT, font="Calibri"):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    _set_run(p, text, size=size, bold=bold, color=color, font=font)
    return box


def _card(slide, x, y, w, h, title, body, color_key):
    _add_round(slide, x, y, w, h, C["panel"])
    _add_rect(slide, x + inch(0.2), y + inch(0.2), inch(0.45), inch(0.05), C[color_key])
    _add_text(slide, x + inch(0.22), y + inch(0.35), w - inch(0.4), inch(0.45), title, size=18, bold=True)
    _add_text(slide, x + inch(0.22), y + inch(0.85), w - inch(0.4), h - inch(1.05), body, size=13, color=C["muted"])


def _slide_base(prs, spec):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_rect(slide, 0, 0, W, H, C["bg"])
    _add_rect(slide, 0, 0, W, inch(0.02), C["line"])
    _add_rect(slide, 0, H - inch(0.02), W, inch(0.02), C["line"])
    _add_text(slide, inch(0.55), inch(0.35), inch(4.5), inch(0.3), spec["kicker"].upper(), size=13, bold=True, color=C["green"])
    _add_text(slide, inch(0.55), inch(0.7), inch(11.5), inch(1.1), spec["title"], size=30, bold=True, font="Calibri")
    if spec.get("subtitle"):
        _add_text(slide, inch(0.55), inch(1.85), inch(11.2), inch(0.6), spec["subtitle"], size=16, color=C["muted"])
    _add_text(slide, inch(11.0), inch(7.05), inch(1.8), inch(0.3), "Урок 03", size=11, color=C["muted"], align=PP_ALIGN.RIGHT)
    return slide


def render_slide(prs, spec):
    slide = _slide_base(prs, spec)
    if spec["type"] == "code":
        _add_round(slide, inch(0.7), inch(2.7), inch(11.9), inch(3.7), C["panel"])
        _add_text(slide, inch(0.95), inch(2.9), inch(2), inch(0.3), "SQL", size=12, bold=True, color=C["green"])
        _add_text(
            slide,
            inch(0.95),
            inch(3.25),
            inch(11.4),
            inch(2.9),
            spec["code"],
            size=12,
            font="Consolas",
        )
    elif spec["type"] == "two":
        left, right = spec["left"], spec["right"]
        _card(slide, inch(0.6), inch(2.7), inch(5.8), inch(3.5), left[0], left[1], left[2])
        _card(slide, inch(6.8), inch(2.7), inch(5.8), inch(3.5), right[0], right[1], right[2])
    elif spec["type"] == "flow":
        width = inch(2.05)
        gap = inch(0.25)
        y = inch(2.85)
        for index, (title, body, color_key) in enumerate(spec["flow"]):
            x = inch(0.55) + index * (width + gap)
            _card(slide, x, y, width, inch(3.3), title, body, color_key)
            if index < len(spec["flow"]) - 1:
                _add_rect(slide, x + width + inch(0.05), y + inch(1.5), gap - inch(0.1), inch(0.04), C["line"])
    else:
        positions = [
            (inch(0.6), inch(2.7)),
            (inch(6.8), inch(2.7)),
            (inch(0.6), inch(4.55)),
            (inch(6.8), inch(4.55)),
        ]
        for index, (title, body, color_key) in enumerate(spec["cards"]):
            x, y = positions[index]
            _card(slide, x, y, inch(5.8), inch(1.65), title, body, color_key)
    return slide


def write_shared_mjs() -> None:
    shared = (ROOT / "decks" / "greenplum-partitioning-theory" / "slides" / "shared.mjs").read_text(encoding="utf-8")
    shared = shared.replace("Урок 02", "Урок 03")
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    (SLIDES_DIR / "shared.mjs").write_text(shared, encoding="utf-8")


def write_content_mjs() -> None:
    def color_expr(key: str) -> str:
        return f"C.{key}"

    chunks = ["import { C } from \"./shared.mjs\";", "", "export const slides = ["]
    for spec in SLIDES:
        chunks.append("  {")
        chunks.append(f'    kicker: {json.dumps(spec["kicker"], ensure_ascii=False)},')
        chunks.append(f'    title: {json.dumps(spec["title"], ensure_ascii=False)},')
        chunks.append(f'    subtitle: {json.dumps(spec.get("subtitle", ""), ensure_ascii=False)},')
        chunks.append(f'    type: {json.dumps(spec["type"], ensure_ascii=False)},')
        if spec["type"] == "code":
            chunks.append(f'    code: {json.dumps(spec["code"], ensure_ascii=False)},')
        elif spec["type"] == "two":
            left = spec["left"]
            right = spec["right"]
            chunks.append(
                f'    left: [{json.dumps(left[0], ensure_ascii=False)}, {json.dumps(left[1], ensure_ascii=False)}, {color_expr(left[2])}],'
            )
            chunks.append(
                f'    right: [{json.dumps(right[0], ensure_ascii=False)}, {json.dumps(right[1], ensure_ascii=False)}, {color_expr(right[2])}],'
            )
        elif spec["type"] == "flow":
            chunks.append("    flow: [")
            for title, body, color_key in spec["flow"]:
                chunks.append(
                    f'      [{json.dumps(title, ensure_ascii=False)}, {json.dumps(body, ensure_ascii=False)}, {color_expr(color_key)}],'
                )
            chunks.append("    ],")
        else:
            chunks.append("    cards: [")
            for title, body, color_key in spec["cards"]:
                chunks.append(
                    f'      [{json.dumps(title, ensure_ascii=False)}, {json.dumps(body, ensure_ascii=False)}, {color_expr(color_key)}],'
                )
            chunks.append("    ],")
        chunks.append("  },")
    chunks.append("];")
    chunks.append("")
    (SLIDES_DIR / "content.mjs").write_text("\n".join(chunks), encoding="utf-8")


def write_slide_modules() -> None:
    for index in range(1, len(SLIDES) + 1):
        name = f"slide-{index:02d}.mjs"
        fn = f"slide{index:02d}"
        body = (
            'import { slides } from "./content.mjs";\n'
            'import { renderContentSlide } from "./shared.mjs";\n\n'
            f"export async function {fn}(presentation, ctx) {{\n"
            f"  return renderContentSlide(presentation, ctx, slides[{index - 1}]);\n"
            "}\n"
        )
        (SLIDES_DIR / name).write_text(body, encoding="utf-8")


def build_pptx() -> None:
    prs = Presentation()
    prs.slide_width = Emu(W)
    prs.slide_height = Emu(H)
    for spec in SLIDES:
        render_slide(prs, spec)
    PPTX_PATH.parent.mkdir(parents=True, exist_ok=True)
    prs.save(PPTX_PATH)


def main() -> None:
    write_shared_mjs()
    write_content_mjs()
    write_slide_modules()
    build_pptx()
    print(f"Wrote {len(SLIDES)} slides to {PPTX_PATH}")
    print(f"Wrote sources under {SLIDES_DIR}")


if __name__ == "__main__":
    main()
