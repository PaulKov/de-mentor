# Metrics — Secrets #38 median Gather to QD

Stand: `labs/greenplum-625`, DB `mentor`.  
Script: `lesson03-secret38-median-gather-qd.sql`.

Lab capture (2026-07-19, 2 seg, 200k rows, `DISTRIBUTED RANDOMLY`):

| Phase | Shape / result | Time |
| --- | --- | --- |
| A exact `percentile_disc(0.5)` | Gather Motion **rows=200000** → Aggregate on QD; median=**500** | 28.255 ms |
| B approx local medians | Gather 2 local values; approx=**500.5** (min 500 / max 501) | 90.708 ms |
| C `optimizer=on` | Often **Legacy fallback** for ordered-set (still Gather-all) | ~27–78 ms |

On 2 segments approx can be slower (Redistribute + Sort). Secrets prod (372 seg, 100M rows): exact ~74s vs approx ~2.3s (×31). Teach **Gather-all shape** + approximate contract.
