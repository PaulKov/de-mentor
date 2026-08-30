# Simple Path: Lesson 04 — Core 60

| Время | Слайды | Фокус | Evidence |
| --- | --- | --- | --- |
| 00–05 | 1–3 | incident + цель | workload constraints |
| 05–13 | 4–6 | GFS/MapReduce/Hadoop/Spark | problem → design response |
| 13–23 | 7–11 | Spark boundaries + architecture | driver/executor mapping |
| 23–34 | 12–16 | lazy, job/stage/task, shuffle | prediction answers |
| 34–49 | 17–23 | PySpark live pipeline | plan + output metrics |
| 49–56 | 24–25 | Spark UI | Exchange ↔ shuffle |
| 56–60 | 26 | exit ticket | five correct answers |

Команды:

```bash
python3 mentor-lab.py up spark
python3 mentor-lab.py seed spark --profile lesson04
python3 mentor-lab.py check spark
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_core_pipeline.py \
  -- --hold-seconds 300
```

Правило Core: не открывать plan internals, AQE/skew appendix и deployment matrix, пока mental model не устойчив.
