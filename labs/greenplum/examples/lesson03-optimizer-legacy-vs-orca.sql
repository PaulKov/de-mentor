-- Demo: Legacy Postgres planner vs GPORCA на одном SQL.
-- Database: mentor. Requires loaded schema lesson03.
--
-- Менторский сценарий:
-- 1) SET optimizer = on;  EXPLAIN ...
-- 2) SET optimizer = off; EXPLAIN ...
-- 3) Сравнить Settings / Optimizer status, join order, Motion.

\echo '=== CURRENT optimizer setting ==='
SHOW optimizer;

\echo '=== GPORCA (optimizer=on) ==='
SET optimizer = on;
EXPLAIN
SELECT *
FROM lesson03.v_star_join_orca_case
ORDER BY revenue DESC
LIMIT 20;

\echo '=== Legacy planner (optimizer=off) ==='
SET optimizer = off;
EXPLAIN
SELECT *
FROM lesson03.v_star_join_orca_case
ORDER BY revenue DESC
LIMIT 20;

\echo '=== Simple query: Legacy often enough ==='
SET optimizer = off;
EXPLAIN
SELECT region, count(*)
FROM lesson03.dim_customer
GROUP BY region;

SET optimizer = on;
EXPLAIN
SELECT region, count(*)
FROM lesson03.dim_customer
GROUP BY region;

\echo '=== Reset session to cluster default ==='
RESET optimizer;
SHOW optimizer;
