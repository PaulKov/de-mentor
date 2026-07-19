-- MENTOR-ONLY reference rewrite for Lesson 03 (NOT student-facing).
-- Demonstrates one valid multi-stage TEMP strategy for v_heavy_olap_monolith.
-- Students must design their own stages (0–3) and prove e2e cost.

\set ON_ERROR_STOP on

SET optimizer = on;  -- fixed for rewrite proof; do not flip mid-comparison

DROP TABLE IF EXISTS tmp_l03_ref_b;
DROP TABLE IF EXISTS tmp_l03_ref_a;

CREATE TEMP TABLE tmp_l03_ref_a
ON COMMIT PRESERVE ROWS
AS
SELECT f.customer_id, f.product_id, f.amount
FROM lesson03.fact_sales f
WHERE f.sale_date >= DATE '2026-02-01'
  AND f.sale_date < DATE '2026-03-01'
DISTRIBUTED BY (customer_id);

ANALYZE tmp_l03_ref_a;

CREATE TEMP TABLE tmp_l03_ref_b
ON COMMIT PRESERVE ROWS
AS
SELECT
    c.region,
    d.category,
    sum(t.amount) AS revenue
FROM tmp_l03_ref_a t
JOIN lesson03.dim_customer c ON c.customer_id = t.customer_id
JOIN lesson03.dim_product d ON d.product_id = t.product_id
WHERE c.segment <> 'test'
GROUP BY c.region, d.category
DISTRIBUTED BY (region);

ANALYZE tmp_l03_ref_b;

-- Final grain aligned with monolith (window on shaped aggregates)
SELECT
    region,
    category,
    revenue,
    rank() OVER (PARTITION BY region ORDER BY revenue DESC) AS category_rank
FROM tmp_l03_ref_b
ORDER BY region, category_rank;
