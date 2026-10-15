# Lesson 06 evidence

## Environment

- OS / Docker Desktop:
- Commit / lesson branch:
- Flink / Kafka connector / Iceberg versions:
- Docker Compose service status:

## Pipeline

- Kafka topic / partitions:
- Consumer group / startup offsets:
- Flink Job ID / parallelism:
- Iceberg catalog / namespace / table:
- Watermark / allowed lateness policy:

## Processing evidence

| Checkpoint ID | Status | Duration | Source partition offsets | State/data size |
|---|---|---:|---|---:|
| | | | | |

| Snapshot ID | Operation | Committed at | Rows/files | Summary / checkpoint identity |
|---|---|---|---:|---|
| | | | | |

## Correctness reconciliation

- Expected business rows/aggregates:
- Actual Iceberg rows/aggregates:
- Late/invalid events and treatment:
- Logical duplicates check:

## Fault and recovery

- Injected failure / exact time:
- Last completed checkpoint before failure:
- Restored checkpoint:
- Kafka offsets replayed:
- Iceberg snapshot result:
- Evidence source (UI, SQL, logs, metrics):

## Interpretation

- Exactly-once state claim:
- Exactly-once sink/table claim:
- Business uniqueness claim:
- Unverified assumptions:
- Suggested production alarms/retention:
