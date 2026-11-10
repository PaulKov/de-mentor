# Lab data

`orders.jsonl` is an ordered training input for the single-partition Kafka topic. The last record is intentionally late: it arrives after the event-time watermark has advanced past its one-minute window.
