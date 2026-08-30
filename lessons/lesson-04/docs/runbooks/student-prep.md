# Подготовка ученика к Lesson 04

## Требования

- Docker Desktop или Docker Engine + Compose v2;
- Git;
- Python 3.9+ только для `mentor-lab.py`;
- 4 CPU threads и 6 GB свободной RAM рекомендуются;
- свободные порты `4040`, `17077`, `18080`, `18081`, `18082`.

Java, Scala, локальный Spark и Jupyter устанавливать не нужно.

## macOS/Linux

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py up spark
python3 mentor-lab.py seed spark --profile tiny
python3 mentor-lab.py check spark
```

## Windows PowerShell

```powershell
py mentor-lab.py doctor --full
py mentor-lab.py up spark
py mentor-lab.py seed spark --profile tiny
py mentor-lab.py check spark
```

## Если не стартует

```bash
python3 mentor-lab.py status spark
python3 mentor-lab.py logs spark
python3 mentor-lab.py config spark
```

Не делай `reset`, если хочешь сохранить локально сгенерированные data artifacts. Dataset лежит в `labs/spark/data/` и не коммитится.

## Что принести

- ответ: «когда Spark не нужен»;
- знакомство с Python functions/classes;
- базовые SQL `SELECT`, `WHERE`, `JOIN`, `GROUP BY`;
- готовность читать plan, а не только код.
