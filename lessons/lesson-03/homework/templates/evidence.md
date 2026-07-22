# Evidence pack — Lesson 03 Query Tuning

## A. Workload contract

- Graded view: `lesson03.v_homework_brand_region`
- Grain: region × brand × revenue × order_cnt × brand_rank
- Predicates / window:
- Same answer means:
- Seed scale (`small` / `principal`):
- Optimizer for rewrite proof (`SET optimizer = …`):
- Stand ready after `check greenplum-625` (timer starts here): yes/no

## B. Baseline plan diagnosis

- Optimizer marker:
- Critical path / Motions:
- Join sides:
- Skew / correlation smell (hot customers, region↔segment):
- First estimate error (or proof estimates are adequate):
- Segment spread (max/avg if measured):

## C. Statistics causality

| Predicate / join | Stats slot | Selectivity hypothesis | Est vs actual | Plan consequence |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## D. Stage design — A/B candidates (≥2 explored)

### Candidate A (≤1 stage / no-TEMP)

| Stage | Input rows | Output rows | Distribution | Storage | Next operator | Why materialization pays (or why skipped) |
| --- | ---: | ---: | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

### Candidate B (multi-stage)

| Stage | Input rows | Output rows | Distribution | Storage | Next operator | Why materialization pays (or why skipped) |
| --- | ---: | ---: | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

Production candidate in `rewrite.sql`: A / B — why:  
TEMP boundary explored (create **or** argue reject): …

## E. End-to-end measurement

| Metric | Monolith (`v_homework_brand_region`) | Candidate A | Candidate B |
| --- | ---: | ---: | ---: |
| Planning time |  |  |  |
| Stage A time | — |  |  |
| Stage B time | — | — |  |
| Final SELECT time |  |  |  |
| **Total pipeline time (median)** |  |  |  |
| Motion count / largest Motion rows |  |  |  |
| Spill bytes |  |  |  |
| TEMP bytes written | — |  |  |
| Max/avg rows per segment |  |  |  |
| Result rows |  |  |  |

Production decision: **merge / do not merge / needs larger-scale validation** — why:

## F. After plan (same optimizer as baseline)

- Motion / join shape vs baseline:
- Co-location proof (if TEMP used):

## G. Optimizer comparison (Principal extension)

Contract used: frozen-input final SELECT **or** full e2e per optimizer: …

| Query | ORCA shape / time | Legacy shape / time | Notes |
| --- | --- | --- | --- |
|  |  |  |  |

Do not declare a winner from estimated cost alone.

## H. Reconciliation

- Baseline object: `lesson03.v_homework_brand_region`
- `baseline_minus_candidate` =
- `candidate_minus_baseline` =
- Counts / aggregate checksums:

## I. Residual risks

(Beyond the verified snapshot — does **not** replace H.)

1.
2.

## J. Question → Lesson 04 (WLM / kill-switch)

…
