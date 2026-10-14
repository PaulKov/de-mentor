# Руководство ментора — Distributed Filesystems and Object Storage

## Подготовка

1. Прочитать [общие internals](deep-dives/distributed-storage-internals.md), отдельные главы [HDFS](deep-dives/hdfs-internals.md), [Ceph](deep-dives/ceph-internals.md), [SeaweedFS](deep-dives/seaweedfs-internals.md), затем [product/deployment comparison](deep-dives/products-and-deployment.md).
2. Поднять стенд через `labs/flink-iceberg/scripts/up.ps1`; убедиться, что SeaweedFS слушает только loopback ports.
3. Проверить доступность `http://localhost:19333/cluster/status` и filer UI `http://localhost:18888`.
4. Убедиться, что bucket `de-mentor-warehouse` создан; не проверять урок через удаление warehouse или reset volumes.
5. Открыть evidence template, выбрать домашний case и согласовать критерии senior review.

## Главные тезисы

- Storage contract определяет, что обещает клиенту API; физическая реализация — другой уровень.
- HDFS, Ceph и SeaweedFS оптимизируют разные абстракции. Ozone, Lustre и RustFS — дополнительные альтернативы, но не взаимозаменяемые реализации одного storage API.
- Apache Ozone — object store с Hadoop `ofs://` и S3, Lustre — parallel POSIX filesystem (OST не S3), RustFS — S3-first object server с собственной erasure/operations моделью.
- Replication и EC дают разные capacity/repair/latency tradeoffs; география shard placement важнее формулы overhead.
- S3 API дает HTTP key/object operations, но «S3-compatible» не гарантирует весь набор semantics конкретного cloud provider.
- Сильная консистентность одного key не делает multi-key update атомарным; Iceberg catalog commit и Flink checkpoint — следующие слои гарантий.
- Local Docker demo доказывает проход API, но не HA, failure domains, durability SLA или production security.

## Как вести discussion

### 0–50 минут: от нужды к API

Не начинайте с vendor list. Дайте участникам четыре workload: database volume, shared user directory, backup archive, Iceberg warehouse. Для каждого заставьте назвать API, read/write pattern, требование к rename/locks и поведение при отказе. Затем спросите, какую задачу решают GFS/HDFS и cloud object APIs.

### 50–90 минут: объяснить data path

На доске рисуются две стрелки: control plane (name/metadata/placement/policy) и data plane (payload/checksum/replica). Пусть группа отдельно проследит HDFS client → NameNode allocation → DataNode pipeline, Ceph client → cluster map/CRUSH → PG/OSDs, Seaweed S3 gateway → Filer/metadata → volume, Ozone OM → SCM/container → DataNode и Lustre client → MDT layout → parallel OSTs. Исправляйте схемы, в которых bytes идут через master без источника или человеку подменяют file API на S3.

### 105–135 минут: durability, quorum, failure domains

Начать с `3×` replicas и `8+3` EC. Уточнить, что арифметика не учитывает reserve, metadata, compaction, repair time и correlated failures. Попросить назвать деградированный read/write и rebuild paths. Не принимать ответ «EC выдерживает три сервера» без placement map и определения shard.

### 135–165 минут: S3/SeaweedFS lab

Следить, чтобы команды выполнялись из корня repo и AWS CLI запускался через `seaweedfs-init` в Compose network. Участник создаёт случайный key только в `storage-lesson/`, делает HEAD/GET/LIST и удаляет свой key. Filer UI подтверждает namespace; master status подтверждает только API health, не full integrity.

### 165–225 минут: selection и ops

Разделить участников на cloud, on-prem и hybrid команды. Каждой дать одинаковый workload и попросить посчитать capacity/requests/egress/repair, назначить owner для identities/backup/restore и предложить test. Уточнить стоимость экспорта и миграции, если выбранный сервис перестанет подходить.

## Частые неверные выводы

| Ошибка | Вопрос ментора |
| --- | --- |
| «S3 — это NFS по HTTP» | Какие операции/API гарантированы, а какие смонтированный adapter эмулирует? |
| «Папка существует, потому что key содержит `/`» | Это directory resource, prefix convention или UI presentation? |
| «Три реплики значит переживаем любые три поломки» | Где физически находятся replicas и какой write ack был подтвержден? |
| «8+3 — значит выдержим три AZ» | Распределены ли три parity/data shards по независимым AZ и есть ли quorum для write? |
| «Успешный CLI PUT доказал production readiness» | Какие были тесты concurrent write, restore, auth, multipart, throttling и node loss? |
| «Filer UI показывает файл — значит object bytes replicated» | Что доказывают filer metadata и где проверить replicas/EC/repair health? |
| «S3 strong consistency даёт транзакцию» | Сколько keys обновляли и какая система координирует multi-object commit? |
| «Объём данных помещается — значит cluster помещается» | Какой reserve нужен для rebuild, равномерно ли размещаются shards и сколько длится repair? |

## Оценка на занятии

Ученик должен объяснить один request path без подмены ролей, правильно рассчитать nominal overhead для replica/EC, показать lab evidence и назвать минимум три проверки конкретного S3-compatible API. Финальный ответ обязан назвать неизвестные, которые требуют измеримого PoC.

## Skip map

- 120 минут: сократить историю до timeline, сравнить HDFS/Ceph/SeaweedFS и сделать только S3 list/head.
- 180 минут: выполнить обе лабораторные и один cloud/on-prem comparison.
- 240 минут: полный workshop с failure map, TCO и case defense.

Материалы: [workbook](student-workbook.md), [матрица выбора](decision-matrix.md), [короткий маршрут](runbooks/simple-path.md), [глубокий маршрут](runbooks/deep-dive-path.md).
