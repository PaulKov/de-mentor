# Домашняя Работа

План выполнения: [homework plan](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/homework-plan.md). На выполнение закладывай 60-90 минут. Следующий урок: `Lesson 02: Partitioning, statistics and incremental loads in MPP`.

## Кейс

Компания собирает события интернет-магазина:

- `orders`
- `order_items`
- `customers`
- `products`
- `payments`
- `delivery_events`

Нужно спроектировать аналитический слой для ежедневной отчетности:

- выручка по дням;
- выручка по регионам;
- топ товаров;
- конверсия успешных оплат;
- задержки доставки.

## Что Нужно Сдать

1. Список фактов и измерений.
2. Grain каждого факта.
3. Distribution key для каждой большой таблицы.
4. Partition key для фактов.
5. Storage choice: heap, AO row или AOCO column.
6. Partitioning strategy: `PARTITION BY RANGE`, `PARTITION BY LIST` или `PARTITION BY HASH`, либо объяснение, почему partitioning пока не нужен.
7. Catalog evidence: `pg_partition_tree` или `gp_toolkit.gp_partitions`, включая `leaf_partitions`.
8. 3 SQL-запроса для проверки качества модели.
9. 3 риска и как ты их проверишь.
10. 2-3 вопроса, которые принесешь на следующий урок.

## Шаблон Ответа

```text
Fact tables:

Dimension tables:

Fact grain:

Distribution strategy:

Partition strategy:

Storage strategy:

Quality checks:

Risks:

Questions for Lesson 02:
```

## Команды Self-Check

Запусти стенд:

```bash
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py psql greenplum
```

Проверь домашку evidence-first autograder:

```bash
python3 mentor-lab.py homework greenplum check --submission submissions/homework.md
```

Autograder смотрит не на объем текста, а на признаки инженерного ответа: facts/dimensions/grain, `DISTRIBUTED BY`, join pattern, cardinality, `PARTITION BY`, storage choice, `pg_partition_tree` / `gp_toolkit.gp_partitions`, `EXPLAIN`, `gp_segment_id`, validation, risks и вопросы к Lesson 02.

Проверь skew:

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_good
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
```

Проверь Motion:

```sql
EXPLAIN
SELECT c.region, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;
```

Проверь storage и partitioning intro:

```sql
\i /mentor-lab/examples/storage-and-partitioning.sql
\d+ lesson01.storage_aoco_demo

EXPLAIN
SELECT sum(amount)
FROM lesson01.fact_sales_partition_good
WHERE sale_date >= DATE '2026-01-01'
  AND sale_date < DATE '2026-02-01';
```

Проверь partitioning strategies и catalog:

```sql
\i /mentor-lab/examples/partitioning-strategies.sql

SELECT *
FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);

SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson01';
```

В выводе найди `DEFAULT partition`, `leaf_partitions`, примеры `PARTITION BY RANGE`, `PARTITION BY LIST`, `PARTITION BY HASH`. Объясни, что будет с out-of-range INSERT без default partition, и где в maintenance пригодятся `ATTACH PARTITION` / `DETACH PARTITION`.

## Опциональные Deep Tasks

- Заполни plan-reading ladder из [student workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md).
- Сравни co-located join, Broadcast Motion и Redistribute Motion.
- Объясни, почему Greenplum vs sharded PostgreSQL - это не только вопрос "несколько PostgreSQL-инстансов".
- Опиши, где бы ты задал `gp_default_storage_options`: table, database, role или instance level.

## Что Принести На Следующий Урок

На `Lesson 02: Partitioning, statistics and incremental loads in MPP` принеси:

- DDL или псевдо-DDL фактов и dimensions;
- rationale по grain, distribution key, partition key и storage;
- partitioning evidence: RANGE/LIST/HASH выбор, `DEFAULT partition` policy, `leaf_partitions`;
- self-check output по `gp_segment_id`;
- один `EXPLAIN` с комментарием про Motion;
- вопросы по partition pruning, retention, late-arriving facts, statistics after load, AOCO partitions и operational maintenance.

## Критерии Приемки

Работа засчитывается, если:

- grain описан до выбора ключей;
- distribution key выбран с аргументацией по cardinality и join pattern;
- partition key не смешан с distribution key;
- есть проверка partitions через `pg_partition_tree` или `gp_toolkit.gp_partitions`;
- storage choice объяснен через workload;
- есть проверка skew;
- есть хотя бы один запрос с `EXPLAIN`.
- есть вопросы или гипотезы для `Lesson 02: Partitioning, statistics and incremental loads in MPP`.
