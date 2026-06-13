# Greenplum Academy v2

Academy v2 превращает первый урок в управляемый тренажер: ученик работает через локальный портал, ментор видит control room, а качество ответа проверяется evidence-first рубрикой.

## Поток Работы

```mermaid
flowchart LR
    A["Student portal"] --> B["Pre-assessment"]
    B --> C["Lesson + query tuning lab"]
    C --> D["EXPLAIN visualizer"]
    D --> E["Runtime diagnostics"]
    E --> F["Random scenario"]
    F --> G["Timed challenge"]
    G --> H["Adaptive review"]
    H --> I["Telemetry report"]
    I --> J["Certificate / next module"]
```

## Маршрут Ученика

```bash
python3 mentor-lab.py portal greenplum --output artifacts/greenplum-student-portal.html
python3 mentor-lab.py assessment greenplum pre
python3 mentor-lab.py visualize-plan greenplum --query product_join --sample --format html --output artifacts/product-plan.html
python3 mentor-lab.py diagnostics greenplum list
python3 mentor-lab.py scenario greenplum start --difficulty medium --seed 42 --dry-run
python3 mentor-lab.py challenge greenplum start --difficulty hard --minutes 15 --seed 7
python3 mentor-lab.py submit greenplum query-tuning
```

## Маршрут Ментора

```bash
python3 mentor-lab.py control-room greenplum --output artifacts/greenplum-control-room.html
python3 mentor-lab.py diagnostics greenplum show segment-skew
python3 mentor-lab.py solutions greenplum show redistribute-join
python3 mentor-lab.py adaptive-review greenplum --submission submissions/query-tuning.md
python3 mentor-lab.py telemetry greenplum --pre 40 --post 85 --review 70
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
- **EXPLAIN visualizer**: Motion, interconnect, coordinator path и join algorithm становятся визуальными.
- **Runtime diagnostics**: `gp_segment_id`, `pg_stat_activity`, statistics и spill-risk входят в практику.
- **Scenario randomizer**: можно выдать replayable задачу по seed.
- **Adaptive review**: оценивается качество reasoning, а не только факт выполнения SQL.
- **Control room**: у ментора есть единая панель для readiness, diagnostics, challenge и review.
- **Golden / anti-solutions**: разбор показывает не только правильный ответ, но и опасные ложные фиксы.
- **Telemetry**: после урока появляется growth report и recommended next focus.
