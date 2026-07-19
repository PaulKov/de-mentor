-- Seed profile: Lesson 01 core dataset on Greenplum 6.25.
-- Database: mentor. Schema: lesson01.
\i /mentor-lab/seed/00_schema.sql
\i /mentor-lab/seed/01_seed_data.sql
\i /mentor-lab/seed/02_bad_distribution.sql
\i /mentor-lab/seed/03_explain_motion.sql
\i /mentor-lab/seed/04_fix_distribution.sql

\echo 'lesson01@gp6.25 ready'
SELECT current_database() AS db, count(*) AS fact_sales_bad_rows
FROM lesson01.fact_sales_bad;
