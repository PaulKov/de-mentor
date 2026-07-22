# Матрица оценки: Урок 03 Homework

База: `mentor`. Схема: `lesson03`.  
Graded workload: **`lesson03.v_homework_brand_region`**.

## Hard gates (без них работа не оценивается дальше)

| Gate | Требование |
| --- | --- |
| Environment | БД `mentor`, воспроизводимый seed/check (`--scale` зафиксирован) |
| Graded view | Baseline / reconcile vs `v_homework_brand_region` (не class-demo monolith) |
| Fixed optimizer | Один `SET optimizer` для baseline ↔ candidate rewrite proof |
| A/B explored | ≥2 candidates в evidence (A shallow / B multi-stage); winner в rewrite.sql |
| Reconciliation | Two-way `EXCEPT ALL` → `0/0` (residual risk **не** заменяет) |
| Business grain | Не изменён скрыто (region × brand × revenue × order_cnt × brand_rank) |
| E2E metrics | Есть total pipeline cost (не только final SELECT) |
| Actual rows | Есть actuals / EXPLAIN ANALYZE evidence, не только estimates |
| Reproducibility | Команды и GUC позволяют повторить эксперимент |

`Environment check: PASS / BLOCKED` — prerequisite, **не** scored skill.

## Scored rubric: 100 баллов

| Раздел | Баллы | Principal / Senior evidence |
| --- | ---: | --- |
| Baseline plan diagnosis | 20 | Critical path на graded view; Motions; skew/correlation smell; first estimate error **or** proof estimates OK |
| Stats / selectivity reasoning | 15 | Concrete predicate/join → slot → sel → plan consequence |
| Physical stage design (A/B) | 20 | ≥2 explored; production winner 0–3 stages; distribution; ANALYZE; TEMP explored or rejected |
| End-to-end measurement | 20 | Full pipeline table (monolith + A + B); TEMP cost; Motion/spill; production decision |
| Reconciliation | 15 | Two-way EXCEPT ALL 0/0 + counts vs graded view; adversarial closed |
| Production risks / operability | 10 | Residual risks beyond snapshot; monitoring / rollback note |

### Уровни

| Сумма | Вердикт |
| ---: | --- |
| 90–100 | Principal (если закрыты extension-артефакты **или** distinction «do not merge» с сильным e2e; `--scale principal` усиливает) |
| 75–89 | Strong Senior — небольшая доработка evidence |
| 60–74 | Работает, но недостаточно доказано |
| &lt;60 | Повторная работа |

Senior core pass: hard gates + **≥75** по scored (без требования полной ORCA matrix).  
Principal: hard gates + **≥90** и закрытый extension block **или** выдающееся доказательное «не внедрять».

## Что не double-count

Структура `evidence.md` (A–J) оценивается внутри разделов выше.  
Отдельных баллов «за полный pack» нет — только за содержание.

Storage (Heap/AO/AOCO) входит в **Physical stage design**, если стадии создавались; отдельной строки нет.

Optimizer policy / 2×2 matrix / principal scale — **Principal extension**, не обязательны для Senior core score.

## Авто-reject (любой пункт)

- baseline/reconcile на `v_heavy_olap_monolith` вместо graded view;
- смена `optimizer` внутри rewrite comparison;
- работа не в `mentor`;
- нет two-way reconciliation 0/0;
- нет A/B сравнения (≥2 explored);
- `DISTRIBUTED RANDOMLY` на join-стадии без обоснования;
- сданный class-demo TEMP (`tmp_lesson03_sales_feb` / `_shaped`) как единственный candidate без собственной архитектуры и e2e таблицы.
