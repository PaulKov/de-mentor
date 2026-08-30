"""Live readiness checks for the Dockerized Spark Lesson 04 stand."""

from __future__ import annotations

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def emit(code: str, passed: bool, detail: str) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"{status} {code}: {detail}")
    if not passed:
        raise RuntimeError(f"{code} failed: {detail}")


def main() -> None:
    spark = SparkSession.builder.appName("lesson04-readiness-smoke").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    emit("spark_master_reachable", spark.sparkContext.master.startswith("spark://"), spark.sparkContext.master)
    emit("spark_version", spark.version.startswith("4.2."), spark.version)

    executors = spark.sparkContext._jsc.sc().getExecutorMemoryStatus().size()
    emit("spark_workers_registered", executors >= 2, f"executor memory endpoints={executors}")

    frame = spark.range(20_000, numPartitions=4).withColumn("bucket", F.col("id") % 8)
    emit("pyspark_dataframe", frame.count() == 20_000, "DataFrame count=20000")

    aggregated = frame.groupBy("bucket").count()
    plan = aggregated._jdf.queryExecution().executedPlan().toString()
    emit("spark_shuffle_plan", "Exchange" in plan, "Exchange found in physical plan")

    output = "/workspace/labs/spark/data/smoke/output"
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    aggregated.write.mode("overwrite").parquet(output)
    emit("spark_output_roundtrip", spark.read.parquet(output).count() == 8, output)
    spark.stop()


if __name__ == "__main__":
    main()
