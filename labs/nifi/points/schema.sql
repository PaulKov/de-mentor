BEGIN;
CREATE SCHEMA IF NOT EXISTS points_lab;

CREATE TABLE IF NOT EXISTS points_lab.inbox (
    event_id uuid PRIMARY KEY,
    account_id text NOT NULL,
    points integer NOT NULL CHECK (points > 0)
);
CREATE TABLE IF NOT EXISTS points_lab.protected_balances (
    account_id text PRIMARY KEY,
    balance bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS points_lab.control_balances (
    account_id text PRIMARY KEY,
    balance bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS points_lab.attempts (
    attempt_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id uuid NOT NULL REFERENCES points_lab.inbox(event_id),
    account_id text NOT NULL,
    points integer NOT NULL,
    topic text NOT NULL,
    partition_id integer NOT NULL,
    kafka_offset bigint NOT NULL,
    flow_uuid uuid NOT NULL,
    decision text NOT NULL CHECK (decision IN ('applied', 'duplicate', 'conflict')),
    observed_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE INDEX IF NOT EXISTS points_attempts_event ON points_lab.attempts (event_id, attempt_id);

CREATE OR REPLACE FUNCTION points_lab.credit(
    p_event uuid, p_account text, p_points integer,
    p_topic text, p_partition integer, p_offset bigint, p_flow uuid
) RETURNS text LANGUAGE plpgsql AS $$
DECLARE
    prior points_lab.inbox%ROWTYPE;
    decision text;
BEGIN
    INSERT INTO points_lab.inbox VALUES (p_event, p_account, p_points)
    ON CONFLICT (event_id) DO NOTHING;
    IF FOUND THEN
        decision := 'applied';
        INSERT INTO points_lab.protected_balances (account_id, balance)
        VALUES (p_account, p_points)
        ON CONFLICT (account_id) DO UPDATE
        SET balance = points_lab.protected_balances.balance + EXCLUDED.balance;
    ELSE
        SELECT * INTO STRICT prior FROM points_lab.inbox WHERE event_id = p_event;
        IF prior.account_id = p_account AND prior.points = p_points THEN
            decision := 'duplicate';
        ELSE
            decision := 'conflict';
        END IF;
    END IF;

    IF decision IN ('applied', 'duplicate') THEN
        -- This separate control table deliberately increments on every matching delivery.
        INSERT INTO points_lab.control_balances (account_id, balance)
        VALUES (p_account, p_points)
        ON CONFLICT (account_id) DO UPDATE
        SET balance = points_lab.control_balances.balance + EXCLUDED.balance;
    END IF;
    INSERT INTO points_lab.attempts
        (event_id, account_id, points, topic, partition_id, kafka_offset, flow_uuid, decision)
    VALUES (p_event, p_account, p_points, p_topic, p_partition, p_offset, p_flow, decision);
    RETURN decision;
END;
$$;
COMMIT;
