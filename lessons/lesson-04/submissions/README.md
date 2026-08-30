# Lesson 04 submissions

Скопируй scaffold:

```bash
cp labs/spark/examples/lesson04_core_pipeline.py \
  lessons/lesson-04/submissions/pipeline.py
cp lessons/lesson-04/homework/templates/evidence.md \
  lessons/lesson-04/submissions/evidence.md
```

Затем измени grain на `event_date × country × device` и заполни evidence.

Проверка:

```bash
python3 mentor-lab.py spark-submit spark lessons/lesson-04/submissions/pipeline.py
python3 mentor-lab.py homework spark check \
  --submission lessons/lesson-04/submissions
```
