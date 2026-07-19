"""Core lecture slides for Lesson 03 — staged student journey.

Structure: Title → TOC → Glossary → stages 1–5 → cases → wrap.
"""

from __future__ import annotations

import sys
from pathlib import Path

GPDB_ARCHIVE = "https://github.com/greenplum-db/gpdb-archive/blob/main"
GPDB_ORCA = "https://github.com/apache/cloudberry/blob/main/src/backend/gporca"

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from lesson03_case_catalog import CASE_SLIDES
from lesson03_front_matter import prepend_front_matter
from lesson03_glossary_catalog import (
    plan_inline_details,
    stats_inline_details_after_equality,
    stats_inline_details_after_map,
    stats_inline_details_after_range,
    term_chip,
)
from lesson03_slide_blocks import stage_gate


PLAN_BASE_TREE = """Gather Motion 2:1  (slice4)     actual rows=4
  -> WindowAgg / Sort
       -> Redistribute Motion 2:2  (region)
            -> HashAggregate (region, category)
                 -> Redistribute Motion 2:2  (region, category)
                      -> HashAggregate
                           -> Hash Join fact ⋈ product
                                -> Hash Join fact ⋈ customer
                                     -> Dynamic Seq Scan fact  -- 2/4 parts
                                          Filter: Feb window
                                     -> Seq Scan dim_customer  -- segment<>test
                                -> Broadcast Motion dim_product
Optimizer: GPORCA"""

PLAN_AFTER_TREE = """Gather Motion 2:1  (slice1)
  -> WindowAgg / Sort
       -> HashAggregate on tmp_lesson03_sales_shaped
            (already Feb + anti-test + dims)
Optimizer: GPORCA
-- TEMP stages: DISTRIBUTED BY + ANALYZE before this plan"""

