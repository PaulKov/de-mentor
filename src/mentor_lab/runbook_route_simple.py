"""Greenplum simple mentor route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_routes_common import greenplum_common_links


def greenplum_simple_runbook() -> Runbook:
    common_links = greenplum_common_links()
    return Runbook(
                        lab_name="greenplum",
                        route="simple",
                        title="Simple path: Greenplum lesson 01, 60 minutes",
                        description=(
                            "Базовый маршрут: дать mental model, показать storage, "
                            "distribution, skew, Motion и закончить коротким design review."
                        ),
                        stages=[
                            RunbookStage(
                                "00:00-10:00",
                                "1-6",
                                "Собираем карту Greenplum",
                                (
                                    "Покажи, что Greenplum не sharded PostgreSQL: QD "
                                    "планирует, QE исполняют slices в gang-процессах."
                                ),
                                [
                                    "python3 mentor-lab.py up greenplum",
                                    "python3 mentor-lab.py check greenplum",
                                    "python3 mentor-lab.py psql greenplum",
                                ],
                                "Что делает master/coordinator, а что делают segments?",
                                (
                                    "Master/QD принимает SQL, строит и dispatch-ит план; "
                                    "segments/QE читают локальные данные и исполняют slices."
                                ),
                                "Ученик может словами развести control plane и data plane.",
                                common_links,
                            ),
                            RunbookStage(
                                "10:00-22:00",
                                "7-12",
                                "Storage и columnstore",
                                (
                                    "Покажи Heap vs AO row vs AOCO, затем как включить "
                                    "columnstore через appendoptimized=true и orientation=column."
                                ),
                                [
                                    "\\i /mentor-lab/examples/cluster-monitoring.sql",
                                    "docker compose -f labs/greenplum/docker-compose.yml exec -T -u gpadmin greenplum bash -lc '. /usr/local/greenplum-db/greenplum_path.sh && psql -U gpadmin -d mentor -v ON_ERROR_STOP=1 -f /mentor-lab/examples/storage-and-partitioning.sql'",
                                    "\\d+ lesson01.storage_aoco_demo",
                                    "SELECT c.relname, am.amname AS access_method FROM pg_class c LEFT JOIN pg_am am ON am.oid = c.relam JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'lesson01' AND c.relname LIKE 'storage_%_demo' ORDER BY c.relname;",
                                ],
                                "Почему AOCO не исправляет плохой distribution key?",
                                (
                                    "AOCO ускоряет scan/compression по колонкам, но строки "
                                    "все равно должны быть равномерно размещены по сегментам."
                                ),
                                "Есть три demo table и catalog checks показывают heap/AO/AOCO.",
                                common_links,
                            ),
                            RunbookStage(
                                "22:00-42:00",
                                "13-18",
                                "Distribution, skew и EXPLAIN",
                                (
                                    "Дай ученику workbook: сначала gp_segment_id, затем "
                                    "EXPLAIN, затем сравнение плохой и хорошей таблицы."
                                ),
                                [
                                    "SELECT gp_segment_id, count(*) FROM lesson01.fact_sales_bad GROUP BY gp_segment_id ORDER BY gp_segment_id;",
                                    "EXPLAIN ANALYZE SELECT c.region, sum(f.amount) FROM lesson01.fact_sales_bad f JOIN lesson01.dim_customers c USING (customer_id) GROUP BY c.region;",
                                    "EXPLAIN ANALYZE SELECT c.region, sum(f.amount) FROM lesson01.fact_sales_good f JOIN lesson01.dim_customers c USING (customer_id) GROUP BY c.region;",
                                ],
                                "На что первым делом смотришь в плане Greenplum?",
                                "На Motion nodes, join key vs distribution key, Rows out и skew.",
                                "Ученик называет Redistribute/Gather Motion и причину skew.",
                                common_links,
                            ),
                            RunbookStage(
                                "42:00-60:00",
                                "19-23",
                                "Incident, design review и homework",
                                (
                                    "Переведи упражнение в RCA: что сломалось, чем доказали, "
                                    "какой fix и что принести на следующий урок."
                                ),
                                [
                                    "\\i /mentor-lab/examples/partitioning-strategies.sql",
                                    "SELECT * FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);",
                                    "SELECT * FROM gp_toolkit.gp_partitions WHERE schemaname = 'lesson01';",
                                    "python3 mentor-lab.py incident start greenplum skewed-distribution",
                                    "python3 mentor-lab.py grade greenplum --dry-run",
                                    "python3 mentor-lab.py runbook greenplum homework",
                                ],
                                "Чем partition key отличается от distribution key?",
                                (
                                    "Partition key режет данные для pruning/retention; "
                                    "distribution key размещает строки по сегментам."
                                ),
                                "Ученик формулирует grain, distribution, partition, leaf_partitions and checks.",
                                common_links,
                            ),
                        ],
                    )
