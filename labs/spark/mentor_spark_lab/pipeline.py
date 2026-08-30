"""Testable PySpark transformations for the marketplace lesson case."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from mentor_spark_lab.schemas import CUSTOMER_SCHEMA, EVENT_SCHEMA


@dataclass(frozen=True)
class PipelineMetrics:
    """Minimal correctness evidence produced by the teaching pipeline."""

    input_events: int
    valid_purchases: int
    output_rows: int
    revenue_total: Decimal


class MarketplacePipeline:
    """Compose ingestion, quality filtering, enrichment and aggregation."""

    def __init__(self, spark: SparkSession) -> None:
        self._spark = spark

    def read_events(self, input_root: str) -> DataFrame:
        """Read event JSON with a stable explicit schema."""

        return self._spark.read.schema(EVENT_SCHEMA).json(f"{input_root}/events")

    def read_customers(self, input_root: str) -> DataFrame:
        """Read the customer CSV dimension without inferSchema."""

        return (
            self._spark.read.option("header", True)
            .option("dateFormat", "yyyy-MM-dd")
            .schema(CUSTOMER_SCHEMA)
            .csv(f"{input_root}/customers")
        )

    @staticmethod
    def valid_purchases(events: DataFrame) -> DataFrame:
        """Keep business-valid purchases and derive the partition date."""

        return (
            events.filter(F.col("event_type") == "purchase")
            .filter(F.col("amount").isNotNull() & (F.col("amount") > 0))
            .withColumn("event_date", F.to_date("event_ts"))
            .select(
                "event_id",
                "event_ts",
                "event_date",
                "customer_id",
                "amount",
                "device",
            )
        )

    @staticmethod
    def daily_revenue(purchases: DataFrame, customers: DataFrame) -> DataFrame:
        """Build the daily country-level revenue mart."""

        return (
            purchases.join(customers, on="customer_id", how="inner")
            .groupBy("event_date", "country")
            .agg(
                F.count("event_id").alias("orders"),
                F.sum("amount").alias("revenue"),
                F.approx_count_distinct("customer_id").alias("customers"),
            )
            .orderBy("event_date", "country")
        )

    @staticmethod
    def write_output(result: DataFrame, output_root: str) -> None:
        """Write an idempotent Parquet mart partitioned by business date."""

        (
            result.write.mode("overwrite")
            .partitionBy("event_date")
            .parquet(output_root)
        )

    def collect_metrics(
        self,
        events: DataFrame,
        purchases: DataFrame,
        result: DataFrame,
    ) -> PipelineMetrics:
        """Materialize the small set of validation metrics used by the lesson."""

        revenue = result.agg(F.sum("revenue").alias("total")).first()["total"]
        return PipelineMetrics(
            input_events=events.count(),
            valid_purchases=purchases.count(),
            output_rows=result.count(),
            revenue_total=revenue or Decimal("0.00"),
        )

    def validate_roundtrip(self, output_root: str, metrics: PipelineMetrics) -> bool:
        """Verify persisted row count and revenue against the in-memory result."""

        persisted = self._spark.read.parquet(output_root)
        actual_rows = persisted.count()
        actual_revenue = persisted.agg(F.sum("revenue").alias("total")).first()["total"]
        return actual_rows == metrics.output_rows and actual_revenue == metrics.revenue_total


def ensure_output_parent(output_root: str) -> None:
    """Create a local parent when the path is backed by the shared workspace."""

    if output_root.startswith("/workspace/"):
        Path(output_root).parent.mkdir(parents=True, exist_ok=True)