_CORE_BODY = [
    {
        "kicker": "Урок 03 · Core",
        "title": "Декомпозиция и тюнинг тяжёлых запросов в MPP",
        "subtitle": "Следующий слайд — режимы Core 60 / 90 / Full. Не листать всё подряд.",
        "type": "cards",
        "cards": [
            [
                "Цель",
                "Научить читать план и доказывать rewrite.",
                "green"
            ],
            [
                "Стенд",
                "labs/greenplum-625 · БД mentor · схема lesson03.",
                "blue"
            ],
            [
                "Путь",
                "Режим → проблема → план → stats → TEMP → proof.",
                "amber"
            ],
            [
                "DoD",
                "Before/after + equivalence + один bottleneck.",
                "green"
            ]
        ]
    },
    {
        "anchor": "stage-problem",
        "kicker": "Этап 1",
        "title": "Проблема: тяжёлый OLAP",
        "subtitle": "Сквозной кейс-мотивация. Дальше теория объяснит, как его читать и чинить.",
        "type": "cards",
        "cards": [
            [
                "Симптом",
                "Месячный отчёт «горит» по времени.",
                "red"
            ],
            [
                "Данные",
                "fact AOCO ⋈ dims, фильтр февраля.",
                "amber"
            ],
            [
                "Baseline",
                "Три точки: Motion · cardinality · spill.",
                "blue"
            ],
            [
                "Дальше",
                "Теория плана → stats → storage → практика.",
                "green"
            ]
        ]
    },
    {
        "kicker": "Проблема · Incident",
        "title": "Симптом: месячный OLAP «горит» по времени",
        "subtitle": "Production frame: SLA нарушен. На стенде учим метод на измеримом SQL.",
        "type": "cards",
        "cards": [
            [
                "Симптом",
                "Долгий reporting: fact ⋈ dims + window + window за месяц.",
                "red"
            ],
            [
                "Вопрос",
                "Где критический путь: Motion, misestimate или spill?",
                "amber"
            ],
            [
                "Контракт",
                "Фиксируем optimizer + statement_mem до любых before/after.",
                "green"
            ],
            [
                "Lab scale",
                "2 сегмента, ~45k Feb rows — метод, не «47 минут wall».",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Проблема · Data",
        "title": "Архитектура данных кейса",
        "subtitle": "fact_sales (AOCO, range partitions) ⋈ dim_customer ⋈ dim_product.",
        "type": "panel",
        "body": (
            "Таблицы стенда lesson03:\n\n"
            "• fact_sales — AOCO, DISTRIBUTED BY (customer_id),\n"
            "  PARTITION BY RANGE (sale_date) — 4 партиции на стенде.\n"
            "• dim_customer — справочник клиента (segment, region).\n"
            "• dim_product — справочник продукта (category).\n\n"
            "Фильтр кейса:\n"
            "  sale_date ∈ [2026-02-01, 2026-03-01)\n"
            "  segment <> 'test'\n\n"
            "Grain результата: region × category + window rank по revenue."
        ),
    },
    {
        "kicker": "Проблема · SQL",
        "title": "Исходный SQL (monolith)",
        "subtitle": "Один запрос: filter → joins → agg → window. Без TEMP.",
        "type": "code",
        "code": (
            "SELECT region, category, revenue,\n"
            "       rank() OVER (PARTITION BY region ORDER BY revenue DESC)\n"
            "FROM (\n"
            "  SELECT c.region, p.category, sum(f.amount) AS revenue\n"
            "  FROM lesson03.fact_sales f\n"
            "  JOIN lesson03.dim_customer c USING (customer_id)\n"
            "  JOIN lesson03.dim_product  p USING (product_id)\n"
            "  WHERE f.sale_date >= DATE '2026-02-01'\n"
            "    AND f.sale_date <  DATE '2026-03-01'\n"
            "    AND c.segment <> 'test'\n"
            "  GROUP BY 1, 2\n"
            ") s;"
        ),
    },
    {
        "kicker": "Проблема · Baseline",
        "title": "Baseline: три симптома на плане",
        "subtitle": "Не весь EXPLAIN — три точки. Полный текст: lessons/lesson-03/artifacts/case/.",
        "type": "cards",
        "cards": [
            [
                "Motion",
                "Broadcast product + Redistribute agg keys + Gather (slice4).",
                "amber"
            ],
            [
                "Cardinality",
                "Scan/joins ~ok; финальные groups 9→actual 4.",
                "blue"
            ],
            [
                "Spill",
                "На 256MB — Disk:0; при малом statement_mem возможен Sort spill.",
                "green"
            ],
            [
                "Warm median",
                "Plan ~15 ms · Exec ~15 ms (n=3, lab).",
                "green"
            ]
        ]
    },
    {
        "anchor": "stage-plan",
        "kicker": "Этап 2",
        "title": "Теория: как читать distributed-план",
        "subtitle": "QD/QE, Motion, slices, ORCA vs Legacy — язык EXPLAIN ANALYZE.",
        "type": "cards",
        "cards": [
            [
                "Модель",
                "Данные + сеть + оценки + optimizer.",
                "green"
            ],
            [
                "Метод",
                "Алгоритм чтения плана слоями.",
                "blue"
            ],
            [
                "Практика",
                "5 слайдов baseline-дерева.",
                "amber"
            ],
            [
                "Осторожно",
                "ORCA ≠ всегда лучше Legacy.",
                "red"
            ]
        ]
    },
    {
        "kicker": "План · Model",
        "title": "Тяжёлый OLAP = данные + сеть + оценки + optimizer",
        "subtitle": "Полный словарь — в начале презентации; здесь — напоминание для плана.",
        "type": "flow",
        "flow": [
            [
                "Данные",
                "Storage / part / dist",
                "green"
            ],
            [
                "Сеть",
                "Motion / slices",
                "blue"
            ],
            [
                "Оценки",
                "Stats / CE",
                "amber"
            ],
            [
                "Optimizer",
                "ORCA | Legacy",
                "green"
            ],
            [
                "Stage",
                "TEMP proof",
                "blue"
            ]
        ]
    },
    {
        "kicker": "План · MPP",
        "title": "QD / QE / slice / Motion — в контексте плана",
        "subtitle": "Наведите на чип термина — коротко; клик — детали рядом (теория → словарь).",
        "type": "cards",
        "cards": [
            [
                "QD",
                "Master/coordinator: parse, optimize, gather.",
                "green"
            ],
            [
                "QE",
                "Segment executor своего slice.",
                "blue"
            ],
            [
                "Slice",
                "Кусок плана между Motion; своя gang процессов.",
                "amber"
            ],
            [
                "Motion",
                "Redistribute / Broadcast / Gather — плата сетью.",
                "red"
            ]
        ],
        "terms": [
            term_chip("qd_qe"),
            term_chip("motion"),
            term_chip("orca"),
            term_chip("guc"),
        ],
    },
    {
        "kicker": "План · Method 1/2",
        "title": "Алгоритм чтения EXPLAIN ANALYZE",
        "subtitle": "Shape недостаточен — нужен execution profile. Шаги 1–6.",
        "type": "cards",
        "cards": [
            ["1–2", "Зафиксировать optimizer + GUC. Разметить Motion / slices.", "green"],
            ["3–4", "Max actual rows flow. Первый крупный estimate vs actual.", "blue"],
            ["5", "Avg vs max по сегментам — ищем skew.", "amber"],
            ["6", "Hash build/probe и длина join-chain.", "red"],
        ],
    },
    {
        "kicker": "План · Method 2/2",
        "title": "Алгоритм чтения EXPLAIN ANALYZE",
        "subtitle": "Шаги 7–12. В конце — одна проверяемая гипотеза.",
        "type": "cards",
        "cards": [
            ["7–8", "Distribution keys vs join keys. Sort/Hash mem и Disk spill.", "green"],
            ["9–10", "Partition elimination. Planning vs execution bottleneck.", "blue"],
            ["11", "Critical path ≠ сумма времён всех узлов.", "amber"],
            ["12", "Одна проверяемая гипотеза → TEMP / rewrite / GUC.", "red"],
        ],
    },
    {
        "kicker": "План · Interactive",
        "title": "90 секунд: где первая причина плохого плана?",
        "subtitle": "Смотрите baseline. Не называйте «просто медленный SQL».",
        "type": "cards",
        "cards": [
            [
                "A",
                "Broadcast маленького dim — нормальная цена?",
                "green"
            ],
            [
                "B",
                "Redistribute после широкого join — нужен ли раньше filter?",
                "amber"
            ],
            [
                "C",
                "Window над уже маленьким agg — bottleneck wall-clock?",
                "blue"
            ],
            [
                "D",
                "Estimate groups 9 vs 4 — влияет на Motion?",
                "red"
            ]
        ]
    },
    {
        "kicker": "План · Plan 1/5",
        "title": "Форма дерева (baseline)",
        "subtitle": "4 slices. Полный plan: case/baseline-explain-analyze.txt",
        "type": "code",
        "code": "Gather Motion 2:1  (slice4)     actual rows=4\n  -> WindowAgg / Sort\n       -> Redistribute Motion 2:2  (region)\n            -> HashAggregate (region, category)\n                 -> Redistribute Motion 2:2  (region, category)\n                      -> HashAggregate\n                           -> Hash Join fact ⋈ product\n                                -> Hash Join fact ⋈ customer\n                                     -> Dynamic Seq Scan fact  -- 2/4 parts\n                                          Filter: Feb window\n                                     -> Seq Scan dim_customer  -- segment<>test\n                                -> Broadcast Motion dim_product\nOptimizer: GPORCA"
    },
    {
        "kicker": "План · Plan 2/5",
        "title": "Где едут данные (Motion)",
        "subtitle": "Сеть дороже CPU на широком промежуточном set. Чип Motion → детали.",
        "type": "cards",
        "terms": [term_chip("motion"), term_chip("qd_qe")],
        "cards": [
            [
                "Broadcast",
                "dim_product → все seg (800 rows) — дёшево на lab.",
                "green"
            ],
            [
                "Redistribute #1",
                "После partial agg по (region, category).",
                "amber"
            ],
            [
                "Redistribute #2",
                "По region перед window.",
                "amber"
            ],
            [
                "Gather",
                "Финальный 2:1 на QD — маленький результат.",
                "blue"
            ]
        ]
    },
    {
        "kicker": "План · Plan 3/5",
        "title": "Где ошиблась cardinality",
        "subtitle": "Порог ×N — эвристика; смотрите абсолютный объём узла.",
        "type": "code",
        "code": "Dynamic Seq Scan fact:  est 22400  act 22896   (~ok)\nHash Join customer:     est 21062  act 21432   (~ok)\nHash Join product:      est 21010  act 21432   (~ok)\nFinal groups / Gather:  est 9      act 4       (overestimate)\n\nНа lab misestimate мал по абсолюту.\nВ production тот же паттерн на млрд rows → Motion/mem."
    },
    {
        "kicker": "План · Plan 4/5",
        "title": "Память и диск",
        "subtitle": "statement_mem=256MB → quicksort, Disk:0. Spill — другой слой, чем TEMP.",
        "type": "cards",
        "cards": [
            [
                "Memory used",
                "262144kB (cap statement_mem) на baseline run.",
                "blue"
            ],
            [
                "Sort",
                "quicksort 66kB — без external merge.",
                "green"
            ],
            [
                "Spill path",
                "pgsql_tmp_Sort_* только при нехватке mem.",
                "amber"
            ],
            [
                "Демо spill",
                "SET statement_mem='8MB' + широкий ORDER BY — кнопка ниже → Appendix.",
                "red"
            ]
        ],
        "jumps": [
            {
                "label": "→ Appendix: spill / pgsql_tmp",
                "anchor": "appendix-spill",
            }
        ],
    },
    {
        "kicker": "План · Plan 5/5",
        "title": "Bottleneck на этом плане",
        "subtitle": "Гипотеза для проверки декомпозицией.",
        "type": "cards",
        "cards": [
            [
                "Критический путь",
                "Scan+два Hash Join на широком Feb set до agg.",
                "red"
            ],
            [
                "Гипотеза",
                "Вынести filter/join в TEMP stage → меньше Motion/work в финале.",
                "amber"
            ],
            [
                "Не гипотеза",
                "«Выключить ORCA» как первый рычаг на lab-scale.",
                "blue"
            ],
            [
                "Проверка",
                "TEMP + ANALYZE + тот же optimizer → metrics.",
                "green"
            ]
        ]
    },
    {
        "kicker": "План · Optimizers",
        "title": "ORCA vs Legacy: осторожные формулировки",
        "subtitle": "На 2 сегментах сравниваем shape. Production claim требует объёма.",
        "type": "two",
        "left": [
            "На стенде",
            "ORCA и Legacy могут выбрать разный join order / Motion. Фиксируйте GUC. Смотрите actual rows и runtime, не только маркер Optimizer.",
            "green"
        ],
        "right": [
            "Не говорим",
            "«ORCA всегда быстрее» / «Legacy для каждого короткого SQL». Legacy = diagnostic control + fallback при feature gap.",
            "amber"
        ],
        "terms": [
            term_chip("orca"),
            term_chip("motion"),
            term_chip("guc"),
        ],
    },
    # --- теория плана → детали словаря рядом ---
    *plan_inline_details(),
    {
        "anchor": "stage-stats",
        "kicker": "Этап 3",
        "title": "Теория: статистика и selectivity",
        "subtitle": "Из каких чисел в pg_stats планировщик получает rows_est — и когда ANALYZE бессилен.",
        "type": "cards",
        "cards": [
            [
                "MCV / hist",
                "Equality → MCV+freqs. Range → equi-depth histogram. Разные структуры — разные формулы.",
                "green",
            ],
            [
                "Selectivity",
                "sel ∈ (0,1], rows≈N·sel. Дальше — формулы Legacy AND и ORCA damping с числами.",
                "blue",
            ],
            [
                "ANALYZE",
                "Пересобирает sample → MCV/hist/NDV. После bulk load и TEMP stage — обязательно.",
                "amber",
            ],
            [
                "Лимит",
                "Свежий ANALYZE ≠ хороший план: корреляция, выражения, many-join, skew.",
                "red",
            ],
        ],
        "terms": [
            term_chip("selectivity"),
            term_chip("mcv"),
            term_chip("histogram"),
            term_chip("n_distinct"),
        ],
    },
    {
        "kicker": "Статистика · Карта",
        "title": "Цепочка: от EXPLAIN к числам в каталоге",
        "subtitle": "Учимся читать plan → проверять, откуда взялась оценка.",
        "type": "panel",
        "body": (
            "1) В EXPLAIN смотрим rows (estimate) vs actual rows.\n"
            "2) Если сильно расходятся — открываем pg_stats по фильтруемым колонкам:\n"
            "     n_distinct, most_common_vals/freqs, histogram_bounds.\n"
            "3) Физически это строки pg_statistic (heap + TOAST), не «отдельный stats file».\n"
            "4) Из этих массивов планировщик считает selectivity → rows_est → cost join/Motion.\n\n"
            "Дальше сразу идут карточки словаря по этим терминам — не только «в начале презентации»."
        ),
        "terms": [
            term_chip("selectivity"),
            term_chip("n_distinct"),
            term_chip("mcv"),
            term_chip("histogram"),
        ],
    },
    *stats_inline_details_after_map(),
    {
        "kicker": "Статистика · Equality",
        "title": "Equality: MCV или 1/NDV",
        "subtitle": "Рабочий пример на segment. Наведите на MCV / n_distinct — кратко; клик — детали рядом.",
        "type": "panel",
        "body": (
            "Предикат: segment = 'enterprise'.  N = 100 000.\n"
            "MCV={enterprise,mid,smb,test}  MCF={0.31,0.31,0.31,0.06}  NDV=4\n\n"
            "∈ MCV → sel=0.31 → rows_est=31 000.\n"
            "Без MCV → sel≈1/NDV=0.25 → rows_est=25 000.\n"
            "MCV точнее на «толстых» значениях → NLJ vs Hash может переехать.\n\n"
            "Вне MCV (NDV > |MCV|): sel ≈ (1−Σ MCF)/(NDV−|MCV|)."
        ),
        "terms": [
            term_chip("mcv"),
            term_chip("mcv_adv"),
            term_chip("n_distinct"),
            term_chip("selectivity"),
        ],
        "jumps": [
            {
                "label": "→ Appendix: equality / MCV (selfuncs)",
                "anchor": "appendix-legacy-eq",
            },
            {
                "label": "→ Appendix: anatomy pg_stats",
                "anchor": "appendix-stats",
            },
        ],
    },
    *stats_inline_details_after_equality(),
    {
        "kicker": "Статистика · Range",
        "title": "Range: histfrac по equi-depth histogram",
        "subtitle": "Корзины = равные кучи строк. Чипы Histogram → детали рядом.",
        "type": "panel",
        "body": (
            "Предикат: amount > 50 → смотрим histogram_bounds.\n"
            "Equi-depth: соседние границы делят ~равную долю строк.\n"
            "Границ ≈ default_statistics_target+1 (target=100 → ≈101).\n\n"
            "sel ≈ доля полных корзин справа от 50\n"
            "    + доля частичной корзины с 50  (= histfrac).\n\n"
            "NDV мал и всё в MCV → histogram_bounds=NULL (segment на стенде).\n\n"
            "Стенд: SELECT attname, n_distinct,\n"
            "  array_length(histogram_bounds,1) AS hist_n\n"
            "FROM pg_stats WHERE schemaname='lesson03';"
        ),
        "terms": [
            term_chip("histogram"),
            term_chip("histogram_adv"),
            term_chip("mcv"),
            term_chip("selectivity"),
        ],
        "jumps": [
            {
                "label": "→ Appendix: histogram equi-depth",
                "anchor": "appendix-histogram",
            },
            {
                "label": "→ Appendix: Legacy range / histfrac",
                "anchor": "appendix-legacy-range",
            },
        ],
    },
    *stats_inline_details_after_range(),
    {
        "kicker": "Статистика · MCV/Hist SQL",
        "title": "Стенд: MCV vs histogram в pg_stats",
        "subtitle": "Скопируйте на mentor / lesson03 и сравните segment vs amount.",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            "-- segment: NDV мал → всё в MCV, hist NULL\n"
            "SELECT most_common_vals, most_common_freqs,\n"
            "       n_distinct, histogram_bounds IS NULL AS hist_null\n"
            "FROM pg_stats\n"
            "WHERE schemaname='lesson03'\n"
            "  AND tablename='dim_customer' AND attname='segment';\n"
            "\n"
            "-- amount: hist_n ≈ statistics_target+1\n"
            "SELECT attname, n_distinct,\n"
            "       array_length(histogram_bounds,1) AS hist_n\n"
            "FROM pg_stats\n"
            "WHERE schemaname='lesson03' AND tablename='fact_sales';"
        ),
    },
    {
        "kicker": "Статистика · Legacy AND",
        "title": "Legacy AND: произведение selectivities",
        "subtitle": "Гипотеза независимости: sel(A∧B) = sel(A)·sel(B).",
        "type": "panel",
        "body": (
            "Legacy AND: sel(A ∧ B ∧ C) ≈ s₁ · s₂ · s₃  (∏ sᵢ).\n\n"
            "Пример: s(enterprise)=0.31, s(NW)=0.10\n"
            "  → sel≈0.031 → rows_est≈3 100 из 100k.\n\n"
            "Ломается при корреляции (enterprise почти всегда в NW):\n"
            "истинная доля ≠ произведению → врёт join/Motion.\n\n"
            "GP6: нет multivariate CREATE STATISTICS → лечим rewrite/TEMP,\n"
            "не «ещё ANALYZE». Детали — Appendix."
        ),
        "jumps": [
            {
                "label": "→ Appendix: Legacy AND/OR/NOT + clausesel.c",
                "anchor": "appendix-legacy-and",
            },
            {
                "label": "→ Appendix: equality / MCV формулы",
                "anchor": "appendix-legacy-eq",
            },
        ],
    },
    {
        "kicker": "Статистика · ORCA AND",
        "title": "ORCA AND: scale factors + damping 0.75ⁿ",
        "subtitle": "ORCA не всегда тупо перемножает — демпфирует накопление фильтров.",
        "type": "panel",
        "body": (
            "ORCA: scale factors + damping — много AND не «обнуляют» rows.\n\n"
            "Идея: после 1-го фильтра следующие смягчаются (~0.75ⁿ),\n"
            "а не всегда полным sᵢ.\n\n"
            "Пример (схема, не байт-в-байт):\n"
            "  s1=0.31, s2=0.10, s3=0.50\n"
            "  Legacy: 0.31·0.10·0.50 = 0.0155\n"
            "  ORCA*:  0.31·(0.10·0.75)·(0.50·0.75²) ≈ 0.0087\n\n"
            "Вывод: ORCA ≠ ∏ sᵢ → планы расходятся на одном ANALYZE.\n"
            "Константы/код — Appendix."
        ),
        "jumps": [
            {
                "label": "→ Appendix: ORCA AND + damping 0.75ⁿ",
                "anchor": "appendix-orca-and",
            },
            {
                "label": "→ Appendix: сводка CE Legacy vs ORCA",
                "anchor": "appendix-ce-summary",
            },
        ],
    },
    {
        "kicker": "Статистика · Сводка формул",
        "title": "Шпаргалка формул selectivity",
        "subtitle": "Держите рядом с EXPLAIN ANALYZE. Глубокие формулы — кнопки ниже.",
        "type": "cards",
        "cards": [
            [
                "Equality ∈ MCV",
                "sel = MCF[i]. rows ≈ N · MCF[i].",
                "green",
            ],
            [
                "Equality ∉ MCV",
                "sel ≈ (1−ΣMCF) / (NDV−|MCV|), иначе ≈ 1/NDV.",
                "blue",
            ],
            [
                "Range",
                "sel ≈ histfrac (+ края корзины). MCV из hist исключены.",
                "amber",
            ],
            [
                "AND",
                "Legacy: ∏ sᵢ. ORCA: scale factors + damping. GP6: нет multivariate stats.",
                "red",
            ],
        ],
        "jumps": [
            {
                "label": "→ Appendix: Legacy AND/OR (clausesel)",
                "anchor": "appendix-legacy-and",
            },
            {
                "label": "→ Appendix: Legacy range / histfrac",
                "anchor": "appendix-legacy-range",
            },
            {
                "label": "→ Appendix: anatomy pg_stats",
                "anchor": "appendix-stats",
            },
        ],
    },
    {
        "kicker": "Статистика · ANALYZE",
        "title": "Как обновлять статистику",
        "subtitle": "Вручную в ETL. Авто — gp_autostats_mode, не «магический vacuum».",
        "type": "code",
        "code": (
            "ANALYZE lesson03.fact_sales;          -- вручную\n"
            "SHOW gp_autostats_mode;               -- default on_no_stats\n\n"
            "SELECT relname, last_analyze, last_autoanalyze,\n"
            "       n_mod_since_analyze\n"
            "FROM pg_stat_user_tables\n"
            "WHERE schemaname='lesson03';\n\n"
            "-- После CREATE TEMP AS → ANALYZE stage:\n"
            "-- иначе оценки часто грубые (не «всегда врут»)."
        ),
    },
    {
        "kicker": "Статистика · Physical",
        "title": "Статистика — не отдельный «stats file»",
        "subtitle": "pg_statistic = heap catalog (+ TOAST). Lab filepath ниже.",
        "type": "code",
        "code": (
            "pg_statistic\n"
            "  → pg_relation_filepath → base/<dboid>/<relfilenode>\n"
            "  → 8KB heap pages → ItemId → HeapTupleHeader\n"
            "  → stavalues/stanumbers (varlena)\n"
            "  → TOAST relation при больших arrays\n\n"
            "-- стенд mentor:\n"
            "filepath(pg_statistic) ≈ base/16587/12537\n"
            "pg_statistic ~928 kB; toast ~96 kB"
        ),
    },
    {
        "kicker": "Статистика · Fail",
        "title": "Когда свежий ANALYZE не спасает",
        "subtitle": "Тогда TEMP / rewrite — не «ещё раз ANALYZE».",
        "type": "cards",
        "cards": [
            [
                "Корреляция",
                "region ∧ segment: истинная sel ≠ s1·s2. Multivariate stats в GP6 нет.",
                "red",
            ],
            [
                "Выражения",
                "date_trunc(col) / (col+1): stats колонки не применяются к выражению.",
                "amber",
            ],
            [
                "Many-join",
                "Ошибка sel на каждом join перемножается → взрыв Motion/NLJ.",
                "blue",
            ],
            [
                "Skew",
                "Тяжёлый хвост вне MCV: avg-оценка лжёт, один сегмент горит.",
                "green",
            ],
        ],
    },
    {
        "anchor": "stage-storage",
        "kicker": "Этап 4",
        "title": "Теория: физика хранения",
        "subtitle": "Heap / AO / AOCO — что реально читает scan и почему AOCO ≠ «быстрее всегда».",
        "type": "cards",
        "cards": [
            [
                "Heap",
                "Классические 8KB pages: tuple целиком на странице. Удобно для частых UPDATE.",
                "green",
            ],
            [
                "AO / AOCO",
                "Append-Only: row blocks vs column streams + visimap. AOCO читает нужные колонки.",
                "blue",
            ],
            [
                "Следствие",
                "Физика бьёт по IO scan/projection. Motion/skew storage не лечит.",
                "amber",
            ],
            [
                "Решение",
                "Выбираем storage под access pattern кейса (wide fact + узкий SELECT → AOCO).",
                "green",
            ],
        ],
    },
    {
        "kicker": "Storage · Storage",
        "title": "Физика хранения: зачем она в тюнинге",
        "subtitle": "AOCO не лечит Motion/skew. Но решает IO projection.",
        "type": "cards",
        "cards": [
            [
                "Heap",
                "Page + tuple + MVCC — dims / updates.",
                "green"
            ],
            [
                "AO row",
                "Append blocks — bulk row insert.",
                "blue"
            ],
            [
                "AOCO",
                "Column streams — narrow analytic scan.",
                "amber"
            ],
            [
                "Ключ",
                "Access pattern + types, не «модно».",
                "red"
            ]
        ]
    },
    {
        "kicker": "Storage · Heap",
        "title": "Heap page anatomy",
        "subtitle": "Строка лежит в page; SELECT * читает весь tuple width.",
        "type": "code",
        "code": "Page (обычно 8KB)\n  PageHeaderData\n  ItemIdData[]          -- line pointers\n  free space\n  HeapTupleHeaderData   -- xmin/xmax, infomask, …\n    None bitmap\n    fixed attrs (+ alignment/padding)\n    varlena attrs → inline | compressed | TOAST pointer\n\nForks: main / FSM / VM\nUpdate/delete → новые версии; vacuum освобождает"
    },
    {
        "kicker": "Storage · AO",
        "title": "AO row: blocks, aoseg, visimap",
        "subtitle": "Append-optimized row orientation.",
        "type": "cards",
        "cards": [
            [
                "Segfiles",
                "segment file + segno; append varblocks.",
                "green"
            ],
            [
                "Metadata",
                "gp_aoseg / pg_aoseg: EOF, tupcount, …",
                "blue"
            ],
            [
                "Visimap",
                "Какие rows видны; не классический heap HOT.",
                "amber"
            ],
            [
                "Blockdir",
                "Ускоряет fetch по position.",
                "green"
            ]
        ]
    },
    {
        "kicker": "Storage · AOCO",
        "title": "AOCO: column streams × segno",
        "subtitle": "Projection: узкий SELECT не читает payload column files.",
        "type": "code",
        "code": "pg_appendonly:\n  segrelid      → aoseg/aocsseg metadata\n  blkdirrelid   → block directory\n  visimaprelid  → visibility map\n\nФизика: (column × segno) → compressed blocks\nEncoding per column (zstd/rle/…)\nSELECT * / wide projection → читаем почти все streams\nGP6 DDL: appendoptimized=True  (alias appendonly=True)"
    },
    {
        "kicker": "Storage · Types",
        "title": "Типы данных: физика → следствие",
        "subtitle": "Один слайд сравнения — обязателен к заданию.",
        "type": "code",
        "code": "int4/date          fixed     → плотный stream / inline\nint8/timestamp     fixed+align → шире ключ/Motion\nnumeric            varlena   → CPU + compression variance\ntext/jsonb         varlena   → Heap: TOAST risk; AOCO: свой stream\nNULL               bitmap    → не «байт на колонку» в уме\n\nLab: сравните size + narrow vs wide scan\nHeap dim vs AOCO fact (lesson03)"
    },
    {
        "kicker": "Storage · Decision",
        "title": "Storage decision для кейса",
        "subtitle": "fact → AOCO; dims → Heap. Distribution отдельно.",
        "type": "two",
        "left": [
            "Выбор",
            "fact_sales AOCO + compress: scan/projection. dim_* обновляемые/маленькие → heap-friendly.",
            "green"
        ],
        "right": [
            "Не лечит",
            "Плохой DISTRIBUTED BY, skew, correlated filters, лишний Redistribute.",
            "red"
        ]
    },
    {
        "anchor": "stage-practice",
        "kicker": "Этап 5",
        "title": "Практика: чиним сквозной OLAP",
        "subtitle": "TEMP как physical stage → новый план → metrics → equivalence.",
        "type": "cards",
        "cards": [
            [
                "CTE ≠ stage",
                "Materialization не гарантирована.",
                "amber"
            ],
            [
                "TEMP",
                "DISTRIBUTED BY + ANALYZE на каждом stage.",
                "green"
            ],
            [
                "Proof",
                "Before/after + EXCEPT ALL = 0.",
                "blue"
            ],
            [
                "Дальше",
                "Девять именованных кейсов оптимизации.",
                "red"
            ]
        ]
    },
    {
        "kicker": "Практика · CTE",
        "title": "Почему CTE ≠ physical stage",
        "subtitle": "GP6: optimizer_cte_inlining_bound (ORCA default 0) — не гадайте.",
        "type": "code",
        "code": "| Механизм | Physical stage гарантирован?|\n| Subquery | Нет                         |\n| CTE      | Нет как user relation;      |\n|          | Legacy часто fence;         |\n|          | ORCA зависит от GUC/xforms  |\n| TEMP     | Да: catalog + files + ANALYZE|\n\nSHOW optimizer_cte_inlining_bound;"
    },
    {
        "kicker": "Практика · TEMP",
        "title": "TEMP: session boundary + ON COMMIT",
        "subtitle": "Default PRESERVE ROWS. Чужая сессия не видит ваш TEMP.",
        "type": "cards",
        "cards": [
            [
                "Сессия",
                "Одно соединение QD; \\q → cleanup TEMP namespace.",
                "green"
            ],
            [
                "PRESERVE",
                "После COMMIT таблица+строки живут (default).",
                "blue"
            ],
            [
                "DELETE ROWS",
                "После COMMIT строк 0, каркас жив.",
                "amber"
            ],
            [
                "DROP",
                "После COMMIT relation нет.",
                "red"
            ]
        ]
    },
    {
        "kicker": "Практика · Rewrite",
        "title": "Декомпозиция OLAP-кейса: TEMP stages",
        "subtitle": "Сужаем → join/shape → window. ANALYZE каждый stage.",
        "type": "code",
        "code": "CREATE TEMP TABLE tmp_lesson03_sales_feb AS …\n  WHERE Feb window\n  DISTRIBUTED BY (customer_id);\nANALYZE tmp_lesson03_sales_feb;\n\nCREATE TEMP TABLE tmp_lesson03_sales_shaped AS …\n  JOIN dims, segment<>'test'\n  DISTRIBUTED BY (region);\nANALYZE tmp_lesson03_sales_shaped;\n\n-- финальный window/agg уже на узком stage"
    },
    {
        "kicker": "Практика · FS",
        "title": "TEMP files vs spill files",
        "subtitle": "Стенд default tablespace. Проверяйте temp_tablespaces в prod.",
        "type": "code",
        "code": "TEMP relation (session):\n  pg_temp_NNN, relpersistence='t'\n  base/<dboid>/t_<relfilenode> на QE\n  (на стенде QD-side файл часто 0 bytes — lab observation)\n\nSpill workfiles (executor):\n  base/pgsql_tmp/pgsql_tmp_Sort_*\n  живут во время query, не pg_class TEMP"
    },
    {
        "kicker": "Практика · Cost",
        "title": "Цена materialization",
        "subtitle": "TEMP выгоден, если stage режет cardinality/Motion сильнее IO write+read.",
        "type": "two",
        "left": [
            "Плюсы",
            "Фиксированный grain; DISTRIBUTED BY; ANALYZE; reuse в сессии; доказуемый before/after.",
            "green"
        ],
        "right": [
            "Минусы",
            "Двойной IO; место на всех seg; без фильтра = дорогой materialize всего fact.",
            "red"
        ]
    },
    {
        "kicker": "Практика · After plan",
        "title": "After: форма плана на TEMP stage",
        "subtitle": "Меньше slices/Motion на финальном SQL. Полный текст в case/.",
        "type": "code",
        "code": "Gather Motion 2:1  (slice1)\n  -> WindowAgg / Sort\n       -> HashAggregate on tmp_lesson03_sales_shaped\n            (already Feb + anti-test + dims)\nOptimizer: GPORCA\n-- TEMP stages: DISTRIBUTED BY + ANALYZE before this plan"
    },
    {
        "kicker": "Практика · Metrics",
        "title": "Before / after (warm median, lab)",
        "subtitle": "OLAP metrics.md + NLJ case/nlj-metrics.md.",
        "type": "code",
        "code": "OLAP Feb case (metrics.md):\n  Planning ~15→1.4 ms · Execution ~15→6 ms\n\nNLJ CTE case (nlj-metrics.md, GPORCA):\n  A/B Nested Loop loops=80k  ~98–176 ms\n  C Hash Join est≈actual     ~25 ms\n\nCold planning на baseline — всегда note warm/cold."
    },
    {
        "kicker": "Практика · Equivalence",
        "title": "Доказательство эквивалентности",
        "subtitle": "Без этого rewrite — мнение, не engineering.",
        "type": "code",
        "code": "-- одинаковый optimizer + snapshot + GUC\nSELECT count(*) FROM (\n  SELECT * FROM baseline_grain\n  EXCEPT ALL\n  SELECT * FROM after_grain\n) x;   -- 0\n\n\\i lesson03-e2e-case-metrics.sql\n\\i lesson03-nlj-cte-temp-case.sql"
    },
    {
        "anchor": "cases",
        "kicker": "Этап 6",
        "title": "Кейсы оптимизации",
        "subtitle": "Отдельные ловушки плана. У каждого кейса — титул → разбор → план/код → фикс.",
        "type": "cards",
        "cards": [
            [
                "Формат",
                "Проблема → сигнал в EXPLAIN → почему → как чинить → стенд.",
                "green"
            ],
            [
                "CE",
                "Два кейса недооценки строк (ORCA и Legacy).",
                "red"
            ],
            [
                "Motion / locus",
                "SCD2, NOT IN, window, VALUES, DISTINCT, median.",
                "amber"
            ],
            [
                "Stats ETL",
                "Autostats не срабатывает на INSERT в parent.",
                "blue"
            ]
        ]
    },
    {
        "anchor": "case-orca-ce",
        "kicker": "Кейс 01",
        "title": "ORCA недооценил строки → Nested Loop",
        "subtitle": "Три CTE + join к маленькой dim: план верит в «1 row».",
        "type": "cards",
        "cards": [
            [
                "Проблема",
                "GPORCA выбирает Index Nested Loop при est≪actual.",
                "red"
            ],
            [
                "Сигнал в плане",
                "Nested Loop + Broadcast/Index Scan, loops≈80k, rows=1→80000.",
                "amber"
            ],
            [
                "Как чинить",
                "TEMP stage + ANALYZE → Hash Join; не «просто SET optimizer».",
                "green"
            ],
            [
                "Стенд",
                "lesson03-orca-ce-trap.sql",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Кейс 01 · Суть",
        "title": "Что → как → почему",
        "subtitle": "Скрипт: lesson03-orca-ce-trap.sql · metrics: ce-traps-metrics.md",
        "type": "cards",
        "cards": [
            [
                "Что",
                "3 CTE + opaque preds → join к replicated dim с index.",
                "amber"
            ],
            [
                "Как",
                "ORCA: Nested Loop + Index Scan, est≈1, loops=80k.",
                "red"
            ],
            [
                "Почему",
                "Cardinality under-estimate после CTE/opaque фильтров.",
                "blue"
            ],
            [
                "Фикс",
                "TEMP + ANALYZE enriched stage → Hash Join ~21 ms (lab).",
                "green"
            ]
        ]
    },
    {
        "kicker": "Кейс 01 · SQL",
        "title": "Стендовый запрос (ORCA)",
        "subtitle": "Предикаты почти keep-all. Статы нет / stale.",
        "type": "code",
        "code_kind": "SQL",
        "code": "SET optimizer = on;\nWITH cte_orders AS ( … opaque … ),\n     cte_active AS ( … ),\n     cte_enriched AS ( … )\nSELECT e.*, r.tier, r.score\nFROM cte_enriched e\nJOIN lesson03.orca_ref r USING (customer_id);"
    },
    {
        "kicker": "Кейс 01 · План",
        "title": "Плохой план и после TEMP",
        "subtitle": "Форма важнее абсолютных секунд на 2 seg.",
        "type": "code",
        "code_kind": "PLAN",
        "code": "BAD:\nNested Loop                 rows=1 → actual 80000\n  -> Broadcast Motion        rows=1 → actual 80000\n  -> Index Scan              loops=80000\n\nGOOD (TEMP+ANALYZE):\nHash Join  est≈actual  ~21 ms"
    },
    {
        "anchor": "case-legacy-ce",
        "kicker": "Кейс 02",
        "title": "Legacy: EXISTS → Nested Loop Semi Join",
        "subtitle": "Тот же класс CE-ошибки, другой SQL и другой optimizer.",
        "type": "cards",
        "cards": [
            [
                "Проблема",
                "Postgres planner выбирает Nested Loop Semi при under-estimate.",
                "red"
            ],
            [
                "Сигнал в плане",
                "Nested Loop Semi Join, est≪actual, огромные loops.",
                "amber"
            ],
            [
                "Как чинить",
                "TEMP + ANALYZE; enable_nestloop на стенде включаем явно.",
                "green"
            ],
            [
                "Стенд",
                "lesson03-legacy-ce-trap.sql",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Кейс 02 · Суть",
        "title": "Что → как → почему",
        "subtitle": "Почему нельзя один SQL на оба оптимизатора для демо.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "Opaque filters + EXISTS + join к dim.",
                "amber"
            ],
            [
                "Как",
                "Nested Loop Semi Join + Nested Loop (Legacy).",
                "red"
            ],
            [
                "Почему",
                "EXISTS «приглашает» semi; CE занижает rows.",
                "blue"
            ],
            [
                "Фикс",
                "Physical stage + ANALYZE → Hash Join ~22 ms.",
                "green"
            ]
        ]
    },
    {
        "kicker": "Кейс 02 · План",
        "title": "Плохой план Legacy",
        "subtitle": "HashJoin остаётся ON — NL выбран стоимостью.",
        "type": "code",
        "code_kind": "PLAN",
        "code": "SET optimizer = off;\nSET enable_nestloop = on;\n\nNested Loop\n  -> Nested Loop Semi Join   rows=15 → actual 40060\n       -> Seq Scan … est≈29\n       -> Index Scan         loops=40060"
    },
    {
        "kicker": "Кейс 02 · Вывод",
        "title": "CE trap → TEMP, не «просто сменить optimizer»",
        "subtitle": "Смена движка без cardinality stage часто не лечит корень.",
        "type": "two",
        "left": [
            "Диагноз",
            "est≪actual на join/semi + index dim → NL-семейство. Смотрите loops=.",
            "green"
        ],
        "right": [
            "Лечение",
            "Physical stage (TEMP) + ANALYZE; proof в ce-traps-metrics.md.",
            "blue"
        ]
    },
    {
        "anchor": "case-scd2",
        "kicker": "Кейс 03",
        "title": "SCD2: Redistribute при «согласованном» join",
        "subtitle": "Ключи join совпали с DISTRIBUTED BY — а Motion всё равно есть.",
        "type": "cards",
        "cards": [
            [
                "Проблема",
                "CTE max(version) меняет locus: hash(biz_key) ≠ hash(biz_key, version).",
                "red"
            ],
            [
                "Сигнал в плане",
                "Redistribute … Hash Key: biz_key (часто ×2).",
                "amber"
            ],
            [
                "Как чинить",
                "DISTRIBUTED BY (biz_key) под access pattern; TEMP только keys — мало.",
                "green"
            ],
            [
                "Стенд",
                "lesson03-principal-scd2-locus.sql",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Кейс 03 · Суть",
        "title": "Иллюзия co-location",
        "subtitle": "Senior смотрит имена колонок. Нужно читать Hash Key.",
        "type": "cards",
        "cards": [
            [
                "SQL",
                "fact ⋈ (biz_key, max(version)) — classic SCD2 latest.",
                "amber"
            ],
            [
                "Иллюзия",
                "DISTRIBUTED BY (biz_key, version_id) + USING тех же полей.",
                "red"
            ],
            [
                "Факт",
                "hash(пары) ≠ hash(biz_key) → Redistribute обязателен.",
                "blue"
            ],
            [
                "Фикс",
                "Модель: DISTRIBUTED BY (biz_key). Не «ещё ANALYZE».",
                "green"
            ]
        ]
    },
    {
        "kicker": "Кейс 03 · План",
        "title": "A → B → C на стенде",
        "subtitle": "\\i lesson03-principal-scd2-locus.sql",
        "type": "code",
        "code_kind": "PLAN",
        "code": "A) composite dist + CTE max → Redistribute Hash Key: biz_key\nB) TEMP latest BY (biz_key) → Redistribute FACT остаётся\nC) fact BY (biz_key) → local join, только Gather\n\nБонус: int ⋈ int8 → Redistribute Hash Key: (id)::bigint"
    },
    {
        "anchor": "case-not-in",
        "kicker": "Кейс 04",
        "title": "NOT IN раздувает Broadcast",
        "subtitle": "Антифильтр, который тиражирует всю внутреннюю таблицу.",
        "type": "cards",
        "cards": [
            [
                "Проблема",
                "NOT IN (SELECT …) → Hash Left Anti Semi (Not-In) + Broadcast inner.",
                "red"
            ],
            [
                "Сигнал в плане",
                "Broadcast Motion всей t2 на каждый сегмент.",
                "amber"
            ],
            [
                "Как чинить",
                "NOT EXISTS или LEFT JOIN … IS NULL + co-located ключи.",
                "green"
            ],
            [
                "Стенд",
                "lesson03-secret18-not-in-broadcast.sql",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Кейс 04 · Суть",
        "title": "Что → как → почему → фикс",
        "subtitle": "Семантика Not-In (+ NULL) ≠ обычный anti-join.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "WHERE t1.n NOT IN (SELECT n FROM t2).",
                "amber"
            ],
            [
                "Как",
                "Not-In Join; часто Broadcast полной t2.",
                "red"
            ],
            [
                "Почему",
                "Xform Not-In + семантика NULL.",
                "blue"
            ],
            [
                "Фикс",
                "NOT EXISTS / LEFT JOIN IS NULL.",
                "green"
            ]
        ]
    },
    {
        "kicker": "Кейс 04 · План",
        "title": "Broadcast vs Hash Anti",
        "subtitle": "Lab: форма важнее секунд на 2 seg.",
        "type": "code",
        "code_kind": "PLAN",
        "code": "A NOT IN:\n  Hash Left Anti Semi (Not-In)\n    -> Broadcast Motion  ← вся t2\n\nB NOT EXISTS:\n  Hash Anti Join  ← без Broadcast t2"
    },
    {
        "kicker": "Кейс 04 · Код GP",
        "title": "Куда смотреть в исходниках",
        "subtitle": "ORCA xform + Motion executor.",
        "type": "cards",
        "cards": [
            [
                "Xform Not-In",
                "https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/xforms/CXformLeftAntiSemiJoinNotIn2HashJoinNotIn.cpp",
                "red"
            ],
            [
                "Broadcast",
                "https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp",
                "amber"
            ],
            [
                "Motion",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeMotion.c",
                "blue"
            ],
            [
                "Deep-dive",
                "deep-dives/secret18-not-in-broadcast.md",
                "green"
            ]
        ]
    },
    {
        "anchor": "case-window",
        "kicker": "Кейс 05",
        "title": "Окно по константе → сегмент-жертва",
        "subtitle": "PARTITION BY ключ с NDV=1 собирает всю таблицу на один сегмент.",
        "type": "cards",
        "cards": [
            [
                "Проблема",
                "WindowAgg требует все строки partition key вместе.",
                "red"
            ],
            [
                "Сигнал в плане",
                "Redistribute Motion … Hash Key: <partition col>.",
                "amber"
            ],
            [
                "Как чинить",
                "Убрать бессмысленный PARTITION BY или DISTRIBUTED BY реальному ключу.",
                "green"
            ],
            [
                "Стенд",
                "lesson03-secret14-window-partition-skew.sql",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Кейс 05 · Суть",
        "title": "Коллапс параллелизма",
        "subtitle": "Константа invalid_id = один hash = один QE.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "row_number() OVER (PARTITION BY invalid_id …).",
                "amber"
            ],
            [
                "Как",
                "Redistribute на partition key.",
                "red"
            ],
            [
                "Почему",
                "NDV=1 → victim segment, spill/workfile.",
                "blue"
            ],
            [
                "Фикс",
                "Смысл ключа? Иначе убрать PARTITION BY.",
                "green"
            ]
        ]
    },
    {
        "kicker": "Кейс 05 · План",
        "title": "Redistribute → без Motion → rewrite",
        "subtitle": "\\i lesson03-secret14-window-partition-skew.sql",
        "type": "code",
        "code_kind": "PLAN",
        "code": "A) BY (id) + PARTITION BY const → Redistribute Hash Key: invalid_id\nC) BY (invalid_id) → Motion нет, но NDV=1 → всё равно один seg\nD) без PARTITION BY → Gather + WindowAgg (если ключ мусор)"
    },
    {
        "kicker": "Кейс 05 · Код GP",
        "title": "WindowAgg + hash-distribute",
        "subtitle": "deep-dives/secret14-window-partition-skew.md",
        "type": "cards",
        "cards": [
            [
                "WindowAgg",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeWindowAgg.c",
                "green"
            ],
            [
                "ORCA window",
                "https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/xforms/CXformImplementSequenceProject.cpp",
                "blue"
            ],
            [
                "Hash Motion",
                "https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/operators/CPhysicalMotionHashDistribute.cpp",
                "amber"
            ],
            [
                "Deep-dive",
                "secret14-window-partition-skew.md",
                "red"
            ]
        ]
    },
    {
        "anchor": "case-values",
        "kicker": "Кейс 06",
        "title": "Параметры в VALUES двигают fact",
        "subtitle": "Красивый CTE с параметрами — едет большая таблица, не params.",
        "type": "cards",
        "cards": [
            [
                "Проблема",
                "WITH data_batch AS (VALUES …) JOIN fact без ключа/статы.",
                "red"
            ],
            [
                "Сигнал в плане",
                "Lab: Gather fact→QD; prod: часто Broadcast fact.",
                "amber"
            ],
            [
                "Как чинить",
                "WHERE/литералы; или DISTRIBUTED BY join-ключа + ANALYZE.",
                "green"
            ],
            [
                "Стенд",
                "lesson03-secret29-values-params-broadcast.sql",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Кейс 06 · Суть",
        "title": "Какую сторону двигает Motion?",
        "subtitle": "Всегда читайте сторону Broadcast/Gather.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "CTE VALUES «параметры отчёта» ⋈ fact.",
                "amber"
            ],
            [
                "Как",
                "Fact едет к params (Gather/Broadcast).",
                "red"
            ],
            [
                "Почему",
                "CE rows≈1 без ANALYZE + RANDOM dist.",
                "blue"
            ],
            [
                "Фикс",
                "Scalar WHERE или dist key + ANALYZE.",
                "green"
            ]
        ]
    },
    {
        "kicker": "Кейс 06 · План",
        "title": "A Gather → B local → D filter",
        "subtitle": "\\i lesson03-secret29-values-params-broadcast.sql",
        "type": "code",
        "code_kind": "PLAN",
        "code": "A RANDOM, no ANALYZE: Hash Join → Gather/Broadcast fact\nB DISTRIBUTED BY (n_txt): Seq Scan fact, без Motion fact\nD WHERE n_txt = '10': Filter — без join к VALUES\nE IN (VALUES) ≠ IN list → ANY filter"
    },
    {
        "kicker": "Кейс 06 · Код GP",
        "title": "Motion + CE defaults",
        "subtitle": "deep-dives/secret29-values-params-broadcast.md",
        "type": "cards",
        "cards": [
            [
                "Broadcast",
                "https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp",
                "red"
            ],
            [
                "Hash redistribute",
                "https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/operators/CPhysicalMotionHashDistribute.cpp",
                "amber"
            ],
            [
                "selfuncs",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/utils/adt/selfuncs.c",
                "blue"
            ],
            [
                "Deep-dive",
                "secret29-values-params-broadcast.md",
                "green"
            ]
        ]
    },
    {
        "anchor": "case-distinct",
        "kicker": "Кейс 07",
        "title": "Считаем DISTINCT по сегментам",
        "subtitle": "Map count(DISTINCT) на каждом seg → SUM. Exact только при dist key.",
        "type": "cards",
        "cards": [
            [
                "Проблема",
                "Глобальный COUNT(DISTINCT) на огромной AOCO — spill/timeout.",
                "red"
            ],
            [
                "Сигнал в плане",
                "Тяжёлый Aggregate/spill; map-версия — двухфазный HashAggregate.",
                "amber"
            ],
            [
                "Как чинить",
                "sum(cnt) GROUP BY gp_segment_id, если DISTINCT ⊆ DISTRIBUTED BY.",
                "green"
            ],
            [
                "Стенд",
                "lesson03-secret42-distinct-by-segment.sql",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Кейс 07 · Суть",
        "title": "Exact vs overcount",
        "subtitle": "Фаза D стенда — обязательный negative case.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "COUNT(DISTINCT id) на большой AOCO.",
                "amber"
            ],
            [
                "Как",
                "sum(count DISTINCT) … GROUP BY gp_segment_id.",
                "blue"
            ],
            [
                "Exact",
                "Только если id на одном seg (dist key).",
                "green"
            ],
            [
                "Ловушка",
                "DISTRIBUTED RANDOMLY → SUM завышает.",
                "red"
            ]
        ]
    },
    {
        "kicker": "Кейс 07 · План",
        "title": "Canonical vs map",
        "subtitle": "Lab может быть медленнее map — учим контракт exactness.",
        "type": "code",
        "code_kind": "PLAN",
        "code": "A) count(DISTINCT id) → Aggregate → Gather\nB) sum per gp_segment_id → HashAggregate (seg, id) → sum\nC) canonical = mapped\nD) RANDOM: mapped > canonical"
    },
    {
        "kicker": "Кейс 07 · Код GP",
        "title": "Agg + GbAgg xform",
        "subtitle": "deep-dives/secret42-distinct-by-segment.md",
        "type": "cards",
        "cards": [
            [
                "nodeAgg",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeAgg.c",
                "green"
            ],
            [
                "ORCA HashAgg",
                "https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/xforms/CXformGbAgg2HashAgg.cpp",
                "blue"
            ],
            [
                "Motion",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeMotion.c",
                "amber"
            ],
            [
                "Контракт",
                "Exact только при coverage DISTINCT dist-ключом.",
                "red"
            ]
        ]
    },
    {
        "anchor": "case-autostats",
        "kicker": "Кейс 08",
        "title": "Autostats молчит после INSERT в parent",
        "subtitle": "on_no_stats ≠ «стата появится сама» для партиций.",
        "type": "cards",
        "cards": [
            [
                "Проблема",
                "INSERT в top-level parent не триггерит autostats на leaves.",
                "red"
            ],
            [
                "Сигнал в плане",
                "Каталог: leaves MISSING pg_statistic после parent load.",
                "amber"
            ],
            [
                "Как чинить",
                "Явный ANALYZE parent/leaves в ETL; insert в leaf — другой контракт.",
                "green"
            ],
            [
                "Стенд",
                "lesson03-secret41-autostats-partitions.sql",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Кейс 08 · Суть",
        "title": "Parent miss → leaf hit → ANALYZE",
        "subtitle": "Документированное поведение GP6, не баг.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "INSERT в parent партицированной таблицы.",
                "amber"
            ],
            [
                "Как",
                "gp_autostats_mode=on_no_stats не обновляет tree.",
                "red"
            ],
            [
                "Почему",
                "Autostats с leaf insert, не с parent.",
                "blue"
            ],
            [
                "Фикс",
                "ANALYZE в runbook ETL + проверка catalog.",
                "green"
            ]
        ]
    },
    {
        "kicker": "Кейс 08 · Демо",
        "title": "Три шага на стенде",
        "subtitle": "\\i lesson03-secret41-autostats-partitions.sql",
        "type": "code",
        "code_kind": "SQL",
        "code": "SET gp_autostats_mode = on_no_stats;\nINSERT INTO lesson03.sec41_sales …;     -- parent → MISSING\nINSERT INTO lesson03.sec41_sales_1_prt_1 …; -- leaf → HAS stats\nANALYZE lesson03.sec41_sales;            -- ETL policy"
    },
    {
        "kicker": "Кейс 08 · Код GP",
        "title": "analyze.c + GUC",
        "subtitle": "deep-dives/secret41-autostats-partitions.md",
        "type": "cards",
        "cards": [
            [
                "ANALYZE",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/commands/analyze.c",
                "green"
            ],
            [
                "GUC",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/utils/misc/guc.c",
                "blue"
            ],
            [
                "Док",
                "parent insert ≠ autostats; leaf insert = autostats.",
                "amber"
            ],
            [
                "Рядом",
                "gp_autostats_mode_in_functions внутри функции.",
                "red"
            ]
        ]
    },
    {
        "anchor": "case-median",
        "kicker": "Кейс 09",
        "title": "Медиана собирает все строки на мастер",
        "subtitle": "Ordered-set aggregate = полный порядок = Gather-all на QD.",
        "type": "cards",
        "cards": [
            [
                "Проблема",
                "percentile_disc глобально не считается локально exact.",
                "red"
            ],
            [
                "Сигнал в плане",
                "Gather Motion N:1 почти всех rows → Aggregate на QD.",
                "amber"
            ],
            [
                "Как чинить",
                "Exact: мириться с Gather / sample. Approx: avg(local median) при RANDOM.",
                "green"
            ],
            [
                "Стенд",
                "lesson03-secret38-median-gather-qd.sql",
                "blue"
            ]
        ]
    },
    {
        "kicker": "Кейс 09 · Суть",
        "title": "Pure MPP theory",
        "subtitle": "Глобальный порядок нельзя посчитать по кускам без потерь.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "percentile_disc(0.5) WITHIN GROUP (ORDER BY n).",
                "amber"
            ],
            [
                "Как",
                "Gather почти всех строк на QD.",
                "red"
            ],
            [
                "Approx",
                "avg(local median) GROUP BY gp_segment_id.",
                "blue"
            ],
            [
                "Цена",
                "Помечать approximate в отчётах.",
                "green"
            ]
        ]
    },
    {
        "kicker": "Кейс 09 · План",
        "title": "Exact Gather vs local medians",
        "subtitle": "Legacy показывает классическую форму; ORCA часто fallback.",
        "type": "code",
        "code_kind": "PLAN",
        "code": "A exact:\n  Aggregate → Gather Motion (все rows) → Seq Scan\n\nB approx:\n  avg(percentile_disc … GROUP BY gp_segment_id)\n\nLab median=500; approx≈500.5"
    },
    {
        "kicker": "Кейс 09 · Код GP",
        "title": "orderedsetaggs.c",
        "subtitle": "deep-dives/secret38-median-gather-qd.md",
        "type": "cards",
        "cards": [
            [
                "Ordered-set",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/utils/adt/orderedsetaggs.c",
                "green"
            ],
            [
                "nodeAgg",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeAgg.c",
                "blue"
            ],
            [
                "Motion",
                "https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeMotion.c",
                "amber"
            ],
            [
                "Теория",
                "Глобальный порядок = данные к одному месту.",
                "red"
            ]
        ]
    },
    {
        "anchor": "stage-wrap",
        "kicker": "Этап 7",
        "title": "Закрепление",
        "subtitle": "Checklist, маршруты занятия, что унести.",
        "type": "cards",
        "cards": [
            [
                "Checklist",
                "Definition of done для rewrite.",
                "green"
            ],
            [
                "Маршруты",
                "Core 60 / Core 90 / Full — skip-map у ментора.",
                "blue"
            ],
            [
                "Summary",
                "Метод + кейсы + навигация.",
                "amber"
            ],
            [
                "Appendix",
                "Справочник: кнопка ниже или «☰ Меню» → Appendix.",
                "green"
            ]
        ],
        "jumps": [
            {"label": "→ Appendix: старт справочника", "anchor": "appendix"},
            {"label": "→ Appendix: история ORCA/Legacy", "anchor": "appendix-history"},
        ],
    },
    {
        "kicker": "Итог · Checklist",
        "title": "Decision checklist Senior/Principal",
        "subtitle": "Definition of done для любого performance rewrite.",
        "type": "cards",
        "cards": [
            [
                "GUC",
                "Тот же optimizer/mem на before и after.",
                "green"
            ],
            [
                "Profile",
                "Motion Hash Key + misestimate + join type + spill.",
                "blue"
            ],
            [
                "Locus",
                "CTE/GROUP BY/cast меняют hash vs DISTRIBUTED BY?",
                "amber"
            ],
            [
                "Proof",
                "Metrics + plan shape + residual risk.",
                "red"
            ]
        ]
    },
    {
        "kicker": "Итог · Маршруты",
        "title": "Core 60 / Core 90 / Full — что листать",
        "subtitle": "См. «Как смотреть эту презентацию» в начале. Не всё читать вслух.",
        "type": "cards",
        "cards": [
            [
                "Core 60",
                "~30 LIVE: проблема → plan 1–5 → sel lite → TEMP → proof. Словарь/детали — клик.",
                "green"
            ],
            [
                "Core 90",
                "~45 LIVE: + MCV/hist (смысл), storage decision, 2 кейса (01 + 03 или 08).",
                "blue"
            ],
            [
                "Full",
                "Все учебные слайды + appendix по кнопкам. Порталы — только возврат, не урок.",
                "amber"
            ],
            [
                "Homework",
                "Остальные кейсы + RFC evidence pack. Не жечь live-время на 01–09 подряд.",
                "green"
            ]
        ],
        "jumps": [
            {"label": "→ Appendix: GPORCA memo", "anchor": "appendix-orca"},
            {"label": "→ Appendix: spill deep-dive", "anchor": "appendix-spill"},
        ],
    },
    {
        "kicker": "Итог · Summary",
        "title": "Что унести с собой",
        "subtitle": "Метод + теория + 9 именованных кейсов оптимизации.",
        "type": "cards",
        "cards": [
            [
                "Метод",
                "Симптом → profile → гипотеза → stage → proof.",
                "green"
            ],
            [
                "Теория",
                "План MPP · статистика · storage.",
                "blue"
            ],
            [
                "Кейсы",
                "CE, SCD2, NOT IN, window, VALUES, DISTINCT, autostats, median.",
                "amber"
            ],
            [
                "Навигация",
                "☰ Меню и Словарь на каждом слайде.",
                "green"
            ]
        ]
    }
]

CORE_SLIDES = prepend_front_matter(_CORE_BODY)

assert 70 <= len(CORE_SLIDES) <= 140, len(CORE_SLIDES)
