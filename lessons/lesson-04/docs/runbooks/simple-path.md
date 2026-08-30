# Simple Path: Lesson 04 — Core 60

| Время | Слайды | Фокус | Evidence |
| --- | --- | --- | --- |
| 00–05 | 1–3 | incident + цель | workload constraints |
| 05–15 | 4–8 | Big Data history + 3V/10V | pressure → architectural response |
| 15–28 | 9–16 | MapReduce → Spark + version evolution | pain → feature → adoption |
| 28–42 | 17–29 | API/context + scheduler + lazy/cache | task assignment + job/stage/task mapping |
| 42–52 | 30–36 | PySpark live pipeline + plan | Exchange + join strategy + output metrics |
| 52–58 | 37–38 | Spark UI + evidence chain | operator ↔ shuffle metrics |
| 58–60 | 39 | exit ticket | four correct explanations |

Команды:

```bash
python3 mentor-lab.py student spark-foundations start --profile lesson04
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_core_pipeline.py \
  -- --hold-seconds 300
```

Правило Core: не открывать principal matrix, plan internals, AQE/skew appendix и
deployment matrix, пока mental model не устойчив. Слайды 5–8 проводятся как
causal history, а не как перечень терминов.
