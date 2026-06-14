"""Greenplum Lesson 02 simple mentor route."""

from mentor_lab.runbook_models import Runbook, RunbookStage
from mentor_lab.runbook_route_partitioning_common import lesson02_runbook_paths
from mentor_lab.runbook_routes_common import greenplum_partitioning_links


def greenplum_partitioning_simple_runbook() -> Runbook:
    links = greenplum_partitioning_links()
    return Runbook(
        lab_name="greenplum-partitioning",
        route="simple",
        title="Lesson 02 simple path: partitioning, statistics and incremental loads",
        description=(
            "60-минутный маршрут: replay evidence, partition pruning, ANALYZE "
            "после load, late-arriving facts и короткая домашка."
        ),
        stages=[
            RunbookStage(
                "00:00-10:00",
                "1-3",
                "Replay evidence",
                "Начни с качества evidence из Lesson 01: без планов и проверок новый design будет гаданием.",
                [
                    "python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md",
                    "python3 mentor-lab.py calibration greenplum show senior",
                ],
                "Какой missing marker из прошлого урока сильнее всего мешает Lesson 02?",
                "EXPLAIN, gp_segment_id, root cause, validation или residual risk.",
                "Ученик называет конкретный gap и связывает его с будущим partitioning design.",
                links,
            ),
            RunbookStage(
                "10:00-25:00",
                "4-7",
                "Partition pruning",
                "Покажи, что partition key выбирают по фильтрам и retention, а DISTRIBUTED BY по locality.",
                [
                    "python3 mentor-lab.py scenario greenplum show partition-pruning",
                    "python3 mentor-lab.py misconception greenplum diagnose --text \"partition key это то же самое что distribution key\"",
                    "docker compose -f labs/greenplum/docker-compose.yml exec -T -u gpadmin greenplum bash -lc '. /usr/local/greenplum-db/greenplum_path.sh && psql -U gpadmin -d mentor -v ON_ERROR_STOP=1 -f /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql'",
                ],
                "Почему PARTITION BY RANGE (sale_date) не делает join co-located?",
                "Partition pruning отсекает leaf partitions, а distribution key размещает строки по segments.",
                "В ответе отдельно названы pruning/retention и join locality/parallelism.",
                links,
            ),
            RunbookStage(
                "25:00-40:00",
                "8-10",
                "Statistics after load",
                "Свяжи incremental load с optimizer contract: после заметной загрузки нужна статистика.",
                [
                    "ANALYZE lesson02.fact_sales_partitioned;",
                    "SELECT schemaname, relname, n_live_tup, last_analyze FROM pg_stat_user_tables WHERE schemaname = 'lesson02' ORDER BY relname;",
                    "EXPLAIN SELECT product_id, sum(amount) FROM lesson02.fact_sales_partitioned WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-03-01' GROUP BY product_id;",
                ],
                "Почему после load нельзя сразу доверять старому плану?",
                "Stale statistics ломают estimates и могут поменять join strategy, Broadcast или Redistribute Motion.",
                "Ученик говорит про before/after EXPLAIN и last_analyze.",
                links,
            ),
            RunbookStage(
                "40:00-55:00",
                "11-14",
                "Incremental load и late-arriving facts",
                "Разбери stage table, bounded reload window, idempotency и validation до публикации.",
                [
                    "SELECT tableoid::regclass AS physical_partition, count(*) FROM lesson02.fact_sales_partitioned GROUP BY tableoid::regclass ORDER BY 1;",
                    "SELECT * FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass);",
                    "SELECT * FROM gp_toolkit.gp_partitions WHERE schemaname = 'lesson02' ORDER BY partitiontablename;",
                ],
                "Что делать, если факт за прошлый день приехал через три дня?",
                "Нужен bounded reload window, partition-level replace или идемпотентный merge/upsert плюс validation.",
                "Ученик формулирует окно, повторный запуск и проверку row counts/sums.",
                links,
            ),
            RunbookStage(
                "55:00-60:00",
                "15",
                "Домашка",
                "Выдай mini-project: DDL, pruning evidence, stats policy, late facts и критерии приемки.",
                [
                    "python3 mentor-lab.py runbook greenplum-partitioning homework",
                    "python3 mentor-lab.py student greenplum-partitioning homework",
                ],
                "Что ученик принесет на следующий урок?",
                "DDL, EXPLAIN evidence, partition catalog checks, ANALYZE policy и residual risk.",
                "Ученик понимает deliverables и self-check команды.",
                links,
            ),
        ],
        **lesson02_runbook_paths(),
    )
