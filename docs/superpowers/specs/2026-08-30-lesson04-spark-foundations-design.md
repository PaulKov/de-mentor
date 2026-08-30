# Design: Урок 04 — Apache Spark Foundations

## Goal

Добавить первый Spark-модуль для начинающего Data Engineer: история Big Data, PySpark DataFrame API, execution model, plan/UI evidence, воспроизводимый Standalone lab, homework и презентации PPTX/Google Slides.

## Decisions

| Решение | Выбор |
| --- | --- |
| Название | Apache Spark Foundations: Big Data и PySpark execution model |
| Аудитория | начинающий Data Engineer с Python/SQL basics |
| Язык API | PySpark only; Scala вне scope |
| Формат | Core 60 + интегрированный Deep 90 |
| Версия | Spark 4.2.0, official multi-arch Python image |
| Lab | Standalone master + 2 workers + client |
| Case | marketplace events → daily country revenue mart |
| Evidence | explicit schema, formatted plan, Spark UI, reconciliation |
| Route | `spark-foundations` → physical lab `spark` |
| Drive | `lessons/Spark/Lesson 04 - Apache Spark foundations and PySpark` |
| Owner | `pavelkov007@gmail.com` |

## Communication job

К концу занятия начинающий Data Engineer должен объяснить и наблюдать, как DataFrame pipeline превращается в distributed execution, потому что производственные Spark-решения принимаются по partitions, plans, shuffle и correctness evidence.

## Narrative

1. Single-process workload перестал укладываться в SLA.
2. GFS/MapReduce/Hadoop объясняют происхождение distributed data processing.
3. Spark расширяет execution model и отделяется от storage.
4. Driver/executors/partitions дают mental model.
5. Lazy transformations образуют plan; action создаёт job.
6. Shuffle создаёт stage boundary и observable cost.
7. PySpark pipeline проходит plan/UI/correctness proof.
8. Инженер принимает решение, включая «Spark здесь не нужен».

## Out of scope

Scala, direct RDD programming, MLlib, GraphX, Structured Streaming implementation, YARN/Kubernetes operations, GC/executor sizing и lakehouse formats.

## Quality gates

- deterministic seed profiles;
- macOS/Windows/Linux self-service docs;
- no host Java/PySpark dependency;
- automated CLI/catalog/release/homework tests;
- all final PPTX slides rendered and visually inspected;
- native Google Slides imported only after PPTX QA;
- Google Slides owner, taxonomy and slide count verified.
