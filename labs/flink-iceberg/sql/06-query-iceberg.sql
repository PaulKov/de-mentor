USE CATALOG lakekeeper;
USE lesson06;

SELECT window_start, window_end, region, order_count, gross_amount
FROM region_minute_metrics
ORDER BY window_start, region;

SELECT committed_at, snapshot_id, operation, summary
FROM `region_minute_metrics$snapshots`;
