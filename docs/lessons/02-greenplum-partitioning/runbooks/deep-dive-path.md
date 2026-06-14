# Deep-Dive Маршрут Lesson 02: 90-120 Минут

Этот маршрут нужен, если ученик уже уверенно читает `EXPLAIN`, не путает `Motion` с join algorithm и может объяснить `DISTRIBUTED BY`.

## Этап 1: 00:00-15:00 - Workload Contract

Команды:

```bash
python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md
python3 mentor-lab.py coach-plan greenplum --query bad_customer_join --sample
```

Что говорит ментор: physical design начинается не с синтаксиса, а с workload: predicates, retention, SLA, late-arriving facts, retry.

Что спрашиваем: какие вопросы надо задать бизнесу до выбора partition key?

Ожидаемый ответ: типовые фильтры, retention, late facts, объемы, SLA загрузки, частота исправлений.

Как проверяем: ученик отделяет бизнес-окно и reporting date от `loaded_at`.

Ссылки: [Workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/student-workbook.md).

## Этап 2: 15:00-35:00 - Pruning Mechanics

Команды:

```sql
SELECT *
FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass);

SELECT c.oid::regclass, pg_get_partkeydef(c.oid)
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'lesson02'
  AND c.relname = 'fact_sales_partitioned';

EXPLAIN
SELECT sum(amount)
FROM lesson02.fact_sales_partitioned
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';
```

Что спрашиваем: как доказать, что `partition pruning` сработал?

Ожидаемый ответ: показать `EXPLAIN` и catalog/tree, где читаются только нужные leaf partitions.

Как проверяем: ученик не путает pruning с segment distribution.

Ссылки: [SQL-lab](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql).

## Этап 3: 35:00-55:00 - Statistics И Plan Quality

Команды:

```sql
SELECT schemaname, relname, n_live_tup, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson02'
ORDER BY relname;

ANALYZE lesson02.fact_sales_partitioned;

EXPLAIN
SELECT customer_id, sum(amount)
FROM lesson02.fact_sales_partitioned
GROUP BY customer_id;
```

Что спрашиваем: когда достаточно обновить statistics на touched partitions, а когда нужен broader refresh?

Ожидаемый ответ: если изменилось только небольшое окно, обновляем touched data; если изменилась форма распределения, проверяем шире.

Как проверяем: ответ содержит estimates, `ANALYZE`, before/after `EXPLAIN`.

Ссылки: [Cheat-sheet](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/cheat-sheet.md).

## Этап 4: 55:00-85:00 - Incremental Load Algorithm

Команды:

```sql
SELECT sale_date, count(*), sum(amount)
FROM lesson02.fact_sales_stage
GROUP BY sale_date
ORDER BY sale_date;

SELECT tableoid::regclass, count(*)
FROM lesson02.fact_sales_partitioned
GROUP BY tableoid::regclass
ORDER BY 1;

SELECT customer_id, sale_date, count(*)
FROM lesson02.fact_sales_partitioned
GROUP BY customer_id, sale_date
HAVING count(*) > 1
ORDER BY count(*) DESC
LIMIT 10;
```

Что спрашиваем: как сделать load идемпотентным?

Ожидаемый ответ: deterministic keys, dedup в stage, bounded replace/merge, validation before publish, audit evidence.

Как проверяем: ученик описывает retry без двойной загрузки фактов.

Ссылки: [Домашка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md).

## Этап 5: 85:00-105:00 - AOCO Partitions И Maintenance

Команды:

```sql
\d+ lesson02.fact_sales_partitioned

SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson02'
ORDER BY partitiontablename;
```

Что спрашиваем: почему `DETACH PARTITION` или `DROP` старой partition обычно лучше массового `DELETE`?

Ожидаемый ответ: operation работает на partition boundary и не переписывает весь большой fact row-by-row.

Как проверяем: ученик называет retention boundary, rollback/backup consideration и operational risk.

Ссылки: [Partitioning strategies deep dive](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md).

## Этап 6: 105:00-120:00 - Mini-RFC Review

Команды:

```bash
python3 mentor-lab.py runbook greenplum-partitioning homework
python3 mentor-lab.py student greenplum-partitioning homework
```

Что спрашиваем: какие три evidence artifact нужны для приемки?

Ожидаемый ответ: DDL, `EXPLAIN`/catalog checks, statistics/load validation with residual risk.

Как проверяем: ответ покрывает data model, operations и rollback thinking.

Ссылки: [Матрица оценки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/rubric.md).
