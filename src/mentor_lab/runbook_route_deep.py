"""Greenplum deep mentor route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_routes_common import greenplum_common_links


def greenplum_deep_runbook() -> Runbook:
    common_links = greenplum_common_links()
    return Runbook(
                        lab_name="greenplum",
                        route="deep",
                        title="Deep-dive path: Greenplum lesson 01, 90-120 minutes",
                        description=(
                            "Расширенный маршрут: основной урок плюс QD/QE internals, "
                            "EXPLAIN ladder, physical joins, Broadcast vs Redistribute и storage caveats."
                        ),
                        stages=[
                            RunbookStage(
                                "00:00-15:00",
                                "1-8",
                                "QD/QE, gang и slices",
                                (
                                    "Разбери QD/QE сначала через аналогию, затем технически: "
                                    "plan делится на slices, QueryDispatchDesc уезжает на QE."
                                ),
                                [
                                    "python3 mentor-lab.py lesson greenplum --step 2",
                                    "python3 mentor-lab.py hint greenplum plan-reading",
                                    "python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join --sample",
                                ],
                                "Почему slice почти всегда связан с Motion boundary?",
                                (
                                    "Slice описывает часть плана, которую исполняет gang; "
                                    "Motion соединяет producer/consumer slices между QE."
                                ),
                                "Ученик объясняет QD, QE, gang, slice без чтения C-кода.",
                                common_links
                                + ["docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md"],
                            ),
                            RunbookStage(
                                "15:00-40:00",
                                "9-16",
                                "Storage, defaults и partitioning intro",
                                (
                                    "Покажи table/column/database/role/instance defaults. "
                                    "Instance-level gpconfig оставь как production snippet."
                                ),
                                [
                                    "\\i /mentor-lab/examples/storage-and-partitioning.sql",
                                    "\\i /mentor-lab/examples/partitioning-strategies.sql",
                                    "SHOW gp_default_storage_options;",
                                    "SELECT c.relname, am.amname AS access_method FROM pg_class c LEFT JOIN pg_am am ON am.oid = c.relam JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'lesson01' AND c.relname LIKE 'storage_%_demo' ORDER BY c.relname;",
                                    "SELECT * FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);",
                                    "SELECT * FROM gp_toolkit.gp_partitions WHERE schemaname = 'lesson01';",
                                    "EXPLAIN SELECT sum(amount) FROM lesson01.fact_sales_partition_good WHERE sale_date >= DATE '2024-01-01' AND sale_date < DATE '2024-02-01';",
                                ],
                                "Почему partitioning intro не заменяет distribution design?",
                                (
                                    "Partitioning дает pruning/retention по range/list; "
                                    "distribution решает parallel placement и join locality."
                                ),
                                "Ученик находит PARTITION BY RANGE, PARTITION BY LIST, PARTITION BY HASH, DEFAULT partition, leaf_partitions, ATTACH PARTITION and DETACH PARTITION.",
                                common_links,
                            ),
                            RunbookStage(
                                "40:00-75:00",
                                "24-27",
                                "EXPLAIN ladder и joins",
                                (
                                    "Раздели локальный алгоритм join и MPP data movement: "
                                    "Hash Join отдельно, Broadcast/Redistribute/co-located отдельно."
                                ),
                                [
                                    "python3 mentor-lab.py hint greenplum physical-joins",
                                    "EXPLAIN SELECT c.region, sum(f.amount) FROM lesson01.fact_sales_good f JOIN lesson01.dim_customers c USING (customer_id) GROUP BY c.region;",
                                    "EXPLAIN SELECT p.category, sum(f.amount) FROM lesson01.fact_sales_good f JOIN lesson01.dim_products p USING (product_id) GROUP BY p.category;",
                                ],
                                "Когда Broadcast лучше Redistribute?",
                                (
                                    "Когда broadcast-side мала после фильтров и дешевле "
                                    "разослать ее всем segments, чем перераскладывать большой fact."
                                ),
                                "Ученик заполняет plan-reading ladder из student-workbook.md.",
                                common_links
                                + ["docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md"],
                            ),
                            RunbookStage(
                                "75:00-120:00",
                                "28-30",
                                "Source anchors, caveats и next lesson",
                                (
                                    "Закрой deep route source anchors: cdbdisp_query.c, "
                                    "nodeMotion.c, nodeHashjoin.c; затем выдай homework и Lesson 02."
                                ),
                                [
                                    "python3 mentor-lab.py runbook greenplum homework",
                                    "python3 mentor-lab.py report greenplum --dry-run",
                                    "python3 mentor-lab.py certificate greenplum --dry-run",
                                ],
                                "Что ученик принесет на Lesson 02?",
                                (
                                    "DDL модели, skew checks, EXPLAIN evidence, вопросы по "
                                    "partition pruning/statistics/incremental loads."
                                ),
                                "Есть acceptance criteria и список deliverables из homework.md.",
                                common_links
                                + [
                                    "docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md",
                                    "docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md",
                                ],
                            ),
                        ],
                    )
