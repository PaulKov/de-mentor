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
python3 mentor-lab.py runbook greenplum prep
python3 mentor-lab.py runbook greenplum simple
python3 mentor-lab.py runbook greenplum deep
python3 mentor-lab.py runbook greenplum homework
python3 mentor-lab.py hint greenplum skew-investigation
python3 mentor-lab.py portal greenplum
python3 mentor-lab.py visualize-plan greenplum --query product_join --sample --format mermaid
python3 mentor-lab.py diagnostics greenplum list
python3 mentor-lab.py scenario greenplum start --difficulty medium --seed 42 --dry-run
python3 mentor-lab.py check greenplum
python3 mentor-lab.py grade greenplum
python3 mentor-lab.py report greenplum
```

Для incident mode:

```bash
python3 mentor-lab.py incident list greenplum
python3 mentor-lab.py incident start greenplum skew-investigation
python3 mentor-lab.py seed greenplum --profile skewed
```

## Материалы

- [Mentor guide](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/mentor-guide.md) - подсказки для проведения урока.
- [Student workbook](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/student-workbook.md) - задания для ученика.
- [Student prep](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/student-prep.md) - подготовка окружения ученика для macOS, Windows и Linux.
- [Simple path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/simple-path.md) - 60-минутный маршрут: слайды, команды, вопросы, проверки.
- [Deep-dive path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/deep-dive-path.md) - расширенный deep-dive маршрут.
- [Homework plan](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/runbooks/homework-plan.md) - план домашки на 60-90 минут.
- [Cheat sheet](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/cheat-sheet.md) - команды и SQL-шпаргалка.
- [Homework](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/homework.md) - домашняя работа.
- [Case study](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/case-study.md) - сквозной профессиональный кейс.
- [Architecture](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/architecture.md) - визуальная карта Greenplum.
- [Rubric](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/rubric.md) - skill matrix и критерии оценки.
- [Capstone](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/capstone.md) - финальная архитектурная задача.
- [Academy loop](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/academy-loop.md) - professional loop: assessment, analyzer, hidden incidents, submit/review, certificate.
- [Academy v2](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/academy-v2.md) - interactive student portal, visualizer, diagnostics, scenario randomizer, adaptive review.
- [Query tuning lab](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/query-tuning-lab.md) - усложненные задачи по query tuning.
- [QD/QE/gang/slices explained](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/qd-qe-gang-slices-explained.md) - цельное объяснение QD, QE, slices, gangs, Motion и того, как это видно в `EXPLAIN`.
- [Master/segment data path](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md) - глубокая техническая схема master/QD/QE, Motion, gpfdist и storage.
- [EXPLAIN plan reading](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/explain-plan-reading.md) - как читать план и формулировать RCA по `EXPLAIN ANALYZE`.
- [Physical joins in MPP](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/physical-joins-in-mpp.md) - физика joins в MPP: co-located, broadcast, redistribute.
- [Partitioning strategies](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/partitioning-strategies.md) - RANGE / LIST / HASH, DEFAULT partition, no default partitioning, `pg_partition_tree`, `gp_toolkit.gp_partitions`, `leaf_partitions`, `ATTACH PARTITION`, `DETACH PARTITION` и out-of-range INSERT.
- [MPP system taxonomy](https://github.com/PaulKov/de-mentor/blob/master/docs/lessons/01-greenplum/deep-dives/mpp-system-taxonomy.md) - SMP, MPP, EPP, lakehouse, HTAP и цена каждой архитектуры.
- [Greenplum theory deck](https://github.com/PaulKov/de-mentor/blob/master/artifacts/greenplum-theory.pptx) - презентация урока.
- [Greenplum lab README](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/README.md) - запуск стенда.
- [Cluster inspection SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/cluster-inspection.sql) - runnable SQL для проверки topology, settings и disk free учебного Docker-кластера.
- [Cluster monitoring SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/cluster-monitoring.sql) - расширенный monitoring SQL: `gp_segment_configuration`, `gp_toolkit.gp_disk_free`, `gp_segment_id`, `gpstate -s` snippets и segment health.
- [Storage and partitioning SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/storage-and-partitioning.sql) - runnable demo для Heap/AO/AOCO и partitioning intro.
- [Partitioning strategies SQL](https://github.com/PaulKov/de-mentor/blob/master/labs/greenplum/examples/partitioning-strategies.sql) - runnable drill по `PARTITION BY RANGE`, `PARTITION BY LIST`, `PARTITION BY HASH`, `DEFAULT partition` и подсчету partitions через `pg_partition_tree` / `gp_toolkit.gp_partitions`.
