# Lesson 04 — PySpark ETL Evidence

## A. Environment

```text
Spark version:
Master URL:
Workers:
Seed profile:
Submit command:
```

## B. Input contract

Schemas, expected volume, null/invalid policy.

## C. Baseline

```text
Input events count:
Input customers count:
Input partitions:
```

## D. Pipeline design

Business grain, transformations, join, aggregation, output.

## E. Physical plan

Paste relevant `explain("formatted")` fragment.

```text
Join operator:
Exchange:
Why shuffle is/is not required:
```

## F. Spark UI

```text
Job IDs:
Stage IDs:
Tasks:
Shuffle read/write:
Task duration spread:
Spill:
```

## G. Correctness

```text
Valid purchases:
Output rows:
Revenue total before write:
Revenue total after read:
Roundtrip PASS/FAIL:
```

## H. Output contract

Parquet location, partition columns, file-count observation, rerun behavior.

## I. Decision

`merge / do not merge / needs larger-scale experiment`

## J. Residual risks

Skew, data growth, broadcast size, small files, external side effects, monitoring.
