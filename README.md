# DE Mentor

Self-service материалы и локальные стенды для менторинга начинающего дата инженера.

Первый модуль посвящен Greenplum: MPP-архитектуре, distribution key, data skew, Motion nodes и первым архитектурным решениям при проектировании аналитической модели.

## Быстрый Старт Для Ментора

```bash
python3 mentor-lab.py list
python3 mentor-lab.py info greenplum
python3 mentor-lab.py up greenplum
python3 mentor-lab.py psql greenplum
```

После занятия стенд можно остановить:

```bash
python3 mentor-lab.py down greenplum
```

Для полной переинициализации с удалением volume:

```bash
python3 mentor-lab.py reset greenplum
python3 mentor-lab.py up greenplum
```

## Быстрый Старт Для Ученика

Интерфейс одинаковый для macOS и Windows: ученик ставит Docker Desktop, открывает папку репозитория и запускает Greenplum одной командой. Устанавливать Python-пакет не нужно.

### macOS

```bash
python3 mentor-lab.py doctor
python3 mentor-lab.py up greenplum
python3 mentor-lab.py psql greenplum
```

### Windows

Открыть PowerShell в папке репозитория:

```powershell
py mentor-lab.py doctor
py mentor-lab.py up greenplum
py mentor-lab.py psql greenplum
```

`psql` запускается внутри контейнера, поэтому локально ставить PostgreSQL client не нужно.

## Структура

```text
docs/lessons/01-greenplum/  # план урока, roadmap, workbook, homework
labs/greenplum/             # Docker Compose стенд и SQL-практика
src/mentor_lab/             # CLI для управления стендами
tests/                      # автотесты CLI-домена
```

## CLI Команды

```bash
python3 mentor-lab.py list
python3 mentor-lab.py info greenplum
python3 mentor-lab.py lesson greenplum
python3 mentor-lab.py hint greenplum skew-investigation
python3 mentor-lab.py hint greenplum physical-joins --level 2
python3 mentor-lab.py assessment greenplum pre
python3 mentor-lab.py portal greenplum
python3 mentor-lab.py up greenplum
python3 mentor-lab.py status greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py grade greenplum
python3 mentor-lab.py seed greenplum --profile skewed
python3 mentor-lab.py tuning greenplum list
python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join
python3 mentor-lab.py visualize-plan greenplum --query product_join --sample --format mermaid
python3 mentor-lab.py diagnostics greenplum list
python3 mentor-lab.py scenario greenplum start --difficulty medium --seed 42 --dry-run
python3 mentor-lab.py incident list greenplum
python3 mentor-lab.py incident start greenplum skew-investigation
python3 mentor-lab.py submit greenplum advanced-joins
python3 mentor-lab.py review greenplum --submission submissions/advanced-joins.md
python3 mentor-lab.py adaptive-review greenplum --submission submissions/query-tuning.md
python3 mentor-lab.py solutions greenplum show redistribute-join
python3 mentor-lab.py challenge greenplum start --difficulty hard --minutes 15 --seed 7
python3 mentor-lab.py telemetry greenplum --pre 40 --post 85 --review 70
python3 mentor-lab.py dsl greenplum show redistribute-join
python3 mentor-lab.py report greenplum
python3 mentor-lab.py cockpit greenplum
python3 mentor-lab.py control-room greenplum
python3 mentor-lab.py certificate greenplum
python3 mentor-lab.py logs greenplum
python3 mentor-lab.py psql greenplum
python3 mentor-lab.py down greenplum
python3 mentor-lab.py reset greenplum
```

`--dry-run` показывает Docker Compose команду без выполнения:

```bash
python3 mentor-lab.py up greenplum --dry-run
```

## Развитие Платформы

CLI уже содержит registry для будущих стендов:

- `postgres`
- `clickhouse`
- `hadoop-hdfs`
- `spark-yarn`
- `spark-k8s`

Новый стенд добавляется через отдельную папку `labs/<name>/`, Docker Compose файл, документацию и запись в `src/mentor_lab/registry.py`.

## Профессиональный Контур Урока 01

- [План урока](docs/lessons/01-greenplum/README.md)
- [Case study](docs/lessons/01-greenplum/case-study.md)
- [Architecture map](docs/lessons/01-greenplum/architecture.md)
- [Incident mode](docs/lessons/01-greenplum/incidents/skewed-distribution.md)
- [Rubric and skill matrix](docs/lessons/01-greenplum/rubric.md)
- [Capstone](docs/lessons/01-greenplum/capstone.md)
- [Academy loop](docs/lessons/01-greenplum/academy-loop.md)
- [Academy v2](docs/lessons/01-greenplum/academy-v2.md)
- [Query tuning lab](docs/lessons/01-greenplum/query-tuning-lab.md)
- [Plan reading deep dive](docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md)
- [Physical joins deep dive](docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md)
- [MPP system taxonomy](docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md)
- [Theory deck source](decks/greenplum-theory/README.md)
