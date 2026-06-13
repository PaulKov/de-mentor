# Урок 01: Greenplum Теория И Практика

## Цель Урока

За 1 час ученик должен понять, что Greenplum - это не "PostgreSQL побольше", а MPP-база со своими архитектурными правилами: данные живут на сегментах, запросы двигают данные через Motion, а неверный distribution key может испортить даже простой SQL.

## Результаты

После урока ученик сможет:

- объяснить роли coordinator/master и segments;
- отличить OLTP-подход от OLAP/MPP-подхода;
- выбрать первый вариант `DISTRIBUTED BY`;
- увидеть data skew через `gp_segment_id`;
- прочитать базовые Motion nodes в `EXPLAIN`;
- аргументировать, почему модель данных нужно проектировать до загрузки больших объемов.

## Тайминг На 60 Минут

| Время | Блок | Что делает ментор | Что делает ученик |
|---:|---|---|---|
| 0-5 | Контекст | Объясняет цель урока и проблему MPP-мышления | Формулирует ожидания |
| 5-15 | Архитектура | Рисует coordinator, segments, interconnect | Отвечает, где выполняется запрос |
| 15-25 | Distribution | Показывает `DISTRIBUTED BY`, skew, colocated joins | Предлагает ключи распределения |
| 25-35 | EXPLAIN | Разбирает Motion nodes | Находит Motion в плане |
| 35-42 | Storage и partitioning intro | Показывает Heap/AO/AOCO, defaults и `PARTITION BY RANGE` | Запускает demo SQL |
| 42-52 | Практика | Дает задания из workbook | Выполняет SQL и делает выводы |
| 52-58 | Design review | Разбирает мини-кейс витрины продаж | Защищает модель |
| 58-60 | Домашка | Объясняет критерии приемки | Фиксирует вопросы |

## Roadmap

См. [roadmap](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/roadmap.md).

## Практика

1. Запустить стенд.
2. Проверить Docker lab cluster passport: master/coordinator, primary segments, memory settings и disk free.
3. Найти skew в плохо распределенной таблице.
4. Поймать `Redistribute Motion` в плане запроса.
5. Сравнить с исправленной таблицей.
6. Защитить архитектурное решение.
7. Advanced: прочитать план по scan/join/Motion/Rows out.
8. Advanced: сравнить co-located, Broadcast Motion и Redistribute Motion joins.
9. Advanced: выбрать класс системы под workload.

Подробные шаги: [student workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md).

## Автоматизация

```bash
python3 mentor-lab.py lesson greenplum
python3 mentor-lab.py teach greenplum simple --stage 1
python3 mentor-lab.py readiness greenplum --platform macos
python3 mentor-lab.py orchestrate greenplum --route simple --stage 1 --mode recovery
python3 mentor-lab.py runbook greenplum prep
python3 mentor-lab.py runbook greenplum simple
python3 mentor-lab.py runbook greenplum deep
python3 mentor-lab.py runbook greenplum homework
python3 mentor-lab.py hint greenplum skew-investigation
python3 mentor-lab.py portal greenplum --version v2
python3 mentor-lab.py observe greenplum start --output artifacts/greenplum-observe-checklist.md
python3 mentor-lab.py visualize-plan greenplum --query product_join --sample --format mermaid
python3 mentor-lab.py coach-plan greenplum --query bad_customer_join --sample
python3 mentor-lab.py diagnostics greenplum list
python3 mentor-lab.py scenario greenplum start --difficulty medium --seed 42 --dry-run
python3 mentor-lab.py dataset greenplum generate --scale small --seed 42 --skew high --late-facts --wide-rows --output artifacts/generated-enterprise.sql
python3 mentor-lab.py check greenplum
python3 mentor-lab.py grade greenplum
python3 mentor-lab.py report greenplum
python3 mentor-lab.py evidence greenplum collect redistribute-join --output submissions/redistribute-join.md
python3 mentor-lab.py misconception greenplum diagnose --text "partition key это то же самое что distribution key"
python3 mentor-lab.py homework greenplum check --submission submissions/homework.md
python3 mentor-lab.py autograde-sql greenplum --submission labs/greenplum/examples/student-solution-example.sql --output artifacts/sql-autograde.md
python3 mentor-lab.py calibration greenplum show senior
python3 mentor-lab.py debrief greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-debrief.md
python3 mentor-lab.py learning-loop greenplum --pre 40 --post 85 --submission submissions/query-tuning.md --output artifacts/greenplum-learning-loop.md
python3 mentor-lab.py replay greenplum --student Иван --submission submissions/query-tuning.md --pre 40 --post 85 --output artifacts/greenplum-replay.md
python3 mentor-lab.py ci-smoke greenplum --dry-run
```

