"""Generate deterministic JSON/CSV inputs for the Lesson 04 marketplace case."""

from __future__ import annotations

import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=int, required=True)
    parser.add_argument("--customers", type=int, required=True)
    parser.add_argument("--skew-percent", type=int, required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def build_customers(spark: SparkSession, customers: int):
    countries = F.array(*[F.lit(value) for value in ["RU", "KZ", "BY", "AM", "GE"]])
    segments = F.array(*[F.lit(value) for value in ["new", "regular", "vip"]])
    return (
        spark.range(1, customers + 1, numPartitions=4)
        .select(
            F.col("id").alias("customer_id"),
            F.element_at(countries, (F.col("id") % 5 + 1).cast("int")).alias("country"),
            F.element_at(segments, (F.col("id") % 3 + 1).cast("int")).alias("segment"),
            F.date_add(F.lit("2024-01-01").cast("date"), (F.col("id") % 700).cast("int")).alias(
                "registered_at"
            ),
        )
    )


def build_events(spark: SparkSession, events: int, customers: int, skew_percent: int):
    event_types = F.array(*[F.lit(value) for value in ["view", "purchase", "purchase", "refund"]])
    devices = F.array(*[F.lit(value) for value in ["ios", "android", "web"]])
    generated = spark.range(events, numPartitions=8)
    customer_id = F.when(
        (F.col("id") % 100) < skew_percent,
        F.lit(1),
    ).otherwise((F.col("id") % customers) + 1)
    amount = F.when(
        F.col("id") % 997 == 0,
        F.lit(None).cast("decimal(14,2)"),
    ).otherwise((((F.col("id") * 37) % 20_000) / 100 + 1).cast("decimal(14,2)"))
    return generated.select(
        F.col("id").alias("event_id"),
        F.from_unixtime(F.lit(1_754_006_400) + (F.col("id") % 1_209_600)).cast("timestamp").alias(
            "event_ts"
        ),
        customer_id.cast("long").alias("customer_id"),
        F.element_at(event_types, (F.col("id") % 4 + 1).cast("int")).alias("event_type"),
        amount.alias("amount"),
        F.element_at(devices, (F.col("id") % 3 + 1).cast("int")).alias("device"),
    )


def main() -> None:
    args = parse_args()
    spark = SparkSession.builder.appName("lesson04-seed").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    customers = build_customers(spark, args.customers)
    events = build_events(spark, args.events, args.customers, args.skew_percent)

    customers.coalesce(1).write.mode("overwrite").option("header", True).csv(
        f"{args.output}/customers"
    )
    events.write.mode("overwrite").json(f"{args.output}/events")

    print(
        "PASS spark_seed: "
        f"events={events.count()} customers={customers.count()} output={args.output}"
    )
    spark.stop()


if __name__ == "__main__":
    main()
