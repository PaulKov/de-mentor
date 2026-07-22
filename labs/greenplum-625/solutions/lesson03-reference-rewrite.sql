-- MENTOR-ONLY reference rewrite for Lesson 03 (NOT student-facing).
-- Graded target: lesson03.v_homework_brand_region (March × brand × region).
-- Class demo view v_heavy_olap_monolith is separate — do not treat as homework answer.
-- Students must explore ≥2 candidates (A shallow / B multi-stage) and prove e2e cost.

\set ON_ERROR_STOP on

SET optimizer = on;  -- fixed for rewrite proof; do not flip mid-comparison

DROP TABLE IF EXISTS tmp_l03_ref_b;
DROP TABLE IF EXISTS tmp_l03_ref_a;

-- Stage A: prune fact + co-locate on customer for dim join
CREATE TEMP TABLE tmp_l03_ref_a
ON COMMIT PRESERVE ROWS
AS
SELECT f.customer_id, f.product_id, f.amount
FROM lesson03.fact_sales f
WHERE f.sale_date >= DATE '2026-03-01'
  AND f.sale_date < DATE '2026-04-01'
DISTRIBUTED BY (customer_id);

ANALYZE tmp_l03_ref_a;

-- Stage B: join + filter + aggregate to homework grain (pre-window)
CREATE TEMP TABLE tmp_l03_ref_b
ON COMMIT PRESERVE ROWS
AS
SELECT
    c.region,
    d.brand,
    sum(t.amount) AS revenue,
    count(*) AS order_cnt
FROM tmp_l03_ref_a t
JOIN lesson03.dim_customer c ON c.customer_id = t.customer_id
JOIN lesson03.dim_product d ON d.product_id = t.product_id
WHERE c.segment IN ('smb', 'mid')
  AND d.category <> 'security'
GROUP BY c.region, d.brand
DISTRIBUTED BY (region);

ANALYZE tmp_l03_ref_b;

-- Final grain aligned with v_homework_brand_region
SELECT
    region,
    brand,
    revenue,
    order_cnt,
    dense_rank() OVER (PARTITION BY region ORDER BY revenue DESC) AS brand_rank
FROM tmp_l03_ref_b
ORDER BY region, brand_rank;
