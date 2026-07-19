-- Lesson 03 homework — two-way reconciliation template.
-- Adapt column lists to your business-output grain (multiset equality).
-- Hard gate: both EXCEPT ALL diffs must be 0; residual risk does NOT replace this.

\set ON_ERROR_STOP on

-- Use one snapshot (same session / REPEATABLE READ if needed).
-- SET LOCAL optimizer = on;  -- same GUC as rewrite proof

-- Example: materialize monolith and candidate results first, then:
--
-- CREATE TEMP TABLE baseline_result AS
-- SELECT region, category, revenue, category_rank
-- FROM lesson03.v_heavy_olap_monolith
-- DISTRIBUTED BY (region);
--
-- CREATE TEMP TABLE candidate_result AS
-- SELECT region, category, revenue, category_rank
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
    min(revenue) AS revenue_min,
    max(revenue) AS revenue_max
FROM baseline_result;

SELECT
    sum(revenue) AS revenue_sum,
    min(revenue) AS revenue_min,
    max(revenue) AS revenue_max
FROM candidate_result;
