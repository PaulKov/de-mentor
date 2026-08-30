# Apache Spark / PySpark Cheat Sheet — Lesson 04

## CLI

```bash
python3 mentor-lab.py up spark
python3 mentor-lab.py status spark
python3 mentor-lab.py seed spark --profile lesson04
python3 mentor-lab.py check spark
python3 mentor-lab.py logs spark
python3 mentor-lab.py down spark
python3 mentor-lab.py reset spark
```

## Submit

```bash
python3 mentor-lab.py spark-submit spark path/to/app.py
python3 mentor-lab.py spark-submit spark path/to/app.py -- --arg value
```

## Mental model

```text
application = driver + executors
action      → job
shuffle     → stage boundary
partition   → one task in a stage
Exchange    → data redistribution in a physical plan
```

## DataFrame basics

```python
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("lesson04").getOrCreate()

events = spark.read.schema(EVENT_SCHEMA).json(input_path)
valid = events.filter(F.col("amount").isNotNull())
result = valid.groupBy("event_type").agg(F.sum("amount").alias("amount"))

result.explain(mode="formatted")
result.write.mode("overwrite").parquet(output_path)
```

## Transformations vs actions

Transformations: `select`, `filter`, `withColumn`, `join`, `groupBy`, `repartition`.

Actions: `count`, `first`, `show`, `collect`, `write`.

`collect` является action, но для большого dataset опасен: все строки возвращаются в driver.

## Plan checklist

1. Scan: что читаем и какие filters pushed down?
2. Rows: где резко меняется cardinality?
3. Join: какая стратегия и какая build side?
4. `Exchange`: зачем перераспределяем?
5. Aggregate/sort: где wide operation?
6. AQE: final plan или initial plan?

## UI checklist

- SQL: operator graph и metrics;
- Jobs: jobs, stages, DAG;
- Stages: tasks, shuffle, spill, duration spread;
- Executors: task counts, memory, disk, GC;
- Environment: effective Spark configs.

## Не делать автоматически

- `collect()` / `toPandas()` на полном dataset;
- Python UDF, если есть built-in expression;
- `cache()` без повторного reuse и size evidence;
- `repartition(1)` для большого output;
- broadcast без доказанного размера;
- принимать performance change без reconciliation.
