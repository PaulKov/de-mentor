# Metrics — Secrets #14 Window PARTITION BY skew

Stand: `labs/greenplum-625`, DB `mentor`, `SET optimizer = on`.  
Script: `labs/greenplum-625/examples/lesson03-secret14-window-partition-skew.sql`.

| Phase | Shape to expect | Notes |
| --- | --- | --- |
| A constant `invalid_id`, `DISTRIBUTED BY (id)` | `WindowAgg` ← **Redistribute Hash Key: invalid_id** | Victim-segment collapse |
| B segment counts on base | rows split by `id` hash | Before window Motion |
| C `DISTRIBUTED BY (invalid_id)` | Redistribute may disappear | Still NDV=1 → single-seg reality |
| D no PARTITION BY | different Motion profile | Real fix when key is senseless |

Lab capture (2026-07-19, 2 seg, 200k rows, constant `invalid_id=42`):

```text
A Redistribute Hash Key: invalid_id + WindowAgg; 259.500 ms
C DISTRIBUTED BY (invalid_id): no Redistribute; 179.936 ms (still single-seg data)
D no PARTITION BY: Gather then WindowAgg; 88.735 ms
```
