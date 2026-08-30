# Deep Dive: Partitions, shuffle and AQE

## Partition

Partition — логическая часть distributed dataset, обрабатываемая одним task в пределах stage. Это не синоним файла:

- один большой файл может быть прочитан несколькими partitions;
- несколько маленьких файлов могут быть объединены;
- `repartition` создаёт новую partitioning через shuffle;
- `coalesce` обычно уменьшает partitions без полного shuffle, но может ухудшить parallelism.

## Shuffle

Shuffle нужен, когда одинаковые keys должны оказаться вместе для следующего operator:

- `groupBy`;
- `distinct`;
- sort;
- join без совместимого distribution/broadcast;
- `repartition`.

Evidence:

1. `Exchange` в physical plan;
2. новая stage boundary;
3. shuffle write/read bytes;
4. task duration distribution;
5. spill, если execution memory недостаточно.

## Broadcast

Broadcast join копирует маленькую build side на executors и может убрать shuffle большой стороны. Безопасность зависит от фактического размера после filters и memory каждого executor.

## AQE

Adaptive Query Execution может во время исполнения:

- объединять shuffle partitions;
- менять sort-merge join на broadcast/shuffled hash;
- разделять skewed partitions.

AQE не отменяет необходимость читать final plan и runtime metrics.

Источник: [Spark SQL performance tuning](https://spark.apache.org/docs/4.2.0/sql-performance-tuning.html).
