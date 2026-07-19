-- Lesson 03 — Legacy CE trap: opaque filters + EXISTS → Nested Loop Semi Join.
-- Database: mentor. Schema: lesson03.
--
-- Why Legacy (not ORCA): on this shape Legacy naturally chooses
-- Nested Loop Semi Join + Nested Loop Index Scan (est≈29, actual≈40k/seg).
-- ORCA on a similar join often uses Hash Semi Join / different shape —
-- for ORCA's Index Nested Loop demo see lesson03-orca-ce-trap.sql.
--
-- Image note: enable_nestloop defaults to OFF on greenplum-625; we SET it ON
-- (production-like). Hash join stays ON — NL is chosen by cost, not by disabling Hash.
--
-- Story:
--   A) no stats + EXISTS + join to indexed replicated dim → Nested Loop Semi/NL
--   B) TEMP + ANALYZE + drop redundant EXISTS → Hash Join

\echo '=== 0. Setup Legacy case (autostats off) ==='
SET optimizer = off;
SET enable_nestloop = on;
SET enable_hashjoin = on;
SET enable_mergejoin = on;
SET gp_autostats_mode = none;
SET statement_mem = '128MB';
SHOW optimizer;
SHOW enable_nestloop;
SHOW enable_hashjoin;

DROP TABLE IF EXISTS lesson03.leg_orders CASCADE;
DROP TABLE IF EXISTS lesson03.leg_ref CASCADE;

CREATE TABLE lesson03.leg_orders (
    order_id bigint,
    customer_id integer,
    product_id integer,
    order_date date,
    amount numeric(12, 2),
    note text,
    channel text
)
DISTRIBUTED BY (customer_id);

CREATE TABLE lesson03.leg_ref (
    customer_id integer,
    tier text,
    score integer
)
DISTRIBUTED REPLICATED;

INSERT INTO lesson03.leg_orders
SELECT
    gs,
    1 + (gs % 8000),
    1 + (gs % 500),
    DATE '2026-01-01' + ((gs % 90)::int),
    round((1 + (gs % 500))::numeric / 2, 2),
    'note-' || (gs % 17)::text,
    (ARRAY['web', 'app', 'store', 'partner'])[1 + (gs % 4)]
FROM generate_series(1, 80000) AS gs;

INSERT INTO lesson03.leg_ref
SELECT
    gs,
    (ARRAY['bronze', 'silver', 'gold', 'platinum'])[1 + (gs % 4)],
    (gs % 100)
FROM generate_series(1, 8000) AS gs;

CREATE INDEX leg_ref_customer_idx ON lesson03.leg_ref (customer_id);

SET allow_system_table_mods = on;
DELETE FROM pg_statistic
WHERE starelid IN (
    'lesson03.leg_orders'::regclass::oid,
    'lesson03.leg_ref'::regclass::oid
);
UPDATE pg_class
SET relpages = 0, reltuples = 0
WHERE oid IN (
    'lesson03.leg_orders'::regclass::oid,
    'lesson03.leg_ref'::regclass::oid
);
SET allow_system_table_mods = off;

SELECT c.relname, c.reltuples::bigint AS reltuples,
       (SELECT count(*) FROM pg_statistic s WHERE s.starelid = c.oid) AS stat_rows
FROM pg_class c
WHERE c.oid IN ('lesson03.leg_orders'::regclass, 'lesson03.leg_ref'::regclass)
ORDER BY 1;

\echo '=== A. Legacy / NO STATS — Nested Loop Semi Join (est << actual) ==='
EXPLAIN ANALYZE
SELECT o.order_id, o.customer_id, o.amount, r.tier, r.score
FROM lesson03.leg_orders o
JOIN lesson03.leg_ref r ON r.customer_id = o.customer_id
WHERE upper(coalesce(o.note, '')) NOT LIKE '%ZZZNEVER%'
  AND (o.amount * 1.0) >= 0
  AND (mod(o.customer_id, 97) >= 0 OR o.product_id IS NOT NULL)
  AND coalesce(o.channel, '') <> 'IMPOSSIBLE_CHANNEL'
  AND lower(o.channel) IN ('web', 'app', 'store', 'partner')
  AND r.score >= 0
  AND EXISTS (
      SELECT 1
      FROM lesson03.leg_ref r2
      WHERE r2.customer_id = o.customer_id
        AND r2.tier IS NOT NULL
  );

\echo '=== B. TEMP + ANALYZE → Hash Join (EXISTS was redundant for this grain) ==='
DROP TABLE IF EXISTS tmp_leg_enriched;
CREATE TEMP TABLE tmp_leg_enriched AS
SELECT o.order_id, o.customer_id, o.amount, o.channel
FROM lesson03.leg_orders o
WHERE upper(coalesce(o.note, '')) NOT LIKE '%ZZZNEVER%'
  AND (o.amount * 1.0) >= 0
  AND (mod(o.customer_id, 97) >= 0 OR o.product_id IS NOT NULL)
  AND coalesce(o.channel, '') <> 'IMPOSSIBLE_CHANNEL'
  AND lower(o.channel) IN ('web', 'app', 'store', 'partner')
DISTRIBUTED BY (customer_id);

ANALYZE tmp_leg_enriched;
ANALYZE lesson03.leg_ref;

SELECT
    'tmp_leg_enriched' AS rel,
    (SELECT reltuples::bigint FROM pg_class WHERE oid = 'tmp_leg_enriched'::regclass) AS est_rows,
    (SELECT count(*) FROM tmp_leg_enriched) AS actual_rows;

EXPLAIN ANALYZE
SELECT t.order_id, t.customer_id, t.amount, r.tier, r.score
FROM tmp_leg_enriched t
JOIN lesson03.leg_ref r ON r.customer_id = t.customer_id
WHERE r.score >= 0;

\echo 'Done Legacy case. Expect Nested Loop Semi/NL in A, Hash Join in B.'
