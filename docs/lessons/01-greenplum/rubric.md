# Rubric And Skill Matrix

## Score Bands

| Score | Level | Meaning |
|---:|---|---|
| 90-100 | Production-ready | Can reason independently and explain trade-offs. |
| 70-89 | Solid | Understands the core mechanics, needs more practice with edge cases. |
| 50-69 | Developing | Can follow diagnostics, but misses architectural consequences. |
| 0-49 | Needs practice | Needs guided repetition before independent work. |

## Skill Matrix

| Skill | Evidence |
|---|---|
| Environment readiness | Lab starts, schema exists, student can connect. |
| Data setup | Seed data exists and can be reset. |
| MPP diagnostics | Student measures skew with `gp_segment_id`. |
| Distribution design | Student fixes distribution and validates balance. |
| EXPLAIN literacy | Student finds Motion nodes and explains why they appear. |
| Architecture communication | Student defends grain, distribution, partitioning, and risks. |

## Mentor Questions

- Why is `status` a tempting but bad distribution key?
- What changes when fact and dimension are colocated?
- Which query would your model optimize?
- What query would your model make worse?
- How would you validate the design before loading 10 TB?

