-- Greenplum lesson 01: cluster configuration and segment monitoring.
--
-- Purpose:
--   Give the mentor and student a production-style SQL checklist for topology,
--   segment health, disk, resource groups, data skew, and useful pseudo/system
--   columns such as gp_segment_id.
--
-- Safe run pattern:
--   \i /mentor-lab/examples/cluster-monitoring.sql
--
-- Optional CLI commands to run outside psql as gpadmin:
--   gpstate
--   gpstate -s
--   gpstate -m
--   gpstate -c
--   gpstate -e

\echo '01. Full segment map: coordinator/master, primaries, mirrors'
SELECT
    dbid,
    content,
    role,
    preferred_role,
    mode,
    status,
    hostname,
    address,
    port,
    datadir
FROM gp_segment_configuration
ORDER BY content, role, hostname, port;

\echo '02. Cluster size summary: segments, hosts, master rows'
SELECT
    current_database() AS db_name,
    COUNT(DISTINCT CASE WHEN content >= 0 THEN content END) AS total_segments,
    COUNT(CASE WHEN content >= 0 AND role = 'p' THEN 1 END) AS active_primary_segments,
    COUNT(CASE WHEN content >= 0 AND role = 'm' THEN 1 END) AS mirror_segments,
    COUNT(DISTINCT CASE WHEN content >= 0 THEN hostname END) AS segment_hosts,
    COUNT(CASE WHEN content = -1 THEN 1 END) AS master_or_standby_rows
FROM gp_segment_configuration;

\echo '03. Segment instances per host'
SELECT
    hostname,
    COUNT(CASE WHEN content >= 0 AND role = 'p' THEN 1 END) AS active_primary_segments,
    COUNT(CASE WHEN content >= 0 AND role = 'm' THEN 1 END) AS mirror_segments,
    COUNT(CASE WHEN content >= 0 THEN 1 END) AS total_segment_instances,
    MIN(content) AS min_content_id,
    MAX(content) AS max_content_id
FROM gp_segment_configuration
WHERE content >= 0
GROUP BY hostname
ORDER BY hostname;

\echo '04. Segment IDs per host and role'
SELECT
    hostname,
    role,
    STRING_AGG(content::text, ',' ORDER BY content) AS segment_ids,
    COUNT(*) AS segment_count
FROM gp_segment_configuration
WHERE content >= 0
GROUP BY hostname, role
ORDER BY hostname, role;

\echo '05. Segment health summary by role, preferred role, mode, status'
SELECT
    role,
    preferred_role,
    mode,
    status,
    COUNT(*) AS segment_instances
FROM gp_segment_configuration
GROUP BY role, preferred_role, mode, status
ORDER BY role, preferred_role, mode, status;

\echo '06. Problem segments: down, not synchronized, or role switched'
SELECT
    dbid,
    content,
    role,
    preferred_role,
    mode,
    status,
    hostname,
    address,
    port,
    datadir
FROM gp_segment_configuration
WHERE status <> 'u'
   OR (
       mode <> 's'
       AND EXISTS (
           SELECT 1
           FROM gp_segment_configuration AS mirrors
           WHERE mirrors.content >= 0
             AND mirrors.role = 'm'
       )
   )
   OR role <> preferred_role
ORDER BY content, role, hostname, port;

\echo '07. Host inventory with up/down, sync state, and switched roles'
SELECT
    hostname,
    COUNT(CASE WHEN role = 'p' THEN 1 END) AS active_primary_segments,
    COUNT(CASE WHEN role = 'm' THEN 1 END) AS mirror_segments,
    COUNT(*) AS total_segment_instances,
    SUM(CASE WHEN status = 'u' THEN 1 ELSE 0 END) AS up_segments,
    SUM(CASE WHEN status = 'd' THEN 1 ELSE 0 END) AS down_segments,
    SUM(CASE WHEN mode = 's' THEN 1 ELSE 0 END) AS synchronized_segments,
    SUM(CASE WHEN role <> preferred_role THEN 1 ELSE 0 END) AS switched_segments
FROM gp_segment_configuration
WHERE content >= 0
GROUP BY hostname
ORDER BY hostname;

\echo '08. Greenplum executor/resource settings visible from SQL'
SELECT
    name,
    setting,
    unit,
    context,
    source
FROM pg_settings
WHERE name IN (
    'gp_resource_manager',
    'gp_vmem_protect_limit',
    'max_connections',
    'shared_buffers',
    'statement_mem',
    'work_mem'
)
ORDER BY name;

\echo '09. Disk free per segment from gp_toolkit.gp_disk_free'
SELECT
    c.content,
    c.role,
    d.dfsegment,
    d.dfhostname,
    d.dfdevice,
    d.dfspace AS free_kb,
    pg_size_pretty(d.dfspace::bigint * 1024) AS free_pretty
FROM gp_toolkit.gp_disk_free AS d
LEFT JOIN gp_segment_configuration AS c
    ON c.content = d.dfsegment
WHERE c.content >= 0
   OR d.dfsegment >= 0
ORDER BY c.content, c.role, d.dfdevice;

\echo '10. Disk free aggregated by host'
SELECT
    d.dfhostname,
    COUNT(*) AS checked_filesystems,
    pg_size_pretty(MIN(d.dfspace)::bigint * 1024) AS min_free_on_host,
    pg_size_pretty(AVG(d.dfspace)::bigint * 1024) AS avg_free_on_host
FROM gp_toolkit.gp_disk_free AS d
WHERE d.dfsegment >= 0
GROUP BY d.dfhostname
ORDER BY d.dfhostname;

