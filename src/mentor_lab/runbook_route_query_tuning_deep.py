"""Greenplum Lesson 03 deep-dive mentor route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_query_tuning_common import lesson03_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_query_tuning_links


def greenplum_query_tuning_deep_runbook() -> Runbook:
    links = greenplum_query_tuning_links()
    return Runbook(
        lab_name="greenplum-query-tuning",
        route="deep",
        title="Урок 03 deep-dive: internals статистики, storage и TEMP",
        description=(
            "90-120 минут: glossary→code map→plan trees, pg_statistic slots, "
            "TEMP FS/spill, physical layout и design review rewrite."
        ),
        stages=[
            RunbookStage(
                "00:00-25:00",
                "1-25",
                "Glossary, code map, plan trees",
                "Расшифруй GUC/QD/QE, пройди gpdb 6X_STABLE якоря и сравни скрины ORCA/Legacy.",
                [
                    "python3 mentor-lab.py check greenplum-625",
                    "\\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql",
                    "EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;",
                ],
                "Какие слои плана обязательны в Senior readout?",
                "Optimizer marker, Motion/slices, join shape, estimates/actuals, scan/storage.",
                "Ученик даёт полный layered readout со ссылкой на код.",
                links,
            ),
            RunbookStage(
                "25:00-55:00",
                "36-48",
                "Statistics deep-dive",
                "Equi-depth histogram, MCV, selectivity, GROUP BY NDV; fail modes → TEMP. Слоты stakind/TOAST.",
                [
                    "SHOW default_statistics_target;",
                    "SELECT attname, n_distinct, most_common_freqs, array_length(histogram_bounds, 1) FROM pg_stats WHERE schemaname='lesson03' AND tablename='fact_sales';",
                    "SELECT staattnum, stakind1, stanumbers1, left(stavalues1::text,80) FROM pg_statistic WHERE starelid='lesson03.fact_sales'::regclass ORDER BY 1;",
                    "EXPLAIN ANALYZE SELECT count(*) FROM lesson03.fact_sales f JOIN lesson03.dim_customer c ON c.customer_id=f.customer_id WHERE c.segment='test' AND f.sale_date >= DATE '2026-02-01';",
                ],
                "Когда свежий ANALYZE не спасает кардинальность и что делать на GP6?",
                "Корреляция предикатов/many-join/expr — independence assumption; путь: rewrite + TEMP stage + ANALYZE (нет CREATE STATISTICS на GP6).",
                "Ученик связывает slot → predicate → misestimate → decomposition.",
                links,
            ),
            RunbookStage(
                "55:00-70:00",
                "49-50",
                "Physical storage",
                "Свяжи Heap/AO/AOCO с типами данных и projection.",
                [
                    "\\d+ lesson03.fact_sales",
                    "\\d+ lesson03.dim_customer",
                    "SELECT c.relname, pg_size_pretty(pg_relation_size(c.oid)) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'lesson03' ORDER BY pg_relation_size(c.oid) DESC;",
                ],
                "Почему payload в AOCO менее болезненен для узкого SELECT?",
                "Column projection не читает ненужные column files.",
                "Ответ отделяет storage от distribution/Motion.",
                links,
            ),
            RunbookStage(
                "70:00-100:00",
                "51-62",
                "TEMP FS + spill deep-dive",
                "Покажи t_* на QE vs pgsql_tmp_Sort_*; external merge Disk; плюсы/минусы TEMP.",
                [
                    "SELECT n.nspname, c.relname, c.relfilenode, pg_relation_filepath(c.oid) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname LIKE 'pg_temp%' LIMIT 20;",
                    "SET statement_mem = '8MB'; SET optimizer = off; EXPLAIN ANALYZE SELECT customer_id, amount FROM lesson03.fact_sales ORDER BY amount;",
                    "EXPLAIN SELECT region, category, revenue, rank() OVER (PARTITION BY region ORDER BY revenue DESC) FROM tmp_lesson03_sales_shaped;",
                ],
                "Чем путь TEMP TABLE отличается от spill workfiles на FS?",
                "TEMP → base/<dboid>/t_<relfilenode> (session relation); spill → base/pgsql_tmp/pgsql_tmp_Sort_* (executor overflow).",
                "Ученик читает FS evidence и связывает с EXPLAIN Disk.",
                links,
            ),
            RunbookStage(
                "100:00-120:00",
                "63-65",
                "Design review",
                "Попроси защитить rewrite как production mini-RFC при фиксированном GUC optimizer.",
                [
                    "python3 mentor-lab.py runbook greenplum-query-tuning homework",
                ],
                "Какие три доказательства нужны для приёмки rewrite?",
                "Before/after plan при том же GUC, stats/ANALYZE + TEMP distribution evidence, residual business risk.",
                "Ответ звучит как production review, не как учебный SQL.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
