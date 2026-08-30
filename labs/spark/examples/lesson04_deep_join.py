"""Compare shuffle and broadcast join plans for the Lesson 04 deep route."""

from __future__ import annotations

import argparse
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from mentor_spark_lab.pipeline import MarketplacePipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/workspace/labs/spark/data/lesson04")
    parser.add_argument("--hold-seconds", type=int, default=0)
    return parser.parse_args()


def explain_case(label: str, frame) -> None:
    print(f"\n=== {label} ===")
    frame.explain(mode="formatted")
    print(f"{label}_rows={frame.count()}")


def main() -> None:
    args = parse_args()
    spark = SparkSession.builder.appName("lesson04-join-deep-dive").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    pipeline = MarketplacePipeline(spark)
    purchases = pipeline.valid_purchases(pipeline.read_events(args.input))
    customers = pipeline.read_customers(args.input)

    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
    shuffle_join = purchases.join(customers, "customer_id").groupBy("country").count()
    explain_case("SHUFFLE_JOIN", shuffle_join)

    broadcast_join = purchases.join(F.broadcast(customers), "customer_id").groupBy("country").count()
    explain_case("BROADCAST_JOIN", broadcast_join)

    print("PASS join_experiment: compare Exchange and BroadcastHashJoin in plans/UI")
    if args.hold_seconds > 0:
        time.sleep(args.hold_seconds)
    spark.stop()


if __name__ == "__main__":
    main()
