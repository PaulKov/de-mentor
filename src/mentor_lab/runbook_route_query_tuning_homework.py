"""Greenplum Lesson 03 homework route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_query_tuning_common import lesson03_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_query_tuning_links


def greenplum_query_tuning_homework_runbook() -> Runbook:
    links = greenplum_query_tuning_links()
    return Runbook(
        lab_name="greenplum-query-tuning",
        route="homework",
        title="Урок 03 homework: rewrite тяжёлого OLAP с evidence",
        description=(
            "Самостоятельная работа: TEMP-декомпозиция, статистика, storage rationale и before/after EXPLAIN."
        ),
        stages=[
            RunbookStage(
                "prep",
                "prep",
                "Подготовка стенда",
                "Ученик поднимает тот же Greenplum stand и выполняет Lesson 03 SQL-lab.",
                [
                    "python3 mentor-lab.py check greenplum-625",
                    "python3 mentor-lab.py runbook greenplum-query-tuning simple",
                ],
                "Стенд и schema lesson03 готовы?",
                "check проходит, SQL-lab выполнен, есть monolith и TEMP examples.",
                "Есть вывод check и таблицы/view в schema lesson03.",
                links,
            ),
            RunbookStage(
                "before-plan",
                "plan",
                "Before evidence",
                "Снять EXPLAIN монолита и зафиксировать Motion/estimates.",
                [
                    "EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;",
                    "SELECT attname, n_distinct, most_common_vals, histogram_bounds FROM pg_stats WHERE schemaname = 'lesson03' AND tablename = 'fact_sales';",
                ],
                "Какая физическая проблема видна до rewrite?",
                "Конкретный Motion/estimate/scan issue, а не общая жалоба на скорость.",
                "В evidence pack есть before plan и stats snippet.",
                links,
            ),
            RunbookStage(
                "rewrite",
                "practice",
                "TEMP rewrite",
                "Написать собственный TEMP rewrite с DISTRIBUTED BY и ANALYZE.",
                [
                    "-- CREATE TEMP TABLE ... DISTRIBUTED BY (...);",
                    "-- ANALYZE ...;",
                    "-- EXPLAIN final query",
                ],
                "Почему выбран distribution ключ промежуточного TEMP?",
                "Под следующий join/agg, чтобы уменьшить Redistribute bytes.",
                "Rewrite воспроизводим и сопровождается after plan.",
                links,
            ),
            RunbookStage(
                "submit",
                "assessment",
                "Сдача",
                "Собрать SQL + markdown evidence + вопрос к Уроку 04.",
                [
                    "python3 mentor-lab.py student greenplum-query-tuning homework",
                ],
                "Что обязательно в residual risk?",
                "Где rewrite может соврать по бизнес-grain или freshness.",
                "Пакет соответствует rubric Урока 03.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
