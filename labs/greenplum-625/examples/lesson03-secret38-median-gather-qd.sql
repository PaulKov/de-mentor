-- Lesson 03 — Greenplum Secrets #38: ordered-set median → Gather-all to QD.
-- Database: mentor. Schema: lesson03. Prefer Legacy for classic Gather plan shape;
-- ORCA may rewrite, but the physical truth remains: global percentile needs a total order.
--
-- Finger-model: percentile_disc(0.5) WITHIN GROUP (ORDER BY n) must sort the *whole*
-- multiset. In MPP that usually means Gather Motion of (almost) all rows to QD, then
-- Aggregate — QD becomes the bottleneck (Secrets: 100M rows, ~74s on many segs).
--
-- Approximate MPP trick (only when DISTRIBUTED RANDOMLY ≈ i.i.d. shards):
--   avg( local_median ) where local_median = percentile_disc(0.5) … GROUP BY gp_segment_id
-- Not exact; lab shows closeness + plan without gathering every row for the final sort.

\echo '=== 0. Setup RANDOM multiset (1..1000 repeated) ==='
SET optimizer = off;   -- Legacy shows Gather→Aggregate clearly (Secrets used Postgres planner)
SET gp_autostats_mode = none;
SET statement_mem = '256MB';
SHOW optimizer;

DROP TABLE IF EXISTS lesson03.sec38_nums CASCADE;

CREATE TABLE lesson03.sec38_nums (
    n integer
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED RANDOMLY;

INSERT INTO lesson03.sec38_nums
SELECT a.n
FROM generate_series(1, 1000) AS a(n),
     generate_series(1, 200) AS b(k);   -- 200k rows lab-scale of Secrets pattern

ANALYZE lesson03.sec38_nums;

\echo '=== A. Exact median — expect Gather of (almost) all rows to QD ==='
EXPLAIN ANALYZE
SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n) AS median
FROM lesson03.sec38_nums;

SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n) AS median
FROM lesson03.sec38_nums;

\echo '=== B. Approximate — local medians per segment, then AVG ==='
EXPLAIN ANALYZE
SELECT avg(median) AS approx_median
FROM (
    SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n) AS median
    FROM lesson03.sec38_nums
    GROUP BY gp_segment_id
) s;

SELECT avg(median) AS approx_median,
       min(median) AS min_local,
       max(median) AS max_local
FROM (
    SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n) AS median
    FROM lesson03.sec38_nums
    GROUP BY gp_segment_id
) s;

\echo '=== C. TRY optimizer=on (ordered-set often forces Legacy fallback) ==='
SET optimizer = on;
EXPLAIN ANALYZE
SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n) AS median
FROM lesson03.sec38_nums;

EXPLAIN ANALYZE
SELECT avg(median) AS approx_median
FROM (
    SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n) AS median
    FROM lesson03.sec38_nums
    GROUP BY gp_segment_id
) s;
