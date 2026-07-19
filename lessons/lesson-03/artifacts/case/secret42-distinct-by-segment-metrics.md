# Metrics — Secrets #42 DISTINCT by segment

Stand: `labs/greenplum-625`, DB `mentor`, `optimizer=on`.  
Script: `lesson03-secret42-distinct-by-segment.sql`.

Lab capture (2026-07-19, 2 seg, 1M rows, `DISTRIBUTED BY (id)`):

| Phase | Result | Notes |
| --- | --- | --- |
| A canonical `count(DISTINCT)` | 239.480 ms | Aggregate → Gather |
| B map `sum` per `gp_segment_id` | 260.749 ms | Lab may be slower; prod Secrets ≥2× faster |
| C equivalence | 200000 = 200000 | Exact under dist key |
| D RANDOM overcount | 50000 vs 75116 | Negative case |

Teach **exactness contract** + plan shape; do not claim lab wall-time wins.
