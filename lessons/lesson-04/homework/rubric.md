# Матрица оценки: Lesson 04 Homework

## Hard gates

| Gate | Требование |
| --- | --- |
| Reproducibility | одна documented submit-команда |
| Python only | PySpark DataFrame API, без Scala |
| Explicit schema | нет `inferSchema` в graded input |
| Driver safety | нет full-data `collect()` / `toPandas()` |
| Correctness | counts + revenue + persisted roundtrip |
| Physical evidence | `explain("formatted")` и `Exchange` reasoning |
| Idempotency | повторный запуск не дублирует output |

## Scored rubric — 100 баллов

| Раздел | Баллы | Сильное evidence |
| --- | ---: | --- |
| Input/data-quality contract | 15 | schema, null policy, input counts |
| DataFrame pipeline | 20 | built-ins, ясные transformations, business grain |
| Execution model | 15 | action→job, shuffle→stage, partition→task |
| Plan/UI diagnosis | 20 | operator + Exchange + shuffle metrics + task spread |
| Output design | 10 | Parquet, partitioning, file-count consideration |
| Correctness | 15 | counts, totals, persisted roundtrip |
| Production decision | 5 | risk, monitoring, rollback/next experiment |

## Уровни

| Баллы | Вердикт |
| ---: | --- |
| 90–100 | Strong junior / ready for Spark performance module |
| 75–89 | Pass; minor evidence gaps |
| 60–74 | Pipeline работает, но недостаточно доказан |
| <60 | Повторить mental model и evidence workflow |

Принято: все hard gates + минимум 75 баллов.
