# Deep-dive: Secrets #29 — `VALUES`/CTE-параметры → Broadcast факта

> Стенд: [`lesson03-secret29-values-params-broadcast.sql`](../../../../labs/greenplum-625/examples/lesson03-secret29-values-params-broadcast.sql)  
> Метрики: [`lessons/lesson-03/artifacts/case/secret29-values-params-broadcast-metrics.md`](../../artifacts/case/secret29-values-params-broadcast-metrics.md)  
> Идея: канал Greenplum Secrets, секрет 29 («Красиво не значит правильно»).

---

## 1. Что происходит — на пальцах

Отчёту нужны параметры: `mdm_id`, даты периода. Автор «красиво» кладёт их в CTE:

```sql
WITH data_batch AS (
  SELECT … FROM (VALUES (0, '10', '2024-01-01', …)) t(…)
)
SELECT … FROM big_fact s0 JOIN data_batch b ON b.mdm_id = s0.n_txt;
```

Интуиция: «слева одна строка параметров — она и разъедется по сегментам».  
План на таблице **без ключа и без статистики** часто говорит обратное:

- параметры остаются «крошечной» стороной (`Result` / иногда `One-Time Filter: gp_execution_segment() = N` на большом кластере);
- **факт** двигается к параметрам: на проде Secrets — `Broadcast Motion` fact на все сегменты; на lab GP 6.25 (2 сегмента) ORCA часто делает `Gather Motion` fact на QD и Hash Join там.

Общий антипаттерн один: тиражируется / собирается **не параметр, а большая таблица**. Причина — CE (`rows≈1` без ANALYZE) + отсутствие полезного `DISTRIBUTED BY`.

---

## 2. Три режима (как в Secrets) — что → какой Motion

| Состояние fact | Типичный Motion | Смысл |
| --- | --- | --- |
| `DISTRIBUTED RANDOMLY`, **без** `ANALYZE` | Secrets: **Broadcast** fact; lab 2-seg: **Gather** fact→QD | CE `rows≈1` → «дешево» двигать fact |
| `DISTRIBUTED BY (join_key)` (+ стата) | Часто без Broadcast/Gather fact | Join на сегментах по hash ключа |
| `DISTRIBUTED RANDOMLY` + `ANALYZE` | Часто **Redistribute** fact по join key | Стата честнее |

Маркер плохого плана (фаза A, lab 2-seg):

```text
Hash Join                    -- often on QD
  -> Result (VALUES params)
  -> Hash
       -> Gather Motion 2:1
            -> Seq Scan on fact
```

Маркер плохого плана (Secrets / multi-seg):

```text
Hash Join
  -> Result … One-Time Filter: (gp_execution_segment() = …)
  -> Hash
       -> Broadcast Motion
            -> Seq Scan on fact
```

Маркер улучшения (фаза B, `DISTRIBUTED BY (n_txt)`):

```text
Hash Join
  -> Result (params)
  -> Hash
       -> Seq Scan on fact     -- без Broadcast fact
```

---

## 3. Почему — cost model + locus констант

### 3.1. Константный tuple и segment affinity

`VALUES` / Result для констант часто исполняется с привязкой к одному сегменту (one-time filter).  
Это нормальный трюк распределённого executor’а: не плодить одинаковые константы везде без нужды.  
Но join с большой стороной без правильной дистрибуции заставляет двигать **большую** сторону.

### 3.2. CE без статистики

Без `ANALYZE` ORCA/Legacy опираются на default selectivity / default pages.  
Заниженный `rows` на fact → Broadcast выглядит дёшево в cost model (та же семья ошибок, что CE-traps Урока 03).

Код якоря:

- Broadcast operator:  
  [`CPhysicalMotionBroadcast.cpp`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp)
- Hash redistribute:  
  [`CPhysicalMotionHashDistribute.cpp`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/operators/CPhysicalMotionHashDistribute.cpp)
- Motion executor:  
  [`nodeMotion.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeMotion.c)
- Планировщик / create plan (Legacy lineage):  
  [`planner.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/optimizer/plan/planner.c),  
  [`createplan.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/optimizer/plan/createplan.c)
- Selectivity defaults (Legacy):  
  [`selfuncs.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/utils/adt/selfuncs.c)

### 3.3. Родственный антипаттерн: `IN (VALUES …)` vs `IN (1,2,3)`

Отдельный пост Secrets (после #29 / quiz):  
`WHERE id IN (VALUES (1),(2),(3))` → Hash Join + Motion;  
`WHERE id IN (1,2,3)` → `Filter: (id = ANY ('{1,2,3}'::…))` без join.

Фаза E стендового SQL показывает разницу на lab. Не оборачивайте короткий список в `VALUES`, если нужен scalar array op.

---

## 4. Как исправлять

1. **Предпочтительно для отчётных параметров:** литералы / bind-параметры в `WHERE`, не CTE-`VALUES` join.
2. Если join к справочнику параметров неизбежен — fact **`DISTRIBUTED BY` ключу join** + актуальный `ANALYZE`.
3. Маленький param-set можно материализовать в TEMP `DISTRIBUTED REPLICATED` / broadcast-friendly table — но сначала измерьте план.
4. Не путать «красивый SQL» с дешёвым Motion: всегда смотреть, **какая** сторона в Broadcast.
5. Proof: before/after форма Motion + wall time при том же `optimizer`.

---

## 5. Checklist

- [ ] Параметры завёрнуты в `VALUES`/CTE и join’ятся к fact?
- [ ] В плане Broadcast/Redistribute именно **fact**?
- [ ] Есть `One-Time Filter: gp_execution_segment()` на params?
- [ ] У fact есть `DISTRIBUTED BY` join-ключа и свежий `ANALYZE`?
- [ ] Можно ли заменить join на `WHERE col = …` / `IN (…)` list?

---

## 6. Связь с Уроком 03

Мост к Secrets #18 (Broadcast не той стороны) и CE-traps (заниженный rows → плохой выбор Motion/join).  
Правило Principal: в плане читайте **какую таблицу** двигает Motion, не только слово Broadcast.
