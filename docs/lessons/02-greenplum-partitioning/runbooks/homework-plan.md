# План Домашки Lesson 02: 60-90 Минут

## Этап 1: 00:00-15:00 - Поднять Среду

Команды:

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py runbook greenplum-partitioning homework
```

Что сделать: убедиться, что Greenplum доступен, и открыть workbook.

Ожидаемый результат: стенд поднят, `check greenplum` зеленый, понятно где [homework.md](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md).

Как проверяем: есть вывод `python3 mentor-lab.py check greenplum`.

## Этап 2: 15:00-30:00 - Выполнить SQL-Lab

Команды:

```sql
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql
```

Что сделать: создать schema `lesson02`, stage table, bad/good partitioned tables, late-arriving facts.

Ожидаемый результат: есть `lesson02.fact_sales_partitioned`, `lesson02.fact_sales_stage`, `ANALYZE` выполнен.

Как проверяем:

```sql
SELECT schemaname, relname, n_live_tup, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson02'
ORDER BY relname;
```

## Этап 3: 30:00-50:00 - Доказать Partitioning

Команды:

```sql
EXPLAIN
SELECT sum(amount)
FROM lesson02.fact_sales_partitioned
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';

SELECT *
FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass);

SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson02'
ORDER BY partitiontablename;
```

Что сделать: приложить в submission `EXPLAIN` и catalog output.

Ожидаемый ответ: `partition pruning` связан с `sale_date`, а `DISTRIBUTED BY (customer_id)` связан с segment placement.

Как проверяем: в тексте есть pruning/retention и distribution/join locality отдельно.

## Этап 4: 50:00-75:00 - Описать Incremental Load

Команды:

```sql
SELECT sale_date, count(*), sum(amount)
FROM lesson02.fact_sales_stage
GROUP BY sale_date
ORDER BY sale_date;

SELECT load_batch_id, count(*), count(DISTINCT sale_id), sum(amount)
FROM lesson02.fact_sales_partitioned
GROUP BY load_batch_id
ORDER BY load_batch_id;
```

Что сделать: описать stage, publish, late-arriving facts, idempotency, `ANALYZE`, validation.

Ожидаемый ответ: есть bounded reload window или partition-level replace/merge, а не просто повторный `INSERT`.

Как проверяем: повторный запуск не должен логически удваивать факты.

## Этап 5: 75:00-90:00 - Финальная Самопроверка

Команды:

```bash
python3 mentor-lab.py student greenplum-partitioning homework
python3 mentor-lab.py runbook greenplum-partitioning homework
```

Что сделать: сверить submission с [Матрицей оценки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/rubric.md).

Ожидаемый результат: `submissions/lesson02-partitioning.md` содержит DDL, `EXPLAIN`, catalog checks, statistics policy, validation и residual risk.

Как проверяем: можно показать файл ментору и пройти по критериям приемки из [homework.md](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md).
