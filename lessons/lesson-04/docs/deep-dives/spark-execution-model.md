# Deep Dive: Spark execution model

## Application boundary

Spark application состоит из driver и выделенных ей executors. Driver создаёт `SparkContext`/`SparkSession`, строит execution plan, делит работу на stages/tasks и отслеживает выполнение. Executors исполняют tasks и хранят промежуточные/cached blocks.

Cluster manager — отдельная ответственность: выдача ресурсов application. В stand используется Spark Standalone; те же DataFrame transformations могут запускаться через YARN или Kubernetes.

## Job → stages → tasks

- action создаёт job;
- shuffle dependency создаёт границу stages;
- каждый stage содержит tasks;
- один task обрабатывает одну partition для данного stage;
- executor — долгоживущий process, task — единица работы.

## Lazy evaluation

DataFrame transformation добавляет узел в план. До action Spark может:

- push filters ближе к scan;
- удалить ненужные columns;
- переставить/выбрать физические operators;
- объединить выражения;
- подготовить adaptive execution.

## Failure semantics

Spark повторяет потерянные tasks и пересчитывает lineage. Это не означает, что любой внешний side effect exactly-once. Data Engineer отдельно проектирует idempotent output, commit protocol и validation.

Источник: [Spark cluster overview](https://spark.apache.org/docs/4.2.0/cluster-overview.html).
