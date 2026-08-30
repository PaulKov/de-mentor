# Lesson 04 — Apache Spark foundations / PySpark execution model

Стенд: **`spark`** · Spark: **4.2.0** · API: **PySpark DataFrame** · Scala: **вне scope**

| Раздел | Путь | Зачем |
| --- | --- | --- |
| Docs | [docs/](docs/) | теория, workbook, runbooks, deep-dives |
| Homework | [homework/](homework/) | assignment, plan, rubric, evidence template |
| Artifacts | [artifacts/](artifacts/) | полный и core PPTX |
| Submissions | [submissions/](submissions/) | `pipeline.py` + `evidence.md` |

[Google Slides — полная версия, 42 слайда](https://docs.google.com/presentation/d/1U_u3cwqdCzz2oRoa_w5BT7btbLqUlBSou3rJe2YXni0/edit?usp=sharing)

## Быстрый старт

```bash
python3 mentor-lab.py up spark
python3 mentor-lab.py seed spark --profile lesson04
python3 mentor-lab.py check spark
python3 mentor-lab.py runbook spark-foundations simple
```

Запуск core-пайплайна:

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_core_pipeline.py \
  -- --hold-seconds 300
```

Пока приложение удерживается, открой:

- Spark application UI: <http://localhost:4040>;
- Spark master UI: <http://localhost:18080>.

## Ключевые файлы

- [docs/README.md](docs/README.md)
- [docs/mentor-guide.md](docs/mentor-guide.md)
- [docs/student-workbook.md](docs/student-workbook.md)
- [docs/runbooks/live-practice.md](docs/runbooks/live-practice.md)
- [homework/assignment.md](homework/assignment.md)
- [homework/rubric.md](homework/rubric.md)
- [artifacts/apache-spark-foundations-theory.pptx](artifacts/apache-spark-foundations-theory.pptx)

← [Все уроки](../README.md)
