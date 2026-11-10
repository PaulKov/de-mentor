# Deep Dive: Catalog, commit protocol и Iceberg REST

Каталог — не база данных строк таблицы и не сам table format. Его самый важный контракт при записи — согласованно опубликовать новое местоположение Iceberg metadata. Внутри формата данные и snapshots immutable; mutable точка входа — указатель на текущий metadata version. Поэтому стабильность каталога определяет, как разрешается гонка writers.

## 1. От идеи к протоколу

Схема «файлы в object store + одна изменяемая запись о текущем состоянии» похожа на copy-on-write metadata transaction: сначала пишется новая версия, потом выполняется условный swap `current = new`, только если текущая версия всё ещё та, от которой строили изменение. Читатель фиксирует pointer при открытии таблицы и далее читает immutable файлы, значит не видит полуперезаписанный snapshot.

Если два писателя A и B загрузили metadata M10:

```text
A writes data-A, builds M11A ─┐
                             ├─ catalog.compareAndSwap(M10 → M11)
B writes data-B, builds M11B ─┘
```

Только один может atomically заменить M10. Второй получает commit conflict. Он не должен слепо overwrite-ить указатель: нужно перечитать M11 победителя, проверить, можно ли приложить своё изменение (например, append не удаляет те же файлы), собрать новый metadata и повторить. Операции rewrite/delete должны проверять, что набор файлов, на котором они рассчитывались, по-прежнему актуален. Iceberg задаёт validation/isolation поведение, а реализация `Catalog` обеспечивает атомарную точку публикации.

## 2. REST-путь: что клиент говорит сервису

Iceberg REST Catalog Protocol стандартизирует HTTP интерфейс, чтобы Spark/Flink/Trino не зависели от конкретной реализации каталога. При старте client конфигурирует REST endpoint, warehouse/prefix и auth. Дальше lifecycle примерно такой:

```text
Flink Iceberg client
  GET /v1/config              → capabilities, auth URLs, defaults
  POST /v1/namespaces         → namespace (если требуется)
  POST /v1/namespaces/.../tables → create/load table
  GET /v1/namespaces/.../tables/T → metadata-location + config
  PUT /v1/namespaces/.../tables/T → commit requirements + updates
                                     ├─ success: новый pointer опубликован
                                     └─ conflict: клиент refresh/rebase/retry
```

