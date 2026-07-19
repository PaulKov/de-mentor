# Metrics — Secrets #29 VALUES params → Broadcast fact

Stand: `labs/greenplum-625`, DB `mentor`, `SET optimizer = on`.  
Script: `labs/greenplum-625/examples/lesson03-secret29-values-params-broadcast.sql`.

| Phase | Shape observed on lab (2026-07-19, 2 seg) | Notes |
| --- | --- | --- |
| A RANDOM, no ANALYZE | Hash Join on QD + **Gather** of `sec29_fact` (`rows=1` estimate) | Secrets prod: Broadcast fact; same root |
| B `DISTRIBUTED BY (n_txt)` + ANALYZE | Hash Join on segments, Seq Scan fact, **no** Gather/Broadcast fact | ~7.6 ms |
| C RANDOM + ANALYZE | **Redistribute** fact `Hash Key: n_txt` | ~8.0 ms |
| D scalar `WHERE` | `Filter: (n_txt = '10')` | ~1.2 ms |
| E `IN (VALUES)` vs `IN list` | Redistribute+Join vs `ANY` filter | ~8.2 vs ~1.1 ms |

```text
A Execution time: 14.282 ms
B Execution time: 7.579 ms
C Execution time: 8.012 ms
D Execution time: 1.164 ms
E VALUES: 8.213 ms / list ANY: 1.076 ms
```
