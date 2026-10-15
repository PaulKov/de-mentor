# Workbook — Distributed Filesystems and Object Storage

Работай по этапам. Для каждой схемы помечай: **данные**, **metadata**, **placement map**, **кворум**, **клиентский API** и **границу отказа**.

## 1. Storage contract: не начинай с бренда

Для каждой задачи зафиксируй:

| Вопрос | Пример ответа |
| --- | --- |
| Что адресуем? | блоки тома / путь и inode / bucket и key |
| Как пишем? | random overwrite / append or replace file / PUT whole object or multipart |
| Как читаем? | random I/O / sequential stream / GET + byte range |
| Нужны ли rename, locks, directory listing? | `rename` атомарно в namespace / нет / prefix-list как запрос |
| Параллелизм | несколько readers, один writer / конкурирующие writers / overwrite key policy |
| Что значит успех PUT? | block ack quorum / close+metadata commit / сервис принял объект и подтвердил write |
| Отказ | локальный диск / rack / зона / регион / metadata DB / gateway |
| NFR | throughput, p99, durability, RPO/RTO, cost per read/write |

Задание: оцени VM root disk, NFS shared directory, Kafka log, Iceberg warehouse, image CDN, ML checkpoint, миллион JSON по 1 KB и backup archive. Не отвечай «S3 везде»: назови требуемые семантики и цену адаптации клиента.

## 2. Нарисуй history → design

