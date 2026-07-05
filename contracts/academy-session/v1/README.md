# Academy Session v1

`academy-session/v1` — стабильный JSON-контракт между core CLI `de-mentor` и frontend-сервисом `de-mentor-portal`.

Core генерирует `session.json`, портал только читает его через `MENTOR_LAB_SESSION`.

Минимальные требования:

- `contract_version = academy-session/v1`;
- `current_stage` соответствует одному из `stages`;
- `portal.repository = https://github.com/PaulKov/de-mentor-portal`;
- команды остаются обычными строками и могут копироваться из UI;
- `skill_graph` описывает наблюдаемые навыки и evidence.

## Optional Homework Review Studio

`homework_review` появляется только для mentor-led разбора домашки. Это
top-level блок, чтобы портал мог показать dedicated surface без запуска Python
из браузера.

Создать сессию для разбора Lesson 01 без сданного файла:

```bash
python3 mentor-lab.py session greenplum start \
  --homework-review lesson-01 \
  --student Иван \
  --output artifacts/sessions/ivan-review
```

Создать сессию с реальным scoring:

```bash
python3 mentor-lab.py session greenplum start \
  --homework-review lesson-01 \
  --submission submissions/homework.md \
  --student Иван \
  --output artifacts/sessions/ivan-review
```

Портал читает `rubric_items`, `live_checklist`, `sql_snippets`,
`mentor_conclusion` и `next_lesson_plan`, а mentor notes и отметки хранит
локально в браузере.
