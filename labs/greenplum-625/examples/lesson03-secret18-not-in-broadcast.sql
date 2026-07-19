-- Lesson 03 — Greenplum Secrets #18: NOT IN → Broadcast Motion.
-- Database: mentor. Schema: lesson03. Optimizer: GPORCA.
--
-- Finger-model: NOT IN is NOT a cheap "anti-filter". In GPORCA it becomes
-- Hash Left Anti Semi (Not-In) Join and often Broadcasts the *entire*
-- inner set to every segment. NOT EXISTS / LEFT JOIN … IS NULL stay local
-- Hash Anti when keys align with DISTRIBUTED BY.
--
-- Lab scale (2 segments): 400k rows — enough to see Broadcast in the plan.
-- Production story in TG used 100M×100M (~3 orders of magnitude).

\echo '=== 0. Setup equal-sized AOCO tables DISTRIBUTED BY (n) ==='
SET optimizer = on;
SET gp_autostats_mode = none;
SET statement_mem = '256MB';
SHOW optimizer;

DROP TABLE IF EXISTS lesson03.sec18_t1 CASCADE;
DROP TABLE IF EXISTS lesson03.sec18_t2 CASCADE;

CREATE TABLE lesson03.sec18_t1 (
    n integer
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED BY (n);

CREATE TABLE lesson03.sec18_t2 (
    n integer
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED BY (n);

INSERT INTO lesson03.sec18_t1
SELECT generate_series(1, 400000);

INSERT INTO lesson03.sec18_t2
SELECT * FROM lesson03.sec18_t1;

ANALYZE lesson03.sec18_t1;
ANALYZE lesson03.sec18_t2;

\echo '=== A. BAD — NOT IN (expect Broadcast Motion of t2) ==='
EXPLAIN ANALYZE
SELECT t1.*
FROM lesson03.sec18_t1 t1
WHERE t1.n NOT IN (SELECT n FROM lesson03.sec18_t2);

\echo '=== B. GOOD — NOT EXISTS (expect Hash Anti, no Broadcast of full t2) ==='
EXPLAIN ANALYZE
SELECT t1.*
FROM lesson03.sec18_t1 t1
WHERE NOT EXISTS (
    SELECT 1 FROM lesson03.sec18_t2 t2 WHERE t2.n = t1.n
);

\echo '=== C. GOOD — LEFT JOIN anti-pattern (watch duplicates if t2 not unique) ==='
EXPLAIN ANALYZE
SELECT t1.*
FROM lesson03.sec18_t1 t1
LEFT JOIN lesson03.sec18_t2 t2 ON t1.n = t2.n
WHERE t2.n IS NULL;

\echo '=== D. Semantics trap — NULL in NOT IN list voids the filter ==='
-- Educational only: if inner can contain NULL, NOT IN is not equivalent to NOT EXISTS.
EXPLAIN
SELECT t1.*
FROM lesson03.sec18_t1 t1
WHERE t1.n NOT IN (SELECT CASE WHEN n = -1 THEN NULL ELSE n END FROM lesson03.sec18_t2 LIMIT 1);
