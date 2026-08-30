# Evidence pack — Lesson 03 Query Tuning

## A. Workload contract

- Grain:
- Predicates / window:
- Same answer means:
- Optimizer for rewrite proof (`SET optimizer = …`):
- Stand ready after `check greenplum-625` (timer starts here): yes/no

## B. Baseline plan diagnosis

- Optimizer marker:
- Critical path / Motions:
- Join sides:
- First estimate error (or proof estimates are adequate):
- Segment spread (max/avg if measured):

## C. Statistics causality

| Predicate / join | Stats slot | Selectivity hypothesis | Est vs actual | Plan consequence |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## D. Stage design (0–3 physical stages)

| Stage | Input rows | Output rows | Distribution | Storage | Next operator | Why materialization pays (or why skipped) |
| --- | ---: | ---: | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

TEMP boundary explored (create **or** argue reject): …

## E. End-to-end measurement

| Metric | Monolith | Candidate |
| --- | ---: | ---: |
| Planning time |  |  |
| Stage A time | — |  |
| Stage B time | — |  |
| Final SELECT time |  |  |
| **Total pipeline time (median)** |  |  |
| Motion count / largest Motion rows |  |  |
| Spill bytes |  |  |
| TEMP bytes written | — |  |
| Max/avg rows per segment |  |  |
| Result rows |  |  |

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

- `baseline_minus_candidate` =
- `candidate_minus_baseline` =
- Counts / aggregate checksums:

## I. Residual risks

(Beyond the verified snapshot — does **not** replace H.)

1.
2.

## J. Question → Lesson 05 (WLM / kill-switch)

…
