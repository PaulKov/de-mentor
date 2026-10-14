SET 'execution.checkpointing.interval' = '15 s';
SET 'execution.checkpointing.mode' = 'EXACTLY_ONCE';

USE CATALOG lakekeeper;
CREATE DATABASE IF NOT EXISTS lesson06;

CREATE TABLE IF NOT EXISTS lesson06.region_minute_metrics (
  window_start TIMESTAMP(3),
  window_end TIMESTAMP(3),
  region STRING,
  order_count BIGINT,
  gross_amount DECIMAL(20, 2),
  PRIMARY KEY (window_start, window_end, region) NOT ENFORCED
)
PARTITIONED BY (region)
WITH (
  'format-version' = '2',
  'write.upsert.enabled' = 'true',
  'write.format.default' = 'parquet',
  'write.distribution-mode' = 'hash'
);

INSERT INTO lesson06.region_minute_metrics
SELECT
  window_start,
  window_end,
  region,
  COUNT(*) AS order_count,
  SUM(amount) AS gross_amount
FROM TABLE(
  TUMBLE(TABLE orders_source, DESCRIPTOR(event_time), INTERVAL '1' MINUTE)
)
GROUP BY window_start, window_end, region;
