-- Lesson 03 homework — two-way reconciliation template.
-- Baseline MUST be lesson03.v_homework_brand_region (graded view).
-- Hard gate: both EXCEPT ALL diffs must be 0; residual risk does NOT replace this.
-- Do NOT reconcile against v_heavy_olap_monolith (class demo).

\set ON_ERROR_STOP on

-- Use one snapshot (same session / REPEATABLE READ if needed).
-- SET LOCAL optimizer = on;  -- same GUC as rewrite proof

-- Example: materialize graded baseline and candidate results first, then:
--
-- CREATE TEMP TABLE baseline_result AS
-- SELECT region, brand, revenue, order_cnt, brand_rank
-- FROM lesson03.v_homework_brand_region
-- DISTRIBUTED BY (region);
--
-- CREATE TEMP TABLE candidate_result AS
-- SELECT region, brand, revenue, order_cnt, brand_rank
-- FROM ( /* your final SELECT */ ) q
-- DISTRIBUTED BY (region);

SELECT
    (
        SELECT count(*)
        FROM (
            SELECT * FROM baseline_result
            EXCEPT ALL
            SELECT * FROM candidate_result
        ) d1
    ) AS baseline_minus_candidate,
    (
        SELECT count(*)
        FROM (
            SELECT * FROM candidate_result
            EXCEPT ALL
            SELECT * FROM baseline_result
        ) d2
    ) AS candidate_minus_baseline;

-- Additional sanity (not a substitute for EXCEPT ALL)
SELECT count(*) AS baseline_rows FROM baseline_result;
SELECT count(*) AS candidate_rows FROM candidate_result;

SELECT
    sum(revenue) AS revenue_sum,
    sum(order_cnt) AS order_cnt_sum,
    min(revenue) AS revenue_min,
    max(revenue) AS revenue_max
FROM baseline_result;

SELECT
    sum(revenue) AS revenue_sum,
    sum(order_cnt) AS order_cnt_sum,
    min(revenue) AS revenue_min,
    max(revenue) AS revenue_max
FROM candidate_result;