Реальная последовательность endpoint-ов может содержать OAuth/token exchange, credential vending, namespace lookup и дополнительные capabilities. REST — протокол между engine/library и service; он не означает, что все реализации имеют одинаковую БД, authz, multi-table transaction или branch semantics. [Iceberg REST spec](https://iceberg.apache.org/rest-catalog-spec/) · [Catalog concepts](https://iceberg.apache.org/docs/latest/catalog/).

## 3. Где живёт mutable pointer: варианты

| Реализация | Где хранится указатель и commit serialization | Что получает команда |
|---|---|---|
| HadoopCatalog | directory metadata + filesystem rename/lock предположения | минимальная зависимость; ограничения object storage и concurrent semantics нужно оценить внимательно |
| HiveCatalog | Hive Metastore entry / DB transaction | интеграция с Hive ecosystem; метастор становится важной HA/операционной зависимостью |
| JDBC catalog | SQL database row/transaction | понятная транзакционная БД; команда сама отвечает за HA/backup/upgrades |
| AWS Glue | managed catalog service | IAM/cloud integration; привязка к AWS operational model |
| REST service (Lakekeeper, Polaris и др.) | реализация решает через DB/service-specific transaction | общая клиентская граница, централизованные policy/auth/catalog features |
| Nessie | versioned references + Iceberg metadata state | ветки/теги и согласованное versioning набора таблиц; дополнительный storage backend и API semantics |

Таблица не заменяет нагрузочное тестирование и verification матрицы engine versions. Протокол может быть общим, но credential vending, OAuth, branches, views, multi-table semantics, deletion/GC и rollout capabilities различаются.

## 4. Lakekeeper: control plane, Postgres и S3 data plane

В нашем Compose Lakekeeper развернут как service с миграцией схемы и `serve`, Postgres хранит состояние каталога, а SeaweedFS — warehouse objects. Запросы к Lakekeeper идут на `http://localhost:18181`; таблицы физически пишутся в `s3://de-mentor-warehouse/lakekeeper/...`.

```text
Flink TaskManager ── REST control plane ──► Lakekeeper ──► PostgreSQL
       │                                        │
       └──────────── S3 data plane ─────────────┴──────► SeaweedFS
```

Нужно разделять три режима доступа к storage:

1. **Статические credentials у engine**: просто для локальной лабораторной, но секрет попадает в конфиг клиента/контейнера и живёт столько, сколько credential.
2. **Vended/session credentials**: catalog выдаёт ограниченные временные credentials или scoped permissions; workload получает только доступ к нужному warehouse/prefix.
3. **Remote signing**: клиент/engine отправляет REST запрос на подпись, а секрет и signing authority остаются у catalog service. Хорошо показывает границу доверия, но добавляет зависимость от доступности/latency service для signed requests.

В стенде выбран простейший безопасный для воспроизводимости учебный вариант: локальная SeaweedFS, фиктивные ключи и `allowall`, изолированные на loopback. Это иллюстрирует протоколы, но **не** является шаблоном IAM, TLS, multi-tenant authz, secrets management или production deployment. Lakekeeper умеет S3-compatible profiles, remote signing и credentials vending; конкретная комбинация зависит от deployment и клиента. [Lakekeeper S3 configuration](https://docs.lakekeeper.io/docs/latest/storage-s3/) · [Lakekeeper bootstrap](https://docs.lakekeeper.io/docs/latest/bootstrap/).

## 5. Nessie: граф references поверх состояния таблиц

Nessie добавляет catalog-level version control. Branch или tag указывает на commit hash; commit фиксирует набор метаданных таблиц на определённой версии. Это уровень шире Iceberg snapshot: Iceberg snapshot версионирует одну таблицу, Nessie commit может зафиксировать согласованное состояние многих tables/views. Файлы Parquet не копируются при создании branch — ветка меняет ссылки на metadata state.

```text
main:       C0 ── C1 ── C3
                     \
review:                C2

table snapshot A/B at C1  ← consistent catalog state
table snapshot A/B at C2  ← isolated review changes
merge review → main      ← conflict-aware ref operation
```

В стенде включены Nessie API и Iceberg REST на одном server, warehouse `s3://de-mentor-warehouse/nessie`, RocksDB volume для учебного каталога. REST URI может указывать branch, например `http://nessie:19120/iceberg/review`; это относится к конфигурации конкретного Nessie integration и не делает обычные Iceberg snapshots ненужными. Современная документация называет Iceberg REST integration Nessie experimental — учитывайте статус при production выборе. [Nessie REST guide](https://projectnessie.org/guides/iceberg-rest/) · [Nessie concepts](https://projectnessie.org/guides/introduction/).

Lakekeeper и Nessie отвечают на разные акценты: Lakekeeper позиционируется как централизованный catalog service с warehouse/storage access management; Nessie — версионирование ссылок и согласование изменений между таблицами/ветками. Оба могут давать REST интерфейс, но REST не стирает разницу бизнес-семантики.

### S3 delegation — не «просто настройки endpoint»

При Iceberg REST-каталоге клиент получает не только metadata location. В ответ могут входить `io-impl`, endpoint и path-style настройки для FileIO, а также один из механизмов полномочий на запись в object store:

- **credentials vending**: клиент получает ограниченные по времени credentials; обычно нужна STS-совместимая инфраструктура;
- **remote request signing**: клиент строит S3-запрос, но просит catalog подписать его отдельным REST-вызовом; секрет остаётся на стороне catalog;
- **credentials у клиента**: прямой статический ключ, как в нашем изолированном учебном стенде.

Последний вариант проще для локального SeaweedFS, но даёт Flink TaskManager постоянные ключи. Не переносите его в общую среду или production. Nessie предупреждает, что его Iceberg REST integration экспериментальна; возможности endpoint-ов и способы выдачи доступа нужно сверять одновременно для catalog server, Iceberg runtime и движка.

В этом стенде мы поймали полезную межверсионную ошибку. Nessie 0.109.0 возвращал конфигурацию с `s3.signer.uri`/`s3.signer.endpoint`, но установленный Iceberg 1.12.0 вызывал `POST /iceberg/v1/main/namespaces/lesson05/tables/catalog_comparison/sign`; Nessie отвечал 404. Ошибка возникала при закрытии Parquet writer, уходила в fatal exception handler TaskManager и перезапускала сам процесс. Поэтому диагностика только по SQL клиенту выглядела как нестабильность Flink, хотя первичная причина была на REST/S3 delegation границе.

Для лаборатории выбран явный обход: Nessie `request-signing-enabled=false`, а Nessie Iceberg Catalog получает SeaweedFS endpoint и фиктивные статические credentials напрямую в `01-catalogs.sql`. Так запись, commit и последующее чтение работают; учение об auth boundary остаётся в этом Deep Dive. Это локальная compatibility-настройка, не универсальная рекомендация. Перед другим сочетанием версий сделайте короткий write/read smoke test и проверьте `GET /iceberg/v1/config`, конфигурацию загруженной таблицы и реально вызванные REST paths. История Nessie релизов показывает, что поддержка Iceberg REST и S3 credential/signing механизмов добавлялась постепенно; Iceberg 1.11 также существенно расширил REST-протокол. [Nessie Iceberg REST guide](https://projectnessie.org/guides/iceberg-rest/) · [Nessie release history](https://projectnessie.org/releases/) · [Iceberg REST Catalog](https://iceberg.apache.org/rest-catalog-spec/).

## 6. Failure matrix: что ломается и что должно пережить

| Сбой | Видимый эффект | Корректное восстановление |
|---|---|---|
| SeaweedFS недоступен до записи файлов | tasks получают storage error, checkpoint/job может fail | restart job; проверить ретраи и S3 health |
| Catalog недоступен после записи файлов, до commit | новые files могут остаться orphan; старый snapshot виден | восстановить catalog, retry commit; позднее safe orphan cleanup |
| Catalog недоступен при чтении | engine не может разрешить имя → metadata location | восстановить catalog/backup; существующий ранее план иногда уже знает file paths, но это не заменяет каталог |
| Postgres Lakekeeper потерян без backup | REST service поднялся, но pointer/warehouse state может быть потерян | restore согласованного DB backup + metadata/object storage; проверить журнал восстановления |
| два writers публикуют одну базу | проигравший получает conflict | refresh, validate, retry; не overwrite pointer вслепую |
| удалили объект, на который указывает metadata | snapshot повреждён, scan fail | restore object version/backup; политика GC должна учитывать все retained refs/snapshots |
| истёк временный S3 token во время multipart write | upload/commit retry или fail | обновить token path; метрика write/commit lag и expiry alert |

Читатель может продолжить scan по immutable файлам, если уже знает metadata/file list и они доступны, но свежий query обычно начинает с catalog и не должен обходить каталог, сканируя bucket «по папкам».

## 7. Наблюдение commit conflict двумя писателями

В лаборатории создайте отдельные таблицы/операции для безопасного опыта; не запускайте destructive compaction одновременно с cleanup. Сначала откройте два SQL клиента, чтобы оба загрузили одно состояние, затем сделайте конкурентные appends. Конфликт зависит от timing и может потребовать повторов:

```text
Terminal A: INSERT INTO lakekeeper.demo.concurrent_demo VALUES (...);
Terminal B: INSERT INTO lakekeeper.demo.concurrent_demo VALUES (...);
Ожидаемое: оба изменения в serial order либо конфликт/retry; никакой «тихой потери» успешной записи.
```

Соберите evidence: snapshot IDs, operation/summary, manifest count, logs, elapsed time. Потом отдельно сравните append с overwrite/delete — у операций разные validation requirements.

## 8. Код уровня API: Java commit lifecycle

Форматная библиотека обычно скрывает CAS/retry за `TableOperations.commit`. Схематично это выглядит так:

```java
TableMetadata base = operations.refresh();
TableMetadata proposed = update.apply(base); // new snapshot + metadata file
try {
  operations.commit(base, proposed);         // conditional pointer swap
} catch (CommitFailedException conflict) {
  TableMetadata latest = operations.refresh();
  validateCanRebase(base, latest, update);    // operation-specific checks
  TableMetadata rebased = update.apply(latest);
  operations.commit(latest, rebased);
}
```

Это псевдокод контракта, не приглашение реализовать свой Catalog поверх S3 `PUT`. Согласованный swap должен реализовываться storage/catalog механизмом с нужной атомарностью; простой `GET pointer → PUT pointer` теряет конкурентную запись. Исследуйте `BaseMetastoreTableOperations`, REST Catalog client, Lakekeeper commit handler, и тесты conflict/retry конкретной версии.

## Практика Senior

Нарисуйте sequence diagram для: CreateTable, append, конфликт append/overwrite, истекшие credentials, restore Postgres backup. Для каждого запроса укажите кто знает credentials, где лежат данные, какая атомарная операция фиксирует успех, и какая метрика показывает, что поток «checkpoint идёт, а Iceberg commits остановились».
