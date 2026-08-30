"""Run the Lesson 04 evidence-first PySpark marketplace pipeline."""

from __future__ import annotations

import argparse
import time

from pyspark.sql import SparkSession

from mentor_spark_lab.pipeline import MarketplacePipeline, ensure_output_parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/workspace/labs/spark/data/lesson04")
    parser.add_argument("--output", default="/workspace/labs/spark/data/output/core")
    parser.add_argument("--hold-seconds", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_output_parent(args.output)
    spark = (
        SparkSession.builder.appName("lesson04-marketplace-core")
        .config("spark.sql.adaptive.enabled", "true")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    pipeline = MarketplacePipeline(spark)

    events = pipeline.read_events(args.input)
    customers = pipeline.read_customers(args.input)
    purchases = pipeline.valid_purchases(events)
    result = pipeline.daily_revenue(purchases, customers)

    print("\n=== PHYSICAL PLAN ===")
    result.explain(mode="formatted")
    metrics = pipeline.collect_metrics(events, purchases, result)
    pipeline.write_output(result, args.output)
    roundtrip_ok = pipeline.validate_roundtrip(args.output, metrics)

    result.show(20, truncate=False)
    print(f"PASS input_events: {metrics.input_events}")
    print(f"PASS valid_purchases: {metrics.valid_purchases}")
    print(f"PASS output_rows: {metrics.output_rows}")
    print(f"PASS revenue_total: {metrics.revenue_total}")
    print(f"{'PASS' if roundtrip_ok else 'FAIL'} output_roundtrip: {args.output}")
    print("Spark UI: http://localhost:4040")

    if args.hold_seconds > 0:
        print(f"Holding application for Spark UI inspection: {args.hold_seconds}s")
        time.sleep(args.hold_seconds)
    spark.stop()


if __name__ == "__main__":
    main()
