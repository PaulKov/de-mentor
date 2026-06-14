# Workbook Ученика: Lesson 02

Тема: Partitioning, statistics and incremental loads in MPP.

## Перед Стартом

Проверь окружение:

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py readiness greenplum --platform macos
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
```

Windows:

```powershell
py mentor-lab.py doctor --full
py mentor-lab.py readiness greenplum --platform windows
py mentor-lab.py up greenplum
py mentor-lab.py check greenplum
```

Linux:

```bash
python3 mentor-lab.py readiness greenplum --platform linux
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
```

Ключевые ссылки:

- [Домашка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md)
- [План домашки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/homework-plan.md)
- [SQL-lab](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql)
- [Шпаргалка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/cheat-sheet.md)

## Упражнение 1: Partition Key Не Равен Distribution Key

Запусти SQL-lab:

```sql
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql
```

Сравни две таблицы:

```sql
EXPLAIN
SELECT sum(amount)
FROM lesson02.fact_sales_bad_partition_key
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';

EXPLAIN
SELECT sum(amount)
FROM lesson02.fact_sales_partitioned
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';
```

Ответь:

- какой predicate включает `partition pruning`;
- почему `PARTITION BY RANGE (sale_date)` помогает date-filter;
- почему это не делает join co-located;
- какой ключ отвечает за размещение строк по segments.

Self-check:

- в ответе есть `partition pruning`;
- в ответе есть `DISTRIBUTED BY`;
- отдельно названы pruning/retention и join locality;
- есть ссылка на `EXPLAIN`.

## Упражнение 2: Как Смотреть Partitions

```sql
SELECT *
FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass);

SELECT
    schemaname,
    tablename,
    partitiontablename,
    partitionlevel,
    partitionrank,
    partitionboundary
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson02'
ORDER BY tablename, partitionlevel, partitionrank, partitiontablename;
```

Ответь:

- сколько leaf partitions у `lesson02.fact_sales_partitioned`;
- какая partition принимает late-arriving fact за январь;
- зачем нужна default partition;
- чем `tableoid` полезен при проверке физической partition.

Проверка placement:

```sql
SELECT
    tableoid::regclass AS physical_partition,
    count(*) AS rows_count,
    min(sale_date) AS min_sale_date,
    max(sale_date) AS max_sale_date
FROM lesson02.fact_sales_partitioned
GROUP BY tableoid::regclass
ORDER BY tableoid::regclass::text;
```

## Упражнение 3: Statistics After Load

```sql
SELECT schemaname, relname, n_live_tup, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson02'
ORDER BY relname;

ANALYZE lesson02.fact_sales_partitioned;
```

Ответь:

- почему `ANALYZE` входит в incremental load contract;
- когда достаточно анализировать touched partitions;
- когда нужна более широкая проверка statistics;
- как stale estimates могут привести к плохому `Broadcast Motion` или `Redistribute Motion`.

Self-check:

- есть before/after `EXPLAIN`;
- есть `last_analyze`;
- есть вывод про plan quality, а не только “запрос стал быстрее”.

## Упражнение 4: Incremental Load И Late-Arriving Facts

Stage rows:

```sql
SELECT sale_date, count(*) AS rows_count, sum(amount) AS amount_sum
FROM lesson02.fact_sales_stage
GROUP BY sale_date
ORDER BY sale_date;
```

Target rows:

```sql
SELECT
    load_batch_id,
    count(*) AS rows_count,
    count(DISTINCT sale_id) AS distinct_sale_ids,
    sum(amount) AS amount_sum
FROM lesson02.fact_sales_partitioned
GROUP BY load_batch_id
ORDER BY load_batch_id;
```

Мини-шаблон ответа:

```text
Fact grain:
Partition strategy:
Distribution strategy:
Incremental window:
Late-arriving facts:
Idempotency:
Statistics after load:
Validation:
Residual risk:
```

Вопрос: что делать, если факт за прошлый день приехал через три дня?

Ожидаемый ход мысли: bounded reload window, partition-level replace или идемпотентный merge/upsert, затем validation и `ANALYZE`.

## Упражнение 5: AOCO Partitioned Fact

В SQL-lab таблица создается как AOCO:

```sql
CREATE TABLE lesson02.fact_sales_partitioned (...)
WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date);
```

Проверь в psql:

```sql
\d+ lesson02.fact_sales_partitioned
```

Ответь:

- почему AOCO полезен для scan-heavy append fact;
- почему AOCO не исправляет плохой distribution key;
- почему retention через `DETACH PARTITION` или `DROP` старой leaf partition обычно лучше массового `DELETE`.

## Что Сдать После Урока

Файл `submissions/lesson02-partitioning.md`:

- DDL sketch для partitioned fact;
- объяснение partition key и distribution key;
- `EXPLAIN` для pruning;
- вывод `pg_partition_tree` или `gp_toolkit.gp_partitions`;
- statistics policy после incremental load;
- late-arriving facts policy;
- validation и residual risk.

Подробные критерии: [homework.md](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md).

## Что Принести На Следующий Урок

- один вопрос по `partition pruning`;
- один вопрос по statistics;
- один production-риск по incremental load;
- один план, где ты не уверен в `Motion` или estimates.
