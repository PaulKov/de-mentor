# Подготовка ученика к Lesson 04

## Требования

- Docker Desktop или Docker Engine + Compose v2;
- Git;
- Python 3.9+ только для `mentor-lab.py`;
- 4 CPU threads и 6 GB свободной RAM рекомендуются;
- свободные порты `4040`, `14040`, `17077`, `18080`, `18081`, `18082`, `18888`.

Java, Scala, локальный Spark и Jupyter устанавливать не нужно.

## macOS/Linux

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py student spark-foundations start --profile tiny
python3 mentor-lab.py student spark-foundations init
```

## Windows PowerShell

```powershell
py mentor-lab.py doctor --full
py mentor-lab.py student spark-foundations start --profile tiny
py mentor-lab.py student spark-foundations init
```

Команда `start` по умолчанию включает Jupyter. Для просмотра без запуска:

```bash
python3 mentor-lab.py student spark-foundations start --profile tiny --dry-run
```

## Если не стартует

```bash
python3 mentor-lab.py status spark
python3 mentor-lab.py logs spark
python3 mentor-lab.py config spark
```

Не делай `reset`, если хочешь сохранить локально сгенерированные data artifacts. Dataset лежит в `labs/spark/data/` и не коммитится.

Полный контракт команд: [student-cli.md](../student-cli.md).

## Что принести

- ответ: «когда Spark не нужен»;
- знакомство с Python functions/classes;
- базовые SQL `SELECT`, `WHERE`, `JOIN`, `GROUP BY`;
- готовность читать plan, а не только код.
