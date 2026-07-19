-- Full academy seed: Lessons 01 + 02 + 03 on mentor (Greenplum 6.25).
\echo '=== academy: lesson01 ==='
\i /mentor-lab/seed/lesson01.sql
\echo '=== academy: lesson02 ==='
\i /mentor-lab/seed/lesson02.sql
\echo '=== academy: lesson03 ==='
\i /mentor-lab/seed/lesson03.sql
\echo '=== academy seed complete ==='
SELECT current_database() AS db;
SELECT nspname FROM pg_namespace WHERE nspname LIKE 'lesson0%' ORDER BY 1;
