# Lesson 04 submissions

Создай scaffold безопасной командой:

```bash
python3 mentor-lab.py student spark-foundations init
```

CLI не перезаписывает существующие `pipeline.py`/`evidence.md` без явного
`--force`.

Затем измени grain на `event_date × country × device` и заполни evidence.

Проверка:

```bash
python3 mentor-lab.py spark-submit spark lessons/lesson-04/submissions/pipeline.py
python3 mentor-lab.py student spark-foundations test
```
