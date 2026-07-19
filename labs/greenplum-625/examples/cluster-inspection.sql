\echo '01. Greenplum version'
SELECT version();

\echo '02. Coordinator and segment instances'
SELECT
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
ORDER BY content, role;

\echo '03. Lab topology summary'
SELECT
    SUM(CASE WHEN content = -1 AND role = 'p' THEN 1 ELSE 0 END) AS master_count,
    SUM(CASE WHEN content >= 0 AND role = 'p' THEN 1 ELSE 0 END) AS primary_segments,
    SUM(CASE WHEN content >= 0 AND role = 'm' THEN 1 ELSE 0 END) AS mirror_segments,
    COUNT(DISTINCT CASE WHEN content >= 0 THEN hostname END) AS segment_hosts
FROM gp_segment_configuration;

\echo '04. Memory-related Greenplum settings'
SELECT
    name,
    setting,
    unit
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

\echo '05. Current database size'
SELECT
    current_database() AS database_name,
    pg_size_pretty(pg_database_size(current_database())) AS database_size;

\echo '06. Segment disk free'
SELECT
    dfsegment,
    dfhostname,
    dfdevice,
    pg_size_pretty(dfspace::bigint * 1024) AS free_space
FROM gp_toolkit.gp_disk_free
ORDER BY dfsegment;
