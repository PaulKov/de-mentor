# Гайд Ведущего: Lesson 02 Deck

## Упрощенный Маршрут 60 Минут

| Время | Слайды | Что Рассказать |
| --- | --- | --- |
| 00:00-05:00 | 1-2 | Цель урока: partitioning отвечает за pruning/retention, distribution отвечает за segment placement. |
| 05:00-12:00 | 3-4 | Начать с workload contract и показать плохой выбор `loaded_at`. |
| 12:00-22:00 | 5-7 | Показать `PARTITION BY RANGE (sale_date)`, `EXPLAIN`, `pg_partition_tree`, `gp_toolkit.gp_partitions`. |
| 22:00-32:00 | 8-10 | Развести RANGE/LIST/HASH/DEFAULT, AOCO partitions и `ANALYZE`. |
| 32:00-48:00 | 11-14 | Разобрать incremental load, late-arriving facts, idempotency и retention. |
| 48:00-60:00 | 15-18 | Собрать evidence checklist, homework и bridge к Lesson 03. |

## Deep-Dive Маршрут

Для сильного ученика задержись на слайдах 6-7 и 10-14:

- попроси объяснить, как `partition pruning` виден в плане;
- попроси показать, какие leaf partitions вернул `pg_partition_tree`;
- спроси, когда `ANALYZE` touched partitions достаточно;
- разверни late-arriving facts в bounded reload window;
- попроси описать idempotency без двойной загрузки строк.

## Команды Для Демонстрации

```sql
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql

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

ANALYZE lesson02.fact_sales_partitioned;
```

## Финальная Проверка Понимания

Ученик готов к домашке, если он может одной фразой объяснить:

```text
Partition key помогает pruning/retention.
Distribution key помогает segment placement и join locality.
ANALYZE делает load видимым для optimizer.
Incremental load требует retry, validation и late-arriving facts policy.
```
