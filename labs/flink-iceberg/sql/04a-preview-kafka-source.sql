-- Optional unbounded preview. Run in a second SQL Client session and cancel
-- the SELECT when finished; it is intentionally separate from source DDL.
SELECT order_id, region, amount, event_time
FROM default_catalog.default_database.orders_source;
