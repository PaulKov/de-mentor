# Homework — Iceberg catalog design and evidence pack

Ориентир: **3–5 часов**.

Создай `lesson05.orders_curated` минимум с шестью полями, явной схемой и обоснованной partition spec. Запиши данные через Lakekeeper и объясни snapshots/files. Повтори таблицу через Nessie или докажи, почему он не подходит.

Кейс: пять команд пишут operational facts в S3; Flink делает streaming append, Spark — correction/upsert, Trino читает. Нужны audit trail, изоляция, восстановление catalog metadata и time travel минимум на 7 дней.

## Обязательная сдача

1. DDL и воспроизводимый SQL/Java/Python код для write/read.
2. `evidence.md`: row counts, snapshot IDs, file counts и S3 locations.
3. Схема writers/readers → catalogs → storage с security boundary.
4. Сравнение минимум четырёх catalog вариантов.
5. Порядок backup/restore, compaction, snapshot expiration и orphan cleanup.
6. Пять production failure modes и обнаруживающих сигналов.
7. ADR: выбранный catalog, rejected alternatives, assumptions и open questions.

Не обещай exactly-once только из-за Iceberg; не удаляй объекты вручную; не используй только `COUNT(*)` как доказательство; production recommendation должна назвать restore path и владельца secrets.

Сдай [submission layout](../submissions/README.md), оцени по [rubric](rubric.md).
