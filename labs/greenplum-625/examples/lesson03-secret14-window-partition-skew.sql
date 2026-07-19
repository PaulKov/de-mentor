-- Lesson 03 — Greenplum Secrets #14: window PARTITION BY constant / skew.
-- Database: mentor. Schema: lesson03. Optimizer: GPORCA.
--
-- Finger-model: WindowAgg needs *all rows of one PARTITION BY key* on one
-- segment. If the table is NOT distributed by that key, ORCA inserts
-- Redistribute Motion Hash Key: <partition cols>. When the key is a constant
-- (all rows share the same invalid_id), Redistribute collapses the *entire*
-- table onto one "victim" segment → spill / workfile limit.
--
-- Fix is rarely "more memory": either change DISTRIBUTED BY to the window key
-- (only if the key has real NDV), or remove/rewrite a senseless PARTITION BY
-- on a technical constant (business bug).

\echo '=== 0. Setup: constant invalid_id, distributed by another key ==='
SET optimizer = on;
SET gp_autostats_mode = none;
SET statement_mem = '256MB';
SHOW optimizer;

DROP TABLE IF EXISTS lesson03.sec14_foo CASCADE;
DROP TABLE IF EXISTS lesson03.sec14_by_invalid CASCADE;

-- Simulate SCD/tech column that is constant in a batch, but table hashed by id.
CREATE TABLE lesson03.sec14_foo (
    id integer,
    invalid_id integer,
    version_id integer,
    hash_diff numeric
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED BY (id);

INSERT INTO lesson03.sec14_foo
SELECT
    g,
    42,                 -- constant PARTITION BY key (the trap)
    1 + (g % 3),
    random()
FROM generate_series(1, 200000) AS g;

ANALYZE lesson03.sec14_foo;

\echo '=== A. BAD — PARTITION BY constant key → Redistribute to victim segment ==='
EXPLAIN ANALYZE
SELECT
    row_number() OVER (
        PARTITION BY invalid_id
        ORDER BY version_id DESC
    ) AS vsn_rank,
    hash_diff,
    invalid_id,
    id
FROM lesson03.sec14_foo;

\echo '=== B. Proof of collapse — count rows per segment after hash(invalid_id) ==='
-- All rows share invalid_id=42 → one segment receives 100% after redistribute.
SELECT gp_segment_id, count(*) AS rows_on_seg
FROM lesson03.sec14_foo
GROUP BY 1
ORDER BY 1;

\echo '=== C. Synthetic fix — DISTRIBUTED BY (invalid_id): Motion may disappear ==='
-- On lab this "fixes" Redistribute, but with NDV(invalid_id)=1 it is still
-- a single-segment table → not a production cure for a constant key.
CREATE TABLE lesson03.sec14_by_invalid (
    id integer,
    invalid_id integer,
    version_id integer,
    hash_diff numeric
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED BY (invalid_id);

INSERT INTO lesson03.sec14_by_invalid
SELECT * FROM lesson03.sec14_foo;
ANALYZE lesson03.sec14_by_invalid;

EXPLAIN ANALYZE
SELECT
    row_number() OVER (
        PARTITION BY invalid_id
        ORDER BY version_id DESC
    ) AS vsn_rank,
    hash_diff,
    invalid_id,
    id
FROM lesson03.sec14_by_invalid;

\echo '=== D. Real fix for constant key — drop PARTITION BY / use global rank ==='
EXPLAIN ANALYZE
SELECT
    row_number() OVER (ORDER BY version_id DESC, id) AS vsn_rank,
    hash_diff,
    invalid_id,
    id
FROM lesson03.sec14_foo;
