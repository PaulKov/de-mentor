-- There is one Kafka partition but two Flink source subtasks; let the unused subtask go idle.
SET 'table.exec.source.idle-timeout' = '5 s';

CREATE TABLE IF NOT EXISTS orders_source (
  order_id STRING,
  region STRING,
  amount DECIMAL(12, 2),
  event_time TIMESTAMP(3),
  WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
)
WITH (
  'connector' = 'kafka',
  'topic' = 'orders',
  'properties.bootstrap.servers' = 'kafka:29092',
  'properties.group.id' = 'lesson06-flink-iceberg',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json',
  'json.timestamp-format.standard' = 'ISO-8601'
);

SELECT order_id, region, amount, event_time FROM orders_source;
