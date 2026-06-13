# Greenplum Academy v2

Academy v2 превращает первый урок в управляемый тренажер: ученик работает через локальный портал, ментор видит control room, а качество ответа проверяется evidence-first рубрикой.

## Поток Работы

```mermaid
flowchart LR
    A["Readiness Pro"] --> B["Student portal"]
    B --> C["Pre-assessment"]
    C --> D["Live orchestrator"]
    D --> E["Lesson + query tuning lab"]
    E --> F["Observation trail"]
    F --> G["EXPLAIN coach"]
    G --> H["EXPLAIN visualizer"]
    H --> I["Runtime diagnostics"]
    I --> J["Random scenario"]
    J --> K["Timed challenge"]
    K --> L["Evidence pack"]
    L --> M["SQL autograder"]
    M --> N["Misconception diagnosis"]
    N --> O["Homework autograder"]
    O --> P["Adaptive review"]
    P --> Q["Debrief"]
    Q --> R["Learning Loop report"]
    R --> S["Replay pack"]
    S --> T["Live smoke / next module"]
```

## Маршрут Ученика

```bash
python3 mentor-lab.py readiness greenplum --platform macos
python3 mentor-lab.py portal greenplum --version v2 --output artifacts/greenplum-student-portal-v2.html
python3 mentor-lab.py assessment greenplum pre
python3 mentor-lab.py visualize-plan greenplum --query product_join --sample --format html --output artifacts/product-plan.html
python3 mentor-lab.py diagnostics greenplum list
python3 mentor-lab.py scenario greenplum start --difficulty medium --seed 42 --dry-run
python3 mentor-lab.py challenge greenplum start --difficulty hard --minutes 15 --seed 7
python3 mentor-lab.py dataset greenplum generate --scale small --seed 42 --skew high --late-facts --wide-rows --output artifacts/generated-enterprise.sql
python3 mentor-lab.py submit greenplum query-tuning
python3 mentor-lab.py evidence greenplum collect redistribute-join --output submissions/redistribute-join.md
python3 mentor-lab.py misconception greenplum diagnose --text "partition key это то же самое что distribution key"
```

## Маршрут Ментора

```bash
python3 mentor-lab.py control-room greenplum --output artifacts/greenplum-control-room.html
python3 mentor-lab.py teach greenplum simple --stage 1
python3 mentor-lab.py orchestrate greenplum --route simple --stage 1 --mode recovery
python3 mentor-lab.py observe greenplum start --output artifacts/greenplum-observe-checklist.md
python3 mentor-lab.py coach-plan greenplum --query bad_customer_join --sample
python3 mentor-lab.py diagnostics greenplum show segment-skew
python3 mentor-lab.py solutions greenplum show redistribute-join
python3 mentor-lab.py calibration greenplum show senior
python3 mentor-lab.py homework greenplum check --submission submissions/homework.md
python3 mentor-lab.py autograde-sql greenplum --submission labs/greenplum/examples/student-solution-example.sql --output artifacts/sql-autograde.md
python3 mentor-lab.py adaptive-review greenplum --submission submissions/query-tuning.md
python3 mentor-lab.py debrief greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-debrief.md
python3 mentor-lab.py telemetry greenplum --pre 40 --post 85 --review 70
python3 mentor-lab.py learning-loop greenplum --pre 40 --post 85 --submission submissions/query-tuning.md --output artifacts/greenplum-learning-loop.md
python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md
python3 mentor-lab.py ci-smoke greenplum --dry-run
```

## Scenario DSL

Сценарии описываются engine-neutral контрактом: skills, tasks, checks и acceptance criteria. Это позволит тем же способом добавить ClickHouse, Postgres, HDFS, Spark on YARN и Spark on Kubernetes.

```bash
python3 mentor-lab.py dsl greenplum list
python3 mentor-lab.py dsl greenplum show redistribute-join
```

## Контракт Evidence

Хорошая работа ученика должна содержать:

- symptom;
- plan evidence;
- segment or runtime evidence;
- physical cause;
- change;
- validation;
- residual risk.

## Что Делает Это Профессиональным

- **Interactive portal**: ученик видит маршрут урока и команды без ручного поиска по документации.
- **Readiness Doctor Pro**: ученик заранее получает setup path для macOS, Windows или Linux.
- **Student Portal v2**: добавляет progress, evidence checklist, misconception hints и export-ready submission draft.
- **Live Lesson Orchestrator**: ментор ведет stage с timer, decision gate и next action под темп ученика.
- **Teach mode**: ментор получает один stage-oriented экран вместо ручной навигации по документам.
- **Live Lab Observation**: действия ученика превращаются в observation checklist и evidence trail report.
- **Query Plan Coach**: `EXPLAIN` объясняется через root cause hypothesis и следующий SQL.
- **EXPLAIN visualizer**: Motion, interconnect, coordinator path и join algorithm становятся визуальными.
- **Runtime diagnostics**: `gp_segment_id`, `pg_stat_activity`, statistics и spill-risk входят в практику.
- **Scenario randomizer**: можно выдать replayable задачу по seed.
- **Scenario Pack v2**: добавляет production-инциденты про AOCO mutable dimension и coordinator bottleneck.
- **Dataset Generator Pro**: создает live datasets с управляемыми skew, late facts и wide rows.
- **Adaptive review**: оценивается качество reasoning, а не только факт выполнения SQL.
- **Control room**: у ментора есть единая панель для readiness, diagnostics, challenge и review.
- **Golden / anti-solutions**: разбор показывает не только правильный ответ, но и опасные ложные фиксы.
- **Gold submission calibration**: weak/solid/senior примеры помогают одинаково оценивать ответы.
- **Evidence capture**: практическая работа превращается в markdown submission с командами, RCA и validation.
- **Real SQL Autograder**: SQL submission проверяется по physical DDL, `EXPLAIN ANALYZE`, `gp_segment_id`, statistics и validation.
- **Misconception bank**: ментор быстро диагностирует типичные ошибки и получает intervention.
- **Homework autograder**: домашка проверяется на grain, distribution, partitioning, storage и доказательства.
- **Debrief**: после проверки формируется персональный разбор для ученика и private notes для ментора.
- **Telemetry**: после урока появляется growth report и recommended next focus.
- **Learning Loop**: после review появляется карта навыков, missing evidence и план повторения на +1/+3/+7 дней.
- **Lesson Replay Pack**: итоговый артефакт соединяет debrief, learning loop и подготовку к Lesson 02.
- **Greenplum Live Smoke**: workflow поднимает стенд, выполняет SQL demos и прогоняет autograder.

## Academy Experience v5

`Academy Experience v5` заменяет ручную навигацию по portal/control-room артефактам единым session workflow. Портал в `apps/academy-portal` написан на Vue 3 + Nuxt 3 + Vite и читает состояние из `session.json`.

```bash
python3 mentor-lab.py session greenplum start --student Иван --output artifacts/sessions/ivan
MENTOR_LAB_SESSION=artifacts/sessions/ivan/session.json npm --prefix apps/academy-portal run dev
python3 mentor-lab.py session greenplum report --session artifacts/sessions/ivan --output artifacts/greenplum-session-report.md
python3 mentor-lab.py lesson-doctor greenplum --output artifacts/greenplum-lesson-doctor.md
```

Что появляется поверх v2: current stage, timeline, skill graph, copy-command кнопки, evidence checklist, student handoff и pre-flight проверка урока через `lesson-doctor`.
