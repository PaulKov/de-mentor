"""Greenplum Lesson 02 deep-dive mentor route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_partitioning_common import lesson02_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_partitioning_links


def greenplum_partitioning_deep_runbook() -> Runbook:
    links = greenplum_partitioning_links()
    return Runbook(
        lab_name="greenplum-partitioning",
        route="deep",
        title="Lesson 02 deep-dive path: partition internals and load operations",
        description=(
            "90-120 минут для сильного ученика: pruning mechanics, statistics, "
            "late-arriving facts, AOCO partitions, ATTACH/DETACH и production checks."
        ),
        stages=[
            RunbookStage(
                "00:00-15:00",
                "1-4",
                "Evidence replay и workload contract",
                "Собери связь между workload, predicates, distribution и планом до разговора о DDL.",
                [
                    "python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md",
                    "python3 mentor-lab.py coach-plan greenplum --query bad_customer_join --sample",
                ],
                "Какие вопросы надо задать бизнесу до выбора partition key?",
                "Типовые predicates, retention, late facts, SLA загрузки, объемы и частота исправлений.",
                "Ученик отделяет workload contract от синтаксиса CREATE TABLE.",
                links,
            ),
            RunbookStage(
                "15:00-35:00",
                "5-8",
                "Pruning mechanics",
                "Разбери root partition, leaf partitions, partition constraints и visible plan shape.",
                [
                    "SELECT * FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass);",
                    "SELECT c.oid::regclass, pg_get_partkeydef(c.oid) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'lesson02' AND c.relname = 'fact_sales_partitioned';",
                    "EXPLAIN SELECT sum(amount) FROM lesson02.fact_sales_partitioned WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-03-01';",
                ],
                "Как доказать, что pruning сработал?",
                "Показать EXPLAIN и catalog/tree: план обращается только к нужным leaf partitions.",
                "Ученик не путает partition pruning с segment elimination или join locality.",
                links,
            ),
            RunbookStage(
                "35:00-55:00",
                "9-11",
                "Statistics и plan quality",
                "Покажи, что ANALYZE после load обновляет оценки, от которых зависят join/Motion решения.",
                [
                    "SELECT schemaname, relname, n_live_tup, last_analyze FROM pg_stat_user_tables WHERE schemaname = 'lesson02' ORDER BY relname;",
                    "ANALYZE lesson02.fact_sales_partitioned;",
                    "EXPLAIN SELECT customer_id, sum(amount) FROM lesson02.fact_sales_partitioned GROUP BY customer_id;",
                ],
                "Когда ANALYZE можно делать на touched partitions, а когда нужен broader refresh?",
                "После локального окна достаточно touched partitions; после сильной смены распределения нужна более широкая проверка.",
                "Ответ содержит row-count threshold, estimates и before/after plan evidence.",
                links,
            ),
            RunbookStage(
                "55:00-85:00",
                "12-16",
                "Incremental load algorithm",
                "Пройди алгоритм: stage, validate, publish, analyze, audit, retry.",
                [
                    "SELECT sale_date, count(*), sum(amount) FROM lesson02.fact_sales_stage GROUP BY sale_date ORDER BY sale_date;",
                    "SELECT tableoid::regclass, count(*) FROM lesson02.fact_sales_partitioned GROUP BY tableoid::regclass ORDER BY 1;",
                    "SELECT customer_id, sale_date, count(*) FROM lesson02.fact_sales_partitioned GROUP BY customer_id, sale_date HAVING count(*) > 1 ORDER BY count(*) DESC LIMIT 10;",
                ],
                "Как сделать load идемпотентным?",
                "Через deterministic keys, dedup в stage, bounded replace/merge и валидацию перед повторной публикацией.",
                "Ученик описывает retry без двойной загрузки фактов.",
                links,
            ),
            RunbookStage(
                "85:00-105:00",
                "17-19",
                "AOCO partitions и maintenance",
                "Покажи AOCO DDL, leaf partition inspection и admin snippets для retention.",
                [
                    "SELECT * FROM gp_toolkit.gp_partitions WHERE schemaname = 'lesson02' ORDER BY partitiontablename;",
                    "\\d+ lesson02.fact_sales_partitioned",
                    "-- ALTER TABLE lesson02.fact_sales_partitioned DETACH PARTITION ...",
                ],
                "Почему DETACH/DROP старой partition быстрее и безопаснее массового DELETE?",
                "Операция работает на partition boundary и не переписывает весь большой fact как row-by-row DELETE.",
                "Ученик называет retention boundary и rollback/backup consideration.",
                links,
            ),
            RunbookStage(
                "105:00-120:00",
                "20",
                "Design review",
                "Попроси ученика защитить DDL и load policy как production mini-RFC.",
                [
                    "python3 mentor-lab.py runbook greenplum-partitioning homework",
                    "python3 mentor-lab.py student greenplum-partitioning homework",
                ],
                "Какие три evidence artifact нужны для приемки?",
                "DDL, EXPLAIN/catalog checks, statistics/load validation with residual risk.",
                "Ответ покрывает data model, operations и rollback thinking.",
                links,
            ),
        ],
        **lesson02_runbook_paths(),
    )
