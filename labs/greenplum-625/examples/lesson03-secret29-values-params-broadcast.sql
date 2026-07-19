-- Lesson 03 — Greenplum Secrets #29: VALUES/CTE params → Broadcast of FACT.
-- Database: mentor. Schema: lesson03. Optimizer: GPORCA.
--
-- Finger-model: wrapping report parameters in `WITH data_batch AS (VALUES …)`
-- looks elegant, but ORCA may treat the tiny param side as the *build* side
-- sitting on one segment (One-Time Filter gp_execution_segment() = N) and
-- Broadcast the *fact* to join it. Hardcoded predicates (or fact DISTRIBUTED BY
-- the join key / ANALYZE) change Motion shape.
--
-- Related: IN (VALUES …) can become Hash Join + Motion vs IN (1,2,3) → Filter ANY.

\echo '=== 0. Setup fact WITHOUT distribution key and WITHOUT stats (trap) ==='
SET optimizer = on;
SET gp_autostats_mode = none;
SET statement_mem = '256MB';
SHOW optimizer;

DROP TABLE IF EXISTS lesson03.sec29_fact CASCADE;

CREATE TABLE lesson03.sec29_fact (
    n_txt text
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED RANDOMLY;

INSERT INTO lesson03.sec29_fact
SELECT g::text
FROM generate_series(1, 50000) AS g;

-- Intentionally NO ANALYZE here for phase A (Secrets: no key, no stats).

\echo '=== A. BAD — VALUES params CTE ⋈ fact → FACT moves (lab: Gather to QD; prod: often Broadcast) ==='
EXPLAIN ANALYZE
WITH data_batch AS (
    SELECT
        rn::bigint AS rn,
        mdm_id::text AS mdm_id,
        report_dt::date AS report_dt,
        report_from_dt::date AS report_from_dt,
        report_to_dt::date AS report_to_dt
    FROM (
        VALUES
            (0, '10', '2024-01-01', '2023-01-01', '2023-12-31')
    ) AS t(rn, mdm_id, report_dt, report_from_dt, report_to_dt)
)
SELECT
    b.rn,
    b.report_from_dt,
    b.report_to_dt,
    b.report_dt,
    s0.*
FROM lesson03.sec29_fact s0
JOIN data_batch b ON b.mdm_id = s0.n_txt;

\echo '=== B. GOOD — DISTRIBUTED BY join key (params stay tiny, fact local) ==='
ALTER TABLE lesson03.sec29_fact SET DISTRIBUTED BY (n_txt);
ANALYZE lesson03.sec29_fact;

EXPLAIN ANALYZE
WITH data_batch AS (
    SELECT
        rn::bigint AS rn,
        mdm_id::text AS mdm_id,
        report_dt::date AS report_dt,
        report_from_dt::date AS report_from_dt,
        report_to_dt::date AS report_to_dt
    FROM (
        VALUES
            (0, '10', '2024-01-01', '2023-01-01', '2023-12-31')
    ) AS t(rn, mdm_id, report_dt, report_from_dt, report_to_dt)
)
SELECT
    b.rn,
    b.report_from_dt,
    b.report_to_dt,
    b.report_dt,
    s0.*
FROM lesson03.sec29_fact s0
JOIN data_batch b ON b.mdm_id = s0.n_txt;

\echo '=== C. RANDOM + ANALYZE — often Redistribute fact (still Motion) ==='
ALTER TABLE lesson03.sec29_fact SET DISTRIBUTED RANDOMLY;
ANALYZE lesson03.sec29_fact;

EXPLAIN ANALYZE
WITH data_batch AS (
    SELECT
        rn::bigint AS rn,
        mdm_id::text AS mdm_id,
        report_dt::date AS report_dt,
        report_from_dt::date AS report_from_dt,
        report_to_dt::date AS report_to_dt
    FROM (
        VALUES
            (0, '10', '2024-01-01', '2023-01-01', '2023-12-31')
    ) AS t(rn, mdm_id, report_dt, report_from_dt, report_to_dt)
)
SELECT
    b.rn,
    b.report_from_dt,
    b.report_to_dt,
    b.report_dt,
    s0.*
FROM lesson03.sec29_fact s0
JOIN data_batch b ON b.mdm_id = s0.n_txt;

\echo '=== D. Prefer hardcode / scalar params for tiny filters ==='
EXPLAIN ANALYZE
SELECT *
FROM lesson03.sec29_fact s0
WHERE s0.n_txt = '10';

\echo '=== E. Bonus — IN (VALUES) vs IN list (ANY) ==='
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.sec29_fact
WHERE n_txt IN (VALUES ('10'), ('11'), ('12'));

EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.sec29_fact
WHERE n_txt IN ('10', '11', '12');
