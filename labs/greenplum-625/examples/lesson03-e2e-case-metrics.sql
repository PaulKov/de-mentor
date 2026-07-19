-- E2E case: baseline → TEMP decomposition → metrics + equivalence.
-- Database: mentor. Schema: lesson03.
-- Lock GUC; run warm repeats in ONE session. See lessons/lesson-03/artifacts/case/metrics.md.

\echo '=== Locked GUC ==='
SET optimizer = on;
SET statement_mem = '256MB';
SHOW optimizer;
SHOW statement_mem;

\echo '=== Baseline EXPLAIN ANALYZE (monolith grain) ==='
EXPLAIN ANALYZE
SELECT region, category, revenue,
       rank() OVER (PARTITION BY region ORDER BY revenue DESC) AS rnk
FROM (
  SELECT c.region, p.category, sum(f.amount) AS revenue
  FROM lesson03.fact_sales f
  JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
  JOIN lesson03.dim_product p ON p.product_id = f.product_id
  WHERE f.sale_date >= DATE '2026-02-01'
    AND f.sale_date <  DATE '2026-03-01'
    AND c.segment <> 'test'
  GROUP BY c.region, p.category
) s
ORDER BY region, rnk;

\echo '=== TEMP stages ==='
DROP TABLE IF EXISTS tmp_lesson03_sales_shaped;
DROP TABLE IF EXISTS tmp_lesson03_sales_feb;

CREATE TEMP TABLE tmp_lesson03_sales_feb AS
SELECT customer_id, product_id, amount, sale_date
FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date <  DATE '2026-03-01'
DISTRIBUTED BY (customer_id);
ANALYZE tmp_lesson03_sales_feb;

CREATE TEMP TABLE tmp_lesson03_sales_shaped AS
SELECT t.customer_id, t.product_id, t.amount, c.region, p.category
FROM tmp_lesson03_sales_feb t
JOIN lesson03.dim_customer c ON c.customer_id = t.customer_id
JOIN lesson03.dim_product p ON p.product_id = t.product_id
WHERE c.segment <> 'test'
DISTRIBUTED BY (region);
ANALYZE tmp_lesson03_sales_shaped;

\echo '=== After EXPLAIN ANALYZE ==='
EXPLAIN ANALYZE
SELECT region, category, revenue,
       rank() OVER (PARTITION BY region ORDER BY revenue DESC) AS rnk
FROM (
  SELECT region, category, sum(amount) AS revenue
  FROM tmp_lesson03_sales_shaped
  GROUP BY region, category
) s
ORDER BY region, rnk;

\echo '=== Equivalence (EXCEPT ALL both ways) ==='
DROP TABLE IF EXISTS tmp_after_result;
DROP TABLE IF EXISTS tmp_base_result;
CREATE TEMP TABLE tmp_base_result AS
SELECT c.region, p.category, sum(f.amount) AS revenue
FROM lesson03.fact_sales f
JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
JOIN lesson03.dim_product p ON p.product_id = f.product_id
WHERE f.sale_date >= DATE '2026-02-01'
  AND f.sale_date <  DATE '2026-03-01'
  AND c.segment <> 'test'
GROUP BY c.region, p.category;

CREATE TEMP TABLE tmp_after_result AS
SELECT region, category, sum(amount) AS revenue
FROM tmp_lesson03_sales_shaped
GROUP BY region, category;

SELECT 'base_minus_after' AS dir, count(*) FROM (
  SELECT * FROM tmp_base_result EXCEPT ALL SELECT * FROM tmp_after_result
) x
UNION ALL
SELECT 'after_minus_base', count(*) FROM (
  SELECT * FROM tmp_after_result EXCEPT ALL SELECT * FROM tmp_base_result
) y;

\echo '=== TEMP sizes ==='
SELECT pg_size_pretty(pg_total_relation_size('tmp_lesson03_sales_feb')) AS feb,
       pg_size_pretty(pg_total_relation_size('tmp_lesson03_sales_shaped')) AS shaped;

\echo '=== Warm repeats (same session): after agg ×3 ==='
EXPLAIN ANALYZE SELECT region, category, sum(amount) FROM tmp_lesson03_sales_shaped GROUP BY 1,2;
EXPLAIN ANALYZE SELECT region, category, sum(amount) FROM tmp_lesson03_sales_shaped GROUP BY 1,2;
EXPLAIN ANALYZE SELECT region, category, sum(amount) FROM tmp_lesson03_sales_shaped GROUP BY 1,2;

\echo 'Done. Record Planning/Execution times → lessons/lesson-03/artifacts/case/metrics.md'
