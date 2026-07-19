"""Greenplum Lesson 03 deep-dive mentor route (core + appendix)."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_query_tuning_common import lesson03_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_query_tuning_links


def greenplum_query_tuning_deep_runbook() -> Runbook:
    links = greenplum_query_tuning_links()
    return Runbook(
        lab_name="greenplum-query-tuning",
        route="deep",
        title="Урок 03 deep: core 38 + appendix internals",
        description=(
            "90-120+ мин: полный core (stats+storage), затем appendix "
            "(CE/history/ON COMMIT), storage lab и design review."
        ),
        stages=[
            RunbookStage(
                "00:00-45:00",
                "1-20",
                "Core Acts 1–3",
                "Incident → plan profile → statistics + pg_statistic physical chain.",
                [
                    "python3 mentor-lab.py check greenplum-625",
                    "\\i /mentor-lab/examples/lesson03-e2e-case-metrics.sql",
                    "SELECT pg_relation_filepath('pg_statistic'::regclass);",
                    "\\i /mentor-lab/examples/lesson03-stats-analyze-lifecycle.sql",
                ],
                "Чем catalog stats отличается от «файла гистограммы на колонку»?",
                "pg_statistic — heap pages (+TOAST); filepath base/<db>/<relfilenode>.",
                "Ученик показывает filepath + last_analyze.",
                links,
            ),
            RunbookStage(
                "45:00-80:00",
                "Act4–6",
                "Storage + NLJ trap + TEMP",
                "Heap/AO/AOCO; Nested Loop CTE case; TEMP lifecycle.",
                [
                    "\\i /mentor-lab/examples/lesson03-storage-heap-ao-aoco.sql",
                    "\\i /mentor-lab/examples/lesson03-orca-ce-trap.sql",
                    "\\i /mentor-lab/examples/lesson03-legacy-ce-trap.sql",
                    "\\i /mentor-lab/examples/lesson03-principal-scd2-locus.sql",
                    "\\i /mentor-lab/examples/lesson03-temp-on-commit-lifecycle.sql",
                ],
                "Чем CE-trap отличается от SCD2 locus-trap?",
                "CE: est≪actual → NL-семейство. Locus: hash(composite)≠hash(biz_key) → Redistribute.",
                "Ученик показывает Redistribute Hash Key и фикс DISTRIBUTED BY (biz_key).",
                links,
            ),
            RunbookStage(
                "80:00-105:00",
                "Act7 + appendix",
                "Proof + appendix deep",
                "Metrics/equivalence; appendix PPTX для CE formulas / history / full screens.",
                [
                    "lessons/lesson-03/artifacts/case/metrics.md",
                    "lessons/lesson-03/artifacts/case/nlj-metrics.md",
                    "lessons/lesson-03/artifacts/greenplum-query-tuning-appendix.pptx",
                ],
                "Почему ORCA-win на 2 сегментах нельзя выдавать за production proof?",
                "Lab scale; нужны median runs, volume, segments; Legacy = diagnostic/fallback.",
                "Ученик формулирует осторожный вывод.",
                links,
            ),
            RunbookStage(
                "100:00-120:00",
                "homework",
                "Design review",
                "Защита rewrite как production mini-RFC.",
                [
                    "python3 mentor-lab.py runbook greenplum-query-tuning homework",
                ],
                "Три доказательства приёмки?",
                "Same GUC before/after, metrics+equivalence, residual risk.",
                "Ответ звучит как production review.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