`teach` ведет ментора по stage: слайды, что сказать, команды, вопрос, ожидаемый ответ и evidence checkpoint.
`readiness` дает ученику platform-specific setup для macOS, Windows и Linux.
`orchestrate` помогает ментору выбрать следующий шаг по mode-aware decision gate.
`observe` создает checklist и observation report по evidence trail ученика.
`coach-plan` объясняет `EXPLAIN` через root cause hypothesis и следующий SQL.
`dataset generate` создает детерминированный seed SQL с scale, skew, late facts и wide rows.
`evidence collect` создает markdown pack для сдачи практики.
`misconception diagnose` распознает типичные ошибки ученика и предлагает вопрос, мини-эксперимент, hint и follow-up.
`homework check` проверяет домашку по evidence-first контракту: grain, distribution, partitioning, storage, catalog evidence, `EXPLAIN`, `gp_segment_id`, risks и readiness к Lesson 02.
`autograde-sql` проверяет SQL submission по DDL, `EXPLAIN ANALYZE`, `gp_segment_id`, statistics и validation.
`calibration` показывает эталонный senior-level ответ для калибровки ожиданий.
`debrief` генерирует персональную обратную связь ученику и private mentor notes.
`learning-loop` генерирует Learning Loop report: карту навыков ученика, missing evidence и план повторения на +1/+3/+7 дней.
`replay` собирает debrief, learning loop и подготовку к Lesson 02 в один артефакт.
`ci-smoke` показывает live smoke plan для локального запуска и GitHub Actions.

## Academy Experience v5

`Academy Experience v5` добавляет stateful-session слой поверх существующих workbook/runbook/autograder материалов. Основной интерфейс занятия теперь находится в `apps/academy-portal` и написан на Vue 3 + Nuxt 3 + Vite.

```bash
python3 mentor-lab.py session greenplum start --student Иван --output artifacts/sessions/ivan
MENTOR_LAB_SESSION=artifacts/sessions/ivan/session.json npm --prefix apps/academy-portal run dev
python3 mentor-lab.py session greenplum report --session artifacts/sessions/ivan --output artifacts/greenplum-session-report.md
python3 mentor-lab.py lesson-doctor greenplum --output artifacts/greenplum-lesson-doctor.md
```

Портал показывает current stage, timeline, skill graph, copy-command кнопки, evidence checklist и итоговый handoff. `lesson-doctor` перед уроком проверяет презентацию, docs, SQL examples, workflow и Nuxt portal.

Для incident mode:

```bash
python3 mentor-lab.py incident list greenplum
python3 mentor-lab.py incident start greenplum skew-investigation
python3 mentor-lab.py seed greenplum --profile skewed
```

## Материалы

- [Гайд ментора](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/mentor-guide.md) - подсказки для проведения урока.
- [Workbook ученика](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md) - задания для ученика.
- [Подготовка ученика](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/student-prep.md) - подготовка окружения ученика для macOS, Windows и Linux.
- [Упрощенный маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/simple-path.md) - 60-минутный маршрут: слайды, команды, вопросы, проверки.
- [Расширенный маршрут](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/deep-dive-path.md) - расширенный deep-dive маршрут.
- [План домашки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/homework-plan.md) - план домашки на 60-90 минут.
- [Шпаргалка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/cheat-sheet.md) - команды и SQL-шпаргалка.
- [Домашка](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md) - домашняя работа.
- [Сквозной кейс](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/case-study.md) - сквозной профессиональный кейс.
- [Карта архитектуры](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/architecture.md) - визуальная карта Greenplum.
- [Матрица оценки](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/rubric.md) - skill matrix и критерии оценки.
- [Финальная задача](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/capstone.md) - финальная архитектурная задача.
- [Контур Academy](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/academy-loop.md) - профессиональный контур: assessment, analyzer, hidden incidents, submit/review, learning loop и certificate.
- [Academy v2](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/academy-v2.md) - портал ученика, visualizer, diagnostics, scenario randomizer, adaptive review и итоговый learning loop.
- [Лабораторная по query tuning](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/query-tuning-lab.md) - усложненные задачи по query tuning.
- [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md) - цельное объяснение QD, QE, slices, gangs, Motion и того, как это видно в `EXPLAIN`.
- [Master/segment data path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md) - глубокая техническая схема master/QD/QE, Motion, gpfdist и storage.
- [Чтение EXPLAIN-плана](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md) - как читать план и формулировать RCA по `EXPLAIN ANALYZE`.
- [Физические joins в MPP](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md) - физика joins в MPP: co-located, broadcast, redistribute.
- [Стратегии partitioning](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md) - RANGE / LIST / HASH, DEFAULT partition, no default partitioning, `pg_partition_tree`, `gp_toolkit.gp_partitions`, `leaf_partitions`, `ATTACH PARTITION`, `DETACH PARTITION` и out-of-range INSERT.
- [Таксономия MPP-систем](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md) - SMP, MPP, EPP, lakehouse, HTAP и цена каждой архитектуры.
- [Теоретическая презентация Greenplum](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-theory.pptx) - презентация урока.
- [README стенда Greenplum](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/README.md) - запуск стенда.
- [SQL для паспорта кластера](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/cluster-inspection.sql) - runnable SQL для проверки topology, settings и disk free учебного Docker-кластера.
- [SQL для мониторинга кластера](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/cluster-monitoring.sql) - расширенный monitoring SQL: `gp_segment_configuration`, `gp_toolkit.gp_disk_free`, `gp_segment_id`, `gpstate -s` snippets и segment health.
- [SQL по storage и partitioning](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/storage-and-partitioning.sql) - runnable demo для Heap/AO/AOCO и partitioning intro.
- [SQL по partitioning strategies](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql) - runnable drill по `PARTITION BY RANGE`, `PARTITION BY LIST`, `PARTITION BY HASH`, `DEFAULT partition` и подсчету partitions через `pg_partition_tree` / `gp_toolkit.gp_partitions`.
