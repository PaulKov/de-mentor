# План ментора: Урок 04 — Apache Spark Foundations

## Главная линия

1. Начать с workload и SLA, а не с определения Spark.
2. Через историю объяснить, почему распределённая система принимает именно такие компромиссы.
3. Построить mental model API: SparkSession → DataFrame, SparkContext → runtime,
   RDD как low-level abstraction, Dataset как JVM-only typed API.
4. Показать scheduler flow: driver/DAGScheduler/TaskScheduler назначают tasks,
   cluster manager только выделяет executors/resources.
5. Показать lazy DataFrame pipeline: до action нет job; без persist каждый
   следующий action повторяет lineage.
6. Найти `Exchange` в plan и shuffle bytes в UI.
7. Закончить correctness evidence, а не «ускорением любой ценой».

## Перед уроком

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py student spark-foundations start --profile lesson04
python3 mentor-lab.py runbook spark-foundations simple
```

Проверь:

- <http://localhost:18080> показывает два workers;
- все smoke markers — `PASS`;
- `labs/spark/data/lesson04/events/` и `customers/` созданы;
- порт `4040` свободен;
- PPTX открывается без font substitution и warning.

## Режиссура Core 60

### 00–05 — Инцидент

Скажи:

> Python-процесс обрабатывал дневные события за 40 минут. Данные выросли, SLA — 20 минут, процесс падает по памяти. Добавлять Spark или сначала менять SQL/формат/железо?

Не принимай «Spark, потому что Big Data». Спроси:

- какой объём;
- какая latency;
- сколько независимого parallel work;
- можно ли решить задачу СУБД или single-node engine;
- какова операционная цена кластера.

### 05–15 — Big Data: история термина и инженерная причина

Обязательные формулировки:

- у Big Data нет одного бесспорного «изобретателя» и фиксированного порога в байтах;
- John Mashey популяризировал термин в контексте InfraStress в 1998 году;
- Doug Laney в 2001 году описал volume, velocity и variety как независимые давления на data management;
- 6V/10V — последующие расширения, а не единый стандарт;
- архитектуру выбирают по workload, SLA, failure model и стоимости.

Попроси ученика для каждого V назвать не пример данных, а сломанное обещание
системы и архитектурный ответ.

### 15–28 — MapReduce → Spark

История объясняет constraints:

- GFS: данные и failures распределены;
- MapReduce: partitioning/scheduling/retry скрыты от пользователя;
- Hadoop: open ecosystem, storage + batch processing;
- Spark: более общий execution DAG для iterative, interactive и streaming workloads;
- DataFrame/SQL: optimizer получает структуру вычисления.

Не превращай блок в перечисление дат. После каждой вехи отвечай: «какое ограничение сняли и какую цену добавили?»

На версии Spark трать не больше трёх минут: `0.x/1.x` дают PySpark,
Streaming, YARN, MLlib и DataFrame; `2.x–4.x` смещают центр тяжести к SQL engine,
AQE, Connect, Data Source V2 и PySpark UX.

### 28–34 — Границы Spark

Обязательные формулировки:

- Spark — compute engine;
- данные живут во внешнем storage;
- cluster manager выдаёт ресурсы;
- Spark application изолирована собственными executors;
- local/standalone/YARN/Kubernetes меняют deployment, не DataFrame semantics.

### 34–42 — Execution model

На доске/слайде собери цепочку:

```text
DataFrame transformations → logical plan → physical plan
action → job → stages separated by shuffle → tasks per partition
action → DAGScheduler → TaskSet → TaskScheduler → executor slots
```

Сначала разведи API:

- `SparkSession` — вход в DataFrame/SQL;
- `SparkContext` — connection/control plane application;
- DataFrame — основной PySpark API с Catalyst;
- RDD — low-level partitioned collection;
- Dataset — typed Scala/Java API, отдельного Dataset API в Python нет.

Prediction questions:

1. Появится ли job после `filtered = events.filter(...)`?
2. Сколько tasks ожидаем при четырёх input partitions?
3. Почему `groupBy` часто разделяет stages?
4. Что означает `Exchange`?
5. Кто выбирает executor slot для task — cluster manager или driver scheduler?

Покажи два actions над одним DataFrame: без persist upstream выполняется снова;
после `cache()` первый action заполняет blocks, второй использует
`InMemoryTableScan`. Подчеркни, что `cache()` сам по себе остаётся lazy.

### 42–52 — Live demo

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_core_pipeline.py \
  -- --hold-seconds 300
```

Порядок показа:

1. Explicit schema в `schemas.py`.
2. Built-in expressions в pipeline.
3. DataFrame до action.
4. `explain("formatted")`.
5. `count`/write как actions.
6. Spark UI SQL → Jobs → Stages.
7. Output Parquet и roundtrip checks.

### 52–58 — Evidence

Попроси ученика сам найти:

- `Exchange`;
- stage boundary;
- shuffle read/write;
- число tasks;
- самый медленный task;
- output row count.

### 58–60 — Exit ticket

Урок пройден, если ученик отвечает:

1. Чем Spark отличается от storage?
2. Что делает driver?
3. Что запускает job?
4. Почему `Exchange` дорогой?
5. Почему быстрый result нельзя принять без reconciliation?

## Добавки Deep 90

- Spark vs MapReduce на четырёх уровнях: бытовая аналогия → principal cost model;
- архитектуры YARN MapReduce job и Spark application DAG;
- durable job boundaries против shuffle/persist boundaries;
- recovery через materialized output против lineage recompute;
- workload matrix: где преимущество Spark велико, мало или оба engine не подходят;
- DAGScheduler → TaskScheduler → SchedulerBackend, locality, slots, retry/speculation;
- parsed/analyzed/optimized/physical plan;
- narrow vs wide dependency;
- built-in expression vs Python UDF boundary;
- shuffle join vs broadcast join;
- BlockManager, `MEMORY_AND_DISK_DESER`, eviction, lineage recompute и `unpersist()`;
- AQE как runtime re-optimization, а не «магический ускоритель»;
- skew и small files как production risks.

На матрице не принимай «Spark быстрее». Требуй назвать доминирующую стоимость:
число проходов, bytes scanned, shuffle, reuse, recovery path, p95 latency и
operator toil. Обязательно проговори, что Spark умеет spill и пишет shuffle на
disk, поэтому сравнение не сводится к «disk против RAM».

Запуск A/B:

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_deep_join.py \
  -- --hold-seconds 300
```

## Частые ошибки ученика

| Ошибка | Intervention |
| --- | --- |
| «Spark хранит данные» | Попросить показать, где физически лежат JSON/Parquet |
| «Transformation выполняется сразу» | Открыть UI до и после action |
| «Partition = файл» | Показать, что один файл может дать несколько partitions и наоборот |
| «Executor = task» | Один executor выполняет множество tasks во времени |
| «Любой join = shuffle» | Сравнить broadcast join |
| «Cache ускоряет всё» | Спросить: reuse, размер, eviction, materialization |
| «collect удобнее» | Рассчитать объём данных, возвращаемых в driver |
| «Python UDF привычнее» | Проверить наличие built-in function и plan visibility |

## Stop conditions

Не переходи к deep, если ученик путает:

- driver и executor;
- transformation и action;
- partition и stage;
- shuffle и обычное чтение;
- Spark и persistent storage.

## Handoff

```bash
python3 mentor-lab.py student spark-foundations homework
python3 mentor-lab.py student spark-foundations test
python3 mentor-lab.py runbook spark-foundations homework
```

Домашка: [assignment.md](../homework/assignment.md).
