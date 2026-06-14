# Домашка: Lesson 02

Тема: partitioned fact, statistics policy and incremental load design.

Время: 60-90 минут.

## Цель

Сделать мини-проект, где ты не просто пишешь `CREATE TABLE`, а доказываешь физический дизайн evidence:

- partition key выбран под фильтры и retention;
- distribution key выбран под join locality и баланс;
- `partition pruning` подтвержден через `EXPLAIN`;
- partitions проверены через `pg_partition_tree` или `gp_toolkit.gp_partitions`;
- incremental load имеет stage, publish, late-arriving facts, idempotency, `ANALYZE`, validation.

## Подготовка

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py runbook greenplum-partitioning homework
```

В psql:

```sql
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql
```

## Что Сделать

Создай файл `submissions/lesson02-partitioning.md`.

Включи в него:

- business workload: какие фильтры и какие SLA загрузки;
- DDL sketch для fact table;
- rationale для `PARTITION BY RANGE`;
- rationale для `DISTRIBUTED BY`;
- `EXPLAIN` для запроса с date filter;
- вывод `pg_partition_tree` или `gp_toolkit.gp_partitions`;
- проверку `gp_segment_id`;
- policy для `ANALYZE` после incremental load;
- late-arriving facts policy;
- idempotency/retry strategy;
- validation queries;
- residual risk.

## Мини-Шаблон

```text
Fact grain:
Workload predicates:
Retention policy:
Partition strategy:
Distribution strategy:
Storage strategy:
Incremental window:
Late-arriving facts:
Idempotency:
Statistics after load:
Validation:
Residual risk:
```

## Команды Self-Check

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

SELECT gp_segment_id, count(*) AS rows_count
FROM lesson02.fact_sales_partitioned
GROUP BY gp_segment_id
ORDER BY gp_segment_id;

SELECT schemaname, relname, n_live_tup, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson02'
ORDER BY relname;

ANALYZE lesson02.fact_sales_partitioned;
```

CLI:

```bash
python3 mentor-lab.py student greenplum-partitioning homework
python3 mentor-lab.py runbook greenplum-partitioning homework
python3 mentor-lab.py check greenplum
```

## Критерии Приемки

Работа принимается, если:

- DDL разделяет partition key и distribution key;
- есть `PARTITION BY RANGE (sale_date)` или обоснованная альтернатива;
- есть `WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)` для append-heavy AOCO fact или объяснение, почему выбран другой storage;
- есть `EXPLAIN` для pruning;
- есть `pg_partition_tree` или `gp_toolkit.gp_partitions`;
- есть `ANALYZE` policy;
- late-arriving facts не потеряны и не дублируются;
- validation проверяет row counts и суммы;
- residual risk описан честно.

## Optional Deep Tasks

- Добавь default partition и объясни, когда она помогает, а когда скрывает проблему качества данных.
- Опиши `ATTACH PARTITION` и `DETACH PARTITION` для monthly retention.
- Сравни bad table с `PARTITION BY RANGE (loaded_at)` и good table с `PARTITION BY RANGE (sale_date)`.
- Напиши, какие statistics можно обновлять только на touched partitions.

## Что Принести На Следующий Урок

- один DDL вариант;
- один `EXPLAIN`;
- один вывод partition catalog;
- один риск по stale statistics;
- один вопрос про production query tuning.

План выполнения: [homework-plan.md](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/homework-plan.md).
