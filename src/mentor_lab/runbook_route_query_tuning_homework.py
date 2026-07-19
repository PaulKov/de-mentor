"""Greenplum Lesson 03 homework route (Principal, 90 minutes)."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_query_tuning_common import lesson03_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_query_tuning_links


def greenplum_query_tuning_homework_runbook() -> Runbook:
    links = greenplum_query_tuning_links()
    return Runbook(
        lab_name="greenplum-query-tuning",
        route="homework",
        title="Урок 03 homework Principal: 90м optimization deep dive",
        description=(
            "Самостоятельная работа в mentor.lesson03: ≥2 TEMP стадии, stats autopsy, "
            "ORCA/Legacy matrix, spill/TEMP FS, reconciliation и production RFC."
        ),
        stages=[
            RunbookStage(
                "00:00-10:00",
                "prep",
                "Стенд mentor + contract",
                "Поднять greenplum-625, seed в БД mentor, зафиксировать workload contract.",
                [
                    "python3 mentor-lab.py up greenplum-625",
                    "python3 mentor-lab.py seed greenplum-625 --profile lesson03",
                    "python3 mentor-lab.py check greenplum-625",
                    "\\conninfo",
                ],
                "В какой БД должна идти вся работа Урока 03?",
                "mentor (как Lessons 01/02); schema lesson03. postgres — только maintenance.",
                "Есть вывод check и \\conninfo с dbname=mentor.",
                links,
            ),
            RunbookStage(
                "10:00-25:00",
                "before-stats",
                "Before plan + stats autopsy",
                "Layered EXPLAIN монолита и estimate-failure narrative через pg_stats/pg_statistic.",
                [
                    "SET optimizer = on; EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;",
                    "SELECT attname, n_distinct, most_common_vals, histogram_bounds FROM pg_stats WHERE schemaname = 'lesson03' AND tablename = 'fact_sales';",
                    "EXPLAIN ANALYZE SELECT count(*) FROM lesson03.fact_sales f JOIN lesson03.dim_customer c ON c.customer_id=f.customer_id WHERE c.segment='enterprise' AND f.sale_date >= DATE '2026-02-01';",
                ],
                "Какая физическая проблема видна до rewrite?",
                "Конкретный Motion/estimate/scan issue, связанный со stats slot — не общая жалоба на скорость.",
                "В evidence pack есть before plan и stats autopsy.",
                links,
            ),
            RunbookStage(
                "25:00-55:00",
                "rewrite",
                "Многостадийный TEMP rewrite",
                "≥2 TEMP с DISTRIBUTED BY + ANALYZE; after plan при том же optimizer.",
                [
                    "-- CREATE TEMP TABLE tmp_l03_a ... DISTRIBUTED BY (...); ANALYZE ...;",
                    "-- CREATE TEMP TABLE tmp_l03_b ... DISTRIBUTED BY (...); ANALYZE ...;",
                    "-- EXPLAIN final query (same SET optimizer)",
                ],
                "Почему выбран distribution ключ каждой стадии?",
                "Под следующий join/agg, чтобы уменьшить Redistribute bytes; co-location proof в плане.",
                "rewrite.sql воспроизводим и сопровождается after plan.",
                links,
            ),
            RunbookStage(
                "55:00-70:00",
                "matrix-fs",
                "ORCA/Legacy matrix + TEMP FS/spill",
                "Сравнить движки на case view и final; зафиксировать t_* и/или spill.",
                [
                    "SET optimizer = on; EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;",
                    "SET optimizer = off; EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;",
                    "SELECT n.nspname, c.relname, pg_relation_filepath(c.oid) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relname LIKE 'tmp_%';",
                ],
                "Когда в production допустим session SET optimizer=off?",
                "Только с evidence (plan flip/fallback/timeout) и rollback policy — не как default.",
                "Есть матрица 2×2 и FS/spill артефакт.",
                links,
            ),
            RunbookStage(
                "70:00-90:00",
                "submit",
                "Reconciliation + сдача",
                "Равенство vs monolith, adversarial residual risk, вопрос к Уроку 04.",
                [
                    "python3 mentor-lab.py student greenplum-query-tuning homework",
                    "python3 mentor-lab.py runbook greenplum-query-tuning homework",
                ],
                "Что обязательно в residual risk?",
                "Где rewrite может соврать по grain/freshness/NDV drift/ORCA fallback — и как поймать.",
                "Пакет соответствует Principal rubric Урока 03.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
