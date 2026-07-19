# NLJ CTE → TEMP case metrics (greenplum-625, GPORCA)

Lab: 2 segments. Tables: `lesson03.nlj_orders` (80k), `lesson03.nlj_ref` (8k, replicated + index).
Script: `labs/greenplum-625/examples/lesson03-nlj-cte-temp-case.sql`.

| Phase | Stats situation | Join | Est (outer/CTE side) | Actual rows | Execution |
| --- | --- | --- | --- | --- | --- |
| A | no stats | Nested Loop + Index Scan | ~1 | 80 000 | ~176 ms |
| B | ANALYZE all, then reload fact **without** ANALYZE | Nested Loop + Index Scan | ~1 | 80 000 | ~98 ms |
| C | TEMP `tmp_nlj_enriched` + ANALYZE | Hash Join | ~40 000 / 80 000 | 80 000 | ~25 ms |

## Teaching notes

- Complex predicates in 3 CTEs filter almost nothing, but look selective.
- Dim is ~10× smaller than the CTE result; with under-estimate ORCA drives **Nested Loop** and runs **Index Scan loops=80000**.
- Full fresh ANALYZE on fact often flips to HashJoin on this lab; the **stale-after-reload** pattern keeps Nested Loop — classic production miss.
- TEMP materializes the hard predicate grain and gives the optimizer real cardinality → Hash Join.

Raw run: `lessons/lesson-03/artifacts/case/nlj-cte-temp-run.txt`.
