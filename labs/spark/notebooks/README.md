# Lesson 04: PySpark notebooks in VS Code

Три notebook-а выполняются в отдельном Docker-контейнере с Apache Spark `4.2.0`. Kernel подключён к тому же standalone cluster, что и CLI demo; локальные Java, PySpark и Jupyter не нужны.

## Первый запуск

1. В VS Code открой Command Palette: `Cmd+Shift+P`.
2. Выполни `Tasks: Run Task` → `Jupyter · Start server`.
3. Открой любой `.ipynb` из этой директории и нажми `Select Kernel`.
4. Выбери `Existing Jupyter Server` → `Enter the URL of the running Jupyter server`.
5. Вставь `http://localhost:18888/?token=de-mentor` и выбери `Python 3 (ipykernel)`.

VS Code запомнит server для следующих запусков. Код выполняется внутри `spark-notebook`, а не локально на macOS.

Справка: [VS Code — Connect to a remote Jupyter server](https://code.visualstudio.com/docs/datascience/jupyter-notebooks#_connect-to-a-remote-jupyter-server).

## Демо

| Notebook | Фокус | Проверяемое доказательство |
| --- | --- | --- |
| `01_execution_model.ipynb` | lazy, partitions, scheduler и cache reuse | `Exchange`, task mapping, `InMemoryTableScan` |
| `02_shuffle_and_joins.ipynb` | shuffle join против broadcast | `SortMergeJoin` vs `BroadcastHashJoin` |
| `03_quality_and_parquet.ipynb` | data quality и idempotent output | counts/revenue Parquet round-trip |

## Интерфейсы

- Jupyter server: <http://localhost:18888/?token=de-mentor>;
- Spark application UI notebook kernel: <http://localhost:14040>;
- Spark master: <http://localhost:18080>.

Порт `14040` отделён от CLI live-demo на `4040`, поэтому notebook и основной показ не конфликтуют на host. Не запускай два Spark kernel-а одновременно: внутри notebook-контейнера один application UI port.

## Автоматическая проверка

`Tasks: Run Task` → `Jupyter · Smoke all demos` последовательно исполняет все notebooks через `nbconvert`. Выполненные копии создаются во временной директории и не меняют исходники в Git.

CLI-эквивалент:

```bash
docker compose -f labs/spark/docker-compose.yml --profile notebook \
  up -d --build --wait spark-notebook

docker compose -f labs/spark/docker-compose.yml --profile notebook \
  exec -T spark-notebook \
  python3 /workspace/labs/spark/jupyter/run_smoke.py
```

Остановка только notebook-сервера: `Tasks: Run Task` → `Jupyter · Stop server`.

## Безопасность

Jupyter публикуется только на loopback `127.0.0.1` и требует token. Фиксированный token допустим только для локального учебного стенда; не публикуй порт `18888` наружу и не используй эту конфигурацию в production.
