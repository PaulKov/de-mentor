# Self-service CLI ученика — Lesson 04

CLI запускается из корня репозитория и не требует локальной установки Java,
Spark, PySpark или Jupyter. Docker остаётся единственной runtime-зависимостью.

## Полный путь: start → init → test

```bash
python3 mentor-lab.py student spark-foundations start --profile lesson04
python3 mentor-lab.py student spark-foundations init
# измени lessons/lesson-04/submissions/pipeline.py и evidence.md
python3 mentor-lab.py student spark-foundations test
```

`start` выполняет одну воспроизводимую транзакцию готовности:

1. запускает Spark Standalone cluster и профиль `spark-notebook`;
2. ожидает Docker health checks;
3. генерирует детерминированный dataset выбранного профиля;
4. запускает live PySpark smoke application;
5. печатает URL Spark Master и JupyterLab.

Перед первым реальным запуском план можно проверить без Docker-вызовов:

```bash
python3 mentor-lab.py student spark-foundations start --profile tiny --dry-run
```

## Профили данных

| Profile | Назначение | Events | Controlled skew |
| --- | --- | ---: | ---: |
| `tiny` | проверка ноутбука | 25 000 | 20% |
| `lesson04` / `class` | лекция и домашка | 250 000 | 35% |
| `deep` | skew/join experiment | 1 000 000 | 55% |

Если notebook не нужен, добавь `--no-notebook`. Spark master, workers, client,
seed и smoke всё равно будут запущены.

## Безопасный scaffold

```bash
python3 mentor-lab.py student spark-foundations init
```

Команда создаёт только два файла:

- `lessons/lesson-04/submissions/pipeline.py`;
- `lessons/lesson-04/submissions/evidence.md`.

Существующие файлы не перезаписываются. `--force` разрешён только для
осознанного возврата к исходному scaffold. Для отдельного эксперимента укажи
`--output /path/to/submission`.

## Проверка домашки

```bash
python3 mentor-lab.py student spark-foundations test
```

Проверка состоит из двух независимых gates:

1. live smoke подтверждает доступность master, workers, DataFrame execution,
   shuffle plan и Parquet round-trip;
2. механический reviewer проверяет `pipeline.py` и `evidence.md`: explicit input
   contract, DataFrame transformations, idempotent output, plan/runtime evidence,
   correctness и production decision.

Для CI или проверки текста без запущенного Docker:

```bash
python3 mentor-lab.py student spark-foundations test --skip-live
```

`collect()`, `toPandas()` на полном dataset и Python UDF являются hard gates.
Успешный CLI review не заменяет mentor review Spark UI screenshots и
обоснованности production-решения.

## Интерфейсы и диагностика

- Spark master: <http://localhost:18080>;
- JupyterLab: <http://localhost:18888/?token=de-mentor>;
- notebook Spark UI: <http://localhost:14040>;
- CLI application UI: <http://localhost:4040> во время job.

```bash
python3 mentor-lab.py status spark
python3 mentor-lab.py logs spark
python3 mentor-lab.py config spark
```

`reset` удаляет containers и Compose volumes, но bind-mounted evidence в
`labs/spark/data/` и submission-файлы остаются на хосте.
