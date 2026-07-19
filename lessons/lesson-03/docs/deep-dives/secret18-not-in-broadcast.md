# Deep-dive: Secrets #18 — `NOT IN` → Broadcast Motion

> Стенд: [`lesson03-secret18-not-in-broadcast.sql`](../../../../labs/greenplum-625/examples/lesson03-secret18-not-in-broadcast.sql)  
> Метрики: [`lessons/lesson-03/artifacts/case/secret18-not-in-broadcast-metrics.md`](../../artifacts/case/secret18-not-in-broadcast-metrics.md)  
> Идея: канал Greenplum Secrets, секрет 18 («To BE or NOT to BE»).

---

## 1. Что происходит — на пальцах

Представьте два одинаковых мешка с номерами (`t1`, `t2`), разложенных по сегментам кластера по одному и тому же ключу `n`.

Вы хотите: «дай строки из `t1`, которых **нет** в `t2`».

В SQL это часто пишут так:

```sql
SELECT t1.* FROM t1 WHERE t1.n NOT IN (SELECT n FROM t2);
```

Интуиция с OLTP/Oracle: «анти-фильтр, локально по ключу».  
В Greenplum + GPORCA реальность другая: подзапрос `NOT IN` часто превращается в **anti-join**, которому для корректной семантики `NOT IN` (особенно с `NULL`) удобнее **размножить внутреннюю сторону на все сегменты** — `Broadcast Motion`.

На проде Secrets: 100M ⋈ 100M → Broadcast всей `t2` → spill терабайтами, время ~10³× хуже, чем `NOT EXISTS` / `LEFT JOIN … IS NULL`.

---

## 2. Как это выглядит в плане (что искать)

Маркер плохого плана:

```text
Hash Left Anti Semi (Not-In) Join
  -> Seq Scan on t1
  -> Hash
       -> Broadcast Motion …:…
            -> Seq Scan on t2
```

Маркеры хороших планов:

```text
Hash Anti Join          -- NOT EXISTS
-- или --
Hash Left Join … Filter: (t2.n IS NULL)
```

без Broadcast полной большой стороны (на co-located ключах — только Gather к QD).

На lab (2 сегмента, 400k строк) смотрите **форму плана**, не абсолютные секунды.

---

## 3. Почему так — семантика + оптимизатор

### 3.1. SQL-семантика `NOT IN` ≠ `NOT EXISTS`

| Ситуация | `NOT IN (подзапрос)` | `NOT EXISTS` |
| --- | --- | --- |
| Inner без `NULL` | Обычно совпадает с anti-join | Anti-join |
| Inner содержит `NULL` | Весь предикат становится UNKNOWN → **0 строк** | Строки outer без match остаются |
| Дубликаты в inner | Ок для фильтра | Ок |

Поэтому «просто заменить оператор» — не только про скорость, но и про корректность при `NULL`.

### 3.2. Почему Broadcast

Shared-nothing: каждый сегмент видит только свою долю строк.  
Для `NOT IN` GPORCA выбирает xform в **Hash Join Not-In** и часто считает дешевле **доставить полную inner-копию на каждый сегмент**, чем Redistribute обеих сторон — особенно когда оценка rows/cost подталкивает к Broadcast.

Код GPORCA (форк Apache Cloudberry — живой tree GPORCA):

- Xform Not-In → Hash Join Not-In:  
  [`CXformLeftAntiSemiJoinNotIn2HashJoinNotIn.cpp`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/xforms/CXformLeftAntiSemiJoinNotIn2HashJoinNotIn.cpp)  
  header: [`CXformLeftAntiSemiJoinNotIn2HashJoinNotIn.h`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/include/gpopt/xforms/CXformLeftAntiSemiJoinNotIn2HashJoinNotIn.h)
- Физический Broadcast:  
  [`CPhysicalMotionBroadcast.cpp`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/operators/CPhysicalMotionBroadcast.cpp)
- Hash-distribute (альтернатива Motion):  
  [`CPhysicalMotionHashDistribute.cpp`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/operators/CPhysicalMotionHashDistribute.cpp)

Executor Motion (GPDB archive / 6.x lineage):

- [`nodeMotion.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeMotion.c)
- Путь планирования / join paths (Legacy side):  
  [`joinpath.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/optimizer/path/joinpath.c),  
  [`createplan.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/optimizer/plan/createplan.c)

### 3.3. Почему `NOT EXISTS` и `LEFT JOIN` выигрывают

Они выражают **обычный anti-join** без специальной Not-In семантики.  
При `DISTRIBUTED BY (n)` на обеих таблицах join co-located → Motion не нужен (кроме Gather результата).

`LEFT JOIN … WHERE right IS NULL` на проде в Secrets часто был чуть быстрее `NOT EXISTS`; помните про **дубликаты** в правой таблице — без `DISTINCT` outer может размножиться, если правая не уникальна по ключу.

---

## 4. Как исправлять (практический алгоритм)

1. **Заменить `NOT IN (SELECT …)` на `NOT EXISTS`** (или `LEFT JOIN` anti) при отсутствии `NULL` / после явной фильтрации `WHERE col IS NOT NULL`.
2. Проверить **distribution**: join/anti ключ = `DISTRIBUTED BY` обеих сторон.
3. Если inner крошечный и стабильный — иногда выгоднее **literal list** / hardcoded `NOT IN (1,2,3)` (см. Secrets #20), но это другой trade-off (код vs план).
4. Не «лечить» Broadcast увеличением `statement_mem`, пока форма плана — Broadcast большой таблицы.
5. Доказать: тот же `optimizer`, before/after `EXPLAIN ANALYZE`, отсутствие Broadcast большой стороны, эквивалентность результата (`EXCEPT ALL`).

---

## 5. Checklist на ревью

- [ ] В плане есть `Hash Left Anti Semi (Not-In)` + `Broadcast Motion`?
- [ ] Inner может содержать `NULL`?
- [ ] Ключи anti-join совпадают с `DISTRIBUTED BY`?
- [ ] Rewrite на `NOT EXISTS` / `LEFT JOIN` убрал Broadcast?
- [ ] Есть proof эквивалентности на фикстуре с и без `NULL`?

---

## 6. Связь с Уроком 03

Рядом с CE-traps (неверная оценка → Nested Loop) и SCD2 locus (неверный hash ключа).  
Здесь корень — **выбор оператора SQL + xform Not-In**, а не «плохая стата» как единственная причина.
