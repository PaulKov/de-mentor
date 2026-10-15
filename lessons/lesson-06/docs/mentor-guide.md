# Руководство ментора — Lesson 06

## Главная идея занятия

Сформировать у ученика наблюдаемую причинно-следственную модель: Kafka partition record → Flink source position → operator state/time progress → checkpoint completion → Iceberg table commit. Не принимать объяснение «checkpoint сохраняет данные в Iceberg» — checkpoint сохраняет Flink state/positions; sink публикует таблицу своим commit protocol.

## Подготовка

1. Убедиться, что Lesson 05 Compose образ собран и все сервисы healthy.
2. Проверить SQL client jars: Kafka connector 5.0.0-2.2, Iceberg Flink runtime 2.2 1.12.0, AWS bundle.
3. Сохранить отдельный dataset и topic; не очищать общие volumes, пока ученик не экспортировал evidence.
4. Открыть Flink UI, Kafka topic inspection, SeaweedFS filer UI и Lakekeeper.
5. Проговорить lab-only topology: Kafka single broker/partition, local named-volume checkpoint path, no auth/TLS/HA.

## Преподавание: идея → механика → evidence

### Блок 1 — очередь

Пусть студент вручную пронумерует records Kafka partition. Спросить: какая позиция попадёт в checkpoint? Отделить offsets от event timestamps. Уточнить, что Kafka broker committed offsets показывают monitoring progress, а Flink checkpoint хранит recovery position.

### Блок 2 — event time

Ученик рисует event timestamps по порядку arrival; вычисляет watermark с 5s lateness estimate. Добавить idle partition и позднее событие: пусть объяснит, как watermark minimum и idleness меняют окно. Не разрешать отождествлять watermark с «максимальным timestamp всех сообщений навсегда».

### Блок 3 — checkpoint

Показать barrier через `keyBy`/shuffle: найти slow subtask, объяснить alignment и state snapshot. Затем сравнить aligned/un-aligned: почему первый может ждать, а второй записывает in-flight buffers. Проследить Kafka offsets и window state в одном checkpoint.

### Блок 4 — Iceberg commit

Нарисовать файлы до snapshot: data file записан, но не опубликован. Затем completed checkpoint, committable, catalog metadata pointer. Попросить отдельно объяснить crash перед/после CAS. Закончить `$snapshots` и `$files` queries и проверить `elapsedSecondsSinceLastSuccessfulCommit`/logs.

## Вопросы, раскрывающие глубину

- Если task fail между записью data file и checkpoint completion, что видит читатель?
- Если completed checkpoint есть, а Iceberg snapshot не появился, что и где смотреть?
- Почему после restart запись может быть физически обработана повторно, но state effect один раз?
- Почему append-only Iceberg table не проверяет уникальность business key?
- Как retention Kafka и Iceberg влияет на backfill, restore и time travel?
- Как изменится восстановление, если parallelism увеличился с 2 до 4?

## Частые заблуждения

| Ошибка | Коррекция |
|---|---|
| Consumer group offsets — recovery truth | при checkpointed KafkaSource recovery state приходит из Flink checkpoint; broker commit — monitoring |
| Watermark это wall clock | watermark это event-time progress estimate, выводимый стратегией из input |
| Exactly once значит событие выполняется один раз | replay возможен; гарантируется logical effect в state/sink protocol |
| Iceberg snapshot — это checkpoint Flink | у них разные storage и lifecycle; sink связывает их checkpoint identity |
| Каждый checkpoint равен Iceberg commit | checkpoint complete callback запускает sink commit, но commit может fail и наблюдается отдельно |
| Upsert/primary key автоматически гарантирует unique source | `NOT ENFORCED` — planner metadata; validate source keys/deduplication separately |

## Оценка и remediation

Если студент не может нарисовать sequence diagram — вернуться к [exactly-once deep dive](deep-dives/kafka-to-iceberg-exactly-once.md). Если не объясняет задержку окон — повторить [watermark deep dive](deep-dives/kafka-source-event-time-internals.md). Если не читает UI checkpoint details — повторить [runtime deep dive](deep-dives/flink-runtime-and-checkpoint-internals.md) и Lab D.

Домашнюю работу оценивать по [rubric](../homework/rubric.md). Нужны конкретные IDs/metrics/log excerpts, а не только снимок зелёного UI.
