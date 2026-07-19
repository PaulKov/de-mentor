-- Lesson 03 — ORCA CE trap: 3 CTEs + opaque predicates → Nested Loop.
-- Database: mentor. Schema: lesson03.
--
-- Why ORCA (not Legacy): with missing/stale stats + replicated indexed dim,
-- GPORCA picks Nested Loop + Index Scan (est≈1, actual≈80k, loops=80k).
-- Legacy on the same shape often keeps Hash Join despite the same under-estimate
-- (see lesson03-legacy-ce-trap.sql for Legacy's natural NL trap: EXISTS).
--
-- Story:
--   A) no stats              → Nested Loop + Index Scan
--   B) ANALYZE + fact reload without ANALYZE (stale) → Nested Loop remains
--   C) TEMP + ANALYZE stage  → Hash Join, est≈actual
--
-- Tables: orca_orders 80k · orca_ref 8k (~10× smaller), DISTRIBUTED REPLICATED + index.

\echo '=== 0. Setup ORCA case (autostats off) ==='
SET optimizer = on;
SET gp_autostats_mode = none;
SET statement_mem = '128MB';
SHOW optimizer;
SHOW gp_autostats_mode;

DROP TABLE IF EXISTS lesson03.orca_orders CASCADE;
DROP TABLE IF EXISTS lesson03.orca_ref CASCADE;

CREATE TABLE lesson03.orca_orders (
    order_id bigint,
    customer_id integer,
    product_id integer,
    order_date date,
    amount numeric(12, 2),
    note text,
    channel text
)
DISTRIBUTED BY (customer_id);

CREATE TABLE lesson03.orca_ref (
    customer_id integer,
    tier text,
    score integer
)
DISTRIBUTED REPLICATED;

INSERT INTO lesson03.orca_orders
SELECT
    gs,
    1 + (gs % 8000),
    1 + (gs % 500),
    DATE '2026-01-01' + ((gs % 90)::int),
    round((1 + (gs % 500))::numeric / 2, 2),
    'note-' || (gs % 17)::text,
    (ARRAY['web', 'app', 'store', 'partner'])[1 + (gs % 4)]
FROM generate_series(1, 80000) AS gs;

INSERT INTO lesson03.orca_ref
SELECT
    gs,
    (ARRAY['bronze', 'silver', 'gold', 'platinum'])[1 + (gs % 4)],
    (gs % 100)
FROM generate_series(1, 8000) AS gs;

CREATE INDEX orca_ref_customer_idx ON lesson03.orca_ref (customer_id);

SET allow_system_table_mods = on;
DELETE FROM pg_statistic
WHERE starelid IN (
    'lesson03.orca_orders'::regclass::oid,
    'lesson03.orca_ref'::regclass::oid
);
UPDATE pg_class
SET relpages = 0, reltuples = 0
WHERE oid IN (
    'lesson03.orca_orders'::regclass::oid,
    'lesson03.orca_ref'::regclass::oid
);
SET allow_system_table_mods = off;

SELECT c.relname, c.reltuples::bigint AS reltuples,
       (SELECT count(*) FROM pg_statistic s WHERE s.starelid = c.oid) AS stat_rows
FROM pg_class c
WHERE c.oid IN ('lesson03.orca_orders'::regclass, 'lesson03.orca_ref'::regclass)
ORDER BY 1;

\echo '=== A. ORCA / NO STATS — Nested Loop (est << actual) ==='
EXPLAIN ANALYZE
WITH cte_orders AS (
    SELECT *
    FROM lesson03.orca_orders o
    WHERE upper(coalesce(o.note, '')) NOT LIKE '%ZZZNEVER%'
      AND (o.amount * 1.0) >= 0
      AND (mod(o.customer_id, 97) >= 0 OR o.product_id IS NOT NULL)
      AND o.order_date IS NOT NULL
),
cte_active AS (
    SELECT *
    FROM cte_orders
    WHERE coalesce(channel, '') <> 'IMPOSSIBLE_CHANNEL'
      AND length(coalesce(note, '')) >= 0
      AND amount IS NOT NULL
),
cte_enriched AS (
    SELECT
        a.order_id,
        a.customer_id,
        a.product_id,
        a.amount,
        a.channel,
        CASE WHEN a.amount > 100 THEN 'hi' ELSE 'lo' END AS band
    FROM cte_active a
    WHERE (a.order_date >= DATE '2025-01-01' OR a.order_date IS NULL)
      AND lower(a.channel) IN ('web', 'app', 'store', 'partner')
)
SELECT e.order_id, e.customer_id, e.amount, e.band, r.tier, r.score
FROM cte_enriched e
JOIN lesson03.orca_ref r ON r.customer_id = e.customer_id
WHERE r.score >= 0;

