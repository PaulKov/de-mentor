# План Домашки Lesson 03: 90 Минут (Principal)

База данных: **`mentor`**. Схема: **`lesson03`**. Стенд: **`greenplum-625`**.

## Этап 1: 00:00–10:00 — Стенд и контракт

Команды:

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py runbook greenplum-query-tuning homework
python3 mentor-lab.py psql greenplum-625
```

```sql
\conninfo
-- ожидаешь: ... dbname=mentor ...
SHOW optimizer;
```

Что сделать: зафиксировать workload contract (grain, окно дат, что считаешь «тем же ответом»).

Ожидаемый результат: `check greenplum-625` зелёный (после seed), psql в `mentor`, понятен [homework.md](../homework.md).

Как проверяем: в submission есть секция A и вывод `\conninfo` / `check`.

## Этап 2: 10:00–25:00 — Before + stats autopsy

Команды:

```sql
\i /mentor-lab/examples/lesson03-olap-decomposition-tuning.sql

SET optimizer = on;  -- или off; дальше не менять для rewrite proof
EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;

SELECT attname, null_frac, n_distinct, most_common_vals,
       most_common_freqs, array_length(histogram_bounds, 1) AS hist_n
FROM pg_stats
WHERE schemaname = 'lesson03' AND tablename IN ('fact_sales', 'dim_customer')
ORDER BY tablename, attname;

SELECT staattnum, stakind1, stanumbers1, left(stavalues1::text, 80)
FROM pg_statistic
WHERE starelid = 'lesson03.fact_sales'::regclass
ORDER BY 1
LIMIT 20;

EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.fact_sales f
JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
WHERE c.segment = 'enterprise'
  AND f.sale_date >= DATE '2026-02-01'
  AND f.sale_date < DATE '2026-03-01';
```

Что сделать: layered readout + Challenge 1 (estimate failure narrative).

Ожидаемый результат: секции B и C evidence pack.

Как проверяем: в тексте есть Motion/join/estimates и связь predicate → stats slot → rows vs actual.

## Этап 3: 25:00–55:00 — Многостадийный TEMP rewrite

Команды (форма; ключи выбираешь сам):

```sql
-- Stage A
CREATE TEMP TABLE tmp_l03_a
WITH (appendonly=true, orientation=column, compresstype=zstd, compresslevel=1)
AS
SELECT ...
DISTRIBUTED BY (...);
ANALYZE tmp_l03_a;

-- Stage B
CREATE TEMP TABLE tmp_l03_b AS
SELECT ...
FROM tmp_l03_a ...
DISTRIBUTED BY (...);
ANALYZE tmp_l03_b;

EXPLAIN
SELECT ... FROM tmp_l03_b ...;
```

Что сделать: ≥2 стадии, Challenge 2 (co-location proof), after plan при **том же** optimizer.

Ожидаемый результат: `rewrite.sql` + секции D/E.

Как проверяем: есть ANALYZE после каждой стадии; distribution обоснован следующим join/agg; before/after сравнимы.

## Этап 4: 55:00–70:00 — ORCA vs Legacy matrix + spill/TEMP FS

Команды:

```sql
SET optimizer = on;
EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;
EXPLAIN /* твой final */;

SET optimizer = off;
EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case ORDER BY revenue DESC LIMIT 5;
EXPLAIN /* твой final */;

-- TEMP filepath
CREATE TEMP TABLE tmp_l03_fs_demo AS
SELECT customer_id, amount
FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-03-01'
DISTRIBUTED BY (customer_id);

SELECT n.nspname, c.relname, pg_relation_filepath(c.oid)
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relname = 'tmp_l03_fs_demo';

-- optional spill probe (deep)
SET statement_mem = '8MB';
SET optimizer = off;
EXPLAIN ANALYZE
SELECT customer_id, amount FROM lesson03.fact_sales ORDER BY amount;
```

Что сделать: секции F/G + Challenge 3 (optimizer policy RFC).

Ожидаемый результат: матрица 2×2 и хотя бы один FS/spill артефакт.

Как проверяем: маркеры Optimizer: Pivotal… / Postgres…; путь `t_*` или workfile/spill mention.

## Этап 5: 70:00–85:00 — Reconciliation + adversarial review

Команды:

```sql
-- Equality / EXCEPT / checksum aggregates vs monolith window
-- (конкретный SQL — в submission)
```

Что сделать: секции H/I + Challenge 4 (два способа сломать бизнес-результат).

Ожидаемый результат: доказанное равенство на окне **или** честный residual risk с метрикой расхождения.

Как проверяем: без reconciliation/risk — reject по rubric.

## Этап 6: 85:00–90:00 — Финальная самопроверка

Команды:

```bash
python3 mentor-lab.py student greenplum-query-tuning homework
python3 mentor-lab.py runbook greenplum-query-tuning homework
```

Что сделать: сверить пакет с [rubric.md](../rubric.md), добавить вопрос к Уроку 04.

Ожидаемый результат: `submissions/lesson03-query-tuning/` готов к менторскому review.

Как проверяем: можно пройти по критериям приёмки из [homework.md](../homework.md) за 5 минут.
