# Apache Spark / PySpark Cheat Sheet — Lesson 04

## CLI

```bash
python3 mentor-lab.py student spark-foundations start --profile lesson04
python3 mentor-lab.py student spark-foundations init
python3 mentor-lab.py student spark-foundations test
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

action → DAGScheduler → stages → TaskScheduler → executor slots → tasks
```

## API и context

| Понятие | Роль в PySpark |
| --- | --- |
| `SparkSession` | главная точка входа: DataFrame, SQL, catalog |
| `SparkContext` | connection/control plane приложения; доступен как `spark.sparkContext` |
| `DataFrame` | основной structured API со schema и Catalyst optimization |
| `RDD` | низкоуровневая partitioned collection без DataFrame schema/optimizer |
| `Dataset[T]` | typed JVM API для Scala/Java; отдельного Dataset API в Python нет |

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

## Два actions: без cache и с cache

```python
reused = events.filter("event_type = 'purchase'").select("customer_id", "amount")

reused.count()                     # job 1: вычисляет source → filter → select
reused.write.mode("overwrite").parquet(output)  # job 2: upstream вычисляется снова

cached = reused.cache()            # лениво: пока ничего не вычислено
cached.count()                     # первый action вычисляет и заполняет executor blocks
cached.write.mode("overwrite").parquet(output)  # читает cached partitions
cached.unpersist()                 # освобождает storage memory/disk
```

Для DataFrame `cache()/persist()` по умолчанию использует
`MEMORY_AND_DISK_DESER`: partitions хранятся через BlockManager на executors.
Вытесненный или потерянный block может быть пересчитан по lineage. Cache имеет
смысл только при повторном reuse, когда saved compute дороже storage/eviction.

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
