# План ментора: Урок 04 — Apache Spark Foundations

## Главная линия

1. Начать с workload и SLA, а не с определения Spark.
2. Через историю объяснить, почему распределённая система принимает именно такие компромиссы.
3. Построить mental model: driver планирует, executors выполняют tasks над partitions.
4. Показать lazy DataFrame pipeline: до action нет job.
5. Найти `Exchange` в plan и shuffle bytes в UI.
6. Закончить correctness evidence, а не «ускорением любой ценой».

## Перед уроком

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py up spark
python3 mentor-lab.py seed spark --profile lesson04
python3 mentor-lab.py check spark
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

### 05–13 — История

История объясняет constraints:

- GFS: данные и failures распределены;
- MapReduce: partitioning/scheduling/retry скрыты от пользователя;
- Hadoop: open ecosystem, storage + batch processing;
- Spark: более общий execution DAG для iterative, interactive и streaming workloads;
- DataFrame/SQL: optimizer получает структуру вычисления.

Не превращай блок в перечисление дат. После каждой вехи отвечай: «какое ограничение сняли и какую цену добавили?»

### 13–23 — Границы Spark

Обязательные формулировки:

- Spark — compute engine;
- данные живут во внешнем storage;
- cluster manager выдаёт ресурсы;
- Spark application изолирована собственными executors;
- local/standalone/YARN/Kubernetes меняют deployment, не DataFrame semantics.

### 23–34 — Execution model

На доске/слайде собери цепочку:

```text
DataFrame transformations → logical plan → physical plan
action → job → stages separated by shuffle → tasks per partition
```

Prediction questions:

1. Появится ли job после `filtered = events.filter(...)`?
2. Сколько tasks ожидаем при четырёх input partitions?
3. Почему `groupBy` часто разделяет stages?
4. Что означает `Exchange`?

### 34–49 — Live demo

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

### 49–56 — Evidence

Попроси ученика сам найти:

- `Exchange`;
- stage boundary;
- shuffle read/write;
- число tasks;
- самый медленный task;
- output row count.

### 56–60 — Exit ticket

Урок пройден, если ученик отвечает:

1. Чем Spark отличается от storage?
2. Что делает driver?
3. Что запускает job?
4. Почему `Exchange` дорогой?
5. Почему быстрый result нельзя принять без reconciliation?

## Добавки Deep 90

- parsed/analyzed/optimized/physical plan;
- narrow vs wide dependency;
- built-in expression vs Python UDF boundary;
- shuffle join vs broadcast join;
- AQE как runtime re-optimization, а не «магический ускоритель»;
- skew и small files как production risks.

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
python3 mentor-lab.py runbook spark-foundations homework
```

Домашка: [assignment.md](../homework/assignment.md).
