"""Greenplum Lesson 03 simple mentor route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_query_tuning_common import lesson03_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_query_tuning_links


def greenplum_query_tuning_simple_runbook() -> Runbook:
    links = greenplum_query_tuning_links()
    return Runbook(
        lab_name="greenplum-query-tuning",
        route="simple",
        title="Урок 03 simple path: декомпозиция и тюнинг тяжёлых запросов",
        description=(
            "60 минут: glossary, pipeline Optimize (GUC), plan trees ORCA/Legacy, "
            "TEMP FS/spill и proof."
        ),
        stages=[
            RunbookStage(
                "00:00-08:00",
                "1-8",
                "Glossary + pipeline",
                "Расшифруй GUC/QD/QE/Motion и покажи стадии parse→execute на стенде GP 6.25.",
                [
                    "python3 mentor-lab.py seed greenplum-625 --profile lesson03",
                    "python3 mentor-lab.py check greenplum-625",
                    "\\conninfo",
                    "SHOW optimizer;",
                ],
                "В какой БД живут данные Урока 03 и что такое GUC optimizer?",
                "БД mentor / schema lesson03; GUC optimizer: on → GPORCA, off → Legacy на QD.",
                "Ученик видит dbname=mentor и расшифровывает аббревиатуры до EXPLAIN.",
                links,
            ),
            RunbookStage(
                "08:00-22:00",
                "9-25",
                "Optimize deep + plan trees",
                "Пройди code map gpdb 6X_STABLE и сравни деревья/скрины ORCA vs Legacy.",
                [
                    "\\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql",
                    "SET optimizer = on; EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;",
                    "SET optimizer = off; EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;",
                ],
                "Какой маркер в EXPLAIN отличает GPORCA от Legacy?",
                "Optimizer: Pivotal Optimizer (GPORCA) vs Optimizer: Postgres query optimizer.",
                "Ученик сравнивает join order и Redistribute на одном SQL.",
                links,
            ),
            RunbookStage(
                "22:00-30:00",
                "26-35",
                "Case + layered EXPLAIN + Motion",
                "Разбери monolith слоями: Motion → join → estimates alarm.",
                [
                    "EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;",
                    "EXPLAIN ANALYZE SELECT count(*) FROM lesson03.fact_sales WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-03-01';",
                ],
                "Какой Motion переносит больше всего строк по смыслу плана?",
                "Тот, что стоит над самым широким промежуточным set до сужения фильтра/agg.",
                "Ученик читает план без «просто медленный SQL».",
                links,
            ),
            RunbookStage(
                "30:00-42:00",
                "36-48",
                "Statistics deep-dive",
                "Гистограмма equi-depth, MCV, selectivity предикатов, GROUP BY NDV; когда stats не спасают → TEMP.",
                [
                    "SHOW default_statistics_target;",
                    "SELECT attname, n_distinct, most_common_vals, most_common_freqs, array_length(histogram_bounds, 1) AS hist_n FROM pg_stats WHERE schemaname='lesson03' AND tablename IN ('fact_sales','dim_customer') ORDER BY 1,2;",
                    "EXPLAIN ANALYZE SELECT count(*) FROM lesson03.dim_customer WHERE segment = 'enterprise';",
                ],
                "Чем equi-depth histogram отличается от MCV и когда hist = NULL?",
                "Histogram — границы корзин равной плотности для range; MCV — частые значения+freqs для equality; hist NULL если весь NDV ушёл в MCV.",
                "Ученик связывает predicate → stats slot → rows vs actual.",
                links,
            ),
            RunbookStage(
                "42:00-56:00",
                "49-62",
                "Storage + TEMP FS + spill",
                "AOCO кратко; TEMP t_* vs pgsql_tmp_Sort_*; rewrite с ANALYZE.",
                [
                    "CREATE TEMP TABLE tmp_fs_demo AS SELECT customer_id, product_id, amount FROM lesson03.fact_sales WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-03-01' DISTRIBUTED BY (customer_id);",
                    "SELECT n.nspname, c.relname, pg_relation_filepath(c.oid) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'tmp_fs_demo';",
                    "EXPLAIN SELECT region, category, revenue, rank() OVER (PARTITION BY region ORDER BY revenue DESC) FROM tmp_lesson03_sales_shaped;",
                ],
                "Где на диске TEMP TABLE и где spill Sort?",
                "TEMP → base/<dboid>/t_<relfilenode> на QE; spill → base/pgsql_tmp/pgsql_tmp_Sort_* при external merge.",
                "Ученик разделяет TEMP и workfiles и показывает before/after rewrite.",
                links,
            ),
            RunbookStage(
                "56:00-60:00",
                "63-65",
                "Homework handoff",
                "Закрой evidence checklist и мост к WLM уроку.",
                [
                    "python3 mentor-lab.py runbook greenplum-query-tuning homework",
                    "python3 mentor-lab.py student greenplum-query-tuning homework",
                ],
                "Какие артефакты обязательны в домашке?",
                "Before/after EXPLAIN при фиксированном GUC, pg_stats/ANALYZE evidence, TEMP distribution, residual risk.",
                "Ученик повторяет deliverables своими словами.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
