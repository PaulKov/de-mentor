"""Core + appendix slides for Principal A/B/C (Secrets #42 / #41 / #38)."""

from __future__ import annotations

GPDB_ARCHIVE = "https://github.com/greenplum-db/gpdb-archive/blob/main"
GPDB_ORCA = "https://github.com/apache/cloudberry/blob/main/src/backend/gporca"

CORE_ABC_SLIDES = [
    {
        "kicker": "Act 9 · A · #42",
        "title": "DISTINCT map: count по сегменту → SUM",
        "subtitle": "Что: уники. Как: GROUP BY gp_segment_id. Почему: dist key ⇒ id на одном seg.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "COUNT(DISTINCT id) на гигантской AOCO — spill / timeout.",
                "amber",
            ],
            [
                "Как",
                "sum(count(DISTINCT id) … GROUP BY gp_segment_id).",
                "blue",
            ],
            [
                "Почему exact",
                "Только если DISTINCT ⊆ DISTRIBUTED BY (значения не пересекают seg).",
                "green",
            ],
            [
                "Ловушка",
                "DISTRIBUTED RANDOMLY → SUM завышает (фаза D стенда).",
                "red",
            ],
        ],
    },
    {
        "kicker": "Act 9 · A Plans",
        "title": "Canonical vs map DISTINCT (lab)",
        "subtitle": "\\i lesson03-secret42-distinct-by-segment.sql",
        "type": "code",
        "code_kind": "PLAN",
        "code": (
            "A) SELECT count(DISTINCT id) FROM t;\n"
            "   Aggregate → Gather  (тяжёлый local distinct / spill на prod)\n\n"
            "B) SELECT sum(cnt) FROM (\n"
            "     SELECT gp_segment_id, count(DISTINCT id) cnt\n"
            "     FROM t GROUP BY 1) s;\n"
            "   HashAggregate (gp_segment_id, id) → … → sum\n\n"
            "C) canonical = mapped  |  D RANDOM: mapped > canonical"
        ),
    },
    {
        "kicker": "Act 9 · A Code",
        "title": "Agg + GbAgg xform",
        "subtitle": "Secrets #42 · deep-dive secret42-distinct-by-segment.md",
        "type": "cards",
        "cards": [
            [
                "nodeAgg",
                f"{GPDB_ARCHIVE}/src/backend/executor/nodeAgg.c",
                "green",
            ],
            [
                "ORCA HashAgg",
                f"{GPDB_ORCA}/libgpopt/src/xforms/CXformGbAgg2HashAgg.cpp",
                "blue",
            ],
            [
                "Motion",
                f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c",
                "amber",
            ],
            [
                "Контракт",
                "Exact только при dist-key coverage DISTINCT.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Act 9 · B · #41",
        "title": "Autostats × partitions: parent INSERT молчит",
        "subtitle": "on_no_stats ≠ «стата после load в parent».",
        "type": "cards",
        "cards": [
            [
                "Что",
                "INSERT в top-level parent партицированной таблицы.",
                "amber",
            ],
            [
                "Как",
                "gp_autostats_mode=on_no_stats не триггерит ANALYZE на tree.",
                "red",
            ],
            [
                "Почему",
                "Документировано GP6: autostats с leaf insert, не с parent.",
                "blue",
            ],
            [
                "Фикс",
                "Явный ANALYZE parent/leaves в ETL + проверка catalog.",
                "green",
            ],
        ],
    },
    {
        "kicker": "Act 9 · B Demo",
        "title": "Parent miss → leaf hit → ANALYZE",
        "subtitle": "\\i lesson03-secret41-autostats-partitions.sql",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            "SET gp_autostats_mode = on_no_stats;\n"
            "INSERT INTO lesson03.sec41_sales SELECT …;  -- parent\n"
            "-- leaves: stats often MISSING\n\n"
            "INSERT INTO lesson03.sec41_sales_1_prt_1 …; -- leaf\n"
            "-- that leaf: autostats may fire\n\n"
            "ANALYZE lesson03.sec41_sales;  -- ETL policy"
        ),
    },
    {
        "kicker": "Act 9 · B Code",
        "title": "analyze.c + GUC autostats",
        "subtitle": "Secrets #41 · deep-dive secret41-autostats-partitions.md",
        "type": "cards",
        "cards": [
            [
                "ANALYZE",
                f"{GPDB_ARCHIVE}/src/backend/commands/analyze.c",
                "green",
            ],
            [
                "GUC",
                f"{GPDB_ARCHIVE}/src/backend/utils/misc/guc.c",
                "blue",
            ],
            [
                "Док",
                "parent insert ≠ autostats; leaf insert = autostats.",
                "amber",
            ],
            [
                "Рядом",
                "gp_autostats_mode_in_functions внутри функции.",
                "red",
            ],
        ],
    },
    {
        "kicker": "Act 9 · C · #38",
        "title": "Медиана: ordered-set → Gather-all на QD",
        "subtitle": "Pure MPP theory: глобальный порядок нельзя посчитать локально exact.",
        "type": "cards",
        "cards": [
            [
                "Что",
                "percentile_disc(0.5) WITHIN GROUP (ORDER BY n).",
                "amber",
            ],
            [
                "Как",
                "Gather Motion N:1 почти всех строк → Aggregate на QD.",
                "red",
            ],
            [
                "Approx",
                "avg(local median) GROUP BY gp_segment_id при RANDOM.",
                "blue",
            ],
            [
                "Цена",
                "Exact vs скорость; помечать approximate в отчётах.",
                "green",
            ],
        ],
    },
    {
        "kicker": "Act 9 · C Plans",
        "title": "Exact Gather vs local medians",
        "subtitle": "\\i lesson03-secret38-median-gather-qd.sql · Legacy для классической формы",
        "type": "code",
        "code_kind": "PLAN",
        "code": (
            "A exact (Legacy):\n"
            "  Aggregate\n"
            "    -> Gather Motion 2:1\n"
            "         -> Seq Scan  -- почти все rows на QD\n\n"
            "B approx:\n"
            "  Aggregate(avg)\n"
            "    -> Gather local percentile_disc per gp_segment_id\n\n"
            "Secrets prod: ~×31; lab: форма + близость median"
        ),
    },
    {
        "kicker": "Act 9 · C Code",
        "title": "orderedsetaggs.c",
        "subtitle": "Secrets #38 · deep-dive secret38-median-gather-qd.md",
        "type": "cards",
        "cards": [
            [
                "Ordered-set",
                f"{GPDB_ARCHIVE}/src/backend/utils/adt/orderedsetaggs.c",
                "green",
            ],
            [
                "nodeAgg",
                f"{GPDB_ARCHIVE}/src/backend/executor/nodeAgg.c",
                "blue",
            ],
            [
                "Motion",
                f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c",
                "amber",
            ],
            [
                "Теория",
                "Глобальный порядок = данные к одному месту.",
                "red",
            ],
        ],
    },
]