\echo '11. Resource groups per segment if gp_toolkit view is available'
SELECT CASE
    WHEN to_regclass('gp_toolkit.gp_resgroup_status_per_segment') IS NULL THEN
        $$SELECT 'gp_toolkit.gp_resgroup_status_per_segment is not available in this cluster or resource manager mode' AS note;$$
    ELSE
        $$SELECT *
          FROM gp_toolkit.gp_resgroup_status_per_segment
          ORDER BY segment_id
          LIMIT 50;$$
END AS sql_to_run
\gexec

\echo '12. Distribution policy text if helper function is available'
SELECT CASE
    WHEN to_regprocedure('pg_get_table_distributedby(oid)') IS NULL THEN
        $$SELECT 'pg_get_table_distributedby(oid) is not available in this cluster version' AS note;$$
    ELSE
        $$SELECT
              n.nspname AS schema_name,
              c.relname AS table_name,
              pg_get_table_distributedby(c.oid) AS distributed_by
          FROM pg_class AS c
          JOIN pg_namespace AS n ON n.oid = c.relnamespace
          WHERE n.nspname = 'lesson01'
            AND c.relkind IN ('r', 'p')
          ORDER BY n.nspname, c.relname;$$
END AS sql_to_run
\gexec

\echo '13. Data skew: rows per gp_segment_id for lesson facts'
SELECT
    'fact_sales_bad' AS table_name,
    gp_segment_id,
    COUNT(*) AS rows_count
FROM lesson01.fact_sales_bad
GROUP BY gp_segment_id
UNION ALL
SELECT
    'fact_sales_good' AS table_name,
    gp_segment_id,
    COUNT(*) AS rows_count
FROM lesson01.fact_sales_good
GROUP BY gp_segment_id
ORDER BY table_name, gp_segment_id;

\echo '14. Data skew ratios for the intentionally bad table'
WITH segment_counts AS (
    SELECT
        gp_segment_id,
        COUNT(*)::numeric AS rows_count
    FROM lesson01.fact_sales_bad
    GROUP BY gp_segment_id
),
summary AS (
    SELECT
        MIN(rows_count) AS min_rows,
        MAX(rows_count) AS max_rows,
        AVG(rows_count) AS avg_rows
    FROM segment_counts
)
SELECT
    min_rows,
    max_rows,
    ROUND(avg_rows, 2) AS avg_rows,
    ROUND(max_rows / NULLIF(avg_rows, 0), 2) AS max_to_avg_ratio,
    ROUND(max_rows / NULLIF(min_rows, 0), 2) AS max_to_min_ratio
FROM summary;

\echo '15. Toolkit skew coefficients if gp_toolkit views are available'
SELECT CASE
    WHEN to_regclass('gp_toolkit.gp_skew_coefficients') IS NULL THEN
        $$SELECT 'gp_toolkit.gp_skew_coefficients is not available in this cluster version' AS note;$$
    ELSE
        $$SELECT
              skcnamespace,
              skcrelname,
              skccoeff
          FROM gp_toolkit.gp_skew_coefficients
          ORDER BY skccoeff DESC NULLS LAST
          LIMIT 20;$$
END AS sql_to_run
\gexec

\echo '16. Toolkit skew idle fractions if gp_toolkit view is available'
SELECT CASE
    WHEN to_regclass('gp_toolkit.gp_skew_idle_fractions') IS NULL THEN
        $$SELECT 'gp_toolkit.gp_skew_idle_fractions is not available in this cluster version' AS note;$$
    ELSE
        $$SELECT
              sifnamespace,
              sifrelname,
              siffraction
          FROM gp_toolkit.gp_skew_idle_fractions
          ORDER BY siffraction DESC NULLS LAST
          LIMIT 20;$$
END AS sql_to_run
\gexec

\echo '17. Useful pseudo/system columns on a user table'
SELECT
    gp_segment_id,
    tableoid::regclass AS table_name,
    ctid,
    xmin,
    xmax,
    cmin,
    cmax,
    sale_id,
    customer_id,
    status
FROM lesson01.fact_sales_good
ORDER BY sale_id
LIMIT 20;

\echo '18. Execute a tiny query on every segment with gp_dist_random if available'
SELECT CASE
    WHEN NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'gp_dist_random') THEN
        $$SELECT 'gp_dist_random is not available in this cluster version' AS note;$$
    ELSE
        $$SELECT gp_segment_id, *
          FROM gp_dist_random('gp_id')
          ORDER BY gp_segment_id;$$
END AS sql_to_run
\gexec

\echo '19. Current execution segment if gp_execution_segment() is available'
SELECT CASE
    WHEN to_regprocedure('gp_execution_segment()') IS NULL THEN
        $$SELECT 'gp_execution_segment() is not available in this cluster version' AS note;$$
    ELSE
        $$SELECT gp_execution_segment() AS execution_segment_on_current_backend;$$
END AS sql_to_run
\gexec

\echo '20. Operational checklist'
SELECT *
FROM (
    VALUES
        ('topology', 'gp_segment_configuration has expected master, primary, mirror rows'),
        ('health', 'no rows where status <> ''u'', mode <> ''s'', or role <> preferred_role'),
        ('disk', 'gp_toolkit.gp_disk_free has enough free space on every segment filesystem'),
        ('resources', 'gp_toolkit.gp_resgroup_status_per_segment is clean when resource groups are enabled'),
        ('skew', 'gp_segment_id row counts and toolkit skew views do not show critical imbalance'),
        ('cli', 'gpstate -s, gpstate -m, gpstate -c, gpstate -e are clean outside psql')
) AS checklist(area, what_good_looks_like)
ORDER BY area;
