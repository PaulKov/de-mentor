# Deep-dive: Secrets #38 — медиана / ordered-set → Gather на QD

> Стенд: [`lesson03-secret38-median-gather-qd.sql`](../../../../labs/greenplum-625/examples/lesson03-secret38-median-gather-qd.sql)  
> Метрики: [`lessons/lesson-03/artifacts/case/secret38-median-gather-qd-metrics.md`](../../artifacts/case/secret38-median-gather-qd-metrics.md)

---

## 1. Что — на пальцах

Медиана — не `avg`. Нужен **полный порядок** множества:

```sql
SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n) AS median FROM tst;
```

В MPP «полный порядок» почти всегда значит: **собрать (почти) все строки на мастер (QD)** → `Gather Motion …:1` → `Aggregate` на slice0.  
Сегменты почти не помогают в финальной сортировке — pure MPP anti-pattern для глобальных ordered-set aggregates.

Secrets: 100M rows, Legacy planner, ~74s exact vs ~2.3s approximate local medians (×31).

---

## 2. Как в плане

Плохой (точный global percentile):

```text
Aggregate
  -> Gather Motion N:1
       -> Seq Scan on tst     -- почти все строки едут на QD
```

Приближение (случайные шарды):

```sql
SELECT avg(median) FROM (
  SELECT percentile_disc(0.5) WITHIN GROUP (ORDER BY n) AS median
  FROM tst
  GROUP BY gp_segment_id
) s;
```

Каждый сегмент считает локальную медиану (мало строк) → Gather крошечного числа значений → `avg` на QD.

---

## 3. Почему

Ordered-set aggregates (`percentile_disc` / `percentile_cont`, `mode`, …) требуют sorted input всего group.  
Глобальная группа без `GROUP BY` = один group на весь кластер → данные к QD.

Код:

- Ordered-set aggs: [`orderedsetaggs.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/utils/adt/orderedsetaggs.c)
- Agg node: [`nodeAgg.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeAgg.c)
- Motion: [`nodeMotion.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeMotion.c)

Почему `DISTRIBUTED RANDOMLY` важен для approx: каждый сегмент ≈ случайная подвыборка → локальные медианы близки к глобальной; среднее локальных ≈ глобальная. На hash-dist по другому ключу приближение может врать сильнее.

`percentile_disc(0.5)` vs `percentile_cont(0.5)`: disc берёт элемент порядка; cont — интерполяцию (для 1..1000 → 500 vs 500.5).

---

## 4. Как исправлять

| Цель | Действие |
| --- | --- |
| Точная медиана | Мириться с Gather / pre-aggregate / sample с доверительным интервалом |
| Быстрый approximate | Local median + `avg` при RANDOM (или осознанный sample) |
| Отчётность | Явно помечать approximate; не смешивать с финансовым exact |
| Альтернативы | `approx_percentile` (если есть в сборке), внешний stats job |

---

## 5. Checklist

- [ ] В плане `Gather` почти всех rows перед ordered-set Agg?
- [ ] Нужен exact или approx?
- [ ] Distribution RANDOM / i.i.d. для local-median трюка?
- [ ] Proof: exact vs approx на lab + допуск ошибки?
