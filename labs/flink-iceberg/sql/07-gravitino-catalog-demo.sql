-- Start the optional Compose profile before running this file with Flink SQL.
SET 'execution.runtime-mode' = 'BATCH';
SET 'table.dml-sync' = 'true';
SET 'sql-client.execution.result-mode' = 'TABLEAU';
SET 'table.display.max-column-width' = '180';

CREATE CATALOG IF NOT EXISTS gravitino WITH (
  'type' = 'iceberg',
  'catalog-type' = 'rest',
  'uri' = 'http://gravitino:9001/iceberg',
  'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO',
  's3.endpoint' = 'http://seaweedfs:8333',
  's3.path-style-access' = 'true',
  's3.access-key-id' = 'demouser',
  's3.secret-access-key' = 'demosecret123456',
  'client.region' = 'us-east-1'
);

USE CATALOG gravitino;
CREATE DATABASE IF NOT EXISTS lesson05;
USE lesson05;

CREATE TABLE IF NOT EXISTS gravitino_catalog_comparison (
  event_id STRING,
  category STRING,
  amount DECIMAL(12, 2),
  event_time TIMESTAMP(3)
) WITH ('format-version' = '2');

-- Bounded overwrite keeps the demo table's row count stable across reruns.
INSERT OVERWRITE gravitino_catalog_comparison VALUES
  ('grav-001', 'books', 12.50, TIMESTAMP '2025-10-14 10:00:01.000'),
  ('grav-002', 'books', 19.00, TIMESTAMP '2025-10-14 10:00:21.000'),
  ('grav-003', 'music', 8.75, TIMESTAMP '2025-10-14 10:01:05.000');

SELECT category, COUNT(*) AS rows_count, SUM(amount) AS revenue
FROM gravitino_catalog_comparison GROUP BY category ORDER BY category;

SELECT committed_at, snapshot_id, parent_id, operation
FROM `gravitino_catalog_comparison$snapshots` ORDER BY committed_at;

SELECT file_path, record_count, file_size_in_bytes
FROM `gravitino_catalog_comparison$files`;
