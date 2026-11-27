-- psql -v event_id=<UUID> -f ... or pass this file on stdin.
SELECT attempt_id, observed_at, topic, partition_id, kafka_offset, flow_uuid, decision
FROM points_lab.attempts
WHERE event_id = :'event_id'::uuid
ORDER BY attempt_id;

SELECT i.event_id, i.account_id, i.points AS event_points,
       a.balance AS protected_balance, c.balance AS naive_balance,
       count(t.attempt_id) AS attempts,
       count(*) FILTER (WHERE t.decision = 'applied') AS applied,
       count(*) FILTER (WHERE t.decision = 'duplicate') AS duplicates
FROM points_lab.inbox AS i
JOIN points_lab.protected_balances AS a USING (account_id)
JOIN points_lab.control_balances AS c USING (account_id)
JOIN points_lab.attempts AS t USING (event_id)
WHERE i.event_id = :'event_id'::uuid
GROUP BY i.event_id, i.account_id, i.points, a.balance, c.balance;