APPENDIX_ABC_SLIDES = [
    {
        "kicker": "Appendix · ABC map",
        "title": "Principal A/B/C: DISTINCT / autostats / median",
        "subtitle": "#42 exact map · #41 ETL stats lie · #38 Gather theory",
        "type": "cards",
        "cards": [
            ["A #42", "Shard DISTINCT when dist key covers values.", "green"],
            ["B #41", "Parent INSERT ≠ autostats on partitions.", "red"],
            ["C #38", "Global percentile Gather-all; local≈ if RANDOM.", "blue"],
            ["Метод", "Что→EXPLAIN→почему (код/док)→фикс+proof.", "amber"],
        ],
    },
    {
        "kicker": "Appendix · A Exactness",
        "title": "Когда SUM(local DISTINCT) врёт",
        "subtitle": "Фаза D стенда — обязательный negative case.",
        "type": "two",
        "left": [
            "Exact",
            "DISTRIBUTED BY (id)\ncount(DISTINCT id)\n= sum per gp_segment_id",
            "green",
        ],
        "right": [
            "Wrong",
            "DISTRIBUTED RANDOMLY\nтот же rewrite\n→ overcount",
            "red",
        ],
    },
    {
        "kicker": "Appendix · A SQL",
        "title": "Rewrite DISTINCT map",
        "subtitle": "lesson03-secret42-distinct-by-segment.sql",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            "-- BAD / heavy\n"
            "SELECT count(DISTINCT id) FROM lesson03.sec42_ids;\n\n"
            "-- GOOD when DISTRIBUTED BY (id)\n"
            "SELECT sum(cnt) FROM (\n"
            "  SELECT gp_segment_id, count(DISTINCT id) AS cnt\n"
            "  FROM lesson03.sec42_ids\n"
            "  GROUP BY 1\n"
            ") s;"
        ),
    },
    {
        "kicker": "Appendix · B Doc",
        "title": "Цитата поведения autostats на partitions",
        "subtitle": "Не баг — контракт Greenplum 6.",
        "type": "cards",
        "cards": [
            [
                "Parent",
                "INSERT into top-level parent → autostats NOT triggered.",
                "red",
            ],
            [
                "Leaf",
                "INSERT directly into leaf → autostats triggered.",
                "green",
            ],
            [
                "GUC",
                "on_no_stats / on_change / none — всё равно parent-правило.",
                "amber",
            ],
            [
                "ETL",
                "ANALYZE after load — definition of done.",
                "blue",
            ],
        ],
    },
    {
        "kicker": "Appendix · B Catalog",
        "title": "Что смотреть в каталоге после load",
        "subtitle": "Leaves, не только parent relname.",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            "SELECT c.relname, s.last_analyze, s.last_autoanalyze,\n"
            "       CASE WHEN st.starelid IS NULL THEN 'MISSING'\n"
            "            ELSE 'HAS pg_statistic' END\n"
            "FROM pg_class c\n"
            "JOIN pg_namespace n ON n.oid = c.relnamespace\n"
            "LEFT JOIN pg_stat_all_tables s ON s.relid = c.oid\n"
            "LEFT JOIN pg_statistic st\n"
            "  ON st.starelid = c.oid AND st.staattnum = 1\n"
            "WHERE n.nspname = 'lesson03'\n"
            "  AND c.relname LIKE 'sec41_sales%';"
        ),
    },
    {
        "kicker": "Appendix · C Theory",
        "title": "Почему медиана ломает MPP",
        "subtitle": "Нужен total order ⇒ один locus.",
        "type": "flow",
        "flow": [
            ["Scan", "все seg", "green"],
            ["Gather", "все rows→QD", "red"],
            ["Sort", "на мастере", "amber"],
            ["Pick", "p50", "blue"],
            ["Approx", "local p50", "green"],
        ],
    },
    {
        "kicker": "Appendix · C SQL",
        "title": "Exact vs approximate median",
        "subtitle": "lesson03-secret38-median-gather-qd.sql",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            "-- Exact (Gather-all)\n"
            "SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n)\n"
            "FROM lesson03.sec38_nums;\n\n"
            "-- Approx (RANDOM shards)\n"
            "SELECT avg(median) FROM (\n"
            "  SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n) AS median\n"
            "  FROM lesson03.sec38_nums\n"
            "  GROUP BY gp_segment_id\n"
            ") s;"
        ),
    },
    {
        "kicker": "Appendix · C Code links",
        "title": "orderedsetaggs + nodeAgg + Motion",
        "subtitle": "Кликабельные URL в PPTX.",
        "type": "code",
        "code_kind": "SQL",
        "code": (
            f"{GPDB_ARCHIVE}/src/backend/utils/adt/orderedsetaggs.c\n\n"
            f"{GPDB_ARCHIVE}/src/backend/executor/nodeAgg.c\n\n"
            f"{GPDB_ARCHIVE}/src/backend/executor/nodeMotion.c\n\n"
            f"{GPDB_ARCHIVE}/src/backend/commands/analyze.c"
        ),
    },
    {
        "kicker": "Appendix · ABC checklist",
        "title": "Principal checklist A+B+C",
        "subtitle": "Перед тем как трогать statement_mem.",
        "type": "cards",
        "cards": [
            [
                "A DISTINCT",
                "Dist key covers? Proof + RANDOM negative?",
                "green",
            ],
            [
                "B Autostats",
                "Parent vs leaf insert? Explicit ANALYZE?",
                "red",
            ],
            [
                "C Median",
                "Exact Gather vs labeled approx?",
                "blue",
            ],
            [
                "Evidence",
                "EXPLAIN ANALYZE + metrics.md + EXCEPT/tolerance",
                "amber",
            ],
        ],
    },
]
