# DE Mentor

<div align="center">

**Self-service платформа для практического менторинга дата инженеров**

Локальные стенды, теория, практические задания, диагностика, автопроверки и учебные артефакты в одном репозитории.

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB)
![Docker Desktop](https://img.shields.io/badge/Docker-Desktop-2496ED)
![Greenplum](https://img.shields.io/badge/Module-Greenplum-2E7D32)
![Tests](https://img.shields.io/badge/tests-73%20passing-0A7F3F)

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
- Adaptive review по evidence-first rubric.
- Golden solutions и anti-solutions.
- Lesson telemetry report.
- Cross-engine Scenario DSL для будущих стендов.

## Быстрый старт

### Требования

- Python 3.9+
- Docker Desktop
- Docker Compose v2
- macOS или Windows с PowerShell

Проверить окружение:

```bash
python3 mentor-lab.py doctor
```

На Windows:

```powershell
py mentor-lab.py doctor
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
python3 mentor-lab.py portal greenplum
python3 mentor-lab.py assessment greenplum pre
python3 mentor-lab.py lesson greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py grade greenplum
```

Продвинутый маршрут:

```bash
python3 mentor-lab.py tuning greenplum list
python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join
python3 mentor-lab.py visualize-plan greenplum --query product_join --sample --format mermaid
python3 mentor-lab.py diagnostics greenplum list
python3 mentor-lab.py scenario greenplum start --difficulty medium --seed 42 --dry-run
python3 mentor-lab.py challenge greenplum start --difficulty hard --minutes 15 --seed 7
```

После выполнения задания:

```bash
python3 mentor-lab.py submit greenplum query-tuning
python3 mentor-lab.py adaptive-review greenplum --submission submissions/query-tuning.md
python3 mentor-lab.py telemetry greenplum --pre 40 --post 85 --review 70
python3 mentor-lab.py certificate greenplum
```

## Интерфейсы ученика и ментора

Сгенерировать локальный портал ученика:

```bash
python3 mentor-lab.py portal greenplum --output artifacts/greenplum-student-portal.html
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
| Roadmap | [roadmap.md](docs/lessons/01-greenplum/roadmap.md) |
| Workbook ученика | [student-workbook.md](docs/lessons/01-greenplum/student-workbook.md) |
| Guide ментора | [mentor-guide.md](docs/lessons/01-greenplum/mentor-guide.md) |
| Simple runbook | [simple-path.md](docs/lessons/01-greenplum/runbooks/simple-path.md) |
| Deep-dive runbook | [deep-dive-path.md](docs/lessons/01-greenplum/runbooks/deep-dive-path.md) |
| Homework plan | [homework-plan.md](docs/lessons/01-greenplum/runbooks/homework-plan.md) |
| Cheat sheet | [cheat-sheet.md](docs/lessons/01-greenplum/cheat-sheet.md) |
| Academy loop | [academy-loop.md](docs/lessons/01-greenplum/academy-loop.md) |
| Academy v2 | [academy-v2.md](docs/lessons/01-greenplum/academy-v2.md) |
| Query tuning lab | [query-tuning-lab.md](docs/lessons/01-greenplum/query-tuning-lab.md) |
| Rubric | [rubric.md](docs/lessons/01-greenplum/rubric.md) |
| Capstone | [capstone.md](docs/lessons/01-greenplum/capstone.md) |
| Case study | [case-study.md](docs/lessons/01-greenplum/case-study.md) |
| Презентация | [greenplum-theory.pptx](artifacts/greenplum-theory.pptx) |
| Исходники презентации | [decks/greenplum-theory](decks/greenplum-theory/README.md) |
| Стенд Greenplum | [labs/greenplum](labs/greenplum/README.md) |
| Storage/partitioning SQL | [storage-and-partitioning.sql](labs/greenplum/examples/storage-and-partitioning.sql) |

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
73 tests passing
Greenplum health checks passing
22-slide Russian theory deck included
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
