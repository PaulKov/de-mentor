USE CATALOG nessie;
CREATE DATABASE IF NOT EXISTS lesson05;
CREATE TABLE IF NOT EXISTS lesson05.catalog_comparison (
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

INSERT INTO lesson05.catalog_comparison VALUES
  ('evt-101', 'books', 12.50, TIMESTAMP '2025-10-14 10:00:01.000'),
  ('evt-102', 'books', 19.00, TIMESTAMP '2025-10-14 10:00:21.000'),
  ('evt-103', 'music', 8.75, TIMESTAMP '2025-10-14 10:01:05.000');

SELECT category, COUNT(*) AS rows_count, SUM(amount) AS revenue
FROM lesson05.catalog_comparison
GROUP BY category;
