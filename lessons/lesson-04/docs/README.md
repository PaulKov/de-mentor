# Урок 04: Apache Spark Foundations — Big Data и PySpark execution model

## Цель урока

Дать начинающему Data Engineer рабочую модель Spark: почему появился распределённый compute, как DataFrame превращается в job/stages/tasks и как доказать стоимость shuffle через plan и UI.

Главный тезис:

> Spark — не «быстрый Python» и не хранилище. Это распределённый движок исполнения; качество решения доказывается plan, runtime metrics и reconciliation.

## Результаты

После урока ученик умеет:

- провести линию GFS → MapReduce → Hadoop → Spark;
- объяснить, когда Spark нужен и когда создаёт лишнюю сложность;
- различить application, driver, cluster manager, executor, partition, job, stage и task;
- написать pipeline на PySpark DataFrame API без Scala;
- объяснить lazy evaluation и transformation/action;
- найти `Exchange` в `explain("formatted")`;
- связать `Exchange` со shuffle metrics в Spark UI;
- записать Parquet mart и проверить counts/revenue roundtrip;
- распознать `collect()`, `toPandas()`, Python UDF, blind cache и small files как риски.

## Маршруты

```bash
python3 mentor-lab.py runbook spark-foundations prep
python3 mentor-lab.py runbook spark-foundations simple
python3 mentor-lab.py runbook spark-foundations deep
python3 mentor-lab.py runbook spark-foundations homework
```

| Маршрут | Время | Фокус |
| --- | ---: | --- |
| Core | 60 мин | история → architecture → lazy execution → pipeline → plan/UI |
| Deep | 90 мин | Core + plan layers, Python/JVM boundary, shuffle/broadcast, AQE |
| Homework | 90–120 мин | собственный pipeline + evidence pack |

## Стенд

Стенд полностью контейнеризирован:

- `spark-master`;
- `spark-worker-1`;
- `spark-worker-2`;
- `spark-client` для `spark-submit`;
- официальный multi-arch `apache/spark:4.2.0-python3`.

На хосте не нужны Java или PySpark. Нужны Docker Desktop/Engine и Python для `mentor-lab.py`.

## Практический кейс

Marketplace events + customer dimension → дневная выручка по стране:

```text
JSON events
  → explicit schema
  → valid purchases
  → customer join
  → groupBy(event_date, country)
  → Parquet partitioned by event_date
  → reconciliation
```

Данные детерминированы и содержат:

- controlled skew;
- null amount как data-quality defect;
- fact-like event stream;
- small customer dimension для join experiment.

## Версионный контракт

- Apache Spark `4.2.0`;
- Python API only;
- Spark 4.2 требует Python 3.10+ и Java 17+, но зависимости находятся внутри container image;
- RDD обсуждаем только как историческую/внутреннюю абстракцию;
- основной public API — `pyspark.sql.DataFrame`.

## Материалы

- [План ментора](mentor-guide.md)
- [Workbook ученика](student-workbook.md)
- [Cheat sheet](cheat-sheet.md)
- [Core 60](runbooks/simple-path.md)
- [Deep 90](runbooks/deep-dive-path.md)
- [Facilitator skip-map](runbooks/facilitator-skip-map.md)
- [Homework](../homework/assignment.md)
- [Rubric](../homework/rubric.md)
- [Публикация в Google Slides](google-slides-publish.md)

## Официальные источники

- [Apache Spark history](https://spark.apache.org/history)
- [Cluster mode overview](https://spark.apache.org/docs/4.2.0/cluster-overview.html)
- [PySpark DataFrame quickstart](https://spark.apache.org/docs/4.2.0/api/python/getting_started/quickstart_df.html)
- [Spark SQL performance tuning](https://spark.apache.org/docs/4.2.0/sql-performance-tuning.html)
- [Spark Web UI](https://spark.apache.org/docs/4.2.0/web-ui.html)
- [GFS paper](https://research.google/pubs/the-google-file-system/)
- [MapReduce paper](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)

## Вне scope

- Scala API;
- прямое программирование на RDD;
- MLlib и GraphX;
- Structured Streaming implementation;
- YARN/Kubernetes deployment;
- executor sizing, GC и production capacity planning;
- lakehouse table formats.

Эти темы нельзя «втиснуть» в beginner 60/90 без разрушения mental model.
