-- Lesson 03 — Principal challenge: SCD2 "latest version" CTE and Motion locus.
-- Database: mentor. Schema: lesson03. Optimizer: GPORCA.
--
-- Inspired by Greenplum Secrets (TG) #19 (CTE GROUP BY locus ≠ table hash)
-- and #22 (int vs int8 → Redistribute despite "same" DISTRIBUTED BY).
--
-- Trap: table DISTRIBUTED BY (biz_key, version_id); join to
--   (SELECT biz_key, max(version_id) … GROUP BY biz_key)
-- USING (biz_key, version_id) LOOKS co-located — Senior stops there.
-- Principal reads Motion: Redistribute Hash Key: biz_key — base locus is
-- the *pair* hash, aggregate locus is biz_key-only → Motion is mandatory.
--
-- Real fix: physical distribution matches the access pattern → DISTRIBUTED BY (biz_key).
-- TEMP of the aggregate alone is NOT enough while the fact stays on (biz_key, version_id).

\echo '=== 0. Setup SCD2-like fact (composite distribution) ==='
SET optimizer = on;
SET gp_autostats_mode = none;
SET statement_mem = '256MB';
SHOW optimizer;

DROP TABLE IF EXISTS lesson03.scd2_events CASCADE;
DROP TABLE IF EXISTS lesson03.scd2_events_by_key CASCADE;
DROP TABLE IF EXISTS lesson03.t_join_int CASCADE;
DROP TABLE IF EXISTS lesson03.t_join_int8 CASCADE;

CREATE TABLE lesson03.scd2_events (
    biz_key integer,
    version_id integer,
    payload numeric(12, 2),
    note text
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED BY (biz_key, version_id);

-- 80k keys × 3 versions = 240k rows (lab-scale of Secrets #19)
INSERT INTO lesson03.scd2_events
SELECT a.n, b.v, round(((a.n % 1000) + b.v)::numeric / 3, 2), 'v' || b.v::text
FROM generate_series(1, 80000) AS a(n),
     generate_series(1, 3) AS b(v);

ANALYZE lesson03.scd2_events;

\echo '=== A. BAD — CTE max(version) join (expect Redistribute Motion) ==='
EXPLAIN ANALYZE
SELECT e.biz_key, e.version_id, e.payload, e.note
FROM lesson03.scd2_events e
JOIN (
    SELECT biz_key, max(version_id) AS version_id
    FROM lesson03.scd2_events
    GROUP BY 1
) latest
USING (biz_key, version_id);

\echo '=== B. TEMP of latest keys only — Redistribute of FACT remains ==='
DROP TABLE IF EXISTS tmp_scd2_latest;
CREATE TEMP TABLE tmp_scd2_latest AS
SELECT biz_key, max(version_id) AS version_id
FROM lesson03.scd2_events
GROUP BY 1
DISTRIBUTED BY (biz_key);
ANALYZE tmp_scd2_latest;

EXPLAIN ANALYZE
SELECT e.biz_key, e.version_id, e.payload, e.note
FROM lesson03.scd2_events e
JOIN tmp_scd2_latest latest
USING (biz_key, version_id);

\echo '=== C. GOOD — fact DISTRIBUTED BY (biz_key): no Redistribute on join ==='
CREATE TABLE lesson03.scd2_events_by_key (
    biz_key integer,
    version_id integer,
    payload numeric(12, 2),
    note text
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED BY (biz_key);

INSERT INTO lesson03.scd2_events_by_key
SELECT * FROM lesson03.scd2_events;
ANALYZE lesson03.scd2_events_by_key;

EXPLAIN ANALYZE
SELECT e.biz_key, e.version_id, e.payload, e.note
FROM lesson03.scd2_events_by_key e
JOIN (
    SELECT biz_key, max(version_id) AS version_id
    FROM lesson03.scd2_events_by_key
    GROUP BY 1
) latest
USING (biz_key, version_id);

\echo '=== D. BONUS erudition — int vs int8 "same" DISTRIBUTED BY (id) ==='
CREATE TABLE lesson03.t_join_int (
    id integer
) DISTRIBUTED BY (id);

CREATE TABLE lesson03.t_join_int8 (
    id bigint
) DISTRIBUTED BY (id);

INSERT INTO lesson03.t_join_int
SELECT gs FROM generate_series(1, 50000) AS gs;
INSERT INTO lesson03.t_join_int8
SELECT gs FROM generate_series(1, 50000) AS gs;
ANALYZE lesson03.t_join_int;
ANALYZE lesson03.t_join_int8;

EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.t_join_int a
JOIN lesson03.t_join_int8 b ON a.id = b.id;

\echo 'Done. A: Redistribute×2. B: Redistribute fact remains. C: no Redistribute. D: Redistribute + ::bigint cast.'
