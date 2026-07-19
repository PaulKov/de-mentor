"""Core + appendix slides for Greenplum Secrets #18 / #14 / #29 cases."""

from __future__ import annotations

GPDB_ARCHIVE = "https://github.com/greenplum-db/gpdb-archive/blob/main"
GPDB_ORCA = "https://github.com/apache/cloudberry/blob/main/src/backend/gporca"

CORE_SECRETS_SLIDES = [
    {
        "kicker": "Act 8 · Secrets #18",
        "title": "NOT IN → Broadcast всей filter-таблицы",
        "subtitle": "Что: anti-filter. Как в плане: Hash Left Anti Semi (Not-In) + Broadcast.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "WHERE t1.n NOT IN (SELECT n FROM t2) — «дай строки без пары».",
                "amber",
            ],
            [
                "Как",
                "GPORCA: Not-In Join; часто Broadcast полной t2 на каждый seg.",
                "red",
            ],
            [
                "Почему",
                "Семантика Not-In (+ NULL) ≠ обычный anti; xform выбирает Broadcast.",
                "blue",
            ],
            [
                "Фикс",
                "NOT EXISTS / LEFT JOIN … IS NULL + co-located DISTRIBUTED BY.",
                "green",
            ],
        ],
    },
    {
        "kicker": "Act 8 · #18 Plans",
        "title": "Lab: Broadcast vs Hash Anti (одинаковые 400k)",
        "subtitle": "\\i lesson03-secret18-not-in-broadcast.sql · форма важнее секунд на 2 seg",
        "type": "code",
        "code_kind": "PLAN",
        "code": (
            "A NOT IN:\n"
            "  Hash Left Anti Semi (Not-In) Join\n"
            "    -> Broadcast Motion 2:2  ← вся t2\n"
            "         -> Seq Scan on sec18_t2\n\n"
            "B NOT EXISTS:\n"
            "  Hash Anti Join   ← без Broadcast t2\n"
            "    -> Seq Scan t1 / Hash(Seq Scan t2)\n\n"
            "Secrets prod: ~10³×; lab: учите shape."
        ),
    },
    {
        "kicker": "Act 8 · #18 Code",
        "title": "Куда смотреть в коде Greenplum",
        "subtitle": "ORCA xform Not-In + Motion executor.",
        "type": "cards",
        "cards": [
            [
                "Xform Not-In",
                f"{GPDB_ORCA}/libgpopt/src/xforms/CXformLeftAntiSemiJoinNotIn2HashJoinNotIn.cpp",
                "red",
            ],
            [
                "Broadcast",
                f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp",
                "amber",
            ],
            [
                "Motion exec",
                f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c",
                "blue",
            ],
            [
                "Deep-dive",
                "docs/.../deep-dives/secret18-not-in-broadcast.md",
                "green",
            ],
        ],
    },
    {
        "kicker": "Act 8 · Secrets #14",
        "title": "Window PARTITION BY константы → victim segment",
        "subtitle": "Что: row_number по ключу. Как: Redistribute Hash Key = partition col.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "OVER (PARTITION BY invalid_id …) требует все строки ключа вместе.",
                "amber",
            ],
            [
                "Как",
                "Если DISTRIBUTED BY ≠ partition key → Redistribute Motion.",
                "red",
            ],
            [
                "Почему",
                "NDV(key)=1 → hash указывает на один seg — коллапс параллелизма.",
                "blue",
            ],
            [
                "Фикс",
                "Убрать бессмысленный PARTITION BY; иначе DISTRIBUTED BY реальному ключу.",
                "green",
            ],
        ],
    },
    {
        "kicker": "Act 8 · #14 Plans",
        "title": "Redistribute → исчез Motion → настоящий rewrite",
        "subtitle": "\\i lesson03-secret14-window-partition-skew.sql",
        "type": "code",
        "code_kind": "PLAN",
        "code": (
            "A DISTRIBUTED BY (id), PARTITION BY invalid_id=const:\n"
            "  WindowAgg → Redistribute … Hash Key: invalid_id\n\n"
            "C DISTRIBUTED BY (invalid_id):\n"
            "  WindowAgg → Seq Scan  (Motion нет, но NDV=1 → один seg)\n\n"
            "D без PARTITION BY:\n"
            "  Gather → WindowAgg  ← фикс, если ключ технический мусор"
        ),
    },
    {
        "kicker": "Act 8 · #14 Code",
        "title": "WindowAgg + hash-distribute в исходниках",
        "subtitle": "Executor считает окно локально — планировщик обязан собрать partition.",
        "type": "cards",
        "cards": [
            [
                "WindowAgg",
                f"{GPDB_ARCHIVE}/src/backend/executor/nodeWindowAgg.c",
                "green",
            ],
            [
                "ORCA window",
                f"{GPDB_ORCA}/libgpopt/src/xforms/CXformImplementSequenceProject.cpp",
                "blue",
            ],
            [
                "Hash Motion",
                f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionHashDistribute.cpp",
                "amber",
            ],
            [
                "Deep-dive",
                "docs/.../deep-dives/secret14-window-partition-skew.md",
                "red",
            ],
        ],
    },
    {
        "kicker": "Act 8 · Secrets #29",
        "title": "VALUES-параметры → двигается FACT, не params",
        "subtitle": "Красивый CTE с VALUES ≠ дешёвый hardcode.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "WITH data_batch AS (VALUES …) JOIN big_fact — «параметры отчёта».",
                "amber",
            ],
            [
                "Как",
                "Secrets: Broadcast fact; lab 2-seg: Gather fact→QD (rows≈1).",
                "red",
            ],
            [
                "Почему",
                "Нет ключа/статы → CE считает fact крошечным; join тянет большую сторону.",
                "blue",
            ],
            [
                "Фикс",
                "WHERE/литералы; или DISTRIBUTED BY join-ключа + ANALYZE.",
                "green",
            ],
        ],
    },
    {
        "kicker": "Act 8 · #29 Plans",
        "title": "A Gather fact → B local → D scalar filter",
        "subtitle": "\\i lesson03-secret29-values-params-broadcast.sql",
        "type": "code",
        "code_kind": "PLAN",
        "code": (
            "A RANDOM, no ANALYZE:\n"
            "  Hash Join → Gather Motion fact  (lab)\n"
            "  / Broadcast Motion fact         (Secrets)\n\n"
            "B DISTRIBUTED BY (n_txt):\n"
            "  Hash Join → Seq Scan fact\n\n"
            "D WHERE n_txt = '10':\n"
            "  Seq Scan Filter — без join к VALUES\n\n"
            "E IN (VALUES) ≠ IN ('a','b')  → ANY filter"
        ),
    },
    {
        "kicker": "Act 8 · #29 Code",
        "title": "Motion + CE defaults",
        "subtitle": "Читайте, какую сторону двигает Motion.",
        "type": "cards",
        "cards": [
            [
                "Broadcast",
                f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp",
                "red",
            ],
            [
                "Hash redistribute",
                f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionHashDistribute.cpp",
                "amber",
            ],
            [
                "selfuncs (Legacy CE)",
                f"{GPDB_ARCHIVE}/src/backend/utils/adt/selfuncs.c",
                "blue",
            ],
            [
                "Deep-dive",
                "docs/.../deep-dives/secret29-values-params-broadcast.md",
                "green",
            ],
        ],
    },
]

