# Deep-dive: Secrets #42 — `COUNT(DISTINCT)` частями через `gp_segment_id`

> Стенд: [`lesson03-secret42-distinct-by-segment.sql`](../../../../labs/greenplum-625/examples/lesson03-secret42-distinct-by-segment.sql)  
> Метрики: [`lessons/lesson-03/artifacts/case/secret42-distinct-by-segment-metrics.md`](../../artifacts/case/secret42-distinct-by-segment-metrics.md)

---

## 1. Что — на пальцах

Нужно число уникальных `id` в огромной AOCO-таблице:

```sql
SELECT count(DISTINCT id) FROM tst;
```

На проде Secrets (50B rows, `id` = ключ дистрибуции) канонический запрос **таймаутился ~1ч**.  
Тот же ответ быстрее дал «map → reduce»:

```sql
SELECT sum(cnt) FROM (
  SELECT gp_segment_id, count(DISTINCT id) AS cnt FROM tst GROUP BY 1
) s;
```

Интуиция: «раз уж каждый `id` и так живёт на одном сегменте — посчитай уники локально и сложи».

---

## 2. Как в плане

Канон (Secrets, ORCA): per-segment `Aggregate` + `Gather` частичных результатов, но **тяжёлый spill** на сегментах (`Memory wanted` гораздо больше `Memory used`).

Map-версия: двухфазный `HashAggregate` с `Group Key: (gp_segment_id, id)` → дальше агрегация по сегменту → `sum` на QD. На lab смотрите форму и wall time, не 50B.

---

## 3. Почему это (иногда) корректно

| Условие | `sum(local count distinct)` |
| --- | --- |
| `DISTRIBUTED BY (id)` (или DISTINCT-колонки ⊆ dist key) | **Точно** = глобальный `count(DISTINCT)` |
| `DISTRIBUTED RANDOMLY` / другой ключ | **Завышение**: один `id` может быть на нескольких seg |

Служебное поле `gp_segment_id` — готовый ключ локальности строки (см. также Secrets #11 про уникальность `ctid`+`gp_segment_id`).

Код якоря:

- Agg executor: [`nodeAgg.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeAgg.c)
- ORCA GbAgg→HashAgg: [`CXformGbAgg2HashAgg.cpp`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/xforms/CXformGbAgg2HashAgg.cpp)
- Motion: [`nodeMotion.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeMotion.c)

---

## 4. Как исправлять / применять

1. Проверить: DISTINCT-выражение ⊆ `DISTRIBUTED BY` (или доказать, что значения не пересекают сегменты).
2. Rewrite map/sum; сравнить `EXPLAIN ANALYZE` и spill.
3. Обязательный proof: `canonical = mapped` на фикстуре; отдельный negative case на `DISTRIBUTED RANDOMLY`.
4. Не применять «вслепую» на произвольный DISTINCT по не-dist колонкам.

---

## 5. Checklist

- [ ] Dist key покрывает DISTINCT?
- [ ] Есть proof равенства + negative case?
- [ ] Spill/mem wanted уменьшился?
- [ ] Документирован контракт exact vs approx?
