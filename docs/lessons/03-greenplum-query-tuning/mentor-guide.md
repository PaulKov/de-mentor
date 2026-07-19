# План Ментора: Урок 03 (Greenplum 6.25)

## Цель Сессии

Научить Senior/Principal инженера понимать оптимизацию Greenplum по стадиям, сравнивать Legacy vs GPORCA и декомпозировать тяжёлый OLAP через план, статистику и физику хранения.

## Тайминг Simple (60 минут)

| Время | Слайды | Фокус | Вопрос ученику |
| --- | --- | --- | --- |
| 0-8 | 1-4 | Title + glossary (GUC, Motion, **star-join**) | Что такое star-join vs snowflake? |
| 8-14 | 5-8 | Стенд + pipeline + фазы дерева | Где в EXPLAIN видны slices? |
| 14-30 | 9-25 | Parse→Optimize, star-join deep, plan trees ORCA/Legacy | Чем маркер GPORCA отличается от Legacy? |
| 30-40 | 26-36 | Case + layered EXPLAIN + Motion + stats | Какой Motion дороже всего? |
| 40-52 | 37-51 | Storage + TEMP FS/spill deep-dive | Где на диске TEMP vs pgsql_tmp_Sort? |
| 52-60 | 52-55 | Proof + homework | Какой evidence обязателен? |

## Тайминг Deep (90-120 минут)

1. Glossary → code map `6X_STABLE` (gporca / gpopt / cdbpath).
2. ORCA memo/xforms/fallback + minidump.
3. Сравнение полных скринов `explain-orca.png` vs `explain-legacy.png`.
4. `pg_statistic` slots (`stakind`, `stavalues`, TOAST).
5. Физическая раскладка Heap vs AOCO (`appendonly` на GP6).
6. TEMP: `pg_temp` / `t_*` relfilenode на QE + spill `pgsql_tmp_Sort_*` (скрины FS).
7. Design review: rewrite + optimizer policy.

## Что Не Делать

- Не уводи урок в полный WLM — это Урок 04.
- Не принимай rewrite без before/after `EXPLAIN` и без указания `SET optimizer`.
- Не предлагай AOCO как универсальный фикс медленного запроса.
- Не произноси аббревиатуры без расшифровки — начни со слайдов Glossary.

## Материалы

- PPTX: `artifacts/greenplum-query-tuning-theory.pptx`
- Google Slides: https://docs.google.com/presentation/d/1_YfYh4Kf-8Xblule_pprHwlxRlFDBpn4K14i6w18H5U/edit?usp=sharing
- Plan screenshots: `artifacts/lesson03-plan-screens/`
- TEMP/spill FS evidence: `artifacts/lesson03-temp-fs/`
- Plan text dumps: `artifacts/lesson03-plans/`
- Lab: `labs/greenplum-625/`
- SQL-lab: `labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql`
- ORCA demo: `labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql`
- Deep-dives в `docs/lessons/03-greenplum-query-tuning/deep-dives/`
