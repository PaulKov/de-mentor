"""Greenplum Lesson 03 simple mentor route (60 min core lite)."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_query_tuning_common import lesson03_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_query_tuning_links


def greenplum_query_tuning_simple_runbook() -> Runbook:
    links = greenplum_query_tuning_links()
    return Runbook(
        lab_name="greenplum-query-tuning",
        route="simple",
        title="Урок 03 simple: incident → plan → TEMP → proof",
        description=(
            "60 минут core lite: симптом, plan profile, TEMP decomposition, "
            "before/after metrics. Без appendix encyclopedia."
        ),
        stages=[
            RunbookStage(
                "00:00-08:00",
                "1-5",
                "Incident",
                "Зафиксируй GUC, покажи SQL monolith и три симптома на baseline.",
                [
                    "python3 mentor-lab.py seed greenplum-625 --profile lesson03",
                    "python3 mentor-lab.py check greenplum-625",
                    "SET optimizer = on; SHOW optimizer;",
                ],
                "Какие три симптома ищем на плане?",
                "Motion на широком set, misestimate (если есть), spill/mem risk.",
                "Ученик называет симптомы до переписывания SQL.",
                links,
            ),
            RunbookStage(
                "08:00-22:00",
                "6-14",
                "Plan profile + interactive",
                "Алгоритм чтения + серия Plan 1/5…5/5; 90 секунд interactive.",
                [
                    "EXPLAIN ANALYZE /* monolith grain — см. lesson03-e2e-case-metrics.sql */",
                ],
                "Где критический путь и какая проверяемая гипотеза?",
                "Scan+joins до agg; гипотеза — TEMP stage сужает set раньше Motion.",
                "Ученик формулирует одну гипотезу, не «медленный SQL».",
                links,
            ),
            RunbookStage(
                "22:00-38:00",
                "Act5 NLJ",
                "ORCA+Legacy CE traps",
                "ORCA: 3 CTE → NLJ. Legacy: EXISTS → NL Semi. TEMP → Hash у обоих.",
                [
                    "\\i /mentor-lab/examples/lesson03-orca-ce-trap.sql",
                    "\\i /mentor-lab/examples/lesson03-legacy-ce-trap.sql",
                    "lessons/lesson-03/artifacts/case/ce-traps-metrics.md",
                ],
                "Почему два разных SQL, а не один на оба optimizer?",
                "На стенде 3-CTE ломает ORCA; Legacy на нём часто HashJoin — EXISTS ломает Legacy.",
                "Ученик показывает NLJ/Semi → Hash Join после TEMP на обоих.",
                links,
            ),
            RunbookStage(
                "38:00-52:00",
                "Act6-7",
                "OLAP TEMP + proof",
                "Feb TEMP stages + warm metrics / EXCEPT ALL.",
                [
                    "\\i /mentor-lab/examples/lesson03-e2e-case-metrics.sql",
                    "lessons/lesson-03/artifacts/case/metrics.md",
                ],
                "Какие числа обязательны в evidence pack?",
                "Planning/execution, join type, TEMP size, equivalence 0/0, warm/cold note.",
                "Ученик заполняет before/after таблицу.",
                links,
            ),
            RunbookStage(
                "52:00-60:00",
                "checklist",
                "Homework handoff",
                "Checklist + Principal homework.",
                [
                    "python3 mentor-lab.py runbook greenplum-query-tuning homework",
                ],
                "Что сдаём в домашке?",
                "Before/after при том же GUC, stats evidence, TEMP distribution, residual risk.",
                "Ученик повторяет deliverables.",
                links,
            ),
        ],
        **lesson03_runbook_paths(),
    )
