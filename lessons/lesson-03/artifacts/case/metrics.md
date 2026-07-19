# Lesson 03 E2E case metrics (greenplum-625 / mentor / lesson03)

**Snapshot:** GP 6.25.3, **2 segments**, Feb window on `fact_sales` (~44800 rows before anti-test filter).  
**GUC locked:** `optimizer=on`, `statement_mem=256MB`.  
**Warm/cold:** first planning in a fresh session can be hundreds of ms–seconds; use warm median.

## Equivalence

`EXCEPT ALL` both directions on grain `(region, category, revenue)` → **0 / 0** rows.

## Warm median (n=3, same session)

| Metric | Baseline (monolith join) | After (TEMP stages) | Note |
|---|---:|---:|---|
| Planning time (median) | **14.9 ms** | **1.4 ms** | After stages already analyzed |
| Execution time (median) | **15.0 ms** | **6.0 ms** | Lab-scale data — method, not production SLA |
| TEMP `tmp_feb` size | — | **2304 kB** | `DISTRIBUTED BY (customer_id)` |
| TEMP `tmp_shaped` size | — | **2560 kB** | `DISTRIBUTED BY (region)` |
| Spill Disk | **0** | **0** | At 256MB statement_mem |
| Partitions selected | **2 / 4** | n/a (already filtered) | Dynamic Seq Scan baseline |
| Slices (window query) | **4** | **1–2** | See full plans |
| Result rows | **4** | **4** | region×category |

## Representative baseline node (window query, one run)

| Node | Estimate rows | Actual rows | Comment |
|---|---:|---:|---|
| Dynamic Seq Scan fact (Feb) | 22400 | **22896** | Good |
| Hash Join × customer | 21062 | **21432** | Good |
| Hash Join × product | 21010 | **21432** | Good |
| Final Gather | 9 | **4** | Groups overestimated |
| Broadcast dim_product | 800 | 800 | Small dim |

## Cold-cache warning (observed)

| Run | Planning | Execution |
|---|---:|---:|
| Cold-ish baseline | 580–2440 ms | 114–368 ms |
| Warm baseline | ~14–28 ms | ~13–18 ms |

## Teaching frame

On this **2-segment lab**, TEMP decomposition shows **clearer plan shape** and lower compile/exec for the final agg.  
Do **not** claim industrial “ORCA always wins” or “47× faster in production” from these numbers — scale the method to representative volume.

Artifacts:

- `baseline-explain-analyze.txt`
- `after-explain-analyze.txt`
- SQL: `labs/greenplum-625/examples/lesson03-e2e-case-metrics.sql`