APPENDIX_SECRETS_SLIDES = [
    {
        "kicker": "Appendix · Secrets map",
        "title": "Три акта из канала → три класса Motion-багов",
        "subtitle": "#18 оператор SQL · #14 window locus · #29 params CTE/CE",
        "type": "cards",
        "cards": [
            ["#18 NOT IN", "Broadcast inner; фикс NOT EXISTS / LEFT anti.", "red"],
            ["#14 Window", "Redistribute на partition key; константа = victim.", "amber"],
            ["#29 VALUES", "Fact едет к params (Broadcast/Gather).", "blue"],
            ["Метод", "Что→Как в EXPLAIN→Почему (код)→Фикс+proof.", "green"],
        ],
    },
    # ----- #18 deep -----
    {
        "kicker": "Appendix · #18 Finger",
        "title": "NOT IN: идея анти-join",
        "subtitle": "Два мешка номеров на сегментах. Нужны «сироты» из t1.",
        "type": "cards",
        "cards": [
            [
                "Интуиция OLTP",
                "«Анти-фильтр, локально по ключу» — часто ложь в MPP.",
                "amber",
            ],
            [
                "Реальность GP",
                "Not-In Join + тираж всей t2 (Broadcast) на каждый QE.",
                "red",
            ],
            [
                "NULL",
                "NULL в inner → NOT IN даёт UNKNOWN → 0 строк. NOT EXISTS — нет.",
                "blue",
            ],
            [
                "Эквивалент",
                "Без NULL: NOT EXISTS ≈ LEFT JOIN IS NULL (следите за дублями).",
                "green",
            ],
        ],
    },
    {
        "kicker": "Appendix · #18 SQL",
        "title": "Rewrite: NOT IN → NOT EXISTS → LEFT JOIN",
        "subtitle": "Стенд lesson03-secret18-not-in-broadcast.sql",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            "-- BAD\n"
            "SELECT t1.* FROM lesson03.sec18_t1 t1\n"
            "WHERE t1.n NOT IN (SELECT n FROM lesson03.sec18_t2);\n\n"
            "-- GOOD\n"
            "SELECT t1.* FROM lesson03.sec18_t1 t1\n"
            "WHERE NOT EXISTS (\n"
            "  SELECT 1 FROM lesson03.sec18_t2 t2 WHERE t2.n = t1.n);\n\n"
            "-- ALSO\n"
            "SELECT t1.* FROM lesson03.sec18_t1 t1\n"
            "LEFT JOIN lesson03.sec18_t2 t2 ON t1.n = t2.n\n"
            "WHERE t2.n IS NULL;"
        ),
    },
    {
        "kicker": "Appendix · #18 Why code",
        "title": "ORCA xform LeftAntiSemiJoinNotIn → HashJoinNotIn",
        "subtitle": "Именно Not-In путь открывает Broadcast-friendly physical ops.",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            f"-- Xform:\n"
            f"{GPDB_ORCA}/libgpopt/src/xforms/"
            "CXformLeftAntiSemiJoinNotIn2HashJoinNotIn.cpp\n\n"
            f"-- Broadcast physical:\n"
            f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp\n\n"
            f"-- Executor Motion:\n"
            f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c\n\n"
            f"-- Legacy join paths:\n"
            f"{GPDB_ARCHIVE}/src/backend/optimizer/path/joinpath.c"
        ),
    },
    {
        "kicker": "Appendix · #18 Fix ladder",
        "title": "Лестница исправления #18",
        "subtitle": "От синтаксиса к модели данных.",
        "type": "flow",
        "flow": [
            ["1 SQL", "NOT EXISTS", "green"],
            ["2 NULL", "IS NOT NULL", "blue"],
            ["3 Dist", "BY join key", "amber"],
            ["4 Proof", "EXCEPT ALL", "green"],
            ["5 Mem", "не первым", "red"],
        ],
    },
    # ----- #14 deep -----
    {
        "kicker": "Appendix · #14 Finger",
        "title": "Window: PARTITION BY и коллапс параллелизма",
        "subtitle": "PARTITION BY = ключ распределения строк. Константа → один сегмент-жертва.",
        "type": "cards",
        "cards": [
            [
                "Контракт",
                "WindowAgg локален: весь partition key должен быть на сегменте.",
                "blue",
            ],
            [
                "Motion",
                "Иначе Redistribute Hash Key = partition columns.",
                "amber",
            ],
            [
                "Константа",
                "hash(const) → один victim segment; млрд строк съезжают туда.",
                "red",
            ],
            [
                "Симптом",
                "workfile per query size limit / гигантский spill на одном seg.",
                "green",
            ],
        ],
    },
    {
        "kicker": "Appendix · #14 SQL",
        "title": "Стендовый паттерн: constant invalid_id",
        "subtitle": "lesson03-secret14-window-partition-skew.sql",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            "CREATE TABLE lesson03.sec14_foo (…)\n"
            "DISTRIBUTED BY (id);\n"
            "-- insert: invalid_id = 42 для всех строк\n\n"
            "SELECT row_number() OVER (\n"
            "  PARTITION BY invalid_id ORDER BY version_id DESC\n"
            ") … FROM lesson03.sec14_foo;\n\n"
            "-- REAL FIX when key is junk:\n"
            "row_number() OVER (ORDER BY version_id DESC, id)"
        ),
    },
    {
        "kicker": "Appendix · #14 Why code",
        "title": "nodeWindowAgg + CPhysicalMotionHashDistribute",
        "subtitle": "Планировщик обеспечивает locus; executor только считает.",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            f"{GPDB_ARCHIVE}/src/backend/executor/nodeWindowAgg.c\n\n"
            f"{GPDB_ORCA}/libgpopt/src/xforms/"
            "CXformImplementSequenceProject.cpp\n\n"
            f"{GPDB_ORCA}/libgpopt/src/operators/"
            "CPhysicalMotionHashDistribute.cpp\n\n"
            f"{GPDB_ARCHIVE}/src/backend/cdb/cdbmutate.c\n\n"
            f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c"
        ),
    },
    {
        "kicker": "Appendix · #14 Fix ladder",
        "title": "Лестница исправления #14",
        "subtitle": "Сначала смысл PARTITION BY, потом physical model.",
        "type": "flow",
        "flow": [
            ["1 Sense", "нужен ли PB?", "red"],
            ["2 NDV", "pg_stats", "amber"],
            ["3 Dist", "BY key", "blue"],
            ["4 TEMP", "pre-stage", "green"],
            ["5 Mem", "последним", "amber"],
        ],
    },
    # ----- #29 deep -----
    {
        "kicker": "Appendix · #29 Finger",
        "title": "Параметры отчёта: красиво ≠ дёшево",
        "subtitle": "CTE VALUES join к fact — «произведение искусства» с ценой Motion.",
        "type": "cards",
        "cards": [
            [
                "Интуиция",
                "Одна строка params разъедется / останется локальной.",
                "amber",
            ],
            [
                "План",
                "Едет fact: Broadcast (prod) или Gather→QD (lab 2-seg).",
                "red",
            ],
            [
                "CE",
                "Без ANALYZE fact rows≈1 → cost model врёт.",
                "blue",
            ],
            [
                "Hardcode",
                "WHERE col = … / IN list часто на порядок дешевле join к VALUES.",
                "green",
            ],
        ],
    },
    {
        "kicker": "Appendix · #29 SQL",
        "title": "VALUES CTE vs scalar filter",
        "subtitle": "lesson03-secret29-values-params-broadcast.sql",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            "WITH data_batch AS (\n"
            "  SELECT * FROM (VALUES\n"
            "    (0, '10', '2024-01-01'::date, …)\n"
            "  ) t(rn, mdm_id, report_dt, …)\n"
            ")\n"
            "SELECT … FROM lesson03.sec29_fact s0\n"
            "JOIN data_batch b ON b.mdm_id = s0.n_txt;\n\n"
            "-- Prefer:\n"
            "SELECT * FROM lesson03.sec29_fact WHERE n_txt = '10';"
        ),
    },
    {
        "kicker": "Appendix · #29 Modes",
        "title": "Три режима fact: Gather / local / Redistribute",
        "subtitle": "Один SQL params — три physical stories.",
        "type": "cards",
        "cards": [
            ["A RANDOM no stats", "Gather/Broadcast fact (CE trap).", "red"],
            ["B DISTRIBUTED BY key", "Local Hash Join на сегментах.", "green"],
            ["C RANDOM + ANALYZE", "Redistribute fact по join key.", "amber"],
            ["E IN VALUES vs list", "Join+Motion vs Filter ANY.", "blue"],
        ],
    },
    {
        "kicker": "Appendix · #29 Why code",
        "title": "Broadcast / HashDistribute / selfuncs",
        "subtitle": "Смотрите сторону Motion + оценку rows.",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            f"{GPDB_ORCA}/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp\n\n"
            f"{GPDB_ORCA}/libgpopt/src/operators/"
            "CPhysicalMotionHashDistribute.cpp\n\n"
            f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c\n\n"
            f"{GPDB_ARCHIVE}/src/backend/utils/adt/selfuncs.c\n\n"
            f"{GPDB_ARCHIVE}/src/backend/optimizer/plan/planner.c"
        ),
    },
    {
        "kicker": "Appendix · #29 Fix ladder",
        "title": "Лестница исправления #29",
        "subtitle": "От синтаксиса параметров к distribution policy.",
        "type": "flow",
        "flow": [
            ["1 Literal", "WHERE/IN", "green"],
            ["2 ANALYZE", "fact stats", "blue"],
            ["3 Dist", "BY join key", "amber"],
            ["4 TEMP", "params table", "green"],
            ["5 Proof", "Motion side", "red"],
        ],
    },
    {
        "kicker": "Appendix · Secrets checklist",
        "title": "Единый Principal checklist для #18/#14/#29",
        "subtitle": "Перед тем как трогать statement_mem.",
        "type": "cards",
        "cards": [
            [
                "Оператор",
                "NOT IN? VALUES CTE? Window PARTITION BY?",
                "amber",
            ],
            [
                "Motion side",
                "Какая таблица в Broadcast/Redistribute/Gather?",
                "red",
            ],
            [
                "Hash Key / PB",
                "Совпадает с DISTRIBUTED BY? NDV≈1?",
                "blue",
            ],
            [
                "Proof",
                "Тот же optimizer + EXCEPT ALL + metrics.md",
                "green",
            ],
        ],
    },
]
