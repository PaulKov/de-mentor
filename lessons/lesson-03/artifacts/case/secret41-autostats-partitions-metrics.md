# Metrics — Secrets #41 autostats × partitions

Stand: `labs/greenplum-625`, DB `mentor`, `gp_autostats_mode=on_no_stats`.  
Script: `lesson03-secret41-autostats-partitions.sql`.

Lab capture (2026-07-19):

| Phase | Observation |
| --- | --- |
| A INSERT → parent (30k) | All leaves + parent: **MISSING** `pg_statistic` |
| B INSERT → leaf `_1_prt_1` (5k) | That leaf: **HAS pg_statistic**; siblings still MISSING |
| C `ANALYZE` parent | All relations: **HAS pg_statistic** |

`last_analyze` columns may stay empty in this image even when `pg_statistic` rows exist — use `stats_state` / `pg_statistic` as evidence.
