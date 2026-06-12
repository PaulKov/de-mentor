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

См. [roadmap.md](roadmap.md).

## Практика

1. Запустить стенд.
2. Проверить сегменты.
3. Найти skew в плохо распределенной таблице.
4. Поймать `Redistribute Motion` в плане запроса.
5. Сравнить с исправленной таблицей.
6. Защитить архитектурное решение.
7. Advanced: прочитать план по scan/join/Motion/Rows out.
8. Advanced: сравнить co-located, Broadcast Motion и Redistribute Motion joins.
9. Advanced: выбрать класс системы под workload.

Подробные шаги: [student-workbook.md](student-workbook.md).

## Автоматизация

```bash
python3 mentor-lab.py lesson greenplum
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

- [mentor-guide.md](mentor-guide.md) - подсказки для проведения урока.
- [student-workbook.md](student-workbook.md) - задания для ученика.
- [runbooks/simple-path.md](runbooks/simple-path.md) - 60-минутный маршрут: слайды, команды, вопросы, проверки.
- [runbooks/deep-dive-path.md](runbooks/deep-dive-path.md) - расширенный deep-dive маршрут.
- [runbooks/homework-plan.md](runbooks/homework-plan.md) - план домашки на 60-90 минут.
- [cheat-sheet.md](cheat-sheet.md) - команды и SQL-шпаргалка.
- [homework.md](homework.md) - домашняя работа.
- [case-study.md](case-study.md) - сквозной профессиональный кейс.
- [architecture.md](architecture.md) - визуальная карта Greenplum.
- [rubric.md](rubric.md) - skill matrix и критерии оценки.
- [capstone.md](capstone.md) - финальная архитектурная задача.
- [academy-loop.md](academy-loop.md) - professional loop: assessment, analyzer, hidden incidents, submit/review, certificate.
- [academy-v2.md](academy-v2.md) - interactive student portal, visualizer, diagnostics, scenario randomizer, adaptive review.
- [query-tuning-lab.md](query-tuning-lab.md) - усложненные задачи по query tuning.
- [deep-dives/master-segment-data-path.md](deep-dives/master-segment-data-path.md) - глубокая техническая схема master/QD/QE, Motion, gpfdist и storage.
- [deep-dives/explain-plan-reading.md](deep-dives/explain-plan-reading.md) - как читать план и формулировать RCA по `EXPLAIN ANALYZE`.
- [deep-dives/physical-joins-in-mpp.md](deep-dives/physical-joins-in-mpp.md) - физика joins в MPP: co-located, broadcast, redistribute.
- [deep-dives/mpp-system-taxonomy.md](deep-dives/mpp-system-taxonomy.md) - SMP, MPP, EPP, lakehouse, HTAP и цена каждой архитектуры.
- [greenplum-theory.pptx](../../../artifacts/greenplum-theory.pptx) - презентация урока.
- [labs/greenplum](../../../labs/greenplum/README.md) - запуск стенда.
- [storage-and-partitioning.sql](../../../labs/greenplum/examples/storage-and-partitioning.sql) - runnable demo для Heap/AO/AOCO и partitioning intro.
