# Student prep — Lesson 04b

## Требования

- Docker Desktop в режиме Linux containers и Docker Compose v2;
- 5 GB свободной памяти Docker для всего Flink/Iceberg стенда;
- Git clone репозитория и PowerShell в Windows;
- базовое понимание HTTP, files/directories и распределённого процесса.

Java, Hadoop, AWS CLI, Python packages и cloud account на хосте не нужны. AWS CLI контейнер уже входит в Compose и использует demo credentials только внутри loopback lab network.

## Запуск/проверка

Из корня репозитория:

```powershell
./labs/flink-iceberg/scripts/up.ps1
docker compose -f labs/flink-iceberg/compose.yaml ps
Invoke-RestMethod http://localhost:19333/cluster/status
```

Открыть filer UI: <http://localhost:18888>. SeaweedFS S3 endpoint для приложений внутри Compose: `http://seaweedfs:8333`; endpoint с хоста: `http://localhost:19000`. Опубликованные endpoints привязаны к localhost.

## Быстрая S3 проверка

```powershell
docker compose -f labs/flink-iceberg/compose.yaml run --rm --no-deps --entrypoint aws seaweedfs-init `
  --endpoint-url http://seaweedfs:8333 s3api list-buckets
```

Если stack уже работает, `up.ps1` повторно использовать безопасно, но не запускай `down --volumes`. Остановка/удаление текущих лабораторных объектов затронет также данные Iceberg, Kafka и checkpoints.

## Диагностика

```powershell
docker compose -f labs/flink-iceberg/compose.yaml logs seaweedfs
docker compose -f labs/flink-iceberg/compose.yaml ps seaweedfs seaweedfs-init
Invoke-RestMethod http://localhost:19333/cluster/status
```

Если host endpoint не отвечает, проверь Docker Desktop, service health и занятость портов `19000`, `19333`, `18888`. Не открывай этот учебный Compose в LAN и не используй demo credentials в другом окружении.

Читайте [lab README](../../../../labs/flink-iceberg/README.md) про адреса, сервисы, данные и удаление.
