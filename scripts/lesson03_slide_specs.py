"""Slide specifications for Lesson 03 Greenplum query-tuning deck.

Kept separate from the PPTX renderer so content (glossary, plan trees,
code links) can evolve without touching layout helpers.
"""

from __future__ import annotations

# Real EXPLAIN snippets captured from labs/greenplum-625 (GP 6.25.3).
# Full screenshots: artifacts/lesson03-plan-screens/explain-*.png
# Raw text: artifacts/lesson03-plans/*.txt

GPDB_6X = "https://github.com/greenplum-db/gpdb/blob/6X_STABLE"

PLAN_SIMPLE = """Gather Motion 2:1  (slice2; segments: 2)
  ->  GroupAggregate
        Group Key: region
        ->  Sort
              ->  Redistribute Motion 2:2  (slice1)
                    Hash Key: region
                    ->  HashAggregate
                          ->  Seq Scan on dim_customer
Optimizer: Pivotal Optimizer (GPORCA)"""

PLAN_ORCA_STAR = """Limit
  ->  Gather Motion 2:1  (slice3)          -- Execute: gather to QD
        ->  Sort + HashAggregate           -- final grain
              ->  Redistribute Motion 2:2  (slice2)  -- by group keys
                    ->  HashAggregate      -- partial agg on QE
                          ->  Hash Join fact ⋈ product
                                ->  Redistribute Motion 2:2  (slice1)
                                      Hash Key: product_id
                                      ->  Hash Join fact ⋈ customer
                                            ->  Seq Scan fact_sales
                                            ->  Seq Scan dim_customer
                                ->  Seq Scan dim_product
Optimizer: Pivotal Optimizer (GPORCA)"""

PLAN_LEGACY_STAR = """Limit
  ->  Gather Motion 2:1  (slice3)
        ->  Sort + HashAggregate
              ->  Redistribute Motion 2:2  (slice2)
                    ->  HashAggregate
                          ->  Hash Join fact ⋈ customer   -- другой order
                                ->  Hash Join fact ⋈ product
                                      ->  Seq Scan fact_sales
                                      ->  Seq Scan dim_product
                                ->  Seq Scan dim_customer
Optimizer: Postgres query optimizer   -- Legacy"""

