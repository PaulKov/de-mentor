# Simple path — 90 минут

1. Запусти Docker Stand по [student prep](student-prep.md), проверь UI Flink и `docker compose ps`.
2. Создай topic: `./labs/flink-iceberg/scripts/create-topic.ps1`.
3. Запусти `./labs/flink-iceberg/scripts/sql-client.ps1`.
4. Выполни `04-kafka-source.sql`, затем `05-stream-to-iceberg.sql`.
5. Отправь sample через `./labs/flink-iceberg/scripts/publish-orders.ps1`.
6. В Flink UI дождись checkpoint completed и запиши Job ID/checkpoint ID.
7. В новом SQL Client выполни `01-catalogs.sql` и `06-query-iceberg.sql`.
8. Сравни records, event time, aggregated windows и Iceberg snapshot summary.
9. Ответь, почему успешный checkpoint ещё не доказывает, что table commit завершился.
10. Сохрани [evidence](../../homework/templates/evidence.md), останови стенд без `--volumes`.
