# Шпаргалка: Partitioning, Statistics, Incremental Loads

## Короткая Модель

```text
Partition key = pruning, retention, manageability.
Distribution key = segment placement, parallelism, join locality.
Statistics = optimizer visibility after load.
Incremental load = stage + publish + ANALYZE + validation + retry.
```

## DDL

```sql
CREATE TABLE lesson02.fact_sales_partitioned (
    sale_id bigint,
    customer_id integer,
    sale_date date,
    amount numeric(12, 2)
)
WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date);
```

## Смотреть Partitions

```sql
SELECT *
FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass);

SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson02'
ORDER BY partitiontablename;
```

## Смотреть Физическое Попадание Строк

```sql
SELECT
    tableoid::regclass AS physical_partition,
    count(*) AS rows_count
FROM lesson02.fact_sales_partitioned
GROUP BY tableoid::regclass
ORDER BY tableoid::regclass::text;
```

## Смотреть Segments

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson02.fact_sales_partitioned
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
```

## Statistics

```sql
SELECT schemaname, relname, n_live_tup, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson02'
ORDER BY relname;

ANALYZE lesson02.fact_sales_partitioned;
```

## EXPLAIN Для Pruning

```sql
EXPLAIN
SELECT sum(amount)
FROM lesson02.fact_sales_partitioned
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';
```

## Late-Arriving Facts

Проверочный вопрос: что делать, если факт за январь приехал в февральской загрузке?

Хороший ответ:

- bounded reload window;
- partition-level replace или идемпотентный merge/upsert;
- validation row counts/sums;
- `ANALYZE` touched data;
- audit evidence для retry.

## Частые Ошибки

- выбирать partition key как distribution key без workload;
- partition by `loaded_at`, когда отчеты фильтруют `sale_date`;
- забывать `ANALYZE` после load;
- делать massive `DELETE` вместо retention by partition boundary;
- считать AOCO решением skew или bad join locality.

SQL-lab: [lesson02-partitioning-statistics-loads.sql](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql).
