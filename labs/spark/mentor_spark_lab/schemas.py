"""Explicit schemas shared by lesson demos and homework."""

from pyspark.sql.types import (
    DateType,
    DecimalType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


EVENT_SCHEMA = StructType(
    [
        StructField("event_id", LongType(), nullable=False),
        StructField("event_ts", TimestampType(), nullable=False),
        StructField("customer_id", LongType(), nullable=False),
        StructField("event_type", StringType(), nullable=False),
        StructField("amount", DecimalType(14, 2), nullable=True),
        StructField("device", StringType(), nullable=True),
    ]
)

CUSTOMER_SCHEMA = StructType(
    [
        StructField("customer_id", LongType(), nullable=False),
        StructField("country", StringType(), nullable=False),
        StructField("segment", StringType(), nullable=False),
        StructField("registered_at", DateType(), nullable=False),
    ]
)
