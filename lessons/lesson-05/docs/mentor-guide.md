# План ментора — Lesson 05

## Сценарий

Начни с ошибочной mental model «таблица = папка с Parquet». Попроси ученика предсказать, где Iceberg хранит актуальность таблицы и как разрешается concurrent writer. Затем используй два каталога на одном S3: они показывают, что catalog service и object store связаны, но имеют независимые роли и режимы отказа.

## Фасилитация (210 минут)

### 0–15: границы

Пусть ученик нарисует Engine, Catalog, Table Format и Object Store; сохрани исходный ответ.

### 15–45: metadata chain

Разбери metadata JSON → snapshot → manifest list → manifests → files и atomic pointer update. Спроси, чем orphan data file отличается от committed data file.

### 45–60: REST catalog

Сравни протокол и продукт. Lakekeeper — REST implementation с warehouse/storage profile и delegation. Nessie — version store с branches/tags; REST endpoint не равен Nessie native API. Текущая upstream документация помечает Iceberg REST integration Nessie как experimental.

### 60–75: старт

Запусти `./labs/flink-iceberg/scripts/up.ps1`, дождись health checks. При ошибке смотри Compose logs, не удаляй volumes первым действием.

### 75–115: Lakekeeper

До DDL спроси, какие операции идут к Catalog REST, какие к S3. После insert сопоставь `$snapshots`, `$files` и SeaweedFS objects.

### 115–145: Nessie

Повтори DDL на `nessie`, проверь отдельный prefix. Создай branch и объясни, что меняется в catalog reference, а что остаётся общим.

### 145–170: альтернативы

Используй [decision matrix](catalog-decision-matrix.md). Обсуди managed vs self-hosted, protocol maturity, authorization, backup, multi-tenant boundaries и engine compatibility.

### 170–195: design review

Сценарии: catalog отвечает, но S3 медленный; затем catalog недоступен, S3 отвечает. Ученик должен оценить отдельно metadata ops, scans, commit и recovery.

### 195–210: debrief

Вернись к исходной схеме, попроси исправить её и назвать три production guardrails.

## Частые misconceptions

| Ошибка | Интервенция |
| --- | --- |
| «Iceberg сам является storage» | где физически лежит Parquet? |
| «Catalog — только listing файлов» | кто хранит current metadata pointer? |
| «Если Parquet появился в SeaweedFS, commit успешен» | как читатель найдёт object в snapshot chain? |
| «Drop table удаляет все S3 файлы» | раздели catalog drop и physical garbage collection |
| «Branch — полная копия data» | объясни immutable files и diverging metadata commits |

Ученик проходит урок, если прослеживает commit, показывает snapshot в SQL/S3, называет impact двух разных outages и объясняет catalog choice через требования.
