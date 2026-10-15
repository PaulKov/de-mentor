# План ментора — Lesson 05

## Сценарий

Начни с ошибочной mental model «таблица = папка с Parquet». Попроси ученика предсказать, где Iceberg хранит актуальность таблицы и как разрешается concurrent writer. Сначала разложи HMS: запись имени и current pointer в PostgreSQL, а Iceberg metadata/data — в S3. Затем сравни HMS Thrift, Lakekeeper REST и Nessie versioned refs на одном object store: каталоги связаны с storage, но имеют разные API, semantics и режимы отказа.

## Фасилитация (210 минут)

### 0–15: границы

Пусть ученик нарисует Engine, Catalog, Table Format и Object Store; сохрани исходный ответ.

### 15–40: metadata chain

Разбери metadata JSON → snapshot → manifest list → manifests → files и atomic pointer update. Спроси, чем orphan data file отличается от committed data file.

### 40–60: история каталогов и REST

Разбери [deep dive HMS](deep-dives/hive-metastore-and-catalog-evolution.md): почему Facebook создал Hive, как HMS стал общим metadata hub и какие новые требования привели к REST, cloud-managed и versioned catalogs. Подчеркни, что Iceberg table metadata и HMS catalog entry — разные слои.

### 60–75: REST catalog и старт

Запусти `./labs/flink-iceberg/scripts/up.ps1`, дождись health checks. При ошибке смотри Compose logs, не удаляй volumes первым действием. Сравни протокол и продукт: Lakekeeper — REST implementation с warehouse/storage profile и delegation; Nessie — version store с branches/tags; REST endpoint не равен Nessie native API. Текущая upstream документация помечает Iceberg REST integration Nessie как experimental. REST — не synonym для одинаковых возможностей.

### 75–105: Hive Metastore

Выполни `04-hive-catalog-demo.sql`. Проследи `get_table -> metadata_location -> S3 JSON -> manifests -> Parquet`; потом покажи `TABLE_PARAMS` в отдельной HMS PostgreSQL. Уточни, что HMS DB не хранит Iceberg data и не становится S3.

### 105–140: Lakekeeper

До DDL спроси, какие операции идут к Catalog REST, какие к S3. После insert сопоставь `$snapshots`, `$files` и SeaweedFS objects.

### 140–160: Nessie

Повтори DDL на `nessie`, проверь отдельный prefix. Создай branch и объясни, что меняется в catalog reference, а что остаётся общим.

### 160–180: альтернативы

Используй [decision matrix](catalog-decision-matrix.md). Обсуди managed vs self-hosted, protocol maturity, authorization, backup, multi-tenant boundaries и engine compatibility.

### 180–200: design review

Сценарии: catalog отвечает, но S3 медленный; затем catalog недоступен, S3 отвечает. Ученик должен оценить отдельно metadata ops, scans, commit и recovery.

### 200–210: debrief

Вернись к исходной схеме, попроси исправить её и назвать три production guardrails.

## Частые misconceptions

| Ошибка | Интервенция |
| --- | --- |
| «Iceberg сам является storage» | где физически лежит Parquet? |
| «Catalog — только listing файлов» | кто хранит current metadata pointer? |
| «Iceberg уже положил metadata в S3, значит HMS не нужен» | кто по логическому имени выбирает актуальный metadata JSON и публикует новый pointer? |
| «HMS и Hive — одно и то же» | запусти только Flink + Iceberg HiveCatalog: где запросный engine, а где общий metadata service? |
| «REST значит конкретно Lakekeeper» | какие API и semantics у Hive REST, Polaris, Lakekeeper и Nessie? |
| «Если Parquet появился в SeaweedFS, commit успешен» | как читатель найдёт object в snapshot chain? |
| «Drop table удаляет все S3 файлы» | раздели catalog drop и physical garbage collection |
| «Branch — полная копия data» | объясни immutable files и diverging metadata commits |

Ученик проходит урок, если прослеживает commit, показывает snapshot в SQL/S3, называет impact двух разных outages и объясняет catalog choice через требования.
