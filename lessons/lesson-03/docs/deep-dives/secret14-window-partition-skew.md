# Deep-dive: Secrets #14 — Window `PARTITION BY` константы / skew → victim segment

> Стенд: [`lesson03-secret14-window-partition-skew.sql`](../../../../labs/greenplum-625/examples/lesson03-secret14-window-partition-skew.sql)  
> Метрики: [`lessons/lesson-03/artifacts/case/secret14-window-partition-skew-metrics.md`](../../artifacts/case/secret14-window-partition-skew-metrics.md)  
> Идея: канал Greenplum Secrets, секрет 14 («Разделяй и властвуй»).

---

## 1. Что происходит — на пальцах

Оконная функция `row_number() OVER (PARTITION BY invalid_id ORDER BY version_id)` говорит базе:

> «Для **каждого** значения `invalid_id` собери **все** строки с этим значением в одном месте, отсортируй и пронумеруй».

В MPP «в одном месте» = **на одном сегменте**.  
Если таблица распределена **не** по `invalid_id`, оптимизатор обязан сделать `Redistribute Motion … Hash Key: invalid_id`.

Теперь худший случай из жизни DWH: в батче **все** `invalid_id` одинаковы (техническая константа / баг фреймворка).  
Тогда hash(константа) указывает **на один и тот же сегмент** — «жертву». Туда съезжает вся таблица (в Secrets — порядка миллиардов строк) → spill, `workfile per query size limit exceeded`.

Это не «медленный window». Это **коллапс параллелизма** до одного QE.

---

## 2. Как читать план

Плохой (ожидаемый при constant key + wrong distribution):

```text
Gather Motion
  -> WindowAgg
        Partition By: invalid_id
        Order By: version_id
        -> Sort
             -> Redistribute Motion …:…
                  Hash Key: invalid_id
                  -> Seq Scan on foo
```

Хороший (таблица уже `DISTRIBUTED BY (invalid_id)` и ключ имеет реальный NDV):

```text
Gather Motion
  -> WindowAgg
        -> Sort          -- без Redistribute
             -> Seq Scan
```

На lab с `invalid_id = 42` для всех строк фаза C (`DISTRIBUTED BY (invalid_id)`) убирает Motion, но **не восстанавливает параллелизм**: все строки и так живут на одном сегменте. Настоящий фикс для константы — **убрать бессмысленный `PARTITION BY`**.

---

## 3. Почему — модель locus для window

### 3.1. Контракт WindowAgg

Executor считает окно локально на сегменте.  
Код: [`nodeWindowAgg.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeWindowAgg.c).

Планировщик / ORCA обязаны обеспечить, что строки одного partition key не размазаны:

- ORCA sequence project / window implement:  
  [`CXformImplementSequenceProject.cpp`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/xforms/CXformImplementSequenceProject.cpp)
- Физический hash-distribute:  
  [`CPhysicalMotionHashDistribute.cpp`](https://github.com/apache/cloudberry/blob/main/src/backend/gporca/libgpopt/src/operators/CPhysicalMotionHashDistribute.cpp)
- Motion executor:  
  [`nodeMotion.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/executor/nodeMotion.c)
- Мутации распределённого плана (CDB lineage):  
  [`cdbmutate.c`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/cdb/cdbmutate.c)

### 3.2. Почему «константа» = одна жертва

`hash(constant)` детерминирован → один `gp_segment_id`.  
Redistribute **не** делает Broadcast на все сегменты; он **собирает** все строки с данным hash на целевой сегмент. При одном значении ключа цель одна.

Отсюда формулировка Secrets: «времянка DISTRIBUTED REPLICATED из 2 млрд на одном сегменте» — метафора объёма на жертве, не обязательно literal `DISTRIBUTED REPLICATED` policy.

### 3.3. Связь со skew

Даже при высоком NDV «горячий» partition key даёт тот же класс проблем (один сегмент перегружен). Константа — крайняя форма skew (NDV = 1).

---

## 4. Как исправлять

| Ситуация | Действие |
| --- | --- |
| `PARTITION BY` по техполю-константе без бизнес-смысла | Убрать partition / переписать rank (баг выше SQL) |
| Окно по реальному ключу высокой кардинальности | `DISTRIBUTED BY` = partition key (или pre-stage TEMP с тем же ключом) |
| Нужен global `row_number` без partition | `OVER (ORDER BY …)` — другой Motion (часто Gather/Sort на QD/slice), но без victim-collapse по константе |
| Падает workfile limit | Сначала форма плана / locus, не слепой рост `statement_mem` |

Алгоритм ревью:

1. Найти `WindowAgg` + `Partition By`.
2. Сверить с `DISTRIBUTED BY` таблицы.
3. Проверить NDV partition-ключей (`pg_stats.n_distinct`, `count(distinct)` на сэмпле).
4. Если NDV≈1 → эскалация в бизнес/framework, не «перелить таблицу».
5. Proof: план без Redistribute **или** осознанный single-segment + documented risk.

---

## 5. Checklist

- [ ] Есть `Redistribute … Hash Key:` равный `PARTITION BY`?
- [ ] NDV ключа на батче ≈ 1?
- [ ] Таблица распределена по другому ключу?
- [ ] Фикс — модель/rewrite, а не только память?
- [ ] Понятны trade-offs `DISTRIBUTED BY (partition_key)` при реальном skew?

---

## 6. Связь с Уроком 03

Тот же язык, что Principal SCD2 locus: читайте **Hash Key**, не только имена колонок.  
SCD2 ломает join co-location; window ломает **partition co-location**. Оба — про геометрию данных.
