# Recovery drill — checkpoint и каталог

## Перед началом

- Создай отдельный topic и целевую таблицу для прогона. В копиях `04-kafka-source.sql`, `05-stream-to-iceberg.sql` и `06-query-iceberg.sql` укажи имена этого прогона. В producer также укажи тот же topic. Новый `group.id` сам по себе не изолирует данные: при `earliest-offset` job читает всю доступную историю topic.
- Опубликуй первую порцию событий. Дождись completed checkpoint и опубликованного Iceberg snapshot. Запиши Job ID, checkpoint ID, snapshot ID, Kafka topic/partition и доступные метрики offsets.
- Оставь Flink SQL Client открытым, отдельно открой PowerShell для управления сервисами.

## Сценарий A: потеря TaskManager

```powershell
docker compose -f labs/flink-iceberg/compose.yaml stop flink-taskmanager
```

Отправь вторую порцию с известными ID во время простоя TaskManager. Добавь событие с более поздним event time, если надо закрыть последнее окно. Верни TaskManager:

```powershell
docker compose -f labs/flink-iceberg/compose.yaml start flink-taskmanager
```

Проследи восстановление того же Job ID. Сверь REST `/jobs/<job-id>/checkpoints` (в том числе `latest.restored`), offsets в source metrics и Iceberg snapshot. Kafka group offsets показывают прогресс брокера, восстановление Flink опирается на split offsets в checkpoint. Сравни итоговые ключи, суммы и число строк с контрольным прогоном без сбоя. [Kafka source recovery](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/datastream/kafka/) · [Task failure recovery](https://nightlies.apache.org/flink/flink-docs-release-2.2/docs/ops/state/task_failure_recovery/)

## Сценарий B: каталог недоступен во время write

Останови `lakekeeper`, когда job уже работает, затем отправь новые события. По возможности дождись закрытия окна с помощью события с более поздним event time. Наблюдай sink errors и задержку commit, затем подними каталог. Этот сценарий проверяет отказ каталога во время работы. Для воспроизводимого отказа строго после публикации, но до HTTP ответа, нужен fault proxy или управляемая точка сбоя в тестовом каталоге.

```powershell
docker compose -f labs/flink-iceberg/compose.yaml stop lakekeeper
docker compose -f labs/flink-iceberg/compose.yaml start lakekeeper
```

Результат зависит от точной точки сбоя и retry policy. Запиши факты из logs, Checkpoints UI и `$snapshots`; не делай вывод только по зеленому статусу контейнера.

## Сценарий C: сравнить storage и catalog failure

Подготовь таблицу при здоровых сервисах. Затем останови отдельно SeaweedFS или Lakekeeper и сравни:

| Компонент недоступен | Основной эффект |
|---|---|
| Lakekeeper/Postgres | имя таблицы/current metadata commit недоступны; data objects могут оставаться |
| SeaweedFS | JDBC/HMS указатель может читаться, но REST-загрузка таблицы также может упасть при попытке прочитать metadata JSON в S3. Сохранённые метаданные читателя не делают data files доступными |
| Kafka | Checkpoint хранит offset. Для replay сами сообщения должны оставаться доступными в Kafka либо в архиве |
| Checkpoint volume | job может продолжить обработку до checkpoint/failure; recovery guarantee ухудшается |

Не выключай контейнеры до истечения checkpoint timeout без причины. Lab single-node не доказывает production HA.
