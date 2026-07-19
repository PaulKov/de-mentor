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
                "1-7",
                "Glossary + pipeline",
                "Расшифруй GUC/QD/QE/Motion и покажи стадии parse→execute на стенде GP 6.25.",
                [
                    "python3 mentor-lab.py check greenplum-625",
                    "python3 mentor-lab.py seed greenplum-625 --profile lesson03",
                    "SHOW optimizer;",
                ],
                "Что такое GUC optimizer и кто строит plan при on/off?",
                "GUC = Grand Unified Configuration; on → GPORCA, off → Legacy Postgres planner на QD.",
                "Ученик расшифровывает аббревиатуры до чтения EXPLAIN.",
                links,
            ),
            RunbookStage(
                "08:00-22:00",
                "8-22",
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
                "22:00-35:00",
                "23-33",
                "Case + layered EXPLAIN + stats",
                "Разбери monolith слоями и свяжи selectivity с pg_stats / pg_statistic.",
                [
                    "EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;",
                    "SELECT attname, null_frac, n_distinct, most_common_vals, histogram_bounds FROM pg_stats WHERE schemaname = 'lesson03' AND tablename = 'fact_sales' ORDER BY attname;",
                ],
                "Какой Motion переносит больше всего строк по смыслу плана?",
                "Тот, что стоит над самым широким промежуточным set до сужения фильтра/agg.",
                "Ученик читает план без «просто медленный SQL».",
                links,
            ),
            RunbookStage(
                "35:00-52:00",
                "34-48",
                "TEMP FS + spill + rewrite",
                "Раздели TEMP TABLE (t_* на QE) и spill (pgsql_tmp_Sort_*); пройди rewrite с ANALYZE.",
                [
                    "CREATE TEMP TABLE tmp_fs_demo AS SELECT customer_id, product_id, amount FROM lesson03.fact_sales WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-03-01' DISTRIBUTED BY (customer_id);",
                    "SELECT n.nspname, c.relname, pg_relation_filepath(c.oid), pg_size_pretty(pg_total_relation_size(c.oid)) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relname = 'tmp_fs_demo';",
                    "EXPLAIN SELECT region, category, revenue, rank() OVER (PARTITION BY region ORDER BY revenue DESC) FROM tmp_lesson03_sales_shaped;",
                ],
                "Где на диске лежит TEMP TABLE и где spill Sort?",
                "TEMP → base/<dboid>/t_<relfilenode> на QE; spill → base/pgsql_tmp/pgsql_tmp_Sort_* при external merge.",
                "Ученик разделяет TEMP relation и workfiles и показывает before/after rewrite.",
                links,
            ),
            RunbookStage(
                "52:00-60:00",
                "49-52",
                "Homework handoff",
                "Закрой evidence checklist и мост к WLM уроку.",
                [
                    "python3 mentor-lab.py runbook greenplum-query-tuning homework",
                    "python3 mentor-lab.py student greenplum-query-tuning homework",
                ],
                "Какие артефакты обязательны в домашке?",
                "Before/after EXPLAIN при фиксированном GUC optimizer, stats snippet, TEMP/distribution rationale, residual risk.",
                "Ученик повторяет deliverables своими словами.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
