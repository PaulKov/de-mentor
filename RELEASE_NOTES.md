# Release Notes

## Academy Self-Service v1

Этот релиз добавляет единый self-service маршрут для проведения первого урока Greenplum Academy.

### Новые команды

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py academy greenplum start --student Иван
python3 mentor-lab.py academy greenplum start --student Иван --dry-run
python3 mentor-lab.py academy greenplum start --student Иван --skip-lab
python3 mentor-lab.py student greenplum bootstrap --platform macos
python3 mentor-lab.py student greenplum bootstrap --platform windows
python3 mentor-lab.py student greenplum homework
```

### Что автоматизирует

- Создание `session.json` для Academy Control Plane.
- Экспорт session state в Nuxt portal repo.
- Подготовку команд запуска Greenplum, runbook и portal.
- Отдельный student-facing bootstrap для macOS, Windows и Linux.
- Видимый quality guard: `SLOC <= 400` и `avg clustering <= 0.180`.

### Как проверять

```bash
python3 -m pytest tests -q
python3 -m compileall -q src mentor-lab.py
python3 mentor-lab.py academy greenplum start --student Иван --dry-run
python3 mentor-lab.py student greenplum bootstrap --platform windows
python3 mentor-lab.py student greenplum homework
```
