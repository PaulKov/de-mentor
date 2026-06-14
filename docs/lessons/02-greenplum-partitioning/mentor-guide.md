# План Ментора: Lesson 02

Тема: Partitioning, statistics and incremental loads in MPP.

## Перед Уроком

Проверь стенд:

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py runbook greenplum-partitioning simple
```

Проверь SQL-lab:

```sql
BEGIN;
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql
ROLLBACK;
```

Материалы:

- [Упрощенный маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/simple-path.md)
- [Deep-dive маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/deep-dive-path.md)
- [Workbook ученика](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/student-workbook.md)
- [Домашка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md)
- [SQL-lab](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql)

## Главная Линия Объяснения

1. Сначала workload: какие фильтры, retention, SLA загрузки, late-arriving facts.
2. Потом физика: partition key для pruning/retention, `DISTRIBUTED BY` для segment placement.
3. Потом evidence: `EXPLAIN`, `pg_partition_tree`, `gp_toolkit.gp_partitions`, `gp_segment_id`, `last_analyze`.
4. Потом operation contract: stage, publish, `ANALYZE`, validation, retry, residual risk.

## Что Показать В Greenplum

Запуск SQL-lab:

```sql
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql
```

Bad/good pruning:

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

Catalog checks:

```sql
SELECT *
FROM pg_partition_tree('lesson02.fact_sales_partitioned'::regclass);

SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson02'
ORDER BY partitiontablename;
```

Segment distribution:

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson02.fact_sales_partitioned
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
```

Statistics:

```sql
SELECT schemaname, relname, n_live_tup, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson02'
ORDER BY relname;

ANALYZE lesson02.fact_sales_partitioned;
```

Late-arriving facts:

```sql
SELECT
    tableoid::regclass AS physical_partition,
    sale_id,
    sale_date,
    loaded_at,
    load_batch_id
FROM lesson02.fact_sales_partitioned
WHERE sale_id IN (900001, 900002)
ORDER BY sale_id;
```

## Вопросы Ученику

- Почему `PARTITION BY RANGE (sale_date)` помогает date-filter, но не делает join co-located?
- Как доказать, что `partition pruning` сработал?
- Почему `ANALYZE` после incremental load влияет на join и `Motion`?
- Как сделать load идемпотентным?
- Что делать с late-arriving facts?
- Почему AOCO полезен для append-heavy fact, но не лечит skew?

## Ожидаемые Ответы

- Partitioning отсекает leaf partitions и помогает retention.
- Distribution размещает строки по segments и влияет на locality join.
- `EXPLAIN` должен показать, что читаются только нужные partitions.
- `pg_partition_tree` и `gp_toolkit.gp_partitions` показывают структуру partitioned table.
- `ANALYZE` обновляет statistics, без которых optimizer может выбрать плохой `Broadcast Motion` или `Redistribute Motion`.
- Late-arriving facts требуют bounded reload window, partition-level replace или идемпотентного merge/upsert.

## Как Проверять На Уроке

Ученик готов идти дальше, если он:

- не смешивает partition key и distribution key;
- показывает `EXPLAIN`, а не только рассказывает DDL;
- использует `pg_partition_tree` или `gp_toolkit.gp_partitions`;
- говорит про `ANALYZE` как часть load pipeline;
- формулирует validation before/after;
- называет residual risk.

## Deep-Dive Переключатель

Переходи на [deep-dive маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/deep-dive-path.md), если ученик уверенно отвечает на базовые вопросы.

Не углубляйся, если ученик путает:

- pruning и distribution;
- root partition и leaf partition;
- `loaded_at` и business date;
- `ANALYZE` и `VACUUM`;
- idempotency и “просто еще раз вставить строки”.

## Handoff В Конце

Покажи ученику:

```bash
python3 mentor-lab.py student greenplum-partitioning homework
python3 mentor-lab.py runbook greenplum-partitioning homework
```

Ссылка на домашку: [homework.md](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md).