По [GFS paper](https://research.google/pubs/the-google-file-system/), [HDFS design](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html), [S3 launch](https://aws.amazon.com/blogs/aws/eight-years-and-counting-of-cloud-computing/) и [Ceph paper](https://www.usenix.org/legacy/event/osdi06/tech/full_papers/weil/weil_html/index.html) заполни:

| Система/период | Ограничение прежнего подхода | Идея дизайна | Что оптимизировано | Что усложнилось |
| --- | --- | --- | --- | --- |
| GFS, 2003 |  |  |  |  |
| HDFS / Hadoop, 2000-е |  |  |  |  |
| Amazon S3, 2006 |  |  |  |  |
| Ceph, OSDI 2006 и далее |  |  |  |  |
| Cloud data lakes / lakehouse |  |  |  |  |

Отдельно ответь: почему cheap commodity nodes, большие файлы и streaming scan ведут к другому дизайну, чем small random I/O? Почему separation compute/storage полезно и какой сетевой/metadata cost оно добавляет?

## 3. Два durability бюджета

Сравни:

1. Три полные реплики: для `D` полезных bytes нужно примерно `3D` raw capacity до учета свободного резерва, metadata и write amplification.
2. Erasure set `8+3`: `k=8` data shards, `m=3` parity shards, `n=11`. Для объёма полезных данных `D` нужно примерно `D × 11/8 = 1.375D` raw capacity; идеальная схема восстанавливает кодовое слово после потери до трёх shards того же stripe.

Это арифметика, а не SLA. Нарисуй два разных failure map: все три replica на одном rack и EC shards по одному на 11 независимых узлах. Затем укажи, что произойдёт при потере целого rack, при исчерпании write quorum, при недоступном network path и во время repair. Оцени стоимость деградированного чтения: реконструкция может читать несколько shards и потреблять CPU/network.

## 4. Lab A — проверить S3 endpoint

Требования: Docker Desktop с уже поднятым `flink-iceberg` stack. AWS CLI контейнер использует demo credentials из Compose environment; копировать secrets в shell history не нужно.

```powershell
$Compose = "./labs/flink-iceberg/compose.yaml"
docker compose -f $Compose ps seaweedfs seaweedfs-init
Invoke-RestMethod http://localhost:19333/cluster/status
```

Запусти one-shot AWS CLI в Compose network. `seaweedfs-init` закреплён за AWS CLI образом и уже содержит endpoint credentials:

```powershell
$ObjectKey = "storage-lesson/$([guid]::NewGuid().ToString('N'))/probe.txt"
$Aws = @("--endpoint-url", "http://seaweedfs:8333")

docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api list-buckets
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api put-object `
  --bucket de-mentor-warehouse --key $ObjectKey --body /etc/hostname
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api head-object `
  --bucket de-mentor-warehouse --key $ObjectKey
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api get-object `
  --bucket de-mentor-warehouse --key $ObjectKey /tmp/probe.txt
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3 cp `
  "s3://de-mentor-warehouse/$ObjectKey" -
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api list-objects-v2 `
  --bucket de-mentor-warehouse --prefix storage-lesson/
```

Открой `http://localhost:18888` и найди путь bucket/key в filer namespace. Сопоставь endpoint-ы: S3 `:19000`, filer `:18888`, master `:19333`. Gateway принимает S3-запрос, но при чтении master/volume/filer выполняют разные обязанности.

Заверши очисткой только созданного временного key:

```powershell
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api delete-object `
  --bucket de-mentor-warehouse --key $ObjectKey
```

Для повторяемости сохрани JSON результата `put-object`, `head-object`, listing, HTTP status и путь, который увидел в filer UI. Не удаляй bucket и не запускай `down --volumes`.

### Вопросы по trace

1. Какие части запроса проходят через S3 gateway, filer, master и volume server?
2. Почему master не обязан проксировать поток каждого GET?
3. Какие данные останутся, если остановить catalog service, но оставить SeaweedFS запущенным? Какие — если потерять filer metadata store?
4. Какой механизм делает данный локальный demo недоказательным для node/rack failure?

## 5. Lab B — S3 key не равно файловому пути

Создай два соседних key:

```powershell
$KeyA = "training/day=2026-10-14/a.txt"
$KeyB = "training/day=2026-10-14/b.txt"
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api put-object `
  --bucket de-mentor-warehouse --key $KeyA --body /etc/hostname
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api put-object `
  --bucket de-mentor-warehouse --key $KeyB --body /etc/hostname
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api list-objects-v2 `
  --bucket de-mentor-warehouse --prefix training/
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api delete-object `
  --bucket de-mentor-warehouse --key $KeyA
docker compose -f $Compose run --rm --no-deps --entrypoint aws seaweedfs-init @Aws s3api delete-object `
  --bucket de-mentor-warehouse --key $KeyB
```

Сравни объектный key/prefix с реальным directory resource в файловой системе. В обычном flat namespace bucket косая черта является частью key и инструмент отображения может рисовать её как папку. Реальные иерархические namespace доступны как отдельные опции некоторых сервисов и влияют на семантику, возможности и стоимость миграции.

## 6. Lab C — контраст с HDFS и Iceberg

В [Lesson 05 SQL demo](../../lesson-05/) запиши строку в Iceberg и проследи `data file → manifest → snapshot metadata → catalog pointer`. Ответь отдельно:

- кто создал Parquet bytes;
- кто разрешает S3 endpoint и ключ доступа;
- кто публикует текущий Iceberg snapshot;
- какая гарантия потеряется, если удалить объект вручную;
- почему `rename` каталога и atomic Iceberg metadata commit — разные операции.

Если Hadoop client отсутствует, HDFS write path разберись по официальному [HDFS design](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html): NameNode выбирает DataNodes; клиент передаёт block pipeline и ждёт acknowledgement chain; NameNode управляет namespace и блоками, но не проксирует payload bytes.

## 7. Лабораторная D — выбери класс системы и проследи request path

Прочитай [HDFS internals](deep-dives/hdfs-internals.md), [Ceph internals](deep-dives/ceph-internals.md), [SeaweedFS internals](deep-dives/seaweedfs-internals.md) и сравнительный [product/deployment deep dive](deep-dives/products-and-deployment.md). Для каждой системы заполни таблицу своими словами:

| Система | API приложения | Кто владеет namespace/metadata | Кто выбирает placement | Кто передаёт payload | Главный recovery unit | Первая вероятная точка давления |
| --- | --- | --- | --- | --- | --- | --- |
| HDFS |  |  |  |  |  |  |
| Ceph RGW / CephFS / RBD |  |  |  |  |  |  |
| SeaweedFS S3 / Filer |  |  |  |  |  |  |
| Apache Ozone |  |  |  |  |  |  |
| Lustre |  |  |  |  |  |  |
| RustFS |  |  |  |  |  |  |

Ответь и приведи источник для каждого ответа:

1. Почему HDFS NameNode — и одновременно упрощение control plane, и потенциальный namespace bottleneck? Что решают HA и federation, а чего они не решают?
2. Почему Ceph client получает cluster map и вычисляет placement через CRUSH, а не спрашивает центральный locator для каждого RADOS object? Какие компромиссы дают PG/acting set и recovery?
3. В SeaweedFS почему master может не находиться в прямом byte path после получения mapping, и чем долговечность Filer metadata отличается от долговечности volume bytes?
4. Apache Ozone использует слова *volume*, *bucket*, *key*, *block* и *container*: укажи, к какому namespace/слою относится каждое. Почему `ofs://` не следует автоматически называть POSIX mount?
5. Lustre OST называется *Object Storage Target*. Почему отсюда не следует S3 bucket/key API? Нарисуй путь POSIX `open()`/read через MDT и OSS/OST.
6. RustFS — S3-first сервис с erasure coding. Какие проверяемые признаки нужны, прежде чем поручить ему production Iceberg warehouse: S3 operation matrix, node-loss behavior, quorum, heal, upgrade, restore, metrics, IAM/KMS, workload benchmark?

| Workload | Система-кандидат | Почему | Что обязательно проверить |
| --- | --- | --- | --- |
| Hadoop batch scan больших файлов |  |  |  |
| MPI/HPC shared checkpoints, 1000 клиентов |  |  |  |
| on-prem VM block + POSIX + S3 |  |  |  |
| lakehouse на Hadoop/Spark с `ofs://` и S3 |  |  |  |
| миллиарды небольших media blobs |  |  |  |

Это paper lab: Compose стенда намеренно не поднимает HDFS, Ceph, Ozone или Lustre. Не выдавай single-node SeaweedFS S3 lab за отказный PoC этих систем.

## 8. Senior design prompt

На выбор: (A) 5 PB холодного backup, редкие большие GET и compliance hold; (B) 40 TB live Iceberg, параллельный Flink/Spark/Trino, много metadata operations; (C) media service с миллиардами изображений по 10–200 KB и CDN; (D) ML feature store с низким latency и частым overwrite.

Представь architecture decision record: API/semantics, capacity formula, replica/EC и failure domains, identity/encryption, network egress, repair bandwidth, object size/key scheme, lifecycle, monitoring, backup/restore, benchmark и exit strategy. В [decision matrix](decision-matrix.md) отметь hard constraints и unknowns, которые нужно измерить PoC.

Сохрани evidence по [шаблону](../homework/templates/evidence.md) и задай вопросы senior reviewer: что происходит во время деградации, что является source of truth и как показать восстановление, не делая предположений о S3 compatibility?
