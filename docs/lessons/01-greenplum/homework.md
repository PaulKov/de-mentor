# Домашняя Работа

План выполнения: `runbooks/homework-plan.md`. На выполнение закладывай 60-90 минут. Следующий урок: `Lesson 02: Partitioning, statistics and incremental loads in MPP`.

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
6. 3 SQL-запроса для проверки качества модели.
7. 3 риска и как ты их проверишь.
8. 2-3 вопроса, которые принесешь на следующий урок.

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

## Self-Check Commands

Запусти стенд:

```bash
python3 mentor-lab.py up greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py psql greenplum
```

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

## Optional Deep Tasks

- Заполни plan-reading ladder из `student-workbook.md`.
- Сравни co-located join, Broadcast Motion и Redistribute Motion.
- Объясни, почему Greenplum vs sharded PostgreSQL - это не только вопрос "несколько PostgreSQL-инстансов".
- Опиши, где бы ты задал `gp_default_storage_options`: table, database, role или instance level.

## Что Принести На Следующий Урок

На `Lesson 02: Partitioning, statistics and incremental loads in MPP` принеси:

- DDL или псевдо-DDL фактов и dimensions;
- rationale по grain, distribution key, partition key и storage;
- self-check output по `gp_segment_id`;
- один `EXPLAIN` с комментарием про Motion;
- вопросы по partition pruning, retention, late-arriving facts, statistics after load, AOCO partitions и operational maintenance.

## Критерии Приемки

Работа засчитывается, если:

- grain описан до выбора ключей;
- distribution key выбран с аргументацией по cardinality и join pattern;
- partition key не смешан с distribution key;
- storage choice объяснен через workload;
- есть проверка skew;
- есть хотя бы один запрос с `EXPLAIN`.
- есть вопросы или гипотезы для `Lesson 02: Partitioning, statistics and incremental loads in MPP`.
