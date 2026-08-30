"""Reusable Spark-session and plan helpers for Lesson 04 notebooks."""

from __future__ import annotations

import os
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO

from pyspark.sql import DataFrame, SparkSession


@dataclass(frozen=True)
class NotebookSparkConfig:
    """Runtime settings injected into a notebook kernel by Docker Compose."""

    master_url: str
    driver_host: str
    shuffle_partitions: int
    ui_port: int

    @classmethod
    def from_environment(cls) -> "NotebookSparkConfig":
        """Build and validate a laptop-safe notebook configuration."""

        shuffle_partitions = int(os.getenv("SPARK_SHUFFLE_PARTITIONS", "8"))
        ui_port = int(os.getenv("SPARK_UI_PORT", "4040"))
        if shuffle_partitions < 1:
            raise ValueError("SPARK_SHUFFLE_PARTITIONS must be positive")
        if not 1 <= ui_port <= 65535:
            raise ValueError("SPARK_UI_PORT must be between 1 and 65535")
        return cls(
            master_url=os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077"),
            driver_host=os.getenv("SPARK_DRIVER_HOST", "spark-notebook"),
            shuffle_partitions=shuffle_partitions,
            ui_port=ui_port,
        )


def create_spark_session(
    app_name: str,
    config: NotebookSparkConfig | None = None,
) -> SparkSession:
    """Create a standalone-cluster session shared by all notebook demos."""

    effective_config = config or NotebookSparkConfig.from_environment()
    return (
        SparkSession.builder.appName(app_name)
        .master(effective_config.master_url)
        .config("spark.driver.host", effective_config.driver_host)
        .config("spark.driver.bindAddress", "0.0.0.0")
        .config("spark.sql.adaptive.enabled", "true")
        .config(
            "spark.sql.shuffle.partitions",
            str(effective_config.shuffle_partitions),
        )
        .config("spark.ui.port", str(effective_config.ui_port))
        .getOrCreate()
    )


def explain_as_text(frame: DataFrame, mode: str = "formatted") -> str:
    """Capture the public DataFrame explain output for assertions and teaching."""

    buffer = StringIO()
    with redirect_stdout(buffer):
        frame.explain(mode=mode)
    return buffer.getvalue()