PLAN_PHASES = """Parse     → raw parse tree (grammar)
Rewrite   → view expand: v_* → JOIN/WHERE tree
Optimize  → GPORCA memo | Legacy path tree + Motion
Dispatch  → QD режет plan на slices/gangs → QE
Execute   → QE: Scan/Join/Agg + Motion interconnect
            slice N Gather → результат на QD

Смотрите в EXPLAIN: sliceK; segments: N + тип Motion."""

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
        "kicker": "Glossary",
        "title": "Словарь сокращений (1/3) — читайте до «GUC optimizer»",
        "subtitle": "Без расшифровок слайды звучат как внутренний жаргон. Держите этот слайд открытым.",
        "type": "cards",
        "cards": [
            [
                "GUC",
                "Grand Unified Configuration — параметр сервера PostgreSQL/Greenplum "
                "(SHOW/SET / postgresql.conf). Пример: GUC optimizer включает GPORCA или Legacy.",
                "green",
            ],
            [
                "QD / QE",
                "Query Dispatcher (master/coordinator строит план и координирует) / "
                "Query Executor (segment исполняет slice плана).",
                "blue",
            ],
            [
                "MPP",
                "Massively Parallel Processing — запрос режется на slices и бежит параллельно "
                "на сегментах с обменом через interconnect.",
                "amber",
            ],
            [
                "GPORCA / ORCA",
                "Pivotal Optimizer (Cascades/memo). Включается GUC optimizer=on. "
                "В EXPLAIN: Optimizer: Pivotal Optimizer (GPORCA).",
                "green",
            ],
        ],
    },
    {
        "kicker": "Glossary",
        "title": "Словарь сокращений (2/3) — план, storage, stats",
        "subtitle": "Эти термины появятся в каждом EXPLAIN и deep-dive.",
        "type": "cards",
        "cards": [
            [
                "Motion / Slice / Gang",
                "Motion — обмен строк между сегментами (Redistribute/Broadcast/Gather). "
                "Slice — кусок плана на gang процессов QE.",
                "green",
            ],
            [
                "Legacy planner",
                "Postgres-based planner Greenplum (optimizer=off). "
                "В EXPLAIN: Optimizer: Postgres query optimizer.",
                "blue",
            ],
            [
                "AO / AOCO / DXL",
                "Append-Only (row) / Append-Only Column-Oriented. "
                "DXL — XML-IR между GPORCA и executor (gpopt translator).",
                "amber",
            ],
            [
                "MCV / TEMP",
                "Most Common Values в pg_statistic. TEMP — явная temp-таблица "
                "(не путать с spill files при нехватке work_mem).",
                "green",
            ],
        ],
    },
    {
        "kicker": "Glossary",
        "title": "Словарь (3/3) — star-join и схемы данных",
        "subtitle": "До слайдов с ORCA/Legacy на v_star_join_orca_case — что значит «star».",
        "type": "cards",
        "cards": [
            [
                "Star-join",
                "Запрос к fact-таблице + несколько dimension по FK "
                "(«звезда»: факты в центре, dims по лучам). Много equi-joins от одной fact.",
                "green",
            ],
            [
                "Fact / Dimension",
                "Fact — события/меры (продажи, amount). "
                "Dimension — справочники (клиент, продукт, дата) с атрибутами для GROUP BY.",
                "blue",
            ],
            [
                "Snowflake",
                "Dims нормализованы дальше (dim → sub-dim). "
                "Больше joins, чем у чистой star; сложнее reorder для planner.",
                "amber",
            ],
            [
                "Почему важно в GP",
                "Join order + Broadcast/Redistribute dims сильно меняют Motion cost. "
                "Здесь ORCA часто сильнее Legacy.",
                "red",
            ],
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
            "GUC optimizer on/off, ANALYZE, TEMP stages, DISTRIBUTED BY, Heap/AO/AOCO.",
            "green",
        ],
    },
    {
        "kicker": "Pipeline",
        "title": "Как Greenplum оптимизирует запрос: стадии",
        "subtitle": "QD строит план; QE исполняют slices. Ошибка на стадии Optimize = дорогая сеть.",
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
        "kicker": "Phases → tree",
        "title": "Одно дерево на все фазы (ментальная карта)",
        "subtitle": "Ниже — не AST дамп, а то, что Senior должен видеть в голове при чтении EXPLAIN.",
        "type": "code",
        "code": PLAN_PHASES,
    },
    {
        "kicker": "Parse",
        "title": "Фаза Parse: SQL → parse tree",
        "subtitle": "Грамматика + analyze. Ещё нет Motion и cost — только синтаксическая форма.",
        "type": "cards",
        "cards": [
            ["Вход", "Текст SQL / prepared statement.", "green"],
            ["Выход", "Raw/parsed statement tree (SelectStmt…).", "blue"],
            [
                "Код GPDB",
                f"parser/: {GPDB_6X}/src/backend/parser/gram.y\n"
                f"analyze: {GPDB_6X}/src/backend/parser/analyze.c",
                "amber",
            ],
            ["Практика", "Ошибки синтаксиса живут здесь; план ещё не существует.", "green"],
        ],
    },
    {
        "kicker": "Rewrite",
        "title": "Фаза Rewrite: views/rules → query tree",
        "subtitle": "v_heavy_olap_monolith разворачивается в JOIN/WHERE до Optimize.",
        "type": "two",
        "left": [
            "Что происходит",
            "View expansion, rule rewrite, иногда subquery pull-up. "
            "Оптимизатор уже видит развёрнутый join graph, не имя view.",
            "blue",
        ],
        "right": [
            "Код GPDB",
            f"rewriteHandler.c — {GPDB_6X}/src/backend/rewrite/rewriteHandler.c\n"
            "На стенде: \\d+ lesson03.v_star_join_orca_case",
            "green",
        ],
    },
    {
        "kicker": "Optimize = GUC",
        "title": "Фаза Optimize: кто строит plan — решает GUC optimizer",
        "subtitle": "GUC = Grand Unified Configuration. SET optimizer выбирает движок поиска плана.",
        "type": "code",
        "code": (
            "-- GUC optimizer (session / role / postgresql.conf)\n"
            "SHOW optimizer;              -- on | off\n"
            "SET optimizer = on;           -- GPORCA (Pivotal Optimizer)\n"
            "SET optimizer = off;          -- Legacy Postgres-based planner\n\n"
            "-- Маркер в EXPLAIN (снято с greenplum-625):\n"
            "--   Optimizer: Pivotal Optimizer (GPORCA)\n"
            "--   Optimizer: Postgres query optimizer\n\n"
            "-- Важно: SET живёт в сессии psql; новый коннект = default."
        ),
    },
    {
        "kicker": "Code map",
        "title": "Карта кода Greenplum 6.x: куда смотреть в gpdb",
        "subtitle": "Ветка 6X_STABLE на github.com/greenplum-db/gpdb — якоря для deep-dive.",
        "type": "cards",
        "cards": [
            [
                "Legacy planner",
                f"optimizer/plan/planner.c\n{GPDB_6X}/src/backend/optimizer/plan/planner.c\n"
                f"+ cdbpath Motion: {GPDB_6X}/src/backend/cdb/cdbpath.c",
                "green",
            ],
            [
                "GPORCA core",
                f"src/backend/gporca (memo/xforms)\n"
                f"{GPDB_6X.replace('/blob/', '/tree/')}/src/backend/gporca",
                "blue",
            ],
            [
                "Translator DXL",
                f"src/backend/gpopt — DXL ↔ Plan\n"
                f"{GPDB_6X.replace('/blob/', '/tree/')}/src/backend/gpopt",
                "amber",
            ],
            [
                "Dispatch / Motion",
                f"cdbdisp*, execMotion*\n"
                f"{GPDB_6X.replace('/blob/', '/tree/')}/src/backend/cdb",
                "green",
            ],
        ],
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
        "kicker": "Star-join",
        "title": "Star-join на пальцах: fact в центре, dims по лучам",
        "subtitle": "Классическая OLAP-форма. На стенде: lesson03.fact_sales ⋈ dim_customer ⋈ dim_product …",
        "type": "code",
        "code": (
            "                    dim_customer\n"
            "                         \\\n"
            "        dim_date ---- fact_sales ---- dim_product\n"
            "                         /\n"
            "                  dim_store (если есть)\n\n"
            "-- Пример со стенда (упрощённый star; lab ещё дублирует joins):\n"
            "SELECT c.region, d.category, sum(f.amount) AS revenue\n"
            "FROM lesson03.fact_sales f          -- FACT (центр)\n"
            "JOIN lesson03.dim_customer c        -- DIM\n"
            "  ON c.customer_id = f.customer_id\n"
            "JOIN lesson03.dim_product d         -- DIM\n"
            "  ON d.product_id = f.product_id\n"
            "WHERE f.sale_date >= DATE '2026-02-01'\n"
            "  AND c.segment <> 'test'\n"
            "GROUP BY c.region, d.category;\n\n"
            "-- Признаки star-join: 1 большая fact + N маленьких dims по FK;\n"
            "-- фильтры на fact/dim; agg по атрибутам dims."
        ),
    },
    {
        "kicker": "Star-join",
        "title": "Альтернативы star-join и когда их брать",
        "subtitle": "Star — не единственный shape. Выбор = модель данных + стоимость Motion/planning.",
        "type": "cards",
        "cards": [
            [
                "Snowflake",
                "Dims разбиты (product → brand → category). "
                "Больше joins; иногда яснее модель, чаще больнее planner.",
                "amber",
            ],
            [
                "Wide / denorm fact",
                "Атрибуты dims уже в fact (region, category в строке продажи). "
                "Меньше joins, больше хранения и риска рассинхрона.",
                "blue",
            ],
            [
                "TEMP stages",
                "Сначала сузить fact → TEMP, потом 1–2 join к dims. "
                "Контролируемый physical stage вместо одного many-join SQL.",
                "green",
            ],
            [
                "Меньше joins / views",
                "Убрать дубли JOIN (как c2/d2 в v_star_join_orca_case) — "
                "demo-перегруз для ORCA; в prod это anti-pattern.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Plan tree",
        "title": "Дерево плана: простой agg (реальный EXPLAIN GP 6.25)",
        "subtitle": "Фазы Optimize→Dispatch→Execute видны как slices + Motion. Стенд greenplum-625.",
        "type": "code",
        "code": PLAN_SIMPLE,
    },
    {
        "kicker": "Screenshot",
        "title": "Скрин EXPLAIN: GPORCA на простом GROUP BY",
        "subtitle": "artifacts/lesson03-plan-screens/explain-simple.png — снято с живого стенда.",
        "type": "image",
        "image": "artifacts/lesson03-plan-screens/explain-simple.png",
    },
    {
        "kicker": "Plan tree",
        "title": "Дерево плана: star-join под GPORCA (сжатый readout)",
        "subtitle": "Тот же SQL, что в демо. Полный скрин — следующий слайд; raw: artifacts/lesson03-plans/orca.txt",
        "type": "code",
        "code": PLAN_ORCA_STAR,
    },
    {
        "kicker": "Screenshot",
        "title": "Скрин EXPLAIN: GPORCA star-join (v_star_join_orca_case)",
        "subtitle": "Ищите Redistribute до/после Hash Join и маркер Optimizer: GPORCA.",
        "type": "image",
        "image": "artifacts/lesson03-plan-screens/explain-orca.png",
    },
    {
        "kicker": "Plan tree",
        "title": "Дерево плана: тот же SQL под Legacy",
        "subtitle": "Другой join order и маркер Postgres query optimizer. Скрин — следующий слайд.",
        "type": "code",
        "code": PLAN_LEGACY_STAR,
    },
    {
        "kicker": "Screenshot",
        "title": "Скрин EXPLAIN: Legacy на том же star-join",
        "subtitle": "Сравнивайте join order и положение Redistribute с предыдущим скрином ORCA.",
        "type": "image",
        "image": "artifacts/lesson03-plan-screens/explain-legacy.png",
    },
    {
        "kicker": "Screenshot",
        "title": "Скрин EXPLAIN: monolith (WindowAgg + multi-slice)",
        "subtitle": "v_heavy_olap_monolith: несколько Redistribute + WindowAgg — типичный «дорогой» OLAP shape.",
        "type": "image",
        "image": "artifacts/lesson03-plan-screens/explain-monolith.png",
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
            ["MCV", "Most Common Values для equality/IN.", "blue"],
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
            [
                "analyze.c",
                f"Sampling и MCV/histogram.\n{GPDB_6X}/src/backend/commands/analyze.c",
                "green",
            ],
            [
                "selfuncs.c",
                f"Selectivity для costing.\n{GPDB_6X}/src/backend/utils/adt/selfuncs.c",
                "blue",
            ],
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
        "kicker": 'TEMP trio',
        "title": 'Три разных «временных» механизма — не путать',
        "subtitle": 'CTE, TEMP TABLE и spill/workfiles живут в разных слоях стека.',
        "type": 'cards',
        "cards": [
            ['CTE / WITH', 'Логическая подзапросная форма. Optimizer может инлайнить — нет гарантированного physical stage, stats, DISTRIBUTED BY.', 'amber'],
            ['TEMP TABLE', 'Явная relation в pg_temp_NNN. Catalog + relfilenode t_* на QE. Можно ANALYZE и задать distribution.', 'green'],
            ['Spill / workfiles', 'Файлы исполнителей Sort/Hash при нехватке statement_mem. Путь: <datadir>/base/pgsql_tmp/pgsql_tmp_Sort_*. Не relation.', 'red'],
            ['Правило', '«Не было CREATE TEMP ⇒ не было диска» — ложь. Spill пишется и без TEMP TABLE.', 'blue'],
        ],
    },
    {
        "kicker": 'TEMP create',
        "title": 'Как создаётся TEMP: SQL-контракт сессии',
        "subtitle": 'Lifecycle = сессия (или ON COMMIT). Другие сессии объект не видят.',
        "type": 'code',
        "code": "CREATE TEMP TABLE tmp_stage AS\nSELECT customer_id, product_id, amount\nFROM lesson03.fact_sales\nWHERE sale_date >= DATE '2026-02-01'\n  AND sale_date <  DATE '2026-03-01'\nDISTRIBUTED BY (customer_id);   -- обязательный контракт в GP\nANALYZE tmp_stage;               -- иначе следующий plan врёт\n\n-- Варианты lifecycle:\n-- CREATE TEMP TABLE ... ON COMMIT PRESERVE ROWS;  -- default\n-- CREATE TEMP TABLE ... ON COMMIT DROP;\n-- CREATE TEMP TABLE ... ON COMMIT DELETE ROWS;\n\n-- Каталог: nspname = pg_temp_<backend>, relpersistence = 't'",
    },
    {
        "kicker": 'TEMP where',
        "title": 'Где живёт TEMP в Greenplum MPP',
        "subtitle": 'Не отдельный tempdb: та же БД, временный schema, данные на сегментах.',
        "type": 'cards',
        "cards": [
            ['Namespace', 'pg_temp_NNN (+ pg_toast_temp_NNN). Session-local; после disconnect schema исчезает.', 'green'],
            ['Catalog', "Обычные pg_class/pg_attribute во временном namespace. relpersistence='t', filepath base/<dboid>/t_<relfilenode>.", 'blue'],
            ['QD vs QE', 'QD координирует DDL/план. Данные TEMP лежат на QE (master часто держит 0-byte placeholder).', 'amber'],
            ['Distribution', 'TEMP — распределённая таблица. Неверный DISTRIBUTED BY ⇒ лишний Redistribute на следующем join.', 'red'],
        ],
    },
    {
        "kicker": 'TEMP FS map',
        "title": 'Файловая карта: TEMP relation vs spill',
        "subtitle": 'Снято с greenplum-625: два разных каталога под /data/*/gpsne*/base/.',
        "type": 'code',
        "code": '# TEMP TABLE (явная relation)\n/data/data1/gpsne0/base/12812/t_16465     # ~1.1 MB на seg0\n/data/data2/gpsne1/base/12812/t_16465     # ~1.2 MB на seg1\n/data/master/gpsne-1/base/12812/t_16465   # 0 bytes (QD placeholder)\n# pg_relation_filepath → base/12812/t_16465\n# nspname = pg_temp_787, relpersistence = t\n\n# Spill / workfiles (исполнитель Sort/Hash)\n/data/data1/gpsne0/base/pgsql_tmp/pgsql_tmp_Sort_1_<pid>.0\n/data/data2/gpsne1/base/pgsql_tmp/pgsql_tmp_Sort_1_<pid>.0\n# растут во время query, удаляются после завершения',
    },
    {
        "kicker": 'Screenshot',
        "title": 'Скрин FS: TEMP relfilenode t_* на сегментах',
        "subtitle": 'После CREATE TEMP … AS SELECT … DISTRIBUTED BY — данные на QE, не в pgsql_tmp.',
        "type": 'image',
        "image": 'artifacts/lesson03-plan-screens/temp-relfilenode-fs.png',
    },
    {
        "kicker": 'TEMP code',
        "title": 'Код GPDB 6X_STABLE: TEMP и workfiles',
        "subtitle": 'Якоря для deep-dive чтения, не «магия кластера».',
        "type": 'cards',
        "cards": [
            ['TEMP namespace', 'catalog/namespace.c — InitTempTableNamespace\nhttps://github.com/greenplum-db/gpdb/blob/6X_STABLE/src/backend/catalog/namespace.c', 'green'],
            ['Heap / relfilenode', 'storage/smgr + heapam; temp prefix t_\nhttps://github.com/greenplum-db/gpdb/tree/6X_STABLE/src/backend/storage', 'blue'],
            ['Workfile manager', 'utils/workfile_manager/workfile_mgr.c\nhttps://github.com/greenplum-db/gpdb/tree/6X_STABLE/src/backend/utils/workfile_manager', 'amber'],
            ['GUC памяти', 'statement_mem / max_statement_mem, gp_workfile_limit_*, gp_workfile_compression.', 'green'],
        ],
    },
    {
        "kicker": 'Spill',
        "title": 'Spill deep-dive: когда executor пишет pgsql_tmp',
        "subtitle": 'GUC statement_mem (на GP6 work_mem deprecated). Маркер в EXPLAIN ANALYZE.',
        "type": 'code',
        "code": "-- Демо со стенда (ужать память → external sort):\nSET optimizer = off;\nSET statement_mem = '8MB';\nEXPLAIN ANALYZE\nSELECT customer_id, product_id, amount, sale_date\nFROM tmp_spill_fuel   -- ~1M rows amplified TEMP\nORDER BY amount DESC, customer_id, product_id, sale_date;\n\n-- Факт с greenplum-625:\n-- Sort Method: external merge  Disk: 34592kB\n-- Memory used: 8192kB   Memory wanted: 58688kB\n-- FS: pgsql_tmp_Sort_1_*.0 рос 0.4MB → 17MB на сегмент, потом cleanup",
    },
    {
        "kicker": 'Screenshot',
        "title": 'Скрин FS: рост spill-файлов pgsql_tmp_Sort_*',
        "subtitle": 'Поллинг во время EXPLAIN ANALYZE: bytes на seg0/seg1 растут, после query → cleanup.',
        "type": 'image',
        "image": 'artifacts/lesson03-plan-screens/spill-pgsql_tmp-growth.png',
    },
    {
        "kicker": 'Screenshot',
        "title": 'Скрин EXPLAIN: external merge Disk = spill',
        "subtitle": 'Связка план ↔ файлы: Disk: NNkB в EXPLAIN = pgsql_tmp_Sort_* на сегментах.',
        "type": 'image',
        "image": 'artifacts/lesson03-plan-screens/spill-explain-external-merge.png',
    },
    {
        "kicker": 'TEMP ±',
        "title": 'Плюсы и минусы TEMP TABLE',
        "subtitle": 'Physical stage — инструмент, не бесплатный cache.',
        "type": 'two',
        "left": ['Плюсы', 'Фиксирует grain; свой DISTRIBUTED BY; ANALYZE → честный следующий plan; можно переиспользовать в сессии; проще доказать before/after; отделяет дорогой фильтр от join/window.', 'green'],
        "right": ['Минусы', 'Двойной IO (write+read); место на дисках всех сегментов; catalog/planning overhead; риск устаревших данных в сессии; без фильтра = дорогой materialize всего fact.', 'red'],
    },
    {
        "kicker": 'TEMP when',
        "title": 'Когда TEMP хорошо / когда плохо',
        "subtitle": 'Критерий: stage уменьшает cardinality/Motion cost больше, чем стоит materialize.',
        "type": 'two',
        "left": ['Хорошо', 'Узкое окно дат + anti-test; grain под следующий join key; повторное использование stage в сессии; стабилизация плана после ANALYZE; разрез монолита на доказуемые шаги.', 'green'],
        "right": ['Плохо', 'TEMP = весь fact без фильтра; забыли ANALYZE; DISTRIBUTED BY не под join; десятки мелких TEMP; вместо фикса stats/skew; CTE «для красоты» без physical need; игнор spill (диск растёт без CREATE TEMP).', 'red'],
    },
    {
        "kicker": 'Rewrite',
        "title": 'Паттерн rewrite + проверка optimizer',
        "subtitle": 'Before/after при фиксированном SET optimizer (GUC сессии) + FS sanity.',
        "type": 'code',
        "code": "SET optimizer = on;  -- зафиксировали GUC\nCREATE TEMP TABLE tmp_sales_feb AS\nSELECT customer_id, product_id, amount\nFROM lesson03.fact_sales\nWHERE sale_date >= DATE '2026-02-01'\n  AND sale_date <  DATE '2026-03-01'\nDISTRIBUTED BY (customer_id);\nANALYZE tmp_sales_feb;\nEXPLAIN ...\n\n-- Evidence pack:\n-- 1) before/after EXPLAIN (тот же optimizer)\n-- 2) pg_relation_filepath / размер TEMP\n-- 3) при spill: Sort Method external merge + pgsql_tmp_Sort_*",
    },
    {
        "kicker": "Simple path",
        "title": "60 минут на GP 6.25",
        "subtitle": "Glossary → case → optimizer → EXPLAIN trees → stats → TEMP → proof.",
        "type": "flow",
        "flow": [
            ["Glossary", "GUC/QD/QE", "green"],
            ["ORCA", "on vs off", "blue"],
            ["Trees", "скрины", "amber"],
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
            ["GUC", "optimizer on/off — явный выбор движка плана.", "green"],
            ["TEMP ≠ spill", "t_* relation на QE vs pgsql_tmp_Sort_* workfiles.", "blue"],
            ["Доказательство", "before/after EXPLAIN + ANALYZE/distribution + FS sanity.", "amber"],
        ],
    },
]
