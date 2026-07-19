"""Appendix (deep reference) slide specs for Lesson 03.

Kept separate from the PPTX renderer so content (glossary, plan trees,
code links) can evolve without touching layout helpers.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Real EXPLAIN snippets captured from labs/greenplum-625 (GP 6.25.3).
# Full screenshots: lessons/lesson-03/artifacts/plan-screens/explain-*.png
# Raw text: lessons/lesson-03/artifacts/plans/*.txt

GPDB_6X = "https://github.com/greenplum-db/gpdb-archive/blob/main"
GPDB_ORCA = (
    "https://github.com/apache/cloudberry/blob/main/src/backend/gporca"
)

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from lesson03_front_matter import APPENDIX_POINTER
from lesson03_principal_abc_slides import APPENDIX_ABC_SLIDES
from lesson03_secrets_case_slides import APPENDIX_SECRETS_SLIDES

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

APPENDIX_SLIDES = [
    APPENDIX_POINTER,
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
            "View/rule expansion (rewriter). Subquery pull-up — planner preprocessing (prepjointree), не rewrite. "
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
        "subtitle": "Якоря: gpdb-archive (Legacy/CDB) + apache/cloudberry (GPORCA).",
        "type": "cards",
        "cards": [
            [
                "Legacy planner",
                f"planner.c + cdbpath\n{GPDB_6X}/src/backend/optimizer/plan/planner.c",
                "green",
            ],
            [
                "GPORCA core",
                f"memo/xforms/stats\n{GPDB_ORCA}",
                "blue",
            ],
            [
                "Selectivity",
                f"selfuncs.c / clausesel.c\n{GPDB_6X}/src/backend/utils/adt/selfuncs.c",
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
        "kicker": "History",
        "title": "История: зачем в Greenplum два оптимизатора",
        "subtitle": "Legacy = Postgres lineage. GPORCA = ответ на MPP/OLAP, не «вторая кнопка».",
        "type": "cards",
        "cards": [
            [
                "До 2010",
                "Greenplum на PostgreSQL planner + Motion/locus. "
                "Хорошо для короткого SQL, слабо для many-join DWH.",
                "amber",
            ],
            [
                "2010 →",
                "Внутренний проект Greenplum/Pivotal: новый optimizer. "
                "Лидер направления — Florian Waas; архитектура — Soliman et al.",
                "blue",
            ],
            [
                "2014 SIGMOD",
                "Orca: A Modular Query Optimizer Architecture for Big Data — "
                "Cascades/memo, portable, tooling (AMPERE).",
                "green",
            ],
            [
                "GP 4.3.5 → GP5",
                "Появление в продукте; с Greenplum 5 GPORCA = default. "
                "Legacy остаётся fallback и SET optimizer=off.",
                "green",
            ],
        ],
    },
    {
        "kicker": "History",
        "title": "Почему Legacy «не хватило» для MPP analytics",
        "subtitle": "PostgreSQL planner рождался под OLTP single-node — другая целевая функция.",
        "type": "cards",
        "cards": [
            [
                "OLTP vs OLAP",
                "Короткие lookup vs длинные scan/agg/window на терабайтах.",
                "red",
            ],
            [
                "Many-join",
                "Star/snowflake: локальный join search часто даёт "
                "локальный минимум порядка joins.",
                "amber",
            ],
            [
                "Motion cost",
                "Redistribute/Broadcast часто дороже CPU — "
                "нужен first-class costing распределения.",
                "blue",
            ],
            [
                "Partitions",
                "Тысячи leaf partitions: Legacy OOM/slow; "
                "ORCA — partition-aware transforms.",
                "green",
            ],
        ],
    },
    {
        "kicker": "History",
        "title": "Таймлайн GPORCA (четыре якоря)",
        "subtitle": "2010 start → 2014 paper → 4.3.5 ship → GP5 default.",
        "type": "flow",
        "flow": [
            ["2010", "Старт Orca", "amber"],
            ["2014", "SIGMOD paper", "blue"],
            ["4.3.5", "В продукте", "green"],
            ["GP5", "Default on", "green"],
            ["OSS", "gporca в git", "blue"],
        ],
    },
    {
        "kicker": "History",
        "title": "Почему Legacy не удалили",
        "subtitle": "Два оптимизатора — осознанная архитектура, не техдолг «на потом».",
        "type": "cards",
        "cards": [
            [
                "Planning time",
                "Простой SQL: Legacy часто дешевле compile.",
                "green",
            ],
            [
                "Fallback",
                "Feature gap ORCA → Postgres query optimizer.",
                "amber",
            ],
            [
                "Mental model",
                "selfuncs/EXPLAIN привычны PostgreSQL-инженерам.",
                "blue",
            ],
            [
                "Runtime niche",
                "Иногда Legacy быстрее на узком классе запросов — "
                "решает EXPLAIN ANALYZE, не идеология.",
                "red",
            ],
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
        "title": "Star-join: fact в центре, dims по лучам",
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
        "subtitle": "lessons/lesson-03/artifacts/plan-screens/explain-simple.png — снято с живого стенда.",
        "type": "image",
        "image": "lessons/lesson-03/artifacts/plan-screens/explain-simple.png",
    },
    {
        "kicker": "Plan tree",
        "title": "Дерево плана: star-join под GPORCA (сжатый readout)",
        "subtitle": "Тот же SQL, что в демо. Полный скрин — следующий слайд; raw: lessons/lesson-03/artifacts/plans/orca.txt",
        "type": "code",
        "code": PLAN_ORCA_STAR,
    },
    {
        "kicker": "Screenshot",
        "title": "Скрин EXPLAIN: GPORCA star-join (v_star_join_orca_case)",
        "subtitle": "Ищите Redistribute до/после Hash Join и маркер Optimizer: GPORCA.",
        "type": "image",
        "image": "lessons/lesson-03/artifacts/plan-screens/explain-orca.png",
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
        "image": "lessons/lesson-03/artifacts/plan-screens/explain-legacy.png",
    },
    {
        "kicker": "Screenshot",
        "title": "Скрин EXPLAIN: monolith (WindowAgg + multi-slice)",
        "subtitle": "v_heavy_olap_monolith: несколько Redistribute + WindowAgg — типичный «дорогой» OLAP shape.",
        "type": "image",
        "image": "lessons/lesson-03/artifacts/plan-screens/explain-monolith.png",
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
        "title": "Кейс: ORCA выбрал иной shape (проверить на объёме)",
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
        "subtitle": "Сначала доказать estimate vs actual, потом rewrite/optimizer.",
        "type": "code",
        "code": (
            "EXPLAIN ANALYZE\n"
            "SELECT ...;\n\n"
            "-- Ищем на каждом узле:\n"
            "--   rows=<estimate>  vs  actual rows=<fact>\n"
            "-- Порог тревоги: x5–x10 на join/agg input\n"
            "-- Дальше: pg_stats → ANALYZE / SET STATISTICS → TEMP\n"
            "-- И только потом менять SQL shape / optimizer."
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
        "kicker": "Stats why",
        "title": "На что влияет статистика в Greenplum",
        "subtitle": "Не «для красоты catalog»: от rows зависят join order, Motion, mem и spill.",
        "type": "cards",
        "cards": [
            [
                "Join order / hash vs nest",
                "Estimate input rows решает, что строить в hash и какой dim Broadcast.",
                "green",
            ],
            [
                "Motion cost",
                "Завышенный rows → лишний Redistribute/Broadcast «на всякий случай».",
                "blue",
            ],
            [
                "Agg / GROUP BY",
                "NDV групп ≈ n_distinct ключей; ошибка → плохой Redistribute grain.",
                "amber",
            ],
            [
                "Memory / spill",
                "statement_mem и workfiles планируются от estimate; врёт rows → диск.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Stats anatomy",
        "title": "Из чего состоит статистика колонки",
        "subtitle": "Human view: pg_stats. Source of truth: pg_statistic slots после ANALYZE.",
        "type": "cards",
        "cards": [
            [
                "n_distinct",
                ">0 абсолют NDV; <0 доля от rows (−1 ≈ unique). "
                "База для equality без MCV и для GROUP BY.",
                "green",
            ],
            [
                "MCV + freqs",
                "most_common_vals / most_common_freqs. "
                "Equality/IN по частым значениям → берёт freq, не 1/NDV.",
                "blue",
            ],
            [
                "Histogram",
                "histogram_bounds — equi-depth корзины (равная доля строк). "
                "Для range (<, BETWEEN). MCV-значения из hist исключены.",
                "amber",
            ],
            [
                "null_frac / correlation",
                "Доля NULL; correlation физ.порядка vs logical "
                "(влияние на index/scan costing).",
                "green",
            ],
        ],
    },
    {
        "kicker": "Screenshot",
        "title": "Скрин pg_stats со стенда: MCV vs histogram",
        "subtitle": "default_statistics_target=100 → hist_n≈101. sale_date: все в MCV → hist пуст.",
        "type": "image",
        "image": "lessons/lesson-03/artifacts/plan-screens/stats-pg-stats-overview.png",
    },
    {
        "kicker": "Histogram",
        "title": "Гистограмма: equi-depth, сколько шагов, как читать",
        "subtitle": "Не bar-chart «красивый» — массив границ корзин равной плотности строк.",
        "type": "code",
        "code": (
            "-- default_statistics_target = 100  (GUC / SET / ALTER COLUMN SET STATISTICS)\n"
            "-- ANALYZE строит до ~100 MCV и ~100 histogram buckets\n"
            "-- histogram_bounds.length ≈ target + 1  (границы), на стенде: 101\n\n"
            "bucket_i ≈ (значения между bounds[i] и bounds[i+1])\n"
            "каждый bucket ≈ 1/target доли строк (equi-depth / equi-height)\n\n"
            "SELECTIVITY (col BETWEEN lo AND hi):\n"
            "  доля полных корзин внутри [lo,hi]\n"
            "  + доля края (линейная интерполяция в partial bucket)\n\n"
            "-- На стенде amount: bounds {1.67, 4.33, 6.67, ...}\n"
            "-- sale_date: hist NULL — NDV мал, всё ушло в MCV"
        ),
    },
    {
        "kicker": "Histogram",
        "title": "Как выглядит histogram в pg_stats (пример)",
        "subtitle": "Границы — квантили non-MCV sample. MCV из hist исключены.",
        "type": "code",
        "code": (
            "SELECT attname,\n"
            "       histogram_bounds[1] AS lo,\n"
            "       histogram_bounds[2] AS q1,\n"
            "       histogram_bounds[array_length(histogram_bounds,1)] AS hi,\n"
            "       array_length(histogram_bounds,1) AS hist_n\n"
            "FROM pg_stats\n"
            "WHERE schemaname='lesson03' AND tablename='fact_sales'\n"
            "  AND attname='amount';\n\n"
            "-- Типичный readout:\n"
            "-- lo≈1.67  q1≈4.33  hi≈max  hist_n=101  (target=100)\n"
            "-- stakind=2 в pg_statistic; большие arrays → TOAST"
        ),
    },
    {
        "kicker": "Screenshot",
        "title": "Скрин: структура histogram + физический слот",
        "subtitle": "stakind=2 → stavalues = bounds array в tuple pg_statistic (возможен TOAST).",
        "type": "image",
        "image": "lessons/lesson-03/artifacts/plan-screens/stats-histogram-structure.png",
    },
    {
        "kicker": "Histogram",
        "title": "Как обновляется гистограмма",
        "subtitle": "Hist живёт только после ANALYZE; SET STATISTICS меняет target колонки.",
        "type": "cards",
        "cards": [
            [
                "ANALYZE",
                "Sample → rebuild MCV + bounds. После bulk load / exchange — обязательно.",
                "green",
            ],
            [
                "SET STATISTICS N",
                "ALTER COLUMN … SET STATISTICS 200; ANALYZE — больше buckets/MCV.",
                "blue",
            ],
            [
                "TEMP",
                "CREATE TEMP … AS → ANALYZE сразу, иначе оценки stage часто грубые.",
                "amber",
            ],
            [
                "Root partitions",
                "ORCA читает stats root; забыли ANALYZE root → плохие оценки.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Histogram",
        "title": "На что влияет histogram (и на что — нет)",
        "subtitle": "Главный потребитель — range predicates; equality живёт на MCV/NDV.",
        "type": "cards",
        "cards": [
            [
                "Влияет",
                "<, <=, >, >=, BETWEEN → histfrac + края; косвенно join/Motion/spill.",
                "green",
            ],
            [
                "Не заменяет MCV",
                "col = frequent_value берёт most_common_freqs, не bucket density.",
                "blue",
            ],
            [
                "Не лечит",
                "Коррелированные AND/OR, функции на колонках, stale sample.",
                "red",
            ],
            [
                "Код",
                f"ineq_histogram_selectivity в\n"
                f"{GPDB_6X}/src/backend/utils/adt/selfuncs.c",
                "amber",
            ],
        ],
    },
    {
        "kicker": "MCV",
        "title": "MCV: как выглядит и когда histogram не строится",
        "subtitle": "Частые значения + частоты. Если NDV ≤ target — весь столбец может быть MCV.",
        "type": "code",
        "code": (
            "-- dim_customer.segment на стенде:\n"
            "most_common_vals  = {enterprise, mid, smb, test}\n"
            "most_common_freqs = {0.3138, 0.3138, 0.3136, 0.0588}\n"
            "n_distinct = 4   histogram_bounds = NULL\n\n"
            "WHERE segment = 'enterprise'  → sel ≈ 0.314  (не 0.25!)\n"
            "WHERE segment = 'test'        → sel ≈ 0.059\n"
            "WHERE segment = 'unknown'     → sel ≈ (1 - sum(mcf)) / (NDV - |MCV|)\n\n"
            "-- Физика: stakind=1; stavalues=values; stanumbers=freqs"
        ),
    },
    {
        "kicker": "Density",
        "title": "Вектор плотности в Greenplum — что это",
        "subtitle": "Не отдельный тип каталога: MCV freqs + per-bucket density в ORCA.",
        "type": "code",
        "code": (
            "-- 1) MCV frequency vector (stanumbers):\n"
            "density_MCV[i] = most_common_freqs[i] = P(col = mcv[i])\n"
            "Σ density_MCV + residual + null_frac ≈ 1\n\n"
            "-- 2) ORCA CBucket density (uniform в bucket):\n"
            "density_bucket = frequency / max(1, distinct)\n"
            "rows_one_value ≈ rows × density_bucket\n\n"
            "-- CBucket::MakeBucketSingleton:\n"
            "ratio = 1 / max(1, m_distinct)\n"
            "frequency_new = m_frequency * ratio   -- = density\n\n"
            f"-- Код: {GPDB_ORCA}/libnaucrates/src/statistics/CBucket.cpp"
        ),
    },
    {
        "kicker": "Density",
        "title": "CBucket / CHistogram — вероятностные структуры ORCA",
        "subtitle": "Legacy читает slots; ORCA материализует их в CHistogram при costing.",
        "type": "cards",
        "cards": [
            [
                "CBucket",
                "lower/upper, closedness, frequency∈[0,1], distinct (NDV).",
                "green",
            ],
            [
                "CHistogram",
                "массив buckets + NDVRemain/freqRemain + nulls.",
                "blue",
            ],
            [
                "CStatsPred*",
                "Conj / Disj / Point / ArrayCmp — дерево предикатов stats.",
                "amber",
            ],
            [
                "scale_factor",
                "ORCA: rows_out ≈ rows_in / SF; SF ≈ 1/selectivity.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Legacy formula",
        "title": "Legacy: defaults и equality (из selfuncs)",
        "subtitle": "DEFAULT_EQ_SEL=0.005 — когда stats нет. Иначе MCV / residual NDV.",
        "type": "code",
        "code": (
            "DEFAULT_EQ_SEL = 0.005\n"
            "DEFAULT_INEQ_SEL ≈ 1/3\n"
            "DEFAULT_NUM_DISTINCT = 200\n\n"
            "-- var_eq_const / eqsel:\n"
            "если const ∈ MCV:     sel = most_common_freqs[i]\n"
            "иначе:                sel = (1 − Σmcf − null) / (NDV − |MCV|)\n"
            "                      clamp ≤ min(MCV freqs)\n"
            "нет stats:            sel = 1 / NDV_est  или DEFAULT_EQ_SEL\n"
            "для <> (negate):      sel = 1 − sel − null_frac\n\n"
            f"-- {GPDB_6X}/src/backend/utils/adt/selfuncs.c\n"
            f"-- {GPDB_6X}/src/include/utils/selfuncs.h"
        ),
    },
    {
        "kicker": "Legacy formula",
        "title": "Legacy: range по histogram (ineq_histogram_selectivity)",
        "subtitle": "Бинарный поиск границы + линейная интерполяция внутри bucket.",
        "type": "code",
        "code": (
            "если const < bounds[0]:  histfrac = 0\n"
            "если const > bounds[n]:  histfrac = 1\n"
            "иначе:  binfrac = (scalar(c)−scalar(lo)) / (scalar(hi)−scalar(lo))\n"
            "        histfrac = (полные buckets + binfrac) / (n−1)\n\n"
            "-- histfrac относится к non-MCV / non-NULL популяции;\n"
            "-- scalarineqsel домножает residual и учитывает MCV в диапазоне.\n\n"
            "rows ≈ tuples × (MCV_part + residual × histfrac)"
        ),
    },
    {
        "kicker": "Legacy formula",
        "title": "Legacy: AND / OR / NOT (clausesel.c)",
        "subtitle": "Модель независимости событий. Корреляция колонок — главная ловушка.",
        "type": "code",
        "code": (
            "-- Conjunctive AND (clauselist_selectivity):\n"
            "s_AND = s1 * s2 * … * sn\n\n"
            "-- Disjunctive OR (clauselist_selectivity_or):\n"
            "s_OR  = s1 + s2 − s1*s2     -- inclusion–exclusion\n"
            "-- (итеративно для n>2)\n\n"
            "-- NOT P:\n"
            "s_NOT ≈ 1 − s_P − null_adjust   -- для strict ops\n\n"
            f"-- {GPDB_6X}/src/backend/optimizer/path/clausesel.c"
        ),
    },
    {
        "kicker": "Legacy formula",
        "title": "Legacy: IN / NOT IN / ScalarArrayOp",
        "subtitle": "IN ≈ OR equality; NOT IN ≈ AND ≠ (+ ловушки NULL).",
        "type": "cards",
        "cards": [
            [
                "IN / = ANY",
                "scalararraysel: OR по элементам; MCV freqs суммируются с поправкой.",
                "green",
            ],
            [
                "NOT IN",
                "Семантика NULL коварна; оценка через negators. "
                "Часто лучше NOT EXISTS / anti-join.",
                "red",
            ],
            [
                "ALL",
                "AND по элементам массива (useOr=false).",
                "amber",
            ],
            [
                "Практика",
                "Короткий IN из MCV → хорошая оценка; длинный IN + join → дрейф.",
                "blue",
            ],
        ],
    },
    {
        "kicker": "ORCA formula",
        "title": "ORCA: AND с damping (не чистое ∏ s)",
        "subtitle": "DDampingFactorFilter = 0.75. SF сортируются; последующие ослабляются.",
        "type": "code",
        "code": (
            "DampedFilter(n) = 0.75^n     -- n≥2; для 1 колонки → 1.0\n\n"
            "-- CalcScaleFactorCumulativeConj:\n"
            "1) отсортировать SF по убыванию (самый селективный первый)\n"
            "2) SF_AND = ∏ max(MinRows, SFᵢ · DampedFilter(i))\n\n"
            "rows_out ≈ rows_in / SF_AND\n\n"
            "-- Следствие: ORCA менее агрессивно «убивает» rows\n"
            "-- при многих AND, чем Legacy s1*s2*…\n\n"
            f"-- {GPDB_ORCA}/libnaucrates/src/statistics/CScaleFactorUtils.cpp\n"
            f"-- defaults: …/libgpopt/include/gpopt/engine/CStatisticsConfig.h"
        ),
    },
    {
        "kicker": "ORCA formula",
        "title": "ORCA: OR с damped накоплением rows",
        "subtitle": "Не классическое s1+s2−s1s2 — накопление с 0.75^k.",
        "type": "code",
        "code": (
            "-- CalcScaleFactorCumulativeDisj (комментарий в коде):\n"
            "rows ≈ rows0 + rows1·0.75 + rows2·(0.75)^2 + …\n"
            "где rowsᵢ = total_rows / SFᵢ\n\n"
            "SF_OR = total_rows / rows_acc\n\n"
            "-- Conj/Disj деревья: CStatsPredConj / CStatsPredDisj\n"
            f"-- {GPDB_ORCA}/libnaucrates/src/statistics/CFilterStatsProcessor.cpp"
        ),
    },
    {
        "kicker": "ORCA formula",
        "title": "ORCA: equality, join, defaults",
        "subtitle": "Singleton density + NDV join formula + fallback SF.",
        "type": "code",
        "code": (
            "-- Point equality в bucket:\n"
            "SF ≈ 1 / (frequency / max(1, NDV_bucket))\n\n"
            "-- Equi-join (CBucket):\n"
            "|R ⋈ S| ≈ |R|·|S| / max(NDV(R.a), NDV(S.b))\n\n"
            "DefaultInequalityJoinPredScaleFactor = 3.0\n"
            "DefaultJoinPredScaleFactor           = 100.0\n"
            "DDefaultScaleFactorLike              = 150.0\n\n"
            f"-- {GPDB_ORCA}/libnaucrates/src/statistics/CBucket.cpp"
        ),
    },
    {
        "kicker": "Selectivity",
        "title": "Сводка: один предикат — два оценщика",
        "subtitle": "Одинаковые pg_statistic slots → разные комбинаторы.",
        "type": "cards",
        "cards": [
            [
                "Legacy unit",
                "Selectivity ∈ (0,1]; rows ≈ sel × child_rows.",
                "green",
            ],
            [
                "ORCA unit",
                "scale_factor; rows ≈ rows_in / SF.",
                "blue",
            ],
            [
                "AND",
                "Legacy ∏s vs ORCA damped ∏SF (0.75^n).",
                "amber",
            ],
            [
                "OR",
                "Legacy s1+s2−s1s2 vs ORCA damped row sum.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Screenshot",
        "title": "Скрин EXPLAIN ANALYZE: хорошие оценки на стенде",
        "subtitle": "Простые предикаты + свежий ANALYZE → estimate ≈ actual.",
        "type": "image",
        "image": "lessons/lesson-03/artifacts/plan-screens/stats-estimates-good.png",
    },
    {
        "kicker": "Good est",
        "title": "Хорошие оценки: SQL-паттерны",
        "subtitle": "MCV / NDV / range / одноколоночный GROUP BY.",
        "type": "code",
        "code": (
            "-- MCV equality\n"
            "SELECT count(*) FROM lesson03.dim_customer\n"
            "WHERE segment = 'enterprise';          -- sel≈0.314\n\n"
            "-- NDV equality\n"
            "SELECT count(*) FROM lesson03.fact_sales\n"
            "WHERE product_id = 1;\n\n"
            "-- Range по hist\n"
            "SELECT count(*) FROM lesson03.fact_sales\n"
            "WHERE amount BETWEEN 10 AND 20;\n\n"
            "-- GROUP BY 1 ключ\n"
            "SELECT region, count(*) FROM lesson03.dim_customer\n"
            "GROUP BY region;                       -- groups≈4"
        ),
    },
    {
        "kicker": "Bad est",
        "title": "Плохие оценки: SQL-паттерны",
        "subtitle": "Корреляция, expr на колонке, multi GROUP BY — ломают модель.",
        "type": "code",
        "code": (
            "-- Коррелированный AND (независимость врёт)\n"
            "SELECT count(*) FROM lesson03.dim_customer\n"
            "WHERE region='us' AND segment='enterprise';\n\n"
            "-- Функция — stats колонки не применяются\n"
            "SELECT count(*) FROM lesson03.fact_sales\n"
            "WHERE date_trunc('month', sale_date) = DATE '2026-02-01';\n\n"
            "-- Multi GROUP BY: estimate ≈ ∏NDV, actual << product\n"
            "SELECT region, segment, count(*)\n"
            "FROM lesson03.dim_customer\n"
            "GROUP BY region, segment;"
        ),
    },
    {
        "kicker": "GROUP BY",
        "title": "Legacy GROUP BY: estimate_num_groups",
        "subtitle": "Эвристики Postgres: ∏NDV + clamp + restriction; не multivariate stats.",
        "type": "code",
        "code": (
            "-- estimate_num_groups (selfuncs.c), упрощённо:\n"
            "1) boolean expr → ×2 групп\n"
            "2) свести expr к уникальным Vars (a, a+b ≈ a,b)\n"
            "3) внутри rel: ∏ NDV, clamp к rows/10 при >1 Var\n"
            "4) × selectivity restriction clauses\n"
            "5) между rel — перемножить; clamp к input_rows\n\n"
            "groups(a,b) ≈ min( NDV(a)*NDV(b) [clamp], rows )\n\n"
            f"-- {GPDB_6X}/src/backend/utils/adt/selfuncs.c"
        ),
    },
    {
        "kicker": "GROUP BY",
        "title": "ORCA GROUP BY: GetCumulativeNDVs + damping",
        "subtitle": "DDampingFactorGroupBy = 0.75. NDV сортируются по убыванию.",
        "type": "code",
        "code": (
            "DampedGroupBy(i) = 0.75^(i+1)\n\n"
            "cumulative = NDV[0]   -- после sort desc\n"
            "для i=1..n-1:\n"
            "  cumulative *= max(MinDistinct, NDV[i] * DampedGroupBy(i))\n\n"
            "groups = min(cumulative, input_rows)\n\n"
            f"-- {GPDB_ORCA}/libnaucrates/src/statistics/CStatisticsUtils.cpp\n"
            f"-- CGroupByStatsProcessor::CalcGroupByStats"
        ),
    },
    {
        "kicker": "Demo SQL",
        "title": "Демо на стенде: cardinality + histogram",
        "subtitle": "labs/greenplum-625/examples/lesson03-cardinality-histogram-demo.sql",
        "type": "code",
        "code": (
            "-- в psql на mentor / lesson03:\n"
            "\\i /mentor-lab/examples/lesson03-cardinality-histogram-demo.sql\n\n"
            "-- Блоки демо:\n"
            "-- 1) pg_stats: MCV vs hist_n\n"
            "-- 2) хорошие EXPLAIN ANALYZE (MCV/NDV/range/GROUP BY)\n"
            "-- 3) плохие: AND коррел., date_trunc, multi GROUP BY\n"
            "-- 4) IN / OR / NOT IN — ORCA vs Legacy\n"
            "-- 5) SET STATISTICS 200 → rebuild hist → rollback 100\n\n"
            "SET optimizer = on;   -- и повторить с off"
        ),
    },
    {
        "kicker": "Combo",
        "title": "Комбинации AND + OR: как читать глазами",
        "subtitle": "Сначала оцените атомы (MCV/hist), потом комбинатор оптимизатора.",
        "type": "code",
        "code": (
            "WHERE segment IN ('enterprise','mid')          -- OR / array\n"
            "  AND sale_date >= DATE '2026-02-01'           -- range / MCV дат\n"
            "  AND (region = 'us' OR region = 'eu')         -- OR\n\n"
            "-- Legacy mental math:\n"
            "s_seg ≈ f_ent + f_mid − f_ent*f_mid\n"
            "s_date ≈ hist/MCV range\n"
            "s_reg  ≈ s_us + s_eu − s_us*s_eu\n"
            "s_all  ≈ s_seg * s_date * s_reg     -- независимость!\n\n"
            "-- ORCA: те же атомы → SF, затем damped conj/disj.\n"
            "-- На стенде гоняйте блок 5 демо-SQL с on/off."
        ),
    },
    {
        "kicker": "Compare CE",
        "title": "Cardinality estimator: ORCA vs Legacy cheat-card",
        "subtitle": "Держите рядом с EXPLAIN ANALYZE на уроке.",
        "type": "cards",
        "cards": [
            [
                "Equality",
                "Оба: MCV freq или residual/NDV. ORCA через CBucket density.",
                "green",
            ],
            [
                "AND",
                "Legacy ∏s. ORCA ∏(SF·0.75^i) после sort.",
                "amber",
            ],
            [
                "OR",
                "Legacy s1+s2−s1s2. ORCA Σ rows·0.75^k.",
                "blue",
            ],
            [
                "GROUP BY",
                "Legacy estimate_num_groups. ORCA damped ∏NDV.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Readout",
        "title": "Как доказывать misestimate за 3 шага",
        "subtitle": "Без «статистика плохая» общими словами — только числа.",
        "type": "flow",
        "flow": [
            ["1", "EXPLAIN ANALYZE: rows vs actual", "green"],
            ["2", "pg_stats: MCV/hist/NDV колонок", "blue"],
            ["3", "Формула: Legacy∏ / ORCA damp", "amber"],
            ["4", "Fix: ANALYZE / rewrite / TEMP", "green"],
            ["5", "Повтор при том же optimizer", "blue"],
        ],
    },
    {
        "kicker": "Stats fail",
        "title": "Когда хорошая статистика всё равно врёт",
        "subtitle": "Проблема не всегда stale ANALYZE — часто модель независимости и форма SQL.",
        "type": "cards",
        "cards": [
            [
                "Коррелированные фильтры",
                "WHERE region='us' AND segment='enterprise' — "
                "sel≠s1·s2, если атрибуты связаны.",
                "red",
            ],
            [
                "Many-join / star",
                "Ошибка sel на каждом join перемножается → "
                "взрыв/схлопывание rows на Motion.",
                "amber",
            ],
            [
                "Функции на колонках",
                "WHERE date_trunc('week', sale_date)=… — "
                "stats на sale_date не помогают напрямую.",
                "blue",
            ],
            [
                "Skew + редкие значения",
                "Значение вне MCV при высоком skew → "
                "недооценка; hash/Broadcast ломаются.",
                "green",
            ],
        ],
    },
    {
        "kicker": "Stats fix",
        "title": "Путь решения: от ANALYZE до декомпозиции",
        "subtitle": "Market practice: доказать misestimate → починить вход stats → иначе physical stage.",
        "type": "flow",
        "flow": [
            ["Measure", "EXPLAIN ANALYZE rows vs actual.", "green"],
            ["Refresh", "ANALYZE / после load.", "blue"],
            ["Target", "SET STATISTICS N на ключ.", "amber"],
            ["Rewrite", "убрать expr/коррел.", "green"],
            ["TEMP", "stage + ANALYZE.", "blue"],
        ],
    },
    {
        "kicker": "Stats ops",
        "title": "Как обновлять и настраивать статистику (GP 6.25)",
        "subtitle": "Контракт production: stats = часть data pipeline, не «иногда vacuum».",
        "type": "code",
        "code": (
            "ANALYZE lesson03.fact_sales;\n"
            "ANALYZE lesson03.dim_customer;\n\n"
            "-- Больше buckets/MCV на «важной» колонке (market practice):\n"
            "ALTER TABLE lesson03.fact_sales\n"
            "  ALTER COLUMN sale_date SET STATISTICS 200;\n"
            "ANALYZE lesson03.fact_sales;\n\n"
            "SHOW default_statistics_target;   -- на стенде: 100\n\n"
            "-- После ETL/partition exchange — ANALYZE обязателен\n"
            "-- TEMP stage: ANALYZE сразу после наполнения\n"
            "-- GP6: нет CREATE STATISTICS; на GP7/PG10+ — multivariate NDV/MCV"
        ),
    },
    {
        "kicker": "Autostats",
        "title": "Ручной vs автоматический ANALYZE в GP6",
        "subtitle": "DWH-контракт = явный ANALYZE. Autostats — помощник, не нянька.",
        "type": "cards",
        "cards": [
            [
                "Вручную",
                "ANALYZE table; после load/exchange/TEMP — в ETL обязательно.",
                "green",
            ],
            [
                "Автомат GP",
                "GUC gp_autostats_mode: planner дописывает ANALYZE к CTAS/INSERT/COPY…",
                "blue",
            ],
            [
                "Default",
                "on_no_stats — только если статистики ещё не было.",
                "amber",
            ],
            [
                "Не PG-autovacuum",
                "В GP6 user DB не стройте процесс вокруг autovacuum autoanalyze.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Autostats",
        "title": "gp_autostats_mode: какой «сервис» отвечает",
        "subtitle": "Не отдельный cron-daemon: поведение QD/planner на изменяющих командах.",
        "type": "code",
        "code": (
            "SHOW gp_autostats_mode;                 -- default: on_no_stats\n"
            "SHOW gp_autostats_on_change_threshold;  -- порог для on_change\n"
            "SHOW gp_autostats_mode_in_functions;    -- часто none\n\n"
            "-- on_no_stats: CTAS/INSERT/COPY владельцем, если stats нет\n"
            "-- on_change:   + UPDATE/DELETE, если rows > threshold\n"
            "-- none:        выключено\n\n"
            "-- Docs: Updating Statistics with ANALYZE (Greenplum 6)"
        ),
    },
    {
        "kicker": "Autostats",
        "title": "Где смотреть last_analyze / last_autoanalyze",
        "subtitle": "pg_stat_user_tables — время ручного и автоматического обновления.",
        "type": "code",
        "code": (
            "SELECT relname,\n"
            "       last_analyze,        -- ручной ANALYZE\n"
            "       last_autoanalyze,    -- авто путь\n"
            "       analyze_count,\n"
            "       autoanalyze_count,\n"
            "       n_mod_since_analyze  -- «насколько устарело»\n"
            "FROM pg_stat_user_tables\n"
            "WHERE schemaname = 'lesson03'\n"
            "ORDER BY relname;\n\n"
            "-- missing stats: gp_toolkit.gp_stats_missing\n"
            "-- демо: lesson03-stats-analyze-lifecycle.sql"
        ),
    },
    {
        "kicker": "Stats code",
        "title": "Код: Legacy selfuncs + ORCA statistics",
        "subtitle": "Рабочие ссылки: gpdb-archive (Legacy) + apache/cloudberry (GPORCA).",
        "type": "cards",
        "cards": [
            [
                "ANALYZE",
                f"{GPDB_6X}/src/backend/commands/analyze.c",
                "green",
            ],
            [
                "Legacy sel",
                f"{GPDB_6X}/src/backend/utils/adt/selfuncs.c\n"
                f"{GPDB_6X}/src/backend/optimizer/path/clausesel.c",
                "blue",
            ],
            [
                "ORCA hist",
                f"{GPDB_ORCA}/libnaucrates/.../CBucket.h\n"
                f"{GPDB_ORCA}/.../CFilterStatsProcessor.cpp",
                "amber",
            ],
            [
                "Deep-dive",
                "docs/.../deep-dives/pg-statistic-internals.md",
                "green",
            ],
        ],
    },
    {
        "kicker": "Storage",
        "title": "Heap / AO / AOCO на GP 6.25",
        "subtitle": "GP6: appendoptimized=true — документированный alias; в catalog/legacy часто видно appendonly.",
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
            "  appendoptimized=true,  -- alias: appendonly=true\n"
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
        "code": "CREATE TEMP TABLE tmp_stage AS\nSELECT customer_id, product_id, amount\nFROM lesson03.fact_sales\nWHERE sale_date >= DATE '2026-02-01'\n  AND sale_date <  DATE '2026-03-01'\nDISTRIBUTED BY (customer_id);   -- обязательный контракт в GP\nANALYZE tmp_stage;               -- иначе оценки stage часто грубые\n\n-- Варианты lifecycle:\n-- CREATE TEMP TABLE ... ON COMMIT PRESERVE ROWS;  -- default\n-- CREATE TEMP TABLE ... ON COMMIT DROP;\n-- CREATE TEMP TABLE ... ON COMMIT DELETE ROWS;\n\n-- Каталог: nspname = pg_temp_<backend>, relpersistence = 't'",
    },
    {
        "kicker": "Session",
        "title": "Сессия пользователя: границы и TEMP",
        "subtitle": "Сессия = одно живое соединение клиента с QD. Не путать с транзакцией.",
        "type": "cards",
        "cards": [
            [
                "Сессия",
                "psql/JDBC подключился → backend на master. "
                "Пока TCP жив — живёт pg_temp_NNN.",
                "green",
            ],
            [
                "Транзакция",
                "BEGIN…COMMIT внутри сессии. Их может быть много подряд.",
                "blue",
            ],
            [
                "Чужая сессия",
                "Другой psql не видит ваш TEMP. Это не «общая» таблица.",
                "amber",
            ],
            [
                "Конец",
                "\\q / disconnect / terminate_backend → TEMP уничтожены.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Session",
        "title": "Как узнать «кто я» в сессии",
        "subtitle": "Три якоря: pid, my_temp_schema, строка в pg_stat_activity.",
        "type": "code",
        "code": (
            "SELECT pg_backend_pid() AS backend_pid,\n"
            "       pg_my_temp_schema()::regnamespace AS my_temp;\n\n"
            "SELECT pid, usename, application_name, state\n"
            "FROM pg_stat_activity\n"
            "WHERE pid = pg_backend_pid();"
        ),
    },
    {
        "kicker": "ON COMMIT",
        "title": "ON COMMIT: три режима TEMP (сводка)",
        "subtitle": "Default = PRESERVE ROWS. DROP/DELETE ROWS — транзакционный контракт.",
        "type": "cards",
        "cards": [
            [
                "PRESERVE ROWS",
                "После COMMIT таблица и строки остаются. Умирает в конце сессии.",
                "green",
            ],
            [
                "DELETE ROWS",
                "После COMMIT таблица есть, строк 0. Каркас на сессию.",
                "amber",
            ],
            [
                "DROP",
                "После COMMIT таблицы нет. TEMP «на одну транзакцию».",
                "red",
            ],
            [
                "ROLLBACK",
                "Если CREATE в той же txn — TEMP как будто не создавали.",
                "blue",
            ],
        ],
    },
    {
        "kicker": "ON COMMIT",
        "title": "PRESERVE ROWS: сессионный stage (default)",
        "subtitle": "Паттерн урока: сузили → COMMIT → дальше join/window в той же сессии.",
        "type": "code",
        "code": (
            "BEGIN;\n"
            "CREATE TEMP TABLE tmp_preserve AS\n"
            "SELECT customer_id, amount FROM lesson03.fact_sales\n"
            "WHERE sale_date >= DATE '2026-02-01'\n"
            "DISTRIBUTED BY (customer_id)\n"
            "ON COMMIT PRESERVE ROWS;\n"
            "ANALYZE tmp_preserve;\n"
            "COMMIT;\n\n"
            "SELECT count(*) FROM tmp_preserve;  -- живёт после COMMIT\n"
            "-- другой psql: to_regclass('tmp_preserve') → NULL"
        ),
    },
    {
        "kicker": "ON COMMIT",
        "title": "DELETE ROWS vs DROP — примеры",
        "subtitle": "DELETE ROWS чистит данные; DROP убивает relation на COMMIT.",
        "type": "code",
        "code": (
            "-- DELETE ROWS\n"
            "BEGIN;\n"
            "CREATE TEMP TABLE tmp_del(id int) DISTRIBUTED BY (id)\n"
            "  ON COMMIT DELETE ROWS;\n"
            "INSERT INTO tmp_del VALUES (1);\n"
            "COMMIT;\n"
            "SELECT count(*) FROM tmp_del;   -- 0, таблица есть\n\n"
            "-- DROP\n"
            "BEGIN;\n"
            "CREATE TEMP TABLE tmp_drop AS SELECT 1 x DISTRIBUTED BY (x)\n"
            "  ON COMMIT DROP;\n"
            "COMMIT;\n"
            "SELECT to_regclass('tmp_drop'); -- NULL"
        ),
    },
    {
        "kicker": "ON COMMIT",
        "title": "Когда TEMP удаляется — чеклист",
        "subtitle": "COMMIT / DROP / disconnect — разные события.",
        "type": "cards",
        "cards": [
            [
                "COMMIT + PRESERVE",
                "Не удаляет. Можно переиспользовать stage.",
                "green",
            ],
            [
                "COMMIT + DROP",
                "Relation исчезает сразу.",
                "red",
            ],
            [
                "DROP TABLE",
                "Явно убрали в любой момент сессии.",
                "amber",
            ],
            [
                "Конец сессии",
                "\\q / idle timeout / kill backend → весь pg_temp_NNN cleanup.",
                "blue",
            ],
        ],
    },
    {
        "kicker": "TEMP catalog",
        "title": "Где посмотреть TEMP в каталоге Greenplum",
        "subtitle": "pg_temp_NNN + relpersistence='t' + filepath t_*.",
        "type": "code",
        "code": (
            "SELECT pg_my_temp_schema()::regnamespace;\n\n"
            "SELECT n.nspname, c.relname, c.relpersistence,\n"
            "       pg_relation_filepath(c.oid) AS filepath,\n"
            "       pg_size_pretty(pg_total_relation_size(c.oid))\n"
            "FROM pg_class c\n"
            "JOIN pg_namespace n ON n.oid = c.relnamespace\n"
            "WHERE n.oid = pg_my_temp_schema()\n"
            "ORDER BY c.relname;\n\n"
            "-- Демо: lesson03-temp-on-commit-lifecycle.sql"
        ),
    },
    {
        "kicker": 'TEMP where',
        "title": 'Где живёт TEMP в Greenplum MPP',
        "subtitle": 'Не отдельный tempdb: та же БД, временный schema, данные на сегментах.',
        "type": 'cards',
        "cards": [
            ['Namespace', 'pg_temp_NNN (+ pg_toast_temp_NNN). Session-local; после disconnect schema исчезает.', 'green'],
            ['Catalog', "Обычные pg_class/pg_attribute во временном namespace. relpersistence='t', filepath base/<dboid>/t_<relfilenode>.", 'blue'],
            ['QD vs QE', 'QD координирует DDL/план. Данные TEMP на QE; на стенде QD-side файл часто 0 bytes (lab observation, не универсальный контракт).', 'amber'],
            ['Distribution', 'TEMP — распределённая таблица. Неверный DISTRIBUTED BY ⇒ лишний Redistribute на следующем join.', 'red'],
        ],
    },
    {
        "kicker": 'TEMP FS map',
        "title": 'Файловая карта: TEMP relation vs spill',
        "subtitle": 'Снято с greenplum-625: два разных каталога под /data/*/gpsne*/base/.',
        "type": 'code',
        "code": '# TEMP TABLE (явная relation)\n/data/data1/gpsne0/base/12812/t_16465     # ~1.1 MB на seg0\n/data/data2/gpsne1/base/12812/t_16465     # ~1.2 MB на seg1\n/data/master/gpsne-1/base/12812/t_16465   # 0 bytes on this lab (QD-side)\n# pg_relation_filepath → base/12812/t_16465\n# nspname = pg_temp_787, relpersistence = t\n# Prod: check temp_tablespaces / pg_relation_filepath()\n\n# Spill / workfiles (исполнитель Sort/Hash)\n/data/data1/gpsne0/base/pgsql_tmp/pgsql_tmp_Sort_1_<pid>.0\n/data/data2/gpsne1/base/pgsql_tmp/pgsql_tmp_Sort_1_<pid>.0\n# растут во время query, удаляются после завершения',
    },
    {
        "kicker": 'Screenshot',
        "title": 'Скрин FS: TEMP relfilenode t_* на сегментах',
        "subtitle": 'После CREATE TEMP … AS SELECT … DISTRIBUTED BY — данные на QE, не в pgsql_tmp.',
        "type": 'image',
        "image": 'lessons/lesson-03/artifacts/plan-screens/temp-relfilenode-fs.png',
    },
    {
        "kicker": "TEMP code",
        "title": "Код gpdb-archive: TEMP и workfiles",
        "subtitle": "Рабочие ссылки (ветка 6X_STABLE на github.com/greenplum-db/gpdb часто 404).",
        "type": "cards",
        "cards": [
            [
                "TEMP namespace",
                f"catalog/namespace.c — InitTempTableNamespace\n{GPDB_6X}/src/backend/catalog/namespace.c",
                "green",
            ],
            [
                "Heap / relfilenode",
                f"storage/smgr + heapam; temp prefix t_\n{GPDB_6X.replace('/blob/', '/tree/')}/src/backend/storage",
                "blue",
            ],
            [
                "Workfile manager",
                f"utils/workfile_manager/\n{GPDB_6X.replace('/blob/', '/tree/')}/src/backend/utils/workfile_manager",
                "amber",
            ],
            [
                "GUC памяти",
                "statement_mem / max_statement_mem, gp_workfile_limit_*, gp_workfile_compression.",
                "green",
            ],
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
        "image": 'lessons/lesson-03/artifacts/plan-screens/spill-pgsql_tmp-growth.png',
    },
    {
        "kicker": 'Screenshot',
        "title": 'Скрин EXPLAIN: external merge Disk = spill',
        "subtitle": 'Связка план ↔ файлы: Disk: NNkB в EXPLAIN = pgsql_tmp_Sort_* на сегментах.',
        "type": 'image',
        "image": 'lessons/lesson-03/artifacts/plan-screens/spill-explain-external-merge.png',
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
            ["pg_statistic", "catalog heap pages → tuple → TOAST.", "blue"],
            ["Storage", "appendonly column layout.", "amber"],
            ["RFC", "rewrite + optimizer policy.", "green"],
        ],
    },
    {
        "kicker": "Principal · SCD2",
        "title": "Appendix: SCD2 CTE — Redistribute при «согласованном» join",
        "subtitle": "Greenplum Secrets #19 spirit · lesson03-principal-scd2-locus.sql",
        "type": "code",
        "code": (
            "DISTRIBUTED BY (biz_key, version_id)\n"
            "JOIN (SELECT biz_key, max(version_id) … GROUP BY biz_key)\n"
            "USING (biz_key, version_id)\n\n"
            "Senior: ключи совпали → Motion не нужен.\n"
            "Principal: hash(biz_key, version_id) ≠ hash(biz_key).\n"
            "План: Redistribute … Hash Key: biz_key"
        ),
    },
    {
        "kicker": "Principal · Fix",
        "title": "Почему TEMP latest keys недостаточен",
        "subtitle": "Фаза B vs C в стендовом SQL.",
        "type": "cards",
        "cards": [
            ["TEMP keys", "Aggregate locus ок; fact всё ещё composite → Redistribute fact.", "amber"],
            ["Model fix", "DISTRIBUTED BY (biz_key) под SCD2 latest pattern → local join.", "green"],
            ["Trade-off", "Skew по горячим biz_key; иногда snapshot current-state.", "red"],
            ["Deep-dive", "principal-scd2-locus-redistribute.md", "blue"],
        ],
    },
    {
        "kicker": "Principal · int/int8",
        "title": "Бонус эрудиции: int ⋈ int8 → Redistribute",
        "subtitle": "Secrets #22 · cast в Hash Cond меняет hash.",
        "type": "code",
        "code": (
            "t_int  (id int)   DISTRIBUTED BY (id)\n"
            "t_int8 (id int8)  DISTRIBUTED BY (id)\n"
            "JOIN ON a.id = b.id\n\n"
            "Hash Cond: (t_int8.id = (t_int.id)::bigint)\n"
            "Redistribute … Hash Key: (t_int.id)::bigint\n\n"
            "Имена колонок совпали. Типы — нет. Motion есть."
        ),
    },
    *APPENDIX_SECRETS_SLIDES,
    *APPENDIX_ABC_SLIDES,
    {
        "kicker": "Summary",
        "title": "Что унести с Урока 03",
        "subtitle": "Оптимизация Greenplum — это pipeline + два optimizer + физика данных.",
        "type": "cards",
        "cards": [
            [
                "History",
                "Legacy = Postgres; ORCA с ~2010, SIGMOD’14, default с GP5.",
                "amber",
            ],
            [
                "Stats / CE / SQL",
                "NOT IN; VALUES; DISTINCT map; autostats×partitions; median Gather.",
                "green",
            ],
            [
                "Locus",
                "SCD2 CTE + Window PARTITION BY + int/int8: читайте Hash Key.",
                "blue",
            ],
            [
                "Доказательство",
                "EXPLAIN ANALYZE + before/after при том же optimizer.",
                "green",
            ],
        ],
    },
]


def _ensure_anchor(title_substr: str, anchor: str) -> None:
    """Attach a stable jump target to the first matching appendix slide."""
    for spec in APPENDIX_SLIDES:
        if title_substr in (spec.get("title") or "") and not spec.get("anchor"):
            spec["anchor"] = anchor
            return
    raise RuntimeError(f"Appendix anchor '{anchor}' not found for title containing {title_substr!r}")


# Stable jump targets for core → appendix chips («детали в appendix»).
_ensure_anchor("Из чего состоит статистика колонки", "appendix-stats")
_ensure_anchor("Гистограмма: equi-depth, сколько шагов", "appendix-histogram")
_ensure_anchor("Legacy: defaults и equality", "appendix-legacy-eq")
_ensure_anchor("Legacy: range по histogram", "appendix-legacy-range")
_ensure_anchor("Legacy: AND / OR / NOT", "appendix-legacy-and")
_ensure_anchor("ORCA: AND с damping", "appendix-orca-and")
_ensure_anchor("Сводка: один предикат — два оценщика", "appendix-ce-summary")
_ensure_anchor("Spill deep-dive: когда executor пишет pgsql_tmp", "appendix-spill")
_ensure_anchor("GPORCA: memo, transformations", "appendix-orca")
_ensure_anchor("История: зачем в Greenplum два оптимизатора", "appendix-history")
