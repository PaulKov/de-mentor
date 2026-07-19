-- Demo: гистограммы, MCV, selectivity, ORCA vs Legacy cardinality.
-- Database: mentor. Schema: lesson03 (после seed --profile lesson03|academy).
--
-- Сценарий ментора:
-- 1) Показать pg_stats / histogram_bounds / MCV
-- 2) Хорошие оценки (MCV, NDV, range, GROUP BY 1 col)
-- 3) Плохие оценки (коррелированный AND, expr, multi GROUP BY)
-- 4) Сравнить SET optimizer = on|off на одном SQL
-- 5) SET STATISTICS + ANALYZE → пересборка hist

\echo '=== 0. Контекст ==='
SELECT current_database(), current_setting('optimizer') AS optimizer;
SHOW default_statistics_target;

\echo '=== 1. Анатомия статистики: MCV vs histogram ==='
SELECT
    attname,
    null_frac,
    n_distinct,
    most_common_vals,
    most_common_freqs,
    array_length(histogram_bounds, 1) AS hist_n,
    CASE
        WHEN histogram_bounds IS NULL THEN 'all_in_MCV_or_tiny_NDV'
        ELSE 'equi_depth_hist_present'
    END AS hist_status
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename IN ('fact_sales', 'dim_customer', 'dim_product')
ORDER BY tablename, attname;

\echo '=== 1b. Как выглядит histogram (первые/последние границы amount) ==='
SELECT
    attname,
    histogram_bounds[1] AS bound_first,
    histogram_bounds[2] AS bound_second,
    histogram_bounds[array_length(histogram_bounds, 1)] AS bound_last,
    array_length(histogram_bounds, 1) AS hist_n
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename = 'fact_sales'
  AND attname = 'amount';

\echo '=== 2. ХОРОШИЕ оценки: MCV equality ==='
-- Ожидание: estimate ≈ actual ≈ rows * most_common_freqs[enterprise]
SET optimizer = on;
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.dim_customer
WHERE segment = 'enterprise';

\echo '=== 2b. ХОРОШИЕ: NDV equality на fact ==='
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.fact_sales
WHERE product_id = 1;

\echo '=== 2c. ХОРОШИЕ: range по histogram (amount) ==='
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.fact_sales
WHERE amount BETWEEN 10 AND 20;

\echo '=== 2d. ХОРОШИЕ: GROUP BY одного ключа ==='
EXPLAIN ANALYZE
SELECT region, count(*)
FROM lesson03.dim_customer
GROUP BY region;

\echo '=== 3. ПЛОХИЕ оценки: коррелированный AND (независимость) ==='
-- Legacy ≈ s1*s2; ORCA применяет damping, но корреляцию region×segment не знает.
\echo '--- GPORCA ---'
SET optimizer = on;
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.dim_customer
WHERE region = 'us'
  AND segment = 'enterprise';

\echo '--- Legacy ---'
SET optimizer = off;
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.dim_customer
WHERE region = 'us'
  AND segment = 'enterprise';

\echo '=== 3b. ПЛОХИЕ: функция на колонке (stats не применяются) ==='
SET optimizer = on;
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.fact_sales
WHERE date_trunc('month', sale_date) = DATE '2026-02-01';

-- Контроль: тот же смысл без expr — обычно лучше
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date <  DATE '2026-03-01';

\echo '=== 3c. ПЛОХИЕ/рискованные: multi-column GROUP BY ==='
SET optimizer = on;
EXPLAIN ANALYZE
SELECT region, segment, count(*)
FROM lesson03.dim_customer
GROUP BY region, segment;

SET optimizer = off;
EXPLAIN ANALYZE
SELECT region, segment, count(*)
FROM lesson03.dim_customer
GROUP BY region, segment;

\echo '=== 4. IN / NOT IN / OR — сравнить ORCA vs Legacy ==='
\echo '--- IN (MCV values) GPORCA ---'
SET optimizer = on;
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.dim_customer
WHERE segment IN ('enterprise', 'test');

\echo '--- OR эквивалент ---'
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.dim_customer
WHERE segment = 'enterprise'
   OR segment = 'test';

\echo '--- NOT IN (осторожно с NULL-семантикой) ---'
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.dim_customer
WHERE segment NOT IN ('test');

\echo '--- тот же NOT IN под Legacy ---'
SET optimizer = off;
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.dim_customer
WHERE segment NOT IN ('test');

\echo '=== 5. Комбинация AND+OR на fact+dim (цепочка ошибок) ==='
SET optimizer = on;
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.fact_sales f
JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
WHERE c.segment IN ('enterprise', 'mid')
  AND f.sale_date >= DATE '2026-02-01'
  AND (c.region = 'us' OR c.region = 'eu');

SET optimizer = off;
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.fact_sales f
JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
WHERE c.segment IN ('enterprise', 'mid')
  AND f.sale_date >= DATE '2026-02-01'
  AND (c.region = 'us' OR c.region = 'eu');

\echo '=== 6. Как обновляется histogram: SET STATISTICS ==='
-- Сохраните hist_n до/после. На стенде можно откатить target обратно к 100.
SELECT
    attname,
    array_length(histogram_bounds, 1) AS hist_n_before
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename = 'fact_sales'
  AND attname = 'amount';

ALTER TABLE lesson03.fact_sales
  ALTER COLUMN amount SET STATISTICS 200;
ANALYZE lesson03.fact_sales;

SELECT
    attname,
    array_length(histogram_bounds, 1) AS hist_n_after
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename = 'fact_sales'
  AND attname = 'amount';

-- Вернуть целевой target урока (опционально):
ALTER TABLE lesson03.fact_sales
  ALTER COLUMN amount SET STATISTICS 100;
ANALYZE lesson03.fact_sales;

\echo '=== 7. Reset ==='
RESET optimizer;
SHOW optimizer;

\echo '=== Done. Смотрите rows=estimate vs actual rows в EXPLAIN ANALYZE. ==='
