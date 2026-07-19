# План Ментора: Урок 03 (Greenplum 6.25)

## Цель Сессии

Научить Senior/Principal инженера понимать оптимизацию Greenplum по стадиям, сравнивать Legacy vs GPORCA и декомпозировать тяжёлый OLAP через план, статистику и физику хранения.

## Тайминг Simple (60 минут)

| Время | Слайды | Фокус | Вопрос ученику |
| --- | --- | --- | --- |
| 0-6 | 1-3 | Title + glossary (GUC/QD/QE/Motion) | Что такое GUC `optimizer`? |
| 6-12 | 4-7 | Стенд + pipeline + фазы дерева | Где в EXPLAIN видны slices? |
| 12-28 | 8-22 | Parse→Optimize, code map, plan trees + скрины ORCA/Legacy | Чем маркер GPORCA отличается от Legacy? |
| 28-40 | 23-30 | Case + layered EXPLAIN + Motion | Какой Motion дороже всего? |
| 40-52 | 31-39 | Stats + storage + TEMP | Зачем ANALYZE на TEMP при фиксированном GUC? |
| 52-60 | 40-43 | Proof + homework | Какой evidence обязателен? |

## Тайминг Deep (90-120 минут)

1. Glossary → code map `6X_STABLE` (gporca / gpopt / cdbpath).
2. ORCA memo/xforms/fallback + minidump.
3. Сравнение полных скринов `explain-orca.png` vs `explain-legacy.png`.
4. `pg_statistic` slots (`stakind`, `stavalues`, TOAST).
5. Физическая раскладка Heap vs AOCO (`appendonly` на GP6).
6. TEMP namespace, spill vs TEMP TABLE.
7. Design review: rewrite + optimizer policy.

## Что Не Делать

- Не уводи урок в полный WLM — это Урок 04.
- Не принимай rewrite без before/after `EXPLAIN` и без указания `SET optimizer`.
- Не предлагай AOCO как универсальный фикс медленного запроса.
- Не произноси аббревиатуры без расшифровки — начни со слайдов Glossary.

## Материалы

- PPTX: `artifacts/greenplum-query-tuning-theory.pptx`
- Google Slides: https://docs.google.com/presentation/d/1DGUBklnANac9jKpW85fTCPQ0MEiM7zEs9VnF3rN7aEA/edit?usp=sharing
- Plan screenshots: `artifacts/lesson03-plan-screens/`
- Plan text dumps: `artifacts/lesson03-plans/`
- Lab: `labs/greenplum-625/`
- SQL-lab: `labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql`
- ORCA demo: `labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql`
- Deep-dives в `docs/lessons/03-greenplum-query-tuning/deep-dives/`
