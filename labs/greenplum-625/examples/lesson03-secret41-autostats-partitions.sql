-- Lesson 03 — Greenplum Secrets #41: gp_autostats_mode × partitioned parent.
-- Database: mentor. Schema: lesson03.
--
-- Finger-model: SET gp_autostats_mode = on_no_stats does NOT fire ANALYZE when you
-- INSERT into the *top-level parent* of a partitioned table. Autostats DOES fire when
-- you INSERT directly into a *leaf* partition (where rows live).
--
-- Doc quote (Greenplum 6):
--   "For partitioned tables, automatic statistics collection is not triggered if data
--    is inserted from the top-level parent table… But … if data is inserted directly
--    in a leaf table…"
--
-- Fix: explicit ANALYZE on leaves (or root after load), never assume autostats covered
-- the partition tree after ETL into the parent.

\echo '=== 0. Session: force on_no_stats ==='
SET optimizer = on;
SET gp_autostats_mode = on_no_stats;
SHOW gp_autostats_mode;

DROP TABLE IF EXISTS lesson03.sec41_sales CASCADE;

CREATE TABLE lesson03.sec41_sales (
    sale_id integer,
    sale_date date,
    amount numeric(12, 2)
)
DISTRIBUTED BY (sale_id)
PARTITION BY RANGE (sale_date) (
    START ('2024-01-01'::date) INCLUSIVE
    END ('2024-04-01'::date) EXCLUSIVE
    EVERY ('1 month'::interval)
);

\echo '=== A. INSERT via PARENT — autostats should NOT refresh leaf stats ==='
INSERT INTO lesson03.sec41_sales
SELECT
    g,
    date '2024-01-01' + ((g % 90)) ,
    (g % 1000)::numeric / 3
FROM generate_series(1, 30000) AS g;

-- Catalog view: missing / stale stats after parent insert
SELECT
    c.relname,
    s.last_analyze,
    s.last_autoanalyze,
    s.n_live_tup,
    CASE WHEN st.starelid IS NULL THEN 'MISSING' ELSE 'HAS pg_statistic' END AS stats_state
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_stat_all_tables s ON s.relid = c.oid
LEFT JOIN pg_statistic st ON st.starelid = c.oid AND st.staattnum = 1
WHERE n.nspname = 'lesson03'
  AND c.relname LIKE 'sec41_sales%'
ORDER BY c.relname;

\echo '=== B. INSERT via LEAF — autostats SHOULD fire for that leaf ==='
-- Resolve one leaf name from catalog (GP6 partition children)
SELECT c.relname AS leaf_name
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'lesson03'
  AND c.relname LIKE 'sec41_sales_1_prt_%'
ORDER BY c.relname
LIMIT 1;

-- Insert into first leaf explicitly (name pattern from GP RANGE EVERY)
INSERT INTO lesson03.sec41_sales_1_prt_1
SELECT
    100000 + g,
    date '2024-01-15',
    1.0
FROM generate_series(1, 5000) AS g;

SELECT
    c.relname,
    s.last_analyze,
    s.last_autoanalyze,
    s.n_live_tup,
    CASE WHEN st.starelid IS NULL THEN 'MISSING' ELSE 'HAS pg_statistic' END AS stats_state
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_stat_all_tables s ON s.relid = c.oid
LEFT JOIN pg_statistic st ON st.starelid = c.oid AND st.staattnum = 1
WHERE n.nspname = 'lesson03'
  AND c.relname LIKE 'sec41_sales%'
ORDER BY c.relname;

\echo '=== C. Explicit ANALYZE parent — policy for ETL ==='
ANALYZE lesson03.sec41_sales;

SELECT
    c.relname,
    s.last_analyze,
    CASE WHEN st.starelid IS NULL THEN 'MISSING' ELSE 'HAS pg_statistic' END AS stats_state
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_stat_all_tables s ON s.relid = c.oid
LEFT JOIN pg_statistic st ON st.starelid = c.oid AND st.staattnum = 1
WHERE n.nspname = 'lesson03'
  AND c.relname LIKE 'sec41_sales%'
ORDER BY c.relname;
