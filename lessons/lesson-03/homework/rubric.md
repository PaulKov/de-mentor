# Матрица оценки: Урок 03 Homework

База: `mentor`. Схема: `lesson03`.

## Hard gates (без них работа не оценивается дальше)

| Gate | Требование |
| --- | --- |
| Environment | БД `mentor`, воспроизводимый seed/check |
| Fixed optimizer | Один `SET optimizer` для baseline ↔ candidate rewrite proof |
| Reconciliation | Two-way `EXCEPT ALL` → `0/0` (residual risk **не** заменяет) |
| Business grain | Не изменён скрыто |
| E2E metrics | Есть total pipeline cost (не только final SELECT) |
| Actual rows | Есть actuals / EXPLAIN ANALYZE evidence, не только estimates |
| Reproducibility | Команды и GUC позволяют повторить эксперимент |

`Environment check: PASS / BLOCKED` — prerequisite, **не** scored skill.

## Scored rubric: 100 баллов

| Раздел | Баллы | Principal / Senior evidence |
| --- | ---: | --- |
| Baseline plan diagnosis | 20 | Critical path, Motions, join sides, first estimate error **or** proof estimates OK |
| Stats / selectivity reasoning | 15 | Concrete predicate/join → slot → sel → plan consequence |
| Physical stage design | 20 | 0–3 stages; distribution; ANALYZE rationale; TEMP explored or rejected with cost argument |
| End-to-end measurement | 20 | Full pipeline table; TEMP cost; Motion/spill; production decision |
| Reconciliation | 15 | Two-way EXCEPT ALL 0/0 + counts; adversarial closed |
| Production risks / operability | 10 | Residual risks beyond snapshot; monitoring / rollback note |

### Уровни

| Сумма | Вердикт |
| ---: | --- |
| 90–100 | Principal (если закрыты extension-артефакты **или** distinction «do not merge» с сильным e2e) |
| 75–89 | Strong Senior — небольшая доработка evidence |
| 60–74 | Работает, но недостаточно доказано |
| &lt;60 | Повторная работа |

Senior core pass: hard gates + **≥75** по scored (без требования полной ORCA matrix).  
Principal: hard gates + **≥90** и закрытый extension block **или** выдающееся доказательное «не внедрять».

## Что не double-count

Структура `evidence.md` (A–J) оценивается внутри разделов выше.  
Отдельных баллов «за полный pack» нет — только за содержание.

Storage (Heap/AO/AOCO) входит в **Physical stage design**, если стадии создавались; отдельной строки нет.

Optimizer policy / 2×2 matrix — **Principal extension**, не обязательны для Senior core score.

## Авто-reject (любой пункт)

- смена `optimizer` внутри rewrite comparison;
- работа не в `mentor`;
- нет two-way reconciliation 0/0;
- `DISTRIBUTED RANDOMLY` на join-стадии без обоснования;
- сданный class-demo TEMP (`tmp_lesson03_sales_feb` / `_shaped`) как единственный candidate без собственной архитектуры и e2e таблицы.
