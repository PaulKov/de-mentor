# Principal deep-dive: SCD2 CTE join and Motion locus

> Тонкий кейс «на эрудита». Senior видит `USING (biz_key, version_id)` и `DISTRIBUTED BY (biz_key, version_id)` и закрывает тикет. Principal читает **Hash Key** у Redistribute.

Стендовый скрипт: [`lesson03-principal-scd2-locus.sql`](../../../../labs/greenplum-625/examples/lesson03-principal-scd2-locus.sql).  
Метрики: [`lessons/lesson-03/artifacts/case/principal-scd2-locus-metrics.md`](../../artifacts/case/principal-scd2-locus-metrics.md).

Идеи в духе публичных разборов Greenplum Secrets (TG): #19 (locus CTE/`GROUP BY`) и #22 (`int` vs `int8`).

## Ловушка

Типичный SCD2-паттерн «актуальная версия»:

```sql
SELECT e.*
FROM scd2_events e
JOIN (
  SELECT biz_key, max(version_id) AS version_id
  FROM scd2_events
  GROUP BY 1
) latest
USING (biz_key, version_id);
```

Таблица:

```sql
DISTRIBUTED BY (biz_key, version_id)   -- «ключ join = ключ дистрибуции»
```

Кажется, что join **co-located**, Motion не нужен.

## Почему Motion всё равно есть

В Greenplum placement строки = hash **кортежа ключей дистрибуции**.

| Оператор | Логический ключ | Locus (hash) |
| --- | --- | --- |
| Base `scd2_events` | `(biz_key, version_id)` | hash(biz_key, version_id) |
| `HashAggregate GROUP BY biz_key` | `biz_key` | hash(biz_key) |
| Join `USING (biz_key, version_id)` | оба поля | нужно совместить locus |

`hash(biz_key, version_id)` **≠** `hash(biz_key)`.  
Поэтому ORCA вставляет `Redistribute Motion … Hash Key: biz_key` (часто на **обеих** сторонах на lab-scale).

Это не «баг CTE». Это **несовпадение distribution policy и access pattern**.

## Что не является достаточным фиксом

1. **Только `ANALYZE`** — политика дистрибуции не меняется.  
2. **TEMP только с `max(version)` `DISTRIBUTED BY (biz_key)`** — aggregate становится «правильным», но **fact** всё ещё на composite hash → Redistribute fact остаётся (фаза B в скрипте).  
3. **`SET optimizer`** — форма Motion может измениться, корень (locus) — нет.

## Настоящий фикс (physical model)

Для паттерна «latest per business key» SCD2-таблица должна жить как:

```sql
DISTRIBUTED BY (biz_key)   -- все версии ключа на одном сегменте
```

Тогда `GROUP BY biz_key` и join по `(biz_key, version_id)` выполняются **локально** (на стенде — без Redistribute, фаза C).

Trade-off: skew по «горячим» biz_key; иногда лучше отдельный current-state snapshot / TEMP full grain.

## Бонус эрудиции: `int` vs `int8`

Даже при `DISTRIBUTED BY (id)` на обеих таблицах join `int = int8` даёт:

```text
Hash Cond: (t_int8.id = (t_int.id)::bigint)
Redistribute Motion … Hash Key: (t_int.id)::bigint
```

Приведение типа меняет hash → Motion. Principal смотрит на **cast в Hash Cond / Hash Key**, не только на имена колонок.

## Checklist Principal

1. В плане есть Redistribute? Записать **Hash Key**.  
2. Совпадает ли Hash Key с `DISTRIBUTED BY` **каждого** child?  
3. CTE/`GROUP BY`/window меняют locus относительно base?  
4. Есть ли `::bigint` / `::numeric` / `text` cast на join key?  
5. Фикс: physical distribution / TEMP **полного** grain / rewrite — не «ещё один ANALYZE».

## Связь с Уроком 03

Рядом с CE-traps (ORCA NLJ / Legacy Semi): там ломается **оценка кардинальности**, здесь — **геометрия данных (locus)**. Оба требуют TEMP/модели, но разные корни.
