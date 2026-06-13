# DE Mentor

<div align="center">

**Self-service платформа для практического менторинга дата инженеров**

Локальные стенды, теория, практические задания, диагностика, автопроверки и учебные артефакты в одном репозитории.

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB)
![Docker Desktop](https://img.shields.io/badge/Docker-Desktop-2496ED)
![Greenplum](https://img.shields.io/badge/Module-Greenplum-2E7D32)
![Tests](https://img.shields.io/badge/tests-122%20passing-0A7F3F)

</div>

## Оглавление

- [Что это](#что-это)
- [Для кого](#для-кого)
- [Что уже готово](#что-уже-готово)
- [Быстрый старт](#быстрый-старт)
- [Как пройти первый урок](#как-пройти-первый-урок)
- [Интерфейсы ученика и ментора](#интерфейсы-ученика-и-ментора)
- [Практика и автоматизация](#практика-и-автоматизация)
- [Материалы урока](#материалы-урока)
- [Структура проекта](#структура-проекта)
- [Качество и проверки](#качество-и-проверки)
- [Roadmap](#roadmap)
- [Честный статус](#честный-статус)

## Что это

`DE Mentor` помогает провести сильный практический урок по data engineering без ручной подготовки стенда и разрозненных материалов.

Первый модуль посвящён **Greenplum**: MPP-архитектуре, coordinator/master, segments, interconnect, distribution keys, data skew, Motion nodes, physical joins, heap vs AO/AOCO и чтению `EXPLAIN`.

Идея простая: ученик не просто слушает теорию, а запускает локальный стенд, ломает и чинит данные, читает планы, сдаёт evidence, получает review и понимает, почему MPP-системы требуют другого мышления.

## Для кого

| Роль | Что получает |
|---|---|
| Ментор / дата архитектор | Готовый сценарий урока, презентацию, стенд, задания, rubric, автопроверки, control room и review-инструменты. |
| Начинающий дата инженер | Понятный CLI, локальный Greenplum, student portal, практические задачи, подсказки, визуализацию планов и понятный feedback. |
| Команда данных | Повторяемый onboarding-модуль, который можно расширять под Postgres, ClickHouse, Hadoop, Spark и другие стенды. |

## Что уже готово

### Greenplum Academy

- Docker Compose стенд Greenplum.
- Единый CLI `mentor-lab.py` для macOS и Windows.
- План урока на 60 минут.
- Русская презентация в спокойной светлой теме.
- Facilitator guide: когда показывать каждый слайд и что говорить.
- Student workbook, homework, capstone, case study.
- Deep dives по QD/QE, master/coordinator, Motion, joins, SMP/MPP/EPP.
- Query tuning lab с практикой по `EXPLAIN`, skew, joins, partitions и storage.

### Academy v2

- Student Portal.
- Mentor Control Room.
- EXPLAIN Analyzer.
- EXPLAIN Visualizer в Mermaid/HTML.
- Runtime diagnostics pack.
- Scenario randomizer.
- Timed challenge mode.
- One-Button Mentor Mode для ведения урока по stage.
- Evidence Capture: submission-ready markdown pack для практических сценариев.
- Homework Autograder для проверки физического дизайна и evidence.
- Misconception Bank для быстрых mentor interventions.
- Student Portal v2 с progress, hints, evidence checklist и export-ready submission.
- Debrief Generator для персональной обратной связи после урока.
- Adaptive review по evidence-first rubric.
- Golden solutions и anti-solutions.
- Lesson telemetry report.
- Learning Loop report: карта навыков, gaps по evidence и план повторения на 1/3/7 дней.
- Cross-engine Scenario DSL для будущих стендов.

### Academy Pro v3

- Readiness Doctor Pro для macOS, Windows и Linux.
- Live Lesson Orchestrator с режимами `simple`, `deep`, `recovery` и `fast-student`.
- Live Lab Observation: checklist и evidence trail report по действиям ученика.
- Query Plan Coach: объяснение Motion, slices, root cause hypothesis и следующий SQL.
- Scenario Pack v2 с production-инцидентами про AOCO mutable dimension и coordinator bottleneck.
- Gold submission calibration: слабый, уверенный и senior-level ответы для калибровки оценки.
- Lesson Replay Pack: debrief, learning loop и подготовка к Lesson 02 в одном артефакте.

### Academy Enterprise v4

- Real SQL Autograder: проверяет SQL/evidence submission по `DISTRIBUTED BY`, `PARTITION BY`, AOCO, `EXPLAIN ANALYZE`, `gp_segment_id`, `ANALYZE` и validation.
- Dataset Generator Pro: детерминированные seed SQL с scale, skew, late-arriving facts и wide rows.
- Greenplum Live Smoke: локальный/GitHub Actions план, который поднимает стенд, выполняет SQL demos и прогоняет autograder.
- Эталонный SQL submission для проверки живого контура.

### Academy Experience v5

- Stateful session: `mentor-lab.py session greenplum start` создает `session.json`, timeline, skill graph, mentor cockpit и student handoff.
- Nuxt portal: `apps/academy-portal` — основной интерфейс занятия на Vue 3 + Nuxt 3 + Vite.
- Lesson Doctor: `mentor-lab.py lesson-doctor greenplum` проверяет презентацию, docs, SQL examples, CI smoke и Nuxt portal перед уроком.
- Единый runtime state: портал запускается командой `MENTOR_LAB_SESSION=artifacts/sessions/<name>/session.json npm --prefix apps/academy-portal run dev`.
- Session report: `mentor-lab.py session greenplum report` собирает события, skill graph и next actions после урока.

## Быстрый старт

### Требования

- Python 3.9+
- Docker Desktop
- Docker Compose v2
- macOS или Windows с PowerShell

Проверить окружение:

```bash
python3 mentor-lab.py doctor
python3 mentor-lab.py readiness greenplum --platform macos
```

На Windows:

```powershell
py mentor-lab.py doctor
py mentor-lab.py readiness greenplum --platform windows
```

### Запустить Greenplum

macOS:

```bash
python3 mentor-lab.py up greenplum
python3 mentor-lab.py status greenplum
python3 mentor-lab.py psql greenplum
```

Windows:

```powershell
py mentor-lab.py up greenplum
py mentor-lab.py status greenplum
py mentor-lab.py psql greenplum
```

`psql` запускается внутри контейнера, поэтому локально PostgreSQL client ставить не нужно.

### Остановить или пересоздать стенд

```bash
python3 mentor-lab.py down greenplum
```

Полная переинициализация с удалением volume:

```bash
python3 mentor-lab.py reset greenplum
python3 mentor-lab.py up greenplum
```

## Как пройти первый урок

Минимальный маршрут:

```bash
python3 mentor-lab.py session greenplum start --student Иван --output artifacts/sessions/ivan
MENTOR_LAB_SESSION=artifacts/sessions/ivan/session.json npm --prefix apps/academy-portal run dev
python3 mentor-lab.py portal greenplum
python3 mentor-lab.py assessment greenplum pre
python3 mentor-lab.py teach greenplum simple --stage 1
python3 mentor-lab.py lesson greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py grade greenplum
```

Продвинутый маршрут:

```bash
python3 mentor-lab.py tuning greenplum list
python3 mentor-lab.py orchestrate greenplum --route simple --stage 1 --mode recovery
python3 mentor-lab.py observe greenplum start --output artifacts/greenplum-observe-checklist.md
python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join
python3 mentor-lab.py coach-plan greenplum --query bad_customer_join --sample
python3 mentor-lab.py visualize-plan greenplum --query product_join --sample --format mermaid
python3 mentor-lab.py diagnostics greenplum list
python3 mentor-lab.py scenario greenplum start --difficulty medium --seed 42 --dry-run
python3 mentor-lab.py challenge greenplum start --difficulty hard --minutes 15 --seed 7
python3 mentor-lab.py dataset greenplum generate --scale small --seed 42 --skew high --late-facts --wide-rows --output artifacts/generated-enterprise.sql
python3 mentor-lab.py evidence greenplum collect redistribute-join --output submissions/redistribute-join.md
python3 mentor-lab.py misconception greenplum diagnose --text "partition key это то же самое что distribution key"
python3 mentor-lab.py calibration greenplum show senior
python3 mentor-lab.py lesson-doctor greenplum --output artifacts/greenplum-lesson-doctor.md
python3 mentor-lab.py ci-smoke greenplum --dry-run
```

После выполнения задания:

```bash
python3 mentor-lab.py submit greenplum query-tuning
python3 mentor-lab.py homework greenplum check --submission submissions/homework.md
python3 mentor-lab.py autograde-sql greenplum --submission labs/greenplum/examples/student-solution-example.sql --output artifacts/sql-autograde.md
python3 mentor-lab.py adaptive-review greenplum --submission submissions/query-tuning.md
python3 mentor-lab.py debrief greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-debrief.md
python3 mentor-lab.py telemetry greenplum --pre 40 --post 85 --review 70
python3 mentor-lab.py learning-loop greenplum --pre 40 --post 85 --submission submissions/query-tuning.md --output artifacts/greenplum-learning-loop.md
python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md
python3 mentor-lab.py session greenplum report --session artifacts/sessions/ivan --output artifacts/greenplum-session-report.md
python3 mentor-lab.py certificate greenplum
```

## Интерфейсы ученика и ментора

Основной интерфейс занятия в `Academy Experience v5`:

```bash
python3 mentor-lab.py session greenplum start --student Иван --output artifacts/sessions/ivan
MENTOR_LAB_SESSION=artifacts/sessions/ivan/session.json npm --prefix apps/academy-portal run dev
python3 mentor-lab.py session greenplum report --session artifacts/sessions/ivan --output artifacts/greenplum-session-report.md
python3 mentor-lab.py lesson-doctor greenplum --output artifacts/greenplum-lesson-doctor.md
```

Портал в `apps/academy-portal` написан на Vue 3 + Nuxt 3 + Vite и показывает current stage, timeline, skill graph, copy-command кнопки, evidence checklist и handoff после урока.

Сгенерировать локальный портал ученика:

```bash
python3 mentor-lab.py portal greenplum --output artifacts/greenplum-student-portal.html
python3 mentor-lab.py portal greenplum --version v2 --output artifacts/greenplum-student-portal-v2.html
```

Сгенерировать control room ментора:

```bash
python3 mentor-lab.py control-room greenplum --output artifacts/greenplum-control-room.html
```

Сгенерировать визуализацию плана:

```bash
python3 mentor-lab.py visualize-plan greenplum \
  --query product_join \
  --sample \
  --format html \
  --output artifacts/product-plan.html
```

## Практика и автоматизация

### Диагностика Greenplum

```bash
python3 mentor-lab.py diagnostics greenplum list
python3 mentor-lab.py diagnostics greenplum show segment-skew
python3 mentor-lab.py diagnostics greenplum run segment-skew
```

### Сценарии и incidents

```bash
python3 mentor-lab.py incident list greenplum
python3 mentor-lab.py incident start greenplum skew-investigation
python3 mentor-lab.py scenario greenplum list
python3 mentor-lab.py scenario greenplum start --difficulty medium --seed 42 --dry-run
```

### Seed-профили данных

```bash
python3 mentor-lab.py seed greenplum --profile skewed
python3 mentor-lab.py seed greenplum --profile balanced
python3 mentor-lab.py seed greenplum --profile bad-statistics
python3 mentor-lab.py seed greenplum --profile bad-partitioning
python3 mentor-lab.py seed greenplum --profile wide-aoco
python3 mentor-lab.py seed greenplum --profile small-dimension-broadcast
python3 mentor-lab.py dataset greenplum manifest
python3 mentor-lab.py dataset greenplum generate --scale small --seed 42 --skew high --late-facts --wide-rows --output artifacts/generated-enterprise.sql
```

### Enterprise-проверки

```bash
python3 mentor-lab.py autograde-sql greenplum --submission labs/greenplum/examples/student-solution-example.sql --output artifacts/sql-autograde.md
python3 mentor-lab.py ci-smoke greenplum --dry-run
```

### Эталонные решения

```bash
python3 mentor-lab.py solutions greenplum list
python3 mentor-lab.py solutions greenplum show redistribute-join
```

### Cross-engine DSL

```bash
python3 mentor-lab.py dsl greenplum list
python3 mentor-lab.py dsl greenplum show redistribute-join
```

## Материалы урока

| Материал | Ссылка |
|---|---|
| Главный план урока | [docs/lessons/01-greenplum/README.md](docs/lessons/01-greenplum/README.md) |
| Дорожная карта | [roadmap.md](docs/lessons/01-greenplum/roadmap.md) |
| Workbook ученика | [student-workbook.md](docs/lessons/01-greenplum/student-workbook.md) |
| Гайд ментора | [mentor-guide.md](docs/lessons/01-greenplum/mentor-guide.md) |
| Подготовка ученика | [student-prep.md](docs/lessons/01-greenplum/runbooks/student-prep.md) |
| Упрощенный runbook | [simple-path.md](docs/lessons/01-greenplum/runbooks/simple-path.md) |
| Расширенный runbook | [deep-dive-path.md](docs/lessons/01-greenplum/runbooks/deep-dive-path.md) |
| План домашки | [homework-plan.md](docs/lessons/01-greenplum/runbooks/homework-plan.md) |
| Шпаргалка | [cheat-sheet.md](docs/lessons/01-greenplum/cheat-sheet.md) |
| Контур Academy | [academy-loop.md](docs/lessons/01-greenplum/academy-loop.md) |
| Academy v2 | [academy-v2.md](docs/lessons/01-greenplum/academy-v2.md) |
| Лабораторная по query tuning | [query-tuning-lab.md](docs/lessons/01-greenplum/query-tuning-lab.md) |
| Deep dive по QD/QE/slices/gangs | [qd-qe-gang-slices-explained.md](docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md) |
| Матрица оценки | [rubric.md](docs/lessons/01-greenplum/rubric.md) |
| Финальная задача | [capstone.md](docs/lessons/01-greenplum/capstone.md) |
| Сквозной кейс | [case-study.md](docs/lessons/01-greenplum/case-study.md) |
| Презентация | [greenplum-theory.pptx](artifacts/greenplum-theory.pptx) |
| Исходники презентации | [decks/greenplum-theory](decks/greenplum-theory/README.md) |
| Стенд Greenplum | [labs/greenplum](labs/greenplum/README.md) |
| SQL для паспорта кластера | [cluster-inspection.sql](labs/greenplum/examples/cluster-inspection.sql) |
| SQL для мониторинга кластера | [cluster-monitoring.sql](labs/greenplum/examples/cluster-monitoring.sql) |
| SQL по storage и partitioning | [storage-and-partitioning.sql](labs/greenplum/examples/storage-and-partitioning.sql) |
| SQL по partitioning strategies | [partitioning-strategies.sql](labs/greenplum/examples/partitioning-strategies.sql) |

## Структура проекта

```text
.
├── artifacts/                 # готовые артефакты: PPTX, HTML, reports
├── decks/greenplum-theory/     # исходники презентации и facilitator guide
├── docs/lessons/01-greenplum/  # план урока, workbook, deep dives, academy loop
├── labs/greenplum/             # Docker Compose, init SQL, seed profiles
├── src/mentor_lab/             # CLI и доменные модули платформы
├── tests/                      # unit/integration тесты CLI и учебного домена
└── mentor-lab.py               # entrypoint без установки пакета
```

## Качество и проверки

Полный тестовый прогон:

```bash
python3 -m pytest tests -q
```

Проверка Python-компиляции:

```bash
python3 -m compileall -q src mentor-lab.py
```

Проверка живого Greenplum-стенда:

```bash
python3 mentor-lab.py status greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py grade greenplum
```

На момент публикации:

```text
117 tests passing
Greenplum health checks passing
30-slide Russian theory deck included
```

## Roadmap

CLI уже содержит registry для будущих стендов:

- Postgres
- ClickHouse
- Hadoop HDFS
- Spark on YARN
- Spark on Kubernetes

План развития: добавлять новые стенды через тот же контракт — `labs/<name>/`, документация, seed-профили, checks, scenarios и DSL.

## Честный статус

Это не коммерческая LMS и не замена полноценной платформы обучения. Сейчас это инженерный self-service toolkit для ментора и ученика: локально, прозрачно, воспроизводимо.

Готовый production-grade модуль сейчас один: **Greenplum Academy**. Остальные системы уже предусмотрены архитектурно, но ещё не реализованы как полноценные уроки.

Проект открыт для расширения: новые уроки лучше добавлять маленькими проверяемыми модулями, сохраняя главный принцип — теория должна быстро превращаться в практику, evidence и понятный feedback.
