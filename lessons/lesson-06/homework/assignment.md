# Homework — Exactly-once streaming pipeline design

## Сценарий

Marketplace публикует `orders` в Kafka. Flink группирует события по event-time минутам и региону, пишет Iceberg v2 таблицу в S3 через Lakekeeper. Аналитики читают таблицу из нескольких engines. Ожидаемый SLO: данные доступны не позже 2 минут после события; recovery после TaskManager failure — до 10 минут; time travel — 14 дней.

## Задача

Подготовь implementation/evidence pack для учебного стенда и production design review:

1. Запусти lab SQL pipeline; сохрани offsets, completed checkpoint, результаты и Iceberg snapshot metadata.
2. Выполни recovery drill с TaskManager failure и отдельно опиши catalog outage before/after pointer commit.
3. Сравни Java DataStream, Flink Table/SQL и PyFlink реализации одного pipeline. Выбери production frontend и обоснуй choice.
4. Определи event-time/watermark/late-event policy. Укажи, что делать с invalid/future timestamps.
5. Определи exactly-once contract для source state, table commit и business primary key.
6. Рассчитай retention и maintenance envelope для Kafka, checkpoints, Iceberg snapshots и orphan files.
7. Составь observability/alert design по Kafka lag, event-time lag, watermarks, checkpoints, sink commits, catalog conflicts, file sizes и compaction.
8. Сравни Lakekeeper и Nessie (из Lesson 05) для разных требований, отдельно назови catalog vs format semantics.

## Требуемые deliverables

```text
lessons/lesson-06/submissions/<student>/
├── evidence.md
├── architecture.md
├── failure-matrix.md
├── retention-and-slo.md
├── api-comparison.md
└── code/
    ├── java-pipeline.java
    └── pyflink-pipeline.py
```

Код должен быть достаточно конкретным, чтобы reviewer увидел source offsets/deserializer, watermark, checkpoint settings, state/shuffle, Iceberg table identity and sink mode. Если фрагмент не запускался, пометь его как sketch и перечисли недостающие JAR/configuration; не утверждай compile success.

## Ограничения

- Не включай secrets в submission.
- Не очищай shared Compose volumes до экспорта evidence.
- Не используй `earliest-offset` в production без явной backfill/retention политики.
- Не настраивай очистку orphan files короче максимального checkpoint/commit/restart window.
- Не заявляй business uniqueness на основании `PRIMARY KEY NOT ENFORCED`.
- Не называй checkpoint completed доказательством Iceberg commit.

Подробный критерий оценки: [rubric](rubric.md); evidence заполняй по [template](templates/evidence.md).
