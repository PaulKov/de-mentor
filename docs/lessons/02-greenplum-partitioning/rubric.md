# Матрица Оценки: Lesson 02

## Навыки

| Навык | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Partitioning model | путает partition и distribution | выбирает range key, но слабо объясняет workload | связывает predicate, pruning, retention и leaf partitions |
| Distribution model | выбирает тот же ключ “для порядка” | понимает баланс, но не join locality | отдельно защищает `DISTRIBUTED BY` через join pattern и `gp_segment_id` |
| EXPLAIN evidence | нет плана | есть план без вывода | показывает `partition pruning`, estimates и возможный `Motion` risk |
| Catalog checks | нет checks | есть один query | использует `pg_partition_tree`, `gp_toolkit.gp_partitions`, `tableoid` |
| Statistics policy | забывает `ANALYZE` | пишет “ANALYZE после load” | объясняет touched data, stale estimates и before/after plan |
| Incremental load | только `INSERT` | есть stage и validation | есть stage, publish, late-arriving facts, idempotency, retry, residual risk |
| Storage | не понимает AOCO | включает `orientation=column` | объясняет AOCO как scan/storage choice, а не замену distribution |

## Оценка

- 0-5: нужно повторить Lesson 01 evidence и базовый partitioning intro.
- 6-9: можно идти дальше, но нужен разбор домашки.
- 10-12: готов к production-style query tuning.
- 13-14: сильный уровень, можно давать hidden incident и source-level вопросы.

## Вопросы Ментора

- Чем `partition pruning` отличается от colocated join?
- Почему `PARTITION BY RANGE (sale_date)` может быть правильным, а `DISTRIBUTED BY (customer_id)` тоже правильным?
- Что покажет `pg_partition_tree`?
- Что покажет `gp_toolkit.gp_partitions`?
- Когда `ANALYZE lesson02.fact_sales_partitioned` обязателен?
- Как обрабатывать late-arriving facts без дублей?
- Почему `DETACH PARTITION` полезен для retention?

## Критерии Приемки

Принято, если submission содержит:

- DDL sketch;
- `EXPLAIN`;
- partition catalog output;
- `gp_segment_id` check;
- statistics policy;
- late-arriving facts policy;
- validation;
- residual risk.

План домашки: [homework-plan.md](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/homework-plan.md).
