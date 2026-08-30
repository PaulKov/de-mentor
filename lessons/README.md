# Lessons

Один урок = одна папка. Внутри всё, что нужно для навигации:

| Папка внутри урока | Что здесь |
| --- | --- |
| `docs/` | теория, workbook, runbooks, deep-dives, `lesson.yaml` |
| `homework/` | задание, план, rubric, templates |
| `artifacts/` | презентации (PPTX), screens, case metrics |
| `submissions/` | куда сдавать (layout + ваши файлы) |

Общие стенды Greenplum и Spark **не** лежат в уроке → [`labs/`](../labs/).

## Оглавление

| Урок | Тема | Стенд | Быстрый вход |
| --- | --- | --- | --- |
| [lesson-01](lesson-01/) | MPP foundations | `greenplum` | [README](lesson-01/README.md) · [homework](lesson-01/homework/) · [deck](lesson-01/artifacts/) |
| [lesson-02](lesson-02/) | Partitioning, stats, incremental loads | `greenplum` | [README](lesson-02/README.md) · [homework](lesson-02/homework/) · [deck](lesson-02/artifacts/) |
| [lesson-03](lesson-03/) | Query tuning / OLAP decomposition | `greenplum-625` | [README](lesson-03/README.md) · [homework](lesson-03/homework/) · [deck](lesson-03/artifacts/) |
| [lesson-04](lesson-04/) | Apache Spark foundations / PySpark | `spark` | [README](lesson-04/README.md) · [homework](lesson-04/homework/) · [deck](lesson-04/artifacts/) |

## Как пользоваться

1. Открой папку урока (`lessons/lesson-0N/`).
2. Прочитай `README.md` урока.
3. Теория → `docs/`, практика дома → `homework/`, сдача → `submissions/`.
4. Презентация и evidence → `artifacts/`.

```bash
# Пример: домашка Урока 04
python3 mentor-lab.py student spark-foundations homework
python3 mentor-lab.py homework spark check \
  --submission lessons/lesson-04/submissions
```

## Карта репозитория (коротко)

```text
lessons/                 ← вы здесь (учебный контент по урокам)
labs/                    ← Docker-стенды (shared)
decks/                   ← исходники слайдов (build input)
src/mentor_lab/          ← CLI / academy engine
```
