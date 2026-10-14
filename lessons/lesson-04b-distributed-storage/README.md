# Lesson 04b — Распределённые файловые системы и object storage

Место в курсе: **после Spark foundations и перед Iceberg/Flink** · Практика: **SeaweedFS S3 в стенде `flink-iceberg`** · Уровень: **от базовой модели до senior design review**

| Раздел | Путь | Зачем |
| --- | --- | --- |
| Карта занятия | [docs/](docs/) | цели, тайминг, границы block/file/object |
| Workbook | [student-workbook.md](docs/student-workbook.md) | упражнения и evidence |
| Internals | [Deep dives](docs/deep-dives/README.md) | три полных разбора HDFS, Ceph и SeaweedFS; object API, placement, отказ и repair |
| Сравнение | [decision-matrix.md](docs/decision-matrix.md) | выбрать систему по workload и ограничениям |
| Практика | [runbooks/](docs/runbooks/) | SeaweedFS S3 API и безопасный путь лабораторной |
| Homework | [homework/](homework/) | архитектура хранилища и эксплуатационный план |
| Стенд | [Flink + Kafka + Iceberg lab](../../labs/flink-iceberg/README.md) | переиспользуемые SeaweedFS и AWS CLI контейнер |

## Что такое SeaweedFS

SeaweedFS — распределённая система хранения, способная предоставить одни данные через S3 API и файловые интерфейсы. **Master** назначает file ID и отслеживает размещение томов; **volume servers** хранят blob-ы; **filer** добавляет иерархические имена и сохраняет метаданные файлов в выбранном metadata store; S3 gateway переводит bucket/key-запросы в операции SeaweedFS. При чтении master помогает найти том, а содержимое клиент получает от volume server напрямую. Это S3-compatible реализация, которую можно эксплуатировать самостоятельно, а не Amazon S3 как управляемый сервис.

## Результат урока

После занятия ученик может:

1. Объяснить, какую задачу решают block, file и object interfaces и почему одинаковый диск под ними не означает одинаковых гарантий.
2. Проследить PUT/GET от HTTP-клиента через gateway, metadata/index и storage node до checksum, replica или erasure-coded shards.
3. Проследить внутренности HDFS, Ceph и SeaweedFS; отличать их цели, namespace, control/data plane, quorum и recovery.
4. Сравнить HDFS, Apache Ozone, Lustre, Ceph, SeaweedFS, RustFS и cloud object stores по API, namespace, placement, consistency, отказам и стоимости владения.
5. Подобрать replication или erasure coding, размер данных, failure domains, cache и metadata architecture под требования workload.
6. Провести небольшую S3-лабораторную, найти объект в SeaweedFS и не принять локальный одноконтейнерный demo за distributed failure test.
7. Защитить выбор on-prem, cloud или hybrid-хранилища с RPO/RTO, capacity headroom, security boundary, benchmark plan и планом восстановления.

## Быстрый вход

```powershell
./labs/flink-iceberg/scripts/up.ps1
docker compose -f labs/flink-iceberg/compose.yaml ps
Invoke-RestMethod http://localhost:19333/cluster/status
```

Из корня репозитория. Состав сервиса и loopback endpoints описаны в [README стенда](../../labs/flink-iceberg/README.md). Для лабораторной можно запустить или использовать уже работающий стенд; не выполняй `down --volumes` — эта команда удаляет данные всех уроков стенда.

## Материалы

- [Цели и план урока](docs/README.md)
- [Workbook ученика](docs/student-workbook.md)
- [План ментора](docs/mentor-guide.md)
- [Матрица выбора](docs/decision-matrix.md)
- [Deep dive: модели, устройство и data paths](docs/deep-dives/distributed-storage-internals.md)
- [Deep dive: продукты, внедрение и операции](docs/deep-dives/products-and-deployment.md)
- [Deep dive: HDFS internals](docs/deep-dives/hdfs-internals.md) · [Ceph internals](docs/deep-dives/ceph-internals.md) · [SeaweedFS internals](docs/deep-dives/seaweedfs-internals.md)
- [Быстрый маршрут](docs/runbooks/simple-path.md) · [глубокий маршрут](docs/runbooks/deep-dive-path.md)
- [Домашнее задание](homework/assignment.md) · [оценивание](homework/rubric.md)

← [Lesson 04: Spark](../lesson-04/) · Далее → [Lesson 05: Iceberg](../lesson-05/)
