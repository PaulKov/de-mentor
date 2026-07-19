-- Lesson 03 — Greenplum Secrets #42: shard DISTINCT via gp_segment_id (map then sum).
-- Database: mentor. Schema: lesson03. Optimizer: GPORCA.
--
-- Finger-model: COUNT(DISTINCT id) on a huge AOCO table can spill / timeout even when
-- id is the distribution key. Explicitly compute DISTINCT per segment, then SUM:
--
--   SELECT sum(cnt) FROM (
--     SELECT gp_segment_id, count(DISTINCT id) AS cnt FROM t GROUP BY 1
--   ) s;
--
-- Exactness: ONLY when every distinct value lives on exactly one segment
-- (typical when DISTINCT columns ⊆ DISTRIBUTED BY). Otherwise SUM over-counts.
--
-- Lab: 1M rows, id = distribution key, duplicates within segment to force hash work.

\echo '=== 0. Setup AOCO fact DISTRIBUTED BY (id) ==='
SET optimizer = on;
SET gp_autostats_mode = none;
SET statement_mem = '128MB';
SHOW optimizer;

DROP TABLE IF EXISTS lesson03.sec42_ids CASCADE;

CREATE TABLE lesson03.sec42_ids (
    id integer,
    payload text
)
WITH (appendonly = true, orientation = column, compresstype = zstd, compresslevel = 1)
DISTRIBUTED BY (id);

-- 200k unique ids × 5 duplicates = 1M rows (duplicates stay on same segment)
INSERT INTO lesson03.sec42_ids
SELECT a.n, 'p' || (a.n % 7)::text
FROM generate_series(1, 200000) AS a(n),
     generate_series(1, 5) AS b(k);

ANALYZE lesson03.sec42_ids;

\echo '=== A. Canonical COUNT(DISTINCT) ==='
EXPLAIN ANALYZE
SELECT count(DISTINCT id) AS cnt
FROM lesson03.sec42_ids;

\echo '=== B. Map DISTINCT per gp_segment_id, then SUM (exact if dist key) ==='
EXPLAIN ANALYZE
SELECT sum(cnt) AS cnt
FROM (
    SELECT gp_segment_id, count(DISTINCT id) AS cnt
    FROM lesson03.sec42_ids
    GROUP BY 1
) s;

\echo '=== C. Equivalence proof ==='
SELECT
    (SELECT count(DISTINCT id) FROM lesson03.sec42_ids) AS canonical,
    (
        SELECT sum(cnt)
        FROM (
            SELECT gp_segment_id, count(DISTINCT id) AS cnt
            FROM lesson03.sec42_ids
            GROUP BY 1
        ) s
    ) AS mapped;

\echo '=== D. Counter-example — RANDOM dist: mapped SUM is WRONG ==='
DROP TABLE IF EXISTS lesson03.sec42_ids_random CASCADE;
CREATE TABLE lesson03.sec42_ids_random (
    id integer
)
DISTRIBUTED RANDOMLY;

INSERT INTO lesson03.sec42_ids_random
SELECT n FROM generate_series(1, 50000) AS n
UNION ALL
SELECT n FROM generate_series(1, 50000) AS n;  -- same ids can land on both segs

ANALYZE lesson03.sec42_ids_random;

SELECT
    (SELECT count(DISTINCT id) FROM lesson03.sec42_ids_random) AS canonical,
    (
        SELECT sum(cnt)
        FROM (
            SELECT gp_segment_id, count(DISTINCT id) AS cnt
            FROM lesson03.sec42_ids_random
            GROUP BY 1
        ) s
    ) AS mapped_overcount;
