# Deep-Dive: Физическое Хранение Heap / AO / AOCO

## Контракты Хранения

| Тип | Физическая идея | Когда |
| --- | --- | --- |
| Heap | row-oriented pages, MVCC, update/delete-friendly | dimensions, small staging |
| AO row | append-optimized row blocks | bulk load без частых updates |
| AOCO | append-optimized column files | scan-heavy fact, узкая projection |

## Heap: Как Лежит Строка

Упрощённо:

```text
page
  └─ item pointer
      └─ HeapTupleHeader
          ├─ fixed-length attrs
          └─ varlena attrs (text/numeric/jsonb)
                └─ TOAST, если value слишком большой
```

`numeric`, `text`, `jsonb` — varlena. Маленькие значения inline; большие уезжают в TOAST relation. Поэтому «широкий payload» в Heap раздувает row width даже если SELECT его не читает (если tuple всё равно достаётся row engine целиком).

## AO Row

Append-optimized row хранит строки блоками с AO-specific metadata (visibility/compaction модель отличается от классического heap vacuum). Для аналитических bulk insert это часто выгоднее heap, но это всё ещё row orientation: projection слабо помогает, если читаете 3 колонки из 40.

## AOCO: Column Files

В AOCO каждая колонка — отдельный физический поток (segfile / column file на сегменте). Scan с узким `SELECT` читает меньше IO.

Compression (`zstd`, `zlib`, `rle_type` и т.д.) применяется per-column encoding. Это объясняет, почему:

- low-cardinality `region`-like columns жмутся лучше;
- случайный `text payload` жмется хуже;
- выбор AOCO должен опираться на access pattern, а не на «модно».

Код/подсистемы lineage GPDB, которые стоит знать по имени:

- AOCO scan/projection path в append-optimized AM;
- `pg_appendonly` catalog metadata;
- relfile/segfile раскладка на data directory сегмента.

## Что Показать На Занятии

1. DDL AOCO fact vs Heap dim.
2. `pg_relation_size` / `\d+`.
3. План, где SELECT не трогает `payload` — аргумент в пользу column projection.
4. Контрпример: update-heavy dim в AOCO — плохой контракт.

## Не Путать С Distribution

Storage не распределяет строки по segments. `DISTRIBUTED BY` и Motion живут в другой плоскости. AOCO не лечит skew и не заменяет co-located join.