\echo '=== B. ANALYZE all, reload fact WITHOUT ANALYZE (stale CE) ==='
ANALYZE lesson03.orca_orders;
ANALYZE lesson03.orca_ref;

TRUNCATE lesson03.orca_orders;
INSERT INTO lesson03.orca_orders
SELECT
    gs,
    1 + (gs % 8000),
    1 + (gs % 500),
    DATE '2026-01-01' + ((gs % 90)::int),
    round((1 + (gs % 500))::numeric / 2, 2),
    'note-' || (gs % 17)::text,
    (ARRAY['web', 'app', 'store', 'partner'])[1 + (gs % 4)]
FROM generate_series(1, 80000) AS gs;
-- intentional: no ANALYZE on orca_orders after reload

EXPLAIN ANALYZE
WITH cte_orders AS (
    SELECT *
    FROM lesson03.orca_orders o
    WHERE upper(coalesce(o.note, '')) NOT LIKE '%ZZZNEVER%'
      AND (o.amount * 1.0) >= 0
      AND (mod(o.customer_id, 97) >= 0 OR o.product_id IS NOT NULL)
      AND o.order_date IS NOT NULL
),
cte_active AS (
    SELECT *
    FROM cte_orders
    WHERE coalesce(channel, '') <> 'IMPOSSIBLE_CHANNEL'
      AND length(coalesce(note, '')) >= 0
      AND amount IS NOT NULL
),
cte_enriched AS (
    SELECT
        a.order_id,
        a.customer_id,
        a.product_id,
        a.amount,
        a.channel,
        CASE WHEN a.amount > 100 THEN 'hi' ELSE 'lo' END AS band
    FROM cte_active a
    WHERE (a.order_date >= DATE '2025-01-01' OR a.order_date IS NULL)
      AND lower(a.channel) IN ('web', 'app', 'store', 'partner')
)
SELECT e.order_id, e.customer_id, e.amount, e.band, r.tier, r.score
FROM cte_enriched e
JOIN lesson03.orca_ref r ON r.customer_id = e.customer_id
WHERE r.score >= 0;

\echo '=== C. TEMP + ANALYZE → Hash Join ==='
DROP TABLE IF EXISTS tmp_orca_enriched;
CREATE TEMP TABLE tmp_orca_enriched AS
SELECT
    a.order_id,
    a.customer_id,
    a.product_id,
    a.amount,
    a.channel,
    CASE WHEN a.amount > 100 THEN 'hi' ELSE 'lo' END AS band
FROM lesson03.orca_orders a
WHERE upper(coalesce(a.note, '')) NOT LIKE '%ZZZNEVER%'
  AND (a.amount * 1.0) >= 0
  AND (mod(a.customer_id, 97) >= 0 OR a.product_id IS NOT NULL)
  AND a.order_date IS NOT NULL
  AND coalesce(a.channel, '') <> 'IMPOSSIBLE_CHANNEL'
  AND length(coalesce(a.note, '')) >= 0
  AND a.amount IS NOT NULL
  AND (a.order_date >= DATE '2025-01-01' OR a.order_date IS NULL)
  AND lower(a.channel) IN ('web', 'app', 'store', 'partner')
DISTRIBUTED BY (customer_id);

ANALYZE tmp_orca_enriched;

SELECT
    'tmp_orca_enriched' AS rel,
    (SELECT reltuples::bigint FROM pg_class WHERE oid = 'tmp_orca_enriched'::regclass) AS est_rows,
    (SELECT count(*) FROM tmp_orca_enriched) AS actual_rows;

EXPLAIN ANALYZE
SELECT e.order_id, e.customer_id, e.amount, e.band, r.tier, r.score
FROM tmp_orca_enriched e
JOIN lesson03.orca_ref r ON r.customer_id = e.customer_id
WHERE r.score >= 0;

\echo 'Done ORCA case. Expect Nested Loop in A/B, Hash Join in C.'
