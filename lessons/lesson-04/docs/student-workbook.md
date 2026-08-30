# Workbook ученика: Lesson 04

## Перед стартом

```bash
python3 mentor-lab.py up spark
python3 mentor-lab.py seed spark --profile lesson04
python3 mentor-lab.py check spark
```

Открой:

- <http://localhost:18080> — cluster/master UI;
- <http://localhost:4040> — application UI только пока работает PySpark job.

## Упражнение 1 — Нужен ли здесь Spark?

Для каждого случая запиши `Spark / не Spark / недостаточно данных` и причину:

1. 2 GB CSV раз в сутки, 32 GB RAM, SLA 2 часа.
2. 10 TB Parquet, join нескольких facts, SLA 25 минут.
3. API возвращает одну запись по ключу за 20 ms.
4. 200 GB событий, несколько независимых daily aggregations.

Evidence: решение должно ссылаться на workload, SLA, parallelism и операционную цену.

## Упражнение 2 — Карта application

Заполни:

| Компонент | Ответственность | Где видим |
| --- | --- | --- |
| Driver |  |  |
| Cluster manager |  |  |
| Executor |  |  |
| Partition |  |  |
| Task |  |  |

Проверка: executor и task не должны быть определены как одно и то же.

## Упражнение 3 — Предскажи execution

```python
events = spark.read.schema(EVENT_SCHEMA).json(path)
purchases = events.filter("event_type = 'purchase'")
daily = purchases.groupBy("customer_id").count()
daily.write.mode("overwrite").parquet(output)
```

До запуска ответь:

1. Какие строки — transformations?
2. Где action?
3. Где вероятен shuffle?
4. Что будет task unit?

## Упражнение 4 — Запусти core pipeline

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_core_pipeline.py \
  -- --hold-seconds 300
```

Зафиксируй:

```text
Input events:
Valid purchases:
Output rows:
Revenue total:
Roundtrip PASS/FAIL:
```

## Упражнение 5 — Прочитай plan

В `explain("formatted")` найди:

- scans;
- filters;
- join operator;
- aggregate;
- `Exchange`;
- adaptive plan marker.

Заполни:

| Наблюдение | Физический смысл | Риск/вывод |
| --- | --- | --- |
| `Exchange` |  |  |
| join type |  |  |
| input partitions |  |  |

## Упражнение 6 — Свяжи plan и UI

В UI открой SQL query, затем associated job/stage.

```text
SQL execution id:
Job id:
Stage ids:
Tasks per stage:
Shuffle read:
Shuffle write:
Max/min task duration:
```

Финальный вопрос: какое утверждение ты теперь можешь доказать, которого не мог доказать по коду?

## Deep: shuffle vs broadcast

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_deep_join.py \
  -- --hold-seconds 300
```

| Case | Join operator | Exchange | Shuffle metrics | Safety condition |
| --- | --- | --- | --- | --- |
| Shuffle join |  |  |  |  |
| Broadcast join |  |  |  |  |

Broadcast принимается только при доказанном размере build side после фильтров.

## Exit ticket

- [ ] Я могу объяснить driver/executor без слова «сервер» как единственного определения.
- [ ] Я знаю, что запускает job.
- [ ] Я нахожу `Exchange`.
- [ ] Я связываю partition с task.
- [ ] Я не делаю `collect()` на полном dataset.
- [ ] Я проверяю output counts и суммы.
- [ ] Я могу сказать «Spark здесь не нужен» и обосновать.

## Домашка

[PySpark ETL Evidence Pack](../homework/assignment.md).
