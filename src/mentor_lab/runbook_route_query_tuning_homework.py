"""Greenplum Lesson 03 homework route (Senior core ~90–120m after check)."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_query_tuning_common import lesson03_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_query_tuning_links


def greenplum_query_tuning_homework_runbook() -> Runbook:
    links = greenplum_query_tuning_links()
    return Runbook(
        lab_name="greenplum-query-tuning",
        route="homework",
        title="Урок 03 homework Senior core: physical design + e2e proof",
        description=(
            "После зелёного check: baseline → свой physical design (0–3 стадии) → "
            "e2e cost → two-way reconcile → merge/do-not-merge. "
            "Principal extension (matrix/FS/policy/WLM) — отдельно."
        ),
        stages=[
            RunbookStage(
                "prep (вне таймера)",
                "prep",
                "Стенд mentor + homework seed",
                "Поднять greenplum-625, seed homework-safe (без TEMP answer), check.",
                [
                    "python3 mentor-lab.py up greenplum-625",
                    "python3 mentor-lab.py seed greenplum-625 --profile lesson03 --scale small",
                    "python3 mentor-lab.py check greenplum-625",
                    "\\i /mentor-lab/examples/lesson03-homework-seed.sql",
                    "\\conninfo",
                ],
                "В какой БД должна идти вся работа Урока 03?",
                "mentor (как Lessons 01/02); schema lesson03. postgres — только maintenance.",
                "Есть вывод check и \\conninfo с dbname=mentor. Таймер ещё не стартовал.",
                links,
            ),
            RunbookStage(
                "00:00-25:00",
                "baseline",
                "Baseline + stats causality",
                "Fixed optimizer; EXPLAIN ANALYZE graded view; estimate error или proof estimates OK.",
                [
                    "SET optimizer = on;  -- или off; дальше не менять для rewrite proof",
                    "EXPLAIN ANALYZE SELECT * FROM lesson03.v_homework_brand_region;",
                    "SELECT attname, n_distinct, most_common_vals FROM pg_stats WHERE schemaname = 'lesson03' AND tablename = 'fact_sales';",
                ],
                "Какая физическая проблема видна до rewrite?",
                "Конкретный Motion/estimate/scan/skew issue — не общая жалоба на скорость. "
                "Graded view ≠ class-demo monolith.",
                "Evidence A–C заполнены (v_homework_brand_region).",
                links,
            ),
            RunbookStage(
                "25:00-65:00",
                "physical-design",
                "A/B physical design",
                "≥2 candidates (A shallow / B multi-stage); TEMP boundary explored.",
                [
                    "-- Candidate A: ≤1 stage или no-TEMP",
                    "-- Candidate B: multi-stage TEMP … DISTRIBUTED BY …; ANALYZE …",
                    "-- rewrite.sql = production winner; A/B в evidence D",
                ],
                "Почему materialization окупается (или нет)?",
                "Сравни A vs B по e2e cost — не «рецепт ≥2 TEMP» и не class-demo copy.",
                "rewrite.sql + A/B stage tables (секция D).",
                links,
            ),
            RunbookStage(
                "65:00-85:00",
                "e2e-reconcile",
                "E2E metrics + two-way reconcile",
                "Pipeline cost monolith+A+B; EXCEPT ALL vs graded view = 0/0; residual risks.",
                [
                    "-- заполнить таблицу E (total pipeline median для A и B)",
                    "-- templates/reconcile.sql → baseline = v_homework_brand_region",
                    "python3 mentor-lab.py homework greenplum-625 check --submission lessons/lesson-03/submissions",
                ],
                "Что обязательно кроме residual risk?",
                "Two-way EXCEPT ALL 0/0 vs v_homework_brand_region и production decision.",
                "Gates mechanical checker зелёные.",
                links,
            ),
            RunbookStage(
                "85:00-120:00 / extension",
                "principal-extension",
                "Principal extension (опционально)",
                "ORCA matrix (явный контракт), FS/spill, optimizer policy, вопрос к WLM.",
                [
                    "python3 mentor-lab.py student greenplum-query-tuning homework",
                    "python3 mentor-lab.py runbook greenplum-query-tuning homework",
                ],
                "Когда session SET optimizer=off допустим в production?",
                "Только с evidence и rollback policy — не как default.",
                "Extension не блокирует Senior core pass.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
