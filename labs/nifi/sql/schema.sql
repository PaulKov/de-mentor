CREATE TABLE IF NOT EXISTS integration_events (
    event_id text PRIMARY KEY,
    customer_id text,
    first_seen_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS source_orders (
    id bigint PRIMARY KEY,
    updated_at timestamptz NOT NULL,
    amount numeric(12, 2) NOT NULL
);

INSERT INTO source_orders VALUES
    (1, '2026-01-01T10:00:00Z', 12.50),
    (2, '2026-01-01T10:00:00Z', 20.00),
    (3, '2026-01-01T10:00:01Z', 7.00)
ON CONFLICT (id) DO NOTHING;
