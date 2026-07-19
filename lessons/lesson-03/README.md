# Lesson 03 — Query tuning / OLAP decomposition

Стенд: **`greenplum-625`** · БД: **`mentor`** · схема: **`lesson03`**

| Раздел | Путь | Зачем |
| --- | --- | --- |
| Docs | [docs/](docs/) | теория, workbook, runbooks, deep-dives |
| Homework | [homework/](homework/) | Senior core + Principal extension |
| Artifacts | [artifacts/](artifacts/) | PPTX, screens, case metrics |
| Submissions | [submissions/](submissions/) | pack: rewrite / reconcile / evidence |

## Старт

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py student greenplum-query-tuning homework
python3 mentor-lab.py homework greenplum-625 check \
  --submission lessons/lesson-03/submissions
```

## Ключевые файлы

- [docs/README.md](docs/README.md)
- [homework/assignment.md](homework/assignment.md)
- [homework/plan.md](homework/plan.md)
- [homework/rubric.md](homework/rubric.md)
- [homework/templates/](homework/templates/) — evidence + reconcile
- [artifacts/greenplum-query-tuning-theory.pptx](artifacts/greenplum-query-tuning-theory.pptx)

← [Все уроки](../README.md)
