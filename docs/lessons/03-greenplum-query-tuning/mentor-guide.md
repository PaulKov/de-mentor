# План Ментора: Урок 03 (Greenplum 6.25)

## Цель Сессии

Научить Senior/Principal инженера понимать оптимизацию Greenplum по стадиям, сравнивать Legacy vs GPORCA и декомпозировать тяжёлый OLAP через план, статистику и физику хранения.

## Тайминг Simple (60 минут)

| Время | Слайды | Фокус | Вопрос ученику |
| --- | --- | --- | --- |
| 0-8 | 1-5 | Стенд GP 6.25 + pipeline optimize | Где выбирается Legacy/ORCA? |
| 8-22 | 6-14 | Legacy vs GPORCA | Когда ORCA избыточен? |
| 22-35 | 15-19 | Case + layered EXPLAIN | Какой Motion дороже всего? |
| 35-48 | 20-27 | Stats + storage + TEMP | Зачем ANALYZE на TEMP при фиксированном optimizer? |
| 48-60 | 28-30 | Proof + homework | Какой evidence обязателен? |

## Тайминг Deep (90-120 минут)

1. ORCA memo/xforms/fallback + minidump.
2. `pg_statistic` slots (`stakind`, `stavalues`, TOAST).
3. Физическая раскладка Heap vs AOCO (`appendonly` на GP6).
4. TEMP namespace, spill vs TEMP TABLE.
5. Design review: rewrite + optimizer policy.

## Что Не Делать

- Не уводи урок в полный WLM — это Урок 04.
- Не принимай rewrite без before/after `EXPLAIN` и без указания `SET optimizer`.
- Не предлагай AOCO как универсальный фикс медленного запроса.

## Материалы

- PPTX: `artifacts/greenplum-query-tuning-theory.pptx`
- Google Slides: https://docs.google.com/presentation/d/1PMJJ8_EB65GfS0Ndj0hUSudCPwWyKEMt__GAz5rEGPU/edit?usp=sharing
- Lab: `labs/greenplum-625/`
- SQL-lab: `labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql`
- ORCA demo: `labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql`
- Deep-dives в `docs/lessons/03-greenplum-query-tuning/deep-dives/`
