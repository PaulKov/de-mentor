-- Greenplum 6.25 Lesson 03 — CLASS DEMO (worked TEMP rewrite).
--
-- Loads homework seed, then builds the two-stage TEMP example used in lecture.
-- Graded homework must NOT copy these stage names/logic blindly — design your own
-- physical strategy (0–3 stages) and prove end-to-end cost + reconciliation.
--
-- Usage:
--   \i /mentor-lab/examples/lesson03-class-demo.sql

\set ON_ERROR_STOP on

\i /mentor-lab/examples/lesson03-homework-seed.sql

\echo '05. CLASS DEMO — TEMP decomposition (not homework answer key)'
DROP TABLE IF EXISTS tmp_lesson03_sales_shaped;
DROP TABLE IF EXISTS tmp_lesson03_sales_feb;

CREATE TEMP TABLE tmp_lesson03_sales_feb
ON COMMIT PRESERVE ROWS
AS
SELECT f.customer_id, f.product_id, f.amount
FROM lesson03.fact_sales f
WHERE f.sale_date >= DATE '2026-02-01'
  AND f.sale_date < DATE '2026-03-01'
DISTRIBUTED BY (customer_id);

ANALYZE tmp_lesson03_sales_feb;

CREATE TEMP TABLE tmp_lesson03_sales_shaped
ON COMMIT PRESERVE ROWS
AS
SELECT
    c.region,
    d.category,
    sum(t.amount) AS revenue
FROM tmp_lesson03_sales_feb t
JOIN lesson03.dim_customer c ON c.customer_id = t.customer_id
JOIN lesson03.dim_product d ON d.product_id = t.product_id
WHERE c.segment <> 'test'
GROUP BY c.region, d.category
DISTRIBUTED BY (region);

ANALYZE tmp_lesson03_sales_shaped;

\echo '06. Optimizer probe helpers (run manually in class)'
-- SET optimizer = on;   -- GPORCA
-- EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case;
-- SET optimizer = off;  -- legacy planner
-- EXPLAIN SELECT * FROM lesson03.v_star_join_orca_case;

SELECT 'lesson03 class demo ready (seed + TEMP example)' AS status;
