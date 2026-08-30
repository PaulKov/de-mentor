# Apache Spark 4.2 PySpark academy lab

Локальный Spark Standalone cluster для Lesson 04. Все runtime dependencies находятся в Docker; на хост не устанавливаются Java, Scala или PySpark.

## Топология

| Service | Назначение | Host interface |
| --- | --- | --- |
| `spark-master` | resource coordination | master `17077`, UI `18080` |
| `spark-worker-1` | executor resources: 1 core / 1 GB | UI `18081` |
| `spark-worker-2` | executor resources: 1 core / 1 GB | UI `18082` |
| `spark-client` | driver / `spark-submit` | application UI `4040` |
| `spark-notebook` | optional Jupyter kernel for VS Code | server `18888`, application UI `14040` |

Image: `apache/spark:4.2.0-python3`, multi-arch `amd64`/`arm64`.

## Быстрый старт

```bash
python3 mentor-lab.py student spark-foundations start --profile lesson04
python3 mentor-lab.py student spark-foundations init
```

Первая команда поднимает cluster и Jupyter, ждёт health checks, генерирует
dataset и запускает smoke application. `--dry-run` печатает план без Docker;
`--no-notebook` исключает только Jupyter. Полный UX-контракт:
[student-cli.md](../../lessons/lesson-04/docs/student-cli.md).

Профили:

| Profile | Events | Customers | Controlled skew |
| --- | ---: | ---: | ---: |
| `tiny` | 25 000 | 1 000 | 20% |
| `lesson04` / `class` | 250 000 | 10 000 | 35% |
| `deep` | 1 000 000 | 50 000 | 55% |

## Applications

Core:

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_core_pipeline.py \
  -- --hold-seconds 300
```

Deep join experiment:

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_deep_join.py \
  -- --hold-seconds 300
```

## Jupyter notebooks в VS Code

Notebook-сервис по умолчанию входит в self-service `start` и использует тот же
Spark cluster. Низкоуровневый Compose-вариант для диагностики:

```bash
docker compose -f labs/spark/docker-compose.yml --profile notebook \
  up -d --build --wait spark-notebook
```

Подключение VS Code, каталог demo и smoke-команды: [notebooks/README.md](notebooks/README.md).

## Data lifecycle

Generated input, event logs and outputs are written under `labs/spark/data/` and ignored by Git.

```bash
python3 mentor-lab.py reset spark
```

`reset` removes Compose containers/network. Bind-mounted data remains until the user removes it manually, preventing accidental loss of homework evidence.

## Troubleshooting

```bash
python3 mentor-lab.py status spark
python3 mentor-lab.py logs spark
python3 mentor-lab.py config spark
```

Common issues:

- port collision: stop another Spark/Jupyter application on `4040` or another lab on `18080`;
- notebook kernel unavailable: start the `notebook` Compose profile and connect VS Code to `http://localhost:18888/?token=de-mentor`;
- image pull: confirm Docker network access and retry `up`;
- no workers: inspect `spark-worker-1/2` logs through Docker Compose;
- UI disappears: run the demo with `--hold-seconds 300`;
- stale data: rerun `seed ... --profile lesson04`; writes use `overwrite`.

## Security boundary

The stand is for local training only. Spark services have no authentication/TLS and must not be exposed to an untrusted network.
