USE CATALOG hive_metastore;
CREATE DATABASE IF NOT EXISTS lesson05;
CREATE TABLE IF NOT EXISTS lesson05.hms_catalog_comparison (
  event_id STRING,
  category STRING,
  amount DECIMAL(12, 2),
  event_time TIMESTAMP(3)
)
PARTITIONED BY (category)
WITH (
  'format-version' = '2',
  'write.format.default' = 'parquet',
  'write.distribution-mode' = 'hash'
);

-- Make this bounded teaching write finish before reading the Iceberg metadata.
SET 'execution.runtime-mode' = 'BATCH';
SET 'table.dml-sync' = 'true';
SET 'sql-client.execution.result-mode' = 'TABLEAU';

INSERT INTO lesson05.hms_catalog_comparison VALUES
  ('hms-001', 'books', 12.50, TIMESTAMP '2025-10-14 10:00:01.000'),
  ('hms-002', 'books', 19.00, TIMESTAMP '2025-10-14 10:00:21.000'),
  ('hms-003', 'music', 8.75, TIMESTAMP '2025-10-14 10:01:05.000');

SELECT category, COUNT(*) AS rows_count, SUM(amount) AS revenue
FROM lesson05.hms_catalog_comparison
GROUP BY category;

SELECT committed_at, snapshot_id, operation, summary
FROM lesson05.`hms_catalog_comparison$snapshots`;

SELECT file_path, file_format, record_count, file_size_in_bytes
FROM lesson05.`hms_catalog_comparison$files`;

SET 'table.dml-sync' = 'false';
SET 'execution.runtime-mode' = 'STREAMING';
