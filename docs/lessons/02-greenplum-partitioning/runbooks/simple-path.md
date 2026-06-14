# Упрощенный Маршрут Lesson 02: 60 Минут

Фокус: partitioning, statistics and incremental loads без перегруза deep-dive деталями.

## Этап 1: 00:00-10:00 - Replay Evidence

Что говорит ментор:

> Начинаем не с нового DDL, а с качества evidence. Если в Lesson 01 не было `EXPLAIN`, `gp_segment_id` и validation, partitioning design будет гаданием.

Команды:

```bash
python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md
python3 mentor-lab.py calibration greenplum show senior
```

Что спрашиваем: какой missing marker из прошлого урока сильнее всего мешает Lesson 02?

Ожидаемый ответ: `EXPLAIN`, `gp_segment_id`, root cause, validation или residual risk.

Как проверяем: ученик называет конкретный evidence gap и объясняет, почему без него нельзя защищать physical design.

Ссылки:

- [Workbook ученика](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/student-workbook.md)
- [Домашка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md)

## Этап 2: 10:00-25:00 - Partition Pruning

Что говорит ментор:

> Partition key выбирают по фильтрам и retention. Distribution key выбирают по join locality и балансу. Это разные физические решения.

Команды:

```sql
\i /mentor-lab/examples/lesson02-partitioning-statistics-loads.sql

EXPLAIN
SELECT sum(amount)
FROM lesson02.fact_sales_partitioned
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';
```

Что спрашиваем: почему `PARTITION BY RANGE (sale_date)` помогает этому фильтру, но не делает join co-located?

Ожидаемый ответ: `partition pruning` отсекает leaf partitions, а `DISTRIBUTED BY` размещает строки по segments.

Как проверяем: ученик отдельно объясняет pruning/retention и join locality/parallelism.

Ссылки:

- [SQL-lab](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/lesson02-partitioning-statistics-loads.sql)
- [Шпаргалка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/cheat-sheet.md)

## Этап 3: 25:00-40:00 - Statistics After Load

Что говорит ментор:

> После incremental load optimizer должен видеть новые cardinality. В MPP stale statistics легко превращаются в плохой Broadcast или Redistribute.

Команды:

```sql
SELECT schemaname, relname, n_live_tup, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson02'
ORDER BY relname;

ANALYZE lesson02.fact_sales_partitioned;
```

Что спрашиваем: почему после load нельзя сразу доверять старому плану?

Ожидаемый ответ: stale statistics ломают estimates и могут поменять join strategy, `Broadcast Motion` или `Redistribute Motion`.

Как проверяем: ученик говорит про before/after `EXPLAIN`, `ANALYZE` и `last_analyze`.

Ссылки:

- [Workbook: statistics](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/student-workbook.md)

## Этап 4: 40:00-55:00 - Incremental Load И Late-Arriving Facts

Что говорит ментор:

> Incremental load в MPP - это не только `INSERT`. Нужно описать окно загрузки, late-arriving facts, idempotency, statistics и validation.

Команды:

```sql
SELECT sale_date, count(*) AS rows_count, sum(amount) AS amount_sum
FROM lesson02.fact_sales_stage
GROUP BY sale_date
ORDER BY sale_date;

SELECT tableoid::regclass AS physical_partition, count(*)
FROM lesson02.fact_sales_partitioned
GROUP BY tableoid::regclass
ORDER BY tableoid::regclass::text;
```

Что спрашиваем: что делать, если факт за прошлый день приехал через три дня?

Ожидаемый ответ: bounded reload window, partition-level replace или идемпотентный merge/upsert, затем validation и `ANALYZE`.

Как проверяем: ученик формулирует retry path без двойной загрузки фактов.

Ссылки:

- [План домашки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/runbooks/homework-plan.md)

## Этап 5: 55:00-60:00 - Домашка

Команды:

```bash
python3 mentor-lab.py runbook greenplum-partitioning homework
python3 mentor-lab.py student greenplum-partitioning homework
```

Что спрашиваем: что ученик принесет на следующий урок?

Ожидаемый ответ: DDL, `EXPLAIN`, partition catalog checks, statistics policy, validation и residual risk.

Как проверяем: ученик может назвать файл сдачи `submissions/lesson02-partitioning.md` и self-check команды.

Ссылки:

- [Домашка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/homework.md)
- [Матрица оценки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/02-greenplum-partitioning/rubric.md)
