# Lab D — Gravitino Iceberg REST, PostgreSQL и S3

Ориентир **20–30 минут** после базового маршрута. Профиль запускает standalone Iceberg REST 1.3.1 и отдельную PostgreSQL для Iceberg JDBC catalog. Flink использует свой Iceberg REST client. Тестовая таблица получает отдельный префикс `gravitino/` в общем bucket SeaweedFS.

Из корня репозитория:

```sh
docker compose -f labs/flink-iceberg/compose.yaml --profile gravitino up -d --build --wait
docker compose -f labs/flink-iceberg/compose.yaml --profile gravitino exec -T flink-sql-client /opt/flink/bin/sql-client.sh -f /workspace/labs/flink-iceberg/sql/07-gravitino-catalog-demo.sql
```

Открой [REST config](http://localhost:19001/iceberg/v1/config) и найди список endpoints.

Найди в выводе два агрегата. Для `books` ожидаются 2 строки и 31.50, для `music` — 1 строка и 8.75. Затем сохрани ID последнего snapshot и пути Parquet из `$files`. Скрипт использует batch overwrite, поэтому при повторе появится новая версия таблицы с тем же результатом. Для интерактивной работы выполни команды из [SQL-файла](../../../../labs/flink-iceberg/sql/07-gravitino-catalog-demo.sql) в своей сессии.

Запроси состояние каталога:

```sh
docker compose -f labs/flink-iceberg/compose.yaml --profile gravitino exec -T gravitino-postgres psql -U gravitino -d iceberg -c "SELECT catalog_name, table_namespace, table_name, metadata_location, previous_metadata_location FROM iceberg_tables WHERE table_name = 'gravitino_catalog_comparison';"
```

Сопоставь `metadata_location` с объектом в [SeaweedFS Filer](http://localhost:18888) под `/buckets/de-mentor-warehouse/gravitino/`. Найди `current-snapshot-id` в JSON и сверь его с выводом Flink. PostgreSQL содержит каталожную запись, а JSON, manifests и Parquet лежат в S3. Повтори запрос после второго прогона и сравни оба указателя.

Для проверки границы отказа останови только `gravitino`. Попробуй открыть таблицу из новой сессии и отдельно проверь доступность сохранённого JSON в SeaweedFS. Затем запусти сервис снова.

```sh
docker compose -f labs/flink-iceberg/compose.yaml --profile gravitino stop gravitino
docker compose -f labs/flink-iceberg/compose.yaml --profile gravitino start gravitino
```

Для отчёта сравни путь `Flink → REST → JDBC` с `Flink → Thrift → HMS`. Укажи, какая БД хранит указатель, кто читает metadata и где живут объекты. [Подробный разбор Gravitino](../deep-dives/gravitino-internals.md) · [Сравнительная таблица](../catalog-decision-matrix.md)
