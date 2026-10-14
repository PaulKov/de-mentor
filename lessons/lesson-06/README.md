# Lesson 06 — Kafka → Flink → Iceberg: stateful streaming до snapshot

Стенд: **`flink-iceberg`** · Runtime: **Apache Flink 2.2.1** · Source: **Kafka 4.2.2** · Sink: **Iceberg 1.12.0 / Lakekeeper / SeaweedFS**

| Раздел | Путь | Зачем |
| --- | --- | --- |
| Теория и карта урока | [docs/](docs/) | Kafka offsets, event time, state, checkpoints и Iceberg commit |
| Workbook | [docs/student-workbook.md](docs/student-workbook.md) | пошаговые labs и evidence |
| Internals | [docs/deep-dives/](docs/deep-dives/) | runtime, barriers, source offsets, watermarks, exactly-once |
| Runbooks | [docs/runbooks/](docs/runbooks/) | quickstart, deep route, recovery drill |
| Java/PyFlink code | deep dives + [`../../labs/flink-iceberg/sql/`](../../labs/flink-iceberg/sql/) | API recipes и исполняемый SQL job |
| Homework | [homework/](homework/) | проектирование, fault injection и operational review |
| Общий Docker стенд | [lab README](../../labs/flink-iceberg/README.md) | Flink, Kafka, S3/SeaweedFS, Lakekeeper и Nessie |

## Результат урока

Ученик пишет и объясняет Kafka→Flink→Iceberg pipeline; различает Kafka partition offsets, Flink checkpoint state, event time и watermark; доказывает, что checkpoint, Iceberg snapshot commit и бизнес-уникальность — отдельные гарантии; диагностирует backpressure, поздние события, conflict, file smallness и recovery.

**Prerequisites:** [Lesson 04b — object storage internals](../lesson-04b-distributed-storage/README.md) и [Lesson 05 — Iceberg catalogs/metadata](../lesson-05/README.md). Перед streaming sink важно отличать S3 object consistency, Iceberg snapshot commit и Flink checkpoint recovery.

## Быстрый старт

```powershell
./labs/flink-iceberg/scripts/up.ps1
./labs/flink-iceberg/scripts/create-topic.ps1
./labs/flink-iceberg/scripts/sql-client.ps1
```

Из SQL Client выполнить DDL `04-kafka-source.sql`, затем `05-stream-to-iceberg.sql`; в отдельном PowerShell отправить `data/orders.jsonl` через `publish-orders.ps1`. Опциональный бесконечный preview source вынесен в `04a-preview-kafka-source.sql` — запускай его отдельно и останови после просмотра событий. Подробности, адреса и очистка: [lab README](../../labs/flink-iceberg/README.md).

## Навигация

- [Цели и схема урока](docs/README.md)
- [Workbook ученика](docs/student-workbook.md)
- [Руководство ментора](docs/mentor-guide.md)
- [Deep Dive: Flink runtime и checkpoints](docs/deep-dives/flink-runtime-and-checkpoint-internals.md)
- [Deep Dive: Kafka source и event time](docs/deep-dives/kafka-source-event-time-internals.md)
- [Deep Dive: exactly-once Kafka → Iceberg](docs/deep-dives/kafka-to-iceberg-exactly-once.md)
- [Быстрый путь](docs/runbooks/simple-path.md)
- [Глубокий путь](docs/runbooks/deep-dive-path.md)
- [Fault/recovery drill](docs/runbooks/recovery-drill.md)
- [Homework](homework/assignment.md) · [Rubric](homework/rubric.md)

← [Lesson 05](../lesson-05/) · [Все уроки](../README.md)
