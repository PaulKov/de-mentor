# Deep-Dive Path: Lesson 04 — 90 минут

Deep включает Core и добавляет:

- четыре уровня объяснения Spark vs MapReduce;
- side-by-side architecture и materialization pipeline;
- fault-tolerance и workload comparison matrices;
- четыре plan layers;
- narrow/wide transformations;
- Python/JVM boundary;
- shuffle anatomy;
- sort-merge vs broadcast join;
- AQE и skew как observable runtime decisions;
- small-files/partition output contract.

| Время | Слайды | Фокус |
| --- | --- | --- |
| 00–15 | 1–8 | Big Data history, 3V и расширения |
| 15–28 | 9–16 | MapReduce → Spark, версии и причины adoption |
| 28–42 | 17–25 | application architecture + execution model |
| 42–58 | 26–35 | core pipeline, plan, UI и exit |
| 58–73 | 36–44 | Spark vs MapReduce: layperson → principal |
| 73–80 | 45–48 | Catalyst, narrow/wide, Python/JVM, shuffle |
| 80–87 | 49–52 | join A/B, AQE и skew |
| 87–90 | 53 | production checklist |

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_deep_join.py \
  -- --hold-seconds 300
```

Deep acceptance: ученик показывает не только другой operator name, но и
сравнение shuffle metrics, условие безопасности broadcast и объясняет, почему
one-pass I/O-bound job может почти не получить преимущества от Spark DAG.
