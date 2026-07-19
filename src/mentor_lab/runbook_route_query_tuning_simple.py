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
            "60 минут: монолитный OLAP, layered EXPLAIN, статистика, TEMP rewrite и proof."
        ),
        stages=[
            RunbookStage(
                "00:00-08:00",
                "1-3",
                "Сквозной case",
                "Покажи monolith OLAP и зафиксируй, что цена = данные + сеть + estimates.",
                [
                    "python3 mentor-lab.py check greenplum-625",
                    "python3 mentor-lab.py seed greenplum-625 --profile lesson03",
                ],
                "Что в этом запросе может быть дороже самого join?",
                "Redistribute/Broadcast большого set, плохие estimates, широкая projection, spill.",
                "Ученик называет distributed cost factors до rewrite.",
                links,
            ),
            RunbookStage(
                "08:00-20:00",
                "4-7",
                "Layered EXPLAIN",
                "Разбери план слоями: Motion → join shape → estimates → scan.",
                [
                    "EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;",
                ],
                "Какой Motion переносит больше всего строк по смыслу плана?",
                "Тот, что стоит над самым широким промежуточным set до сужения фильтра/agg.",
                "Ученик читает план без «просто медленный SQL».",
                links,
            ),
            RunbookStage(
                "20:00-32:00",
                "8-11",
                "Статистика",
                "Свяжи selectivity с pg_stats и слотами pg_statistic.",
                [
                    "SELECT attname, null_frac, n_distinct, most_common_vals, histogram_bounds FROM pg_stats WHERE schemaname = 'lesson03' AND tablename = 'fact_sales' ORDER BY attname;",
                    "SELECT c.relname, s.staattnum, s.stakind1, s.stanumbers1 FROM pg_statistic s JOIN pg_class c ON c.oid = s.starelid JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'lesson03' ORDER BY 1, 2 LIMIT 20;",
                ],
                "Какой slot объясняет range-фильтр по sale_date?",
                "Histogram bounds (и связанные stanumbers/stavalues) для range selectivity.",
                "Ученик связывает catalog stats с plan rows.",
                links,
            ),
            RunbookStage(
                "32:00-48:00",
                "12-18",
                "Storage и TEMP rewrite",
                "Сравни Heap/AO/AOCO и пройди TEMP декомпозицию с ANALYZE.",
                [
                    "EXPLAIN SELECT region, category, revenue, rank() OVER (PARTITION BY region ORDER BY revenue DESC) FROM tmp_lesson03_sales_shaped;",
                    "SELECT c.relname, pg_size_pretty(pg_relation_size(c.oid)) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'lesson03' ORDER BY pg_relation_size(c.oid) DESC;",
                ],
                "Зачем ANALYZE на TEMP после наполнения?",
                "Чтобы следующий join/Motion планировался по реальной cardinality этапа.",
                "Ученик показывает before/after мышление на TEMP stages.",
                links,
            ),
            RunbookStage(
                "48:00-60:00",
                "19-22",
                "Homework handoff",
                "Закрой evidence checklist и мост к WLM уроку.",
                [
                    "python3 mentor-lab.py runbook greenplum-query-tuning homework",
                    "python3 mentor-lab.py student greenplum-query-tuning homework",
                ],
                "Какие артефакты обязательны в домашке?",
                "Before/after EXPLAIN, stats snippet, storage rationale, residual risk.",
                "Ученик повторяет deliverables своими словами.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
