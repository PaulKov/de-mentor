"""Greenplum Lesson 02 homework route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_partitioning_common import lesson02_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_partitioning_links


def greenplum_partitioning_homework_runbook() -> Runbook:
    links = greenplum_partitioning_links()
    return Runbook(
        lab_name="greenplum-partitioning",
        route="homework",
        title="Lesson 02 homework path: partitioned fact and incremental load policy",
        description=(
            "Домашка на 60-90 минут: спроектировать partitioned fact, "
            "доказать pruning, описать ANALYZE policy и late-arriving facts."
        ),
        stages=[
            RunbookStage(
                "00:00-15:00",
                "homework",
                "Prepare local stand",
                "Ученик поднимает тот же Greenplum stand и выполняет Lesson 02 SQL-lab.",
                [
                    "python3 mentor-lab.py doctor --full",
                    "python3 mentor-lab.py up greenplum",
                    "python3 mentor-lab.py check greenplum",
                    "python3 mentor-lab.py runbook greenplum-partitioning simple",
                ],
                "Как проверить, что локальная среда совпадает с уроком?",
                "Запустить check greenplum и SQL-lab lesson02-partitioning-statistics-loads.sql.",
                "Есть вывод check и таблицы в schema lesson02.",
                links,
            ),
            RunbookStage(
                "15:00-45:00",
                "homework",
                "Design and evidence",
                "Ученик пишет DDL sketch и прикладывает plan/catalog evidence.",
                [
                    "SELECT * FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass);",
                    "SELECT * FROM gp_toolkit.gp_partitions WHERE schemaname = 'lesson02' ORDER BY partitiontablename;",
                    "EXPLAIN SELECT sum(amount) FROM lesson02.fact_sales_partitioned WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-03-01';",
                ],
                "Какие доказательства показывают, что partitioning выбран под workload?",
                "Predicate, EXPLAIN pruning, partition catalog, retention boundary и отдельный DISTRIBUTED BY rationale.",
                "Submission содержит DDL, EXPLAIN и catalog checks.",
                links,
            ),
            RunbookStage(
                "45:00-75:00",
                "homework",
                "Load policy",
                "Ученик описывает stage, publish, ANALYZE, late facts, retry и validation.",
                [
                    "ANALYZE lesson02.fact_sales_partitioned;",
                    "SELECT schemaname, relname, n_live_tup, last_analyze FROM pg_stat_user_tables WHERE schemaname = 'lesson02' ORDER BY relname;",
                    "SELECT sale_date, count(*), sum(amount) FROM lesson02.fact_sales_partitioned GROUP BY sale_date ORDER BY sale_date;",
                ],
                "Что должно произойти после успешного incremental load?",
                "Validation, ANALYZE touched data, audit evidence и понятный retry path.",
                "Есть statistics policy, self-check commands и residual risk.",
                links,
            ),
        ],
        **lesson02_runbook_paths(),
    )
