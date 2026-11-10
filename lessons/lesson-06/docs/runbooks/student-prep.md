# Student prep

- Docker запущен в режиме Linux containers и доступен Docker Compose v2.
- Docker Compose v2 доступен: `docker compose version`.
- Для стенда доступны около 6 GB RAM и 2 CPU.
- Из корня `de-mentor` запусти `./labs/flink-iceberg/scripts/up.ps1` и проверь `docker compose -f labs/flink-iceberg/compose.yaml ps`.
- UI: Flink `http://localhost:18081`, Lakekeeper `http://localhost:18181/ui/`, SeaweedFS `http://localhost:18888`, Nessie API `http://localhost:19120`.
- Один раз создай Kafka topic через `./labs/flink-iceberg/scripts/create-topic.ps1`.
- Убедись, что другие проекты не заняли host ports `18081`, `19000–19001`, `19092`, `18181`, `19120`, `15432`.
- Не сбрасывай volumes, пока не сохранил свою таблицу/evidence.
