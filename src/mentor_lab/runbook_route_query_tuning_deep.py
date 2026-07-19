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
            "90-120 минут: layered plans, pg_statistic slots, physical layout, "
            "TEMP/spill и design review rewrite."
        ),
        stages=[
            RunbookStage(
                "00:00-20:00",
                "1-7",
                "Case и layered plans",
                "Пройди monolith и layered EXPLAIN до разговора про catalog internals.",
                [
                    "python3 mentor-lab.py check greenplum-625",
                    "EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;",
                ],
                "Какие слои плана обязательны в Senior readout?",
                "Motion, join shape, estimates/actuals, scan/storage.",
                "Ученик даёт полный layered readout.",
                links,
            ),
            RunbookStage(
                "20:00-45:00",
                "8-11",
                "pg_statistic internals",
                "Разбери stakind/stavalues и путь ANALYZE → catalog → planner.",
                [
                    "SELECT starelid::regclass, staattnum, stakind1, stanumbers1, stavalues1 FROM pg_statistic WHERE starelid = 'lesson03.fact_sales'::regclass LIMIT 20;",
                ],
                "Где физически живут значения статистики?",
                "В tuple pg_statistic (heap catalog), большие arrays могут быть в TOAST.",
                "Ученик не ищет отдельный proprietary stats-file per column.",
                links,
            ),
            RunbookStage(
                "45:00-70:00",
                "12-14",
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
                "15-18",
                "TEMP и spill",
                "Разбери pg_temp, файлы сегментов и отличие spill files от TEMP TABLE.",
                [
                    "EXPLAIN SELECT region, category, revenue, rank() OVER (PARTITION BY region ORDER BY revenue DESC) FROM tmp_lesson03_sales_shaped;",
                    "SELECT count(*) FROM tmp_lesson03_sales_feb;",
                ],
                "Чем spill отличается от CREATE TEMP TABLE?",
                "Spill — temporary files исполнителей hash/sort; TEMP TABLE — явная relation в pg_temp.",
                "Ученик корректно разделяет два механизма.",
                links,
            ),
            RunbookStage(
                "100:00-120:00",
                "19-22",
                "Design review",
                "Попроси защитить rewrite как production mini-RFC.",
                [
                    "python3 mentor-lab.py runbook greenplum-query-tuning homework",
                ],
                "Какие три доказательства нужны для приёмки rewrite?",
                "Before/after plan, stats/ANALYZE evidence, residual business risk.",
                "Ответ звучит как production review, не как учебный SQL.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
