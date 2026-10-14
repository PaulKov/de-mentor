# Student prep — Lesson 05

1. Открой `labs/flink-iceberg/README.md`.
2. Запусти Docker Desktop в Linux container mode; оставь около 5 GB памяти Docker.
3. Из корня репозитория запусти `./labs/flink-iceberg/scripts/up.ps1`.
4. Дождись health для Postgres, SeaweedFS, Lakekeeper, Nessie, Kafka и Flink JobManager.
5. Открой `http://localhost:18081`, `http://localhost:18181/ui/`, `http://localhost:18888`, `http://localhost:19120/api/v2/config`.
6. Запусти `./labs/flink-iceberg/scripts/sql-client.ps1`; введи `SHOW CATALOGS;`.
7. При сбое сохрани `docker compose -f labs/flink-iceberg/compose.yaml ps` и service logs до перезапуска.

Не запускай `down --volumes`: named volumes сохраняют данные лабораторной.
