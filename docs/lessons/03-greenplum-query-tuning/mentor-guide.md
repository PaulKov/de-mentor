# План Ментора: Урок 03 (Greenplum 6.25)

## Цель Сессии

Научить Senior/Principal инженера понимать оптимизацию Greenplum по стадиям, сравнивать Legacy vs GPORCA и декомпозировать тяжёлый OLAP через план, статистику и физику хранения.

## Тайминг Simple (60 минут)

| Время | Слайды | Фокус | Вопрос ученику |
| --- | --- | --- | --- |
| 0-6 | 1-4 | Glossary (GUC, Motion, star-join) | Что такое star-join vs snowflake? |
| 6-12 | 5-8 | Стенд + pipeline | Где в EXPLAIN видны slices? |
| 12-24 | 9-25 | Optimize, star-join, plan trees ORCA/Legacy | Чем маркер GPORCA отличается от Legacy? |
| 24-32 | 26-35 | Case + Motion + estimates alarm | Какой Motion дороже всего? |
| 32-44 | 36-48 | **Stats deep**: hist/MCV/selectivity/GROUP BY/fail→TEMP | Чем equi-depth histogram отличается от MCV? |
| 44-56 | 49-62 | Storage + TEMP FS/spill | Где на диске TEMP vs `pgsql_tmp_Sort_*`? |
| 56-60 | 63-65 | Proof + homework | Какой evidence обязателен? |

## Тайминг Deep (90-120 минут)

1. Glossary → code map `6X_STABLE` (gporca / gpopt / cdbpath).
2. Stats deep-dive: equi-depth histogram, MCV freqs, selectivity, GROUP BY NDV; когда stats не спасают → TEMP.
3. ORCA memo/xforms/fallback + minidump; скрины ORCA vs Legacy.
4. `pg_statistic` slots (`stakind`, `stavalues`, TOAST).
5. Физическая раскладка Heap vs AOCO (`appendonly` на GP6).
6. TEMP: `pg_temp` / `t_*` на QE + spill `pgsql_tmp_Sort_*`.
7. Design review: rewrite + optimizer + stats policy.

## Что Не Делать

- Не уводи урок в полный WLM — это Урок 04.
- Не принимай rewrite без before/after `EXPLAIN` и без указания `SET optimizer`.
- Не предлагай AOCO как универсальный фикс медленного запроса.
- Не произноси аббревиатуры без расшифровки — начни со слайдов Glossary.
- Не говори «просто ANALYZE», не показав `rows` vs `actual` и `pg_stats`.

## Материалы

- PPTX: `artifacts/greenplum-query-tuning-theory.pptx`
- Google Slides: https://docs.google.com/presentation/d/1e5vpqatw6ccgeZF0PWLLWMzIqkb4SODE-IwKxrSyqB8/edit?usp=sharing
- Plan / stats screenshots: `artifacts/lesson03-plan-screens/`
- TEMP/spill FS evidence: `artifacts/lesson03-temp-fs/`
- Stats dumps: `artifacts/lesson03-stats/`
- Plan text dumps: `artifacts/lesson03-plans/`
- Lab: `labs/greenplum-625/`
- SQL-lab: `labs/greenplum-625/examples/lesson03-olap-decomposition-tuning.sql`
- ORCA demo: `labs/greenplum-625/examples/lesson03-optimizer-legacy-vs-orca.sql`
- Deep-dives в `docs/lessons/03-greenplum-query-tuning/deep-dives/`
