# Lesson 02 Simple Path: Partitioning, Statistics And Incremental Loads

## 0-10 Минут: Replay И Missing Evidence

Что говорит ментор:

> Начинаем не с новой теории, а с replay прошлого урока. Если evidence слабый, новый partitioning design будет гаданием.

Что показать:

```bash
python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md
python3 mentor-lab.py calibration greenplum show senior
```

Вопрос ученику: какой missing marker из Lesson 01 сильнее всего мешает Lesson 02?

Проверка: ученик называет конкретный evidence gap: `EXPLAIN`, `gp_segment_id`, root cause, validation или residual risk.

## 10-25 Минут: Partition Pruning

Что говорит ментор:

> Partition key выбирают по фильтрам и retention. Distribution key выбирают по join locality и балансу. Это разные физические решения.

Что показать:

```bash
python3 mentor-lab.py scenario greenplum show partition-pruning
python3 mentor-lab.py misconception greenplum diagnose --text "partition key это то же самое что distribution key"
```

SQL для демонстрации:

```sql
EXPLAIN
SELECT sum(amount)
FROM lesson01.sales_partition_good
WHERE sale_date >= DATE '2024-01-01'
  AND sale_date < DATE '2024-02-01';
```

Вопрос ученику: почему `PARTITION BY RANGE (sale_date)` помогает этому фильтру, но не делает join co-located?

Проверка: ученик отдельно объясняет pruning и `DISTRIBUTED BY`.

## 25-40 Минут: Statistics After Load

Что говорит ментор:

> После incremental load optimizer должен видеть новые cardinality. В MPP stale statistics легко превращаются в плохой Broadcast или Redistribute.

Что показать:

```bash
python3 mentor-lab.py diagnostics greenplum show table-statistics
python3 mentor-lab.py scenario greenplum show stale-statistics
```

SQL для демонстрации:

```sql
ANALYZE lesson01.fact_sales_good;

SELECT schemaname, relname, n_live_tup, last_analyze
FROM pg_stat_user_tables
WHERE schemaname = 'lesson01'
ORDER BY relname;
```

Вопрос ученику: почему после load нельзя сразу доверять старому плану?

Проверка: ученик говорит про estimates, `ANALYZE`, before/after `EXPLAIN`.

## 40-55 Минут: Incremental Loads

Что говорит ментор:

> Incremental load в MPP - это не только `INSERT`. Нужно описать окно загрузки, late-arriving facts, idempotency, statistics и validation.

Что показать:

```bash
python3 mentor-lab.py observe greenplum start --output artifacts/greenplum-observe-checklist.md
python3 mentor-lab.py evidence greenplum collect redistribute-join --output submissions/lesson02-incremental-load.md
```

Дизайн-вопрос: что делать, если факт за прошлый день приехал через три дня?

Проверка: ученик предлагает bounded reload window, merge/upsert strategy или partition-level reload и обязательно validation.

## 55-60 Минут: Домашка

Что дать:

- спроектировать daily partitioned fact;
- описать statistics policy после load;
- описать late-arriving facts;
- приложить `EXPLAIN`, catalog checks и validation.

Что принести на следующий раз:

- один DDL вариант;
- один before/after план;
- один риск по retention или stale statistics.
