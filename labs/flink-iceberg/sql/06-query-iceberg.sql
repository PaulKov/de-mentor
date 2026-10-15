USE CATALOG lakekeeper;
USE lesson06;
SET 'execution.runtime-mode' = 'BATCH';

SELECT window_start, window_end, region, order_count, gross_amount
FROM region_minute_metrics;

SELECT committed_at, snapshot_id, operation, summary
FROM `region_minute_metrics$snapshots`;

SET 'execution.runtime-mode' = 'STREAMING';
