# Design: Урок 03 — Декомпозиция и тюнинг тяжёлых запросов в MPP

## Goal

Добавить полный контур Lesson 03 (как Lesson 02): curriculum docs, SQL-lab, runbooks, catalog/control plane, PPTX + Google Slides. Фокус Senior/Principal: чтение сложных планов, статистика до каталогов/файлов/кода, физическое хранение Heap/AO/AOCO, временные таблицы для декомпозиции.

## Decisions

| Решение | Выбор |
|---|---|
| Scope | Deep OLAP + internals; WLM/RCA → Lesson 04 |
| Название | Декомпозиция и тюнинг тяжёлых запросов в MPP |
| Язык | Русский; устоявшиеся термины (`EXPLAIN`, `ANALYZE`, AOCO, Motion) сохраняем |
| Формат | Simple 60 мин + deep-dive 90–120 мин |
| Паттерн | Гибрид: один сквозной OLAP case + deep appendix по internals |
| Артефакты | Полный контур Lesson 02 |
| Route | `greenplum-query-tuning` |
| Deck | `artifacts/greenplum-query-tuning-theory/greenplum-query-tuning-theory.pptx` (~22 слайда) |
| Drive | `lessons/Greenplum/Lesson 03 - Decomposition and tuning of heavy MPP queries` |

## Curriculum blocks

1. Сквозной тяжёлый OLAP и декомпозиция
2. Чтение сложного `EXPLAIN` (slices, Motion, estimates)
3. Статистика: `pg_stats` → `pg_statistic` → файлы/код
4. Физическое хранение Heap / AO / AOCO и типы данных
5. `TEMP` / spill / `pg_temp` vs CTE
6. Homework + мост к Lesson 04 (WLM)

## Out of scope

Workload management, resource groups/queues, полный production RCA framework.
