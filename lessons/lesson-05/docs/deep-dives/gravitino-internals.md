# Apache Gravitino — от федерации метаданных до Iceberg commit

Gravitino вырос из задачи общего доступа к метаданным нескольких систем. В организации могут одновременно существовать HMS для Hive, Iceberg catalog для новых таблиц, JDBC для операционных БД и отдельный реестр Kafka. Каждый хранит свои сущности и понимает свои операции. Проект, первоначально созданный Datastrato, вошёл в Apache Incubator в июне 2024 года и завершил инкубацию в мае 2025 года. Основной сервер даёт этим системам общую модель имён и управления, а Iceberg REST служба предоставляет движкам протокол Iceberg. [Исходный глоссарий](https://gravitino.incubator.apache.org/docs/0.8.0-incubating/glossary/) · [История проектов Apache Incubator](https://incubator.apache.org/projects/)

## 1. Metalake, каталог и backend

```text
Платформа / Gravitino API → metalake commerce
  ├─ catalog legacy_hive  → Hive Metastore
  ├─ catalog orders_oltp  → PostgreSQL
  └─ catalog analytics   → Iceberg backend (например, JDBC)

Flink Iceberg REST client → Gravitino Iceberg REST → backend каталога Iceberg
Flink FileIO и FileIO сервиса → S3 (Iceberg metadata и файлы таблиц)
```

**Metalake** — верхняя граница организации каталогов. У каталога есть provider, который определяет тип внешней системы и доступные операции. **Iceberg namespace** находится внутри выбранного Iceberg catalog. **Warehouse** в настройке backend — корень хранения; в запросе `/v1/config?warehouse=analytics` у именованного Gravitino REST каталога это ключ выбора конфигурации. На стороне Flink имя в `CREATE CATALOG gravitino` — локальный псевдоним SQL-сессии. Эти четыре имени могут отличаться.

Различай два API и два возможных хранилища состояния. Основной Gravitino server ведёт собственные метаданные платформы и конфигурации. Iceberg REST использует выбранный Iceberg backend для регистрации таблиц и публикации новых версий metadata. Запись в БД основного Gravitino и запись JDBC backend Iceberg могут принадлежать разным схемам или системам. В лабораторной включена только standalone служба Iceberg REST. [Iceberg REST: конфигурация и backend](https://gravitino.apache.org/docs/1.3.1/iceberg-rest-service/) · [Iceberg catalog provider](https://gravitino.apache.org/docs/1.3.1/lakehouse-iceberg-catalog/)

| Режим | Конфигурация | Для чего нужен |
| --- | --- | --- |
| Standalone со статической конфигурацией | Файл или переменные окружения, собственный REST endpoint | Независимый Iceberg REST сервис. В лабораторной используется JDBC/PostgreSQL и отдельный S3 prefix |
| Auxiliary service с dynamic provider | Служба внутри основного Gravitino, каталоги берутся из metalake | Управление несколькими каталогами и применение политик Gravitino к Iceberg REST операциям при включённой авторизации |

Документация 1.3.1 описывает backend `jdbc`, `hive` и `rest`; для демонстрации доступен `memory`. Смена backend меняет место и механизм публикации. JDBC опирается на SQL update, Hive — на протокол `HiveCatalog` и HMS, REST — на операции удалённого каталога. Проверяй возможности каждого слоя, в том числе отсутствие multi-table transactions в Gravitino Iceberg REST 1.3.1. [Версия 1.3.1 и ограничения REST](https://gravitino.apache.org/docs/1.3.1/iceberg-rest-service/)

## 2. Что происходит во время INSERT

1. Iceberg REST клиент Flink запрашивает `GET /iceberg/v1/config`. Сервис может вернуть defaults, overrides и доступные endpoints. При открытии таблицы клиент получает её metadata и конфигурацию доступа.
2. Для обычного INSERT Flink пишет Parquet и готовит manifest files. Iceberg REST запрос обновления передаёт требования к текущему состоянию (`requirements`) и изменения (`updates`). Требование, например, может проверять текущий snapshot ref.
3. Служба REST применяет изменения к metadata выбранного каталога. В режиме JDBC новый Iceberg metadata JSON записывается через `FileIO` в S3. Затем `JdbcTableOperations` обновляет запись каталога, если указатель соответствует прочитанному состоянию. Это момент публикации.
4. Читатель, заново загрузивший таблицу после commit, видит новую metadata. Файлы, которые writer успел положить в S3 перед отклонённым commit, сами по себе в таблице не появляются.

Упрощённая модель условного обновления. Сопоставь её с классом `JdbcTableOperations` и его SQL helpers в Iceberg.

```sql
UPDATE iceberg_tables
SET metadata_location = :new_location,
    previous_metadata_location = :old_location
WHERE catalog_name = :catalog_name
  AND table_namespace = :namespace
  AND table_name = :table_name
  AND metadata_location = :old_location;
```

Одна изменённая строка означает успешную замену указателя. Ноль строк означает, что ожидаемая запись больше не совпадает с состоянием БД. Конкретный retry зависит от операции и Iceberg connector. При потере HTTP ответа результат неизвестен, пока writer не сверит состояние таблицы. Повторная отправка исходных событий отдельным запуском может дать повторную загрузку. [Iceberg REST OpenAPI](https://github.com/apache/iceberg/blob/apache-iceberg-1.11.0/open-api/rest-catalog-open-api.yaml) · [JdbcTableOperations](https://github.com/apache/iceberg/blob/apache-iceberg-1.11.0/core/src/main/java/org/apache/iceberg/jdbc/JdbcTableOperations.java)

## 3. Подключение и границы доступа

- Flink 2.2 в стенде использует **нативный Iceberg REST клиент**, поставляемый с Iceberg runtime. Отдельный Gravitino Catalog Store connector в документации 1.3.1 опубликован для Flink 1.18–1.20. Это другой способ подключения к основному серверу. [Flink через Iceberg REST](https://gravitino.apache.org/docs/1.3.1/iceberg-rest-engine/flink/) · [Gravitino Flink connector](https://gravitino.apache.org/docs/1.3.1/flink-connector/flink-connector/)
- Доступ к HTTP каталогу и доступ к объектам S3 проверяются раздельно. Стенд использует статические локальные ключи для Flink и сервиса. В PoC с выдачей временных credentials проверяй, что движок получает, использует и обновляет именно выданные credentials и что их область ограничена нужным префиксом. Политики Gravitino на Iceberg REST в 1.3.1 требуют auxiliary режима, dynamic provider и включённой авторизации. [Credential vending 1.3.1](https://gravitino.apache.org/docs/1.3.1/security/credential-vending/) · [REST access control](https://gravitino.apache.org/docs/1.3.1/iceberg-rest-service/#access-control)
- Если HMS доступен и напрямую, и через Gravitino, проверь обход политик и согласованность двух путей. При переходе особенно важны одинаковая регистрация таблицы, cache invalidation, единый протокол записи и контроль прямого доступа к storage. Одинаковый S3 prefix у двух независимых каталогов сам по себе не создаёт общий commit protocol.

## 4. Где он выигрывает и где усложняет решение

| Задача | Что проверить первым |
| --- | --- |
| Один self-hosted Iceberg warehouse на S3, несколько движков | Lakekeeper и Gravitino REST. Сравни изоляцию warehouse, операции каталога, credential delegation и работу при отказе metadata DB |
| Уже есть HMS, нужен стандартный Iceberg REST API | Gravitino с HMS backend и Hive REST. Проверь возможности конкретных релизов, работу прежних клиентов и восстановление каталога |
| Hive, Iceberg, JDBC и Kafka нужно описать одним реестром | Полный Gravitino с metalake и нужными providers. Проверяй матрицу операций каждого engine и источника |
| Публикация согласованного набора таблиц через ветки и refs | Nessie и его модель версий каталога. Iceberg snapshots и refs одной таблицы относятся к другому уровню |
| Управляемый каталог с IAM и Lake Formation | Glue. Сравни политики, операции выбранного клиента и региональные ограничения |

В [итоговом учебном проекте](../../../lesson-06/homework/principal-capstone.md) каталог отвечает за разрешение имени таблицы, доступ и публикацию Iceberg commit. Границы синтетических выгрузок, устранение повторов и допуск полной выгрузки к публикации определяются контрактом источника и обработкой Flink.

## 5. Пограничные случаи для production PoC

| Сценарий | Что фиксировать |
| --- | --- |
| REST отвечает на `/v1/config`, но выбран неверный warehouse/backend | Фактическая строка в нужной БД и фактический S3 prefix. Успешный healthcheck сам по себе не доказывает маршрутизацию |
| У клиента разрешён HTTP LoadTable, но запрет на S3 GET | Отдельные результаты LoadTable и чтения Parquet. После выдачи credentials проверь доступ к нужному prefix и отказ на соседнем |
| Долгий Flink job переживает срок действия credentials | Первый и последующий запросы к S3, смена identity/expiry, восстановление после временного отказа выдачи |
| HTTP ответ потерян после обновления JDBC строки | Текущий `metadata_location`, snapshot lineage и повторное чтение до принятия решения о retry |
| Writer A пишет через REST, writer B через Thrift в тот же HMS | Указатели до и после конкурирующей записи, потерянные обновления, stale cache и применение авторизации на каждом пути |
| JDBC восстановлен на более ранний момент, S3 содержит более новые файлы | Сверь указатель и достижимый snapshot graph. Удерживай cleanup до решения о roll-forward, rollback и согласовании с downstream |
| Смена backend или версия JDBC schema при обновлении | Экспорт записей каталога, восстановление на тестовой копии, проверка допустимых DDL/commit операций и отката версии |
| Одна из двух таблиц обновилась перед отказом | Reader видит смешанную версию, если приложение не вводит общий протокол публикации. Проверь собственный publish marker и replay |

## 6. Лабораторная и вопросы на защиту

Выполни [Lab D](../runbooks/gravitino-lab.md) и сохрани один `metadata_location` из PostgreSQL, snapshot ID из Flink и путь Parquet из `$files`. Объясни, где они возникают в последовательности выше. Для PoC добавь двух writers, отказ JDBC между записью файлов и commit, восстановление каталога из бэкапа и повторное чтение из второго движка.

1. Какие S3 объекты могут остаться, если БД недоступна после записи Parquet? Как выяснить результат commit после таймаута?
2. Зачем давать ограниченные S3 credentials движку, если HTTP-каталог уже проверил его права?
3. Что придётся восстановить в PostgreSQL и S3? Изменится ли ответ для Gravitino поверх HMS?
4. Как доказать, что два движка через разные API используют одну регистрацию таблицы и согласуют запись?
