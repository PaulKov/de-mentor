# Deep-Dive: Физическое Хранение Heap / AO / AOCO (GP 6.25)

Storage решает **IO и projection**, не Motion и не skew.  
`DISTRIBUTED BY` и optimizer — другая плоскость.

## Контракты

| Тип | Физическая идея | Когда |
|---|---|---|
| **Heap** | 8KB pages, MVCC versions, update/delete-friendly | dimensions, staging, OLTP-like |
| **AO row** | Append-optimized **row** blocks + aoseg/visimap | bulk load без частых updates |
| **AOCO** | Append-optimized **column** streams × segno | scan-heavy fact, узкая projection |

**GP6 DDL:** `appendoptimized=true` — документированный alias; в catalog/legacy output часто видно `appendonly=true`. Оба имени встречаются.

```sql
CREATE TABLE ... WITH (
  appendoptimized=true,   -- или appendonly=true
  orientation=column,     -- AOCO; row = AO row
  compresstype=zstd,
  compresslevel=1
);
```

---

## Heap: page → tuple → TOAST

```text
Page (~8KB)
  PageHeaderData
  ItemIdData[]              -- line pointers
  free space
  HeapTupleHeaderData       -- xmin/xmax, infomask, hoff, …
    null bitmap
    fixed-length attributes (+ alignment / padding)
    varlena attributes
         ├─ inline
         ├─ compressed inline
         └─ external TOAST pointer → toast relation
```

| Элемент | Смысл |
|---|---|
| `ItemIdData` | Указатель на tuple offset внутри page |
| `HeapTupleHeader` | MVCC + nulls + длина header |
| Alignment | `int8`/`timestamp` могут добавить padding |
| Forks | `main` / FSM / VM |
| Update/delete | Новые версии строк; vacuum освобождает место |

**Следствие:** row engine при чтении строки платит за **ширину tuple**, даже если в SELECT мало колонок (если tuple всё равно materialize целиком).

Код lineage: [`htup_details.h`](https://github.com/greenplum-db/gpdb-archive/blob/main/src/include/access/htup_details.h), heapam.

---

## AO Row

```text
AO segment file (segno)
  varblocks
    block header
    compressed / uncompressed row payload
  EOF / tupcount → metadata в aoseg
visimap     — какие rows видны
block directory — ускоряет positional fetch
```

| Каталог / view | Роль |
|---|---|
| `pg_appendonly` | `segrelid`, `blkdirrelid`, `visimaprelid`, … |
| `gp_aoseg` / aoseg relation | EOF, tupcount per segno |
| visimap | Visibility без классического heap HOT path |

Insert = append. Update/delete в AO модели дороже/иначе, чем в Heap — не кладите update-heavy dim в AO «потому что аналитика».

---

## AOCO (Column Orientation)

```text
Для каждой колонки × segno:
  physical column file / stream
    compressed blocks (per-column encoding)
pg_appendonly.segrelid   → aocsseg metadata
pg_appendonly.blkdirrelid
pg_appendonly.visimaprelid
```

| Свойство | Практика |
|---|---|
| Projection | Узкий `SELECT a,b` не читает payload column files |
| `SELECT *` / wide | Почти все streams → AOCO выгода падает |
| Encoding | low-cardinality (`region`) жмётся лучше, чем random `text` |
| Много мелких files | Операционный overhead на сегментах |

```sql
SELECT *
FROM pg_appendonly
WHERE relid = 'lesson03.fact_sales'::regclass;

-- GP toolkit / catalog helpers на стенде:
SELECT * FROM gp_toolkit.__gp_aocsseg('lesson03.fact_sales'::regclass)
LIMIT 20;   -- если доступно на образе
```

---

## Типы данных: физика → следствие

| Тип | Физика | Heap | AOCO |
|---|---|---|---|
| `int4`, `date` | fixed | inline | плотный stream |
| `int8`, `timestamp` | fixed + align | возможен padding | отдельный stream |
| `numeric` | varlena | шире tuple / CPU | compression зависит от данных |
| `text`, `jsonb` | varlena / TOAST | pointer или inline | свой column stream; projection спасает |
| `NULL` | null bitmap | per-tuple bitmap | column-level representation |
| `boolean` | мал логически | alignment в row layout | отдельный stream |

---

## Lab: сравнить Heap vs AO vs AOCO

Скрипт: [`lesson03-storage-heap-ao-aoco.sql`](../../../../labs/greenplum-625/examples/lesson03-storage-heap-ao-aoco.sql).

Минимум измерений на одной выборке:

1. `pg_total_relation_size` / `\d+`
2. narrow scan (`SELECT` 2–3 колонок) — runtime + plan
3. wide scan (`SELECT *` или много text) — runtime
4. (опционально) bulk `INSERT` timing

На `lesson03`: fact уже AOCO; dims — heap-friendly. Не обязательно клонировать fact в три копии на каждом уроке — достаточно показать catalog `pg_appendonly` + размеры + план с/без `payload`.

---

## Не Путать С Distribution

| Вопрос | Рычаг |
|---|---|
| Строки на каких сегментах? | `DISTRIBUTED BY` / Motion |
| Какие байты читаем с диска? | Heap / AO / AOCO + projection |
| Какие партиции? | Partition elimination |

AOCO **не** заменяет co-located join и **не** лечит data skew.
