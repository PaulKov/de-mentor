# Flink + Kafka + Iceberg lab

Изолированный Docker Desktop стенд для Lesson 05 и Lesson 06. Нужны Docker Desktop в режиме Linux containers, Compose v2 и около 5 GB свободной памяти Docker. Java, Maven и Python на хост устанавливать не требуется; Flink SQL и коннекторы собраны в Docker-образ.

## Топология

| Сервис | Роль | Адрес с хоста |
| --- | --- | --- |
| Flink JobManager / TaskManager | SQL и потоковая обработка; один TaskManager, два слота | UI: <http://localhost:18081> |
| Kafka 4.2.2 | входной topic `orders` | `localhost:19092` |
| SeaweedFS 4.46 | S3-compatible object storage | S3 API: <http://localhost:19000>; filer UI/API: <http://localhost:18888>; master: <http://localhost:19333> |
| Lakekeeper 0.13.6 | Iceberg REST catalog, warehouse в SeaweedFS | UI/API: <http://localhost:18181/ui/>; REST: `/catalog` |
| Nessie 0.109.0 | альтернативный REST catalog с refs/ветками | API: <http://localhost:19120> |
| PostgreSQL 17 | metadata store Lakekeeper | `localhost:15432` |

Порт-план намеренно отличен от базового Flink курса. Все опубликованные порты привязаны к loopback. Kafka и Flink общаются через отдельную Docker-сеть.

SeaweedFS предоставляет S3 API и локальный filer UI для просмотра объектов. `demouser / demosecret123456` — учебные ключи только для loopback-стенда; они не предназначены для production.

## Запуск

Из корня клона `de-mentor` в PowerShell:

```powershell
docker compose -f labs/flink-iceberg/compose.yaml up -d --build --wait
docker compose -f labs/flink-iceberg/compose.yaml ps
```

Первый запуск скачает несколько образов и Maven JAR-ы, поэтому займёт больше времени. В Compose автоматически создаются bucket SeaweedFS, схема Lakekeeper, bootstrap default project и warehouse `flink-demo`. Nessie хранит refs в RocksDB volume. Образы и учебные пароли закреплены только для локального демо.

Проверить состояние:

```powershell
docker compose -f labs/flink-iceberg/compose.yaml ps
docker compose -f labs/flink-iceberg/compose.yaml logs lakekeeper nessie flink-jobmanager
```

## Урок 05: каталоги и таблицы Iceberg

Запусти интерактивный Flink SQL Client, который подключится к кластеру и зарегистрирует оба каталога:

```powershell
docker compose -f labs/flink-iceberg/compose.yaml exec flink-sql-client `
  /opt/flink/bin/sql-client.sh -i /workspace/labs/flink-iceberg/sql/01-catalogs.sql
```

Пока SQL Client остаётся открыт, изучи файлы `sql/02-lakekeeper-demo.sql` и `sql/03-nessie-demo.sql` и выполни их команды в этом же prompt. После записи посмотри объекты в SeaweedFS filer UI, snapshots в Iceberg и таблицы в Lakekeeper UI. Для каждого нового SQL Client запускай `01-catalogs.sql` снова: регистрация Flink Catalog относится к SQL-сессии, а сами таблицы и файлы сохраняются в каталоге и S3.

## Урок 06: Kafka → Flink → Iceberg

В отдельном PowerShell:

```powershell
docker compose -f labs/flink-iceberg/compose.yaml exec kafka `
  /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 `
  --create --if-not-exists --topic orders --partitions 1 --replication-factor 1
```

В SQL Client выполни команды из `sql/04-kafka-source.sql`, затем `sql/05-stream-to-iceberg.sql`. После появления job в Flink UI отправь данные:

```powershell
Get-Content labs/flink-iceberg/data/orders.jsonl | docker compose -f labs/flink-iceberg/compose.yaml exec -T kafka `
  /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic orders
```

В Iceberg sink запустится checkpoint-driven commit. Проверь checkpoints в Flink UI, Iceberg snapshots в SQL, объекты через SeaweedFS filer UI/API и Kafka offsets. Затем останови job в Flink UI, перезапусти TaskManager и разберись, какие гарантии дают checkpoint + sink commit, а какие ограничения остаются у локального одноброкерного стенда.

## Управление и очистка

```powershell
docker compose -f labs/flink-iceberg/compose.yaml stop
docker compose -f labs/flink-iceberg/compose.yaml start
docker compose -f labs/flink-iceberg/compose.yaml down
```

`down` оставляет named volumes с каталогом, Kafka offsets, checkpoints и S3-объектами. Полный reset удаляет учебные данные без возможности восстановления:

```powershell
docker compose -f labs/flink-iceberg/compose.yaml down --volumes
```

## Ограничения

- Это не production-конфигурация: нет TLS, аутентификации, отказоустойчивости или отдельного S3 IAM. SeaweedFS credentials и PostgreSQL password — публичные demo-значения.
- Kafka имеет один брокер, один учебный partition и replication factor 1. Checkpoints используют общий локальный Docker volume, не S3. Это удобно для восстановления в лабораторной, но не доказывает production SLA.
- Nessie здесь развёрнут на persistent RocksDB как single-node catalog. Iceberg REST интеграция Nessie отмечена upstream-документацией как experimental; сравни её с Lakekeeper, а для production проверь совместимость и поддержку конкретного движка.
- Lakekeeper и Nessie управляют каталогами/metadata, а сами Parquet и Iceberg metadata files хранятся в SeaweedFS. Остановка catalog не удаляет S3 объекты.

← [Lesson 05](../../lessons/lesson-05/) · [Lesson 06](../../lessons/lesson-06/)
