# Rubric — Lesson 06

100 баллов; Senior-level pass — 85+ и не менее 12 баллов из 15 за failure/recovery.

| Категория | Баллы | Что ожидается |
|---|---:|---|
| Kafka source/offset contract | 10 | offsets per partition, startup policy, checkpoint recovery vs broker commits, retention |
| Event time/watermarks | 12 | payload timestamps, bounded disorder, idle partitions, late events/state cleanup |
| Flink runtime/state | 12 | parallel subtasks, keyBy shuffle, keyed/operator state, key-groups, parallelism |
| Checkpoint reasoning | 15 | barriers, alignment, async snapshot, completed checkpoint/recovery, monitoring metrics |
| Iceberg commit reasoning | 15 | writers/files/committables, notifyCheckpointComplete, catalog pointer commit, orphan/conflict |
| Exactly-once limits | 10 | internal state vs sink transaction vs business uniqueness; no cross-system atomicity assumption |
| Failure/recovery evidence | 10 | observed checkpoint/snapshot IDs and restart timeline; distinguishes untested hypothesis |
| Java/PyFlink/API design | 6 | source, watermark, checkpoint, sink shown; connectors/JVM boundary described |
| Operations/SLO/retention | 6 | lag, checkpoint, commit delay, file size, retention windows and safe GC |
| Communication and reproducibility | 4 | versioned commands, no secrets, evidence file and clear assumptions |

## Hard reject

- Reports success without any completed checkpoint or table snapshot evidence.
- Claims Kafka committed group offsets are Flink recovery state.
- Claims one job checkpoint atomically commits arbitrary Kafka + Iceberg + external effects.
- Deletes recent/orphan data without active writer/checkpoint grace analysis.
- Treats SQL `PRIMARY KEY NOT ENFORCED` as input uniqueness validation.
- Submits credentials/secrets or claims code ran when it was only a design fragment.
