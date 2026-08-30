# Deep-Dive Path: Lesson 04 — 90 минут

Deep включает Core и добавляет:

- четыре уровня объяснения Spark vs MapReduce;
- side-by-side architecture и materialization pipeline;
- fault-tolerance и workload comparison matrices;
- DAGScheduler / TaskScheduler / SchedulerBackend responsibility map;
- четыре plan layers;
- narrow/wide transformations;
- Python/JVM boundary;
- shuffle anatomy;
- BlockManager, storage levels, eviction и lineage recompute;
- sort-merge vs broadcast join;
- AQE и skew как observable runtime decisions;
- small-files/partition output contract.

| Время | Слайды | Фокус |
| --- | --- | --- |
| 00–15 | 1–8 | Big Data history, 3V и расширения |
| 15–28 | 9–16 | MapReduce → Spark, версии и причины adoption |
| 28–42 | 17–29 | API/context, scheduler flow, lazy evaluation и cache |
| 42–58 | 30–39 | core pipeline, plan, UI и exit |
| 58–73 | 40–49 | Spark vs MapReduce + scheduler internals |
| 73–82 | 50–54 | Catalyst, narrow/wide, Python/JVM, shuffle и cache internals |
| 82–88 | 55–58 | join A/B, AQE и skew |
| 88–90 | 59 | production checklist |

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_deep_join.py \
  -- --hold-seconds 300
```

Deep acceptance: ученик показывает не только другой operator name, но и
сравнение shuffle metrics, условие безопасности broadcast и объясняет, почему
one-pass I/O-bound job может почти не получить преимущества от Spark DAG.
