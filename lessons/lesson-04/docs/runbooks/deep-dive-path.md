# Deep-Dive Path: Lesson 04 — 90 минут

Deep включает Core и добавляет:

- четыре plan layers;
- narrow/wide transformations;
- Python/JVM boundary;
- shuffle anatomy;
- sort-merge vs broadcast join;
- AQE и skew как observable runtime decisions;
- small-files/partition output contract.

| Время | Слайды | Фокус |
| --- | --- | --- |
| 00–15 | 1–6 | история и критерий «нужен ли Spark» |
| 15–28 | 7–12 | application architecture |
| 28–42 | 13–18 | execution + plan layers |
| 42–58 | 19–26 | core pipeline |
| 58–70 | 27–30 | shuffle + Python boundary |
| 70–82 | 31–34 | join A/B |
| 82–87 | 35 | AQE, skew, small files |
| 87–90 | 36 | production checklist |

```bash
python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_deep_join.py \
  -- --hold-seconds 300
```

Deep acceptance: ученик показывает не только другой operator name, но и сравнение shuffle metrics и условие безопасности broadcast.
