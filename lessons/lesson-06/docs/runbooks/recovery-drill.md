# Recovery drill — checkpoint и каталог

## Перед началом

- Используй отдельный SQL Client/job и уникальный test table, чтобы не мешать другим лабораторным.
- Дождись хотя бы одного completed checkpoint и сохрани ID/время/offsets.
- Оставь Flink SQL Client открытым, отдельно открой PowerShell для управления сервисами.

## Сценарий A: потеря TaskManager

```powershell
docker compose -f labs/flink-iceberg/compose.yaml stop flink-taskmanager
docker compose -f labs/flink-iceberg/compose.yaml start flink-taskmanager
```

Зафиксируй failed job/restart, restored checkpoint, прочитанные Kafka offsets, количество table rows и Iceberg snapshots. Для корректного теста topic должен содержать больше событий, чем один checkpoint; сравни записи до/после.

## Сценарий B: каталог недоступен во время write

Останови `lakekeeper` после того, как Flink source уже прочитал records, но перед следующим Iceberg checkpoint commit. Наблюдай sink errors/commit lag; не удаляй объекты. Подними каталог и оцени, повторил ли connector commit, или job требует restart.

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
| SeaweedFS | metadata lookup может работать, чтение/запись content files нарушается |
| Kafka | source не читает/offset state восстановим только пока Kafka retention хранит события |
| Checkpoint volume | job может продолжить обработку до checkpoint/failure; recovery guarantee ухудшается |

Не выключай контейнеры до истечения checkpoint timeout без причины. Lab single-node не доказывает production HA.
