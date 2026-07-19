# Deep-Dive: Временные Таблицы, `pg_temp` и Spill (Greenplum 6.25)

## Три Механизма (Не Путать)

| Механизм | Что это | Где на диске | Stats / distribution |
|---|---|---|---|
| **CTE / WITH** | Логическая форма запроса | Обычно нет своей relation | Нет гарантированного `ANALYZE` / `DISTRIBUTED BY` |
| **TEMP TABLE** | Явная session relation | `base/<dboid>/t_<relfilenode>` на QE | Да: `ANALYZE`, `DISTRIBUTED BY` |
| **Spill / workfiles** | Overflow Sort/Hash executor | `<datadir>/base/pgsql_tmp/pgsql_tmp_Sort_*` | Не relation; чистится после query |

Правило: «не было `CREATE TEMP` ⇒ не было диска» — **ложь**.

---

## Для Чайника: Что Такое «Сессия» Пользователя

Представьте: вы открыли `psql` (или DBeaver / JDBC) и подключились к БД `mentor`.

```text
Ваш клиент  ──TCP──►  процесс на master (QD / backend)
                         │
                         ├── «сессия» = это живое соединение
                         ├── у сессии свой backend id
                         └── свой временный schema: pg_temp_<N>
```

**Сессия** — это одно активное соединение клиента с сервером (один backend-процесс на QD).  
Пока соединение живо — живёт и ваш `pg_temp_*`.  
Закрыли клиент / оборвался TCP / `pg_terminate_backend` → сессия умерла → **все TEMP этой сессии уничтожены**.

Важно:

| Миф | Реальность |
|---|---|
| «TEMP общая на всех» | Нет. Чужая сессия **не видит** ваш TEMP (и не должна). |
| «TEMP = на время одной транзакции» | Только если вы явно сказали `ON COMMIT DROP` / `DELETE ROWS`. Default — **до конца сессии**. |
| «TEMP на master» | Catalog/координация на QD; **данные** лежат на сегментах (QE), как у обычных таблиц. |

Проверить «кто я в сессии»:

```sql
SELECT
    pg_backend_pid()          AS backend_pid,      -- PID процесса QD
    current_setting('application_name') AS app,
    inet_client_addr()        AS client_ip,
    pg_my_temp_schema()::regnamespace AS my_temp_schema;  -- pg_temp_NNN или 0
```

В `pg_stat_activity` ваша строка = ваша сессия:

```sql
SELECT pid, usename, application_name, state, query_start, left(query, 60)
FROM pg_stat_activity
WHERE pid = pg_backend_pid();
```

---

## ON COMMIT: Три Режима Lifecycle TEMP

Синтаксис:

```sql
CREATE TEMP TABLE tmp_x (...)
ON COMMIT { PRESERVE ROWS | DELETE ROWS | DROP }
DISTRIBUTED BY (...);
-- или CREATE TEMP TABLE tmp_x AS SELECT ... ON COMMIT ...
```

| Режим | Default? | Что после `COMMIT` | Что после `ROLLBACK` | Что в конце сессии |
|---|---|---|---|---|
| **PRESERVE ROWS** | **да** | Таблица **и строки** остаются | Откат незакоммиченных изменений (как обычно) | `DROP` всего TEMP |
| **DELETE ROWS** | нет | Таблица остаётся, **строки очищаются** | Откат незакоммиченного; уже закоммиченные очистки остаются | `DROP` |
| **DROP** | нет | Таблица **удаляется целиком** | Если CREATE ещё не закоммичен — таблицы как будто не было | — |

### Сессионный vs транзакционный взгляд

```text
СЕССИЯ (connection)
  └── транзакция 1  BEGIN … COMMIT
  └── транзакция 2  BEGIN … COMMIT
  └── …
  └── disconnect → конец сессии
```

- **Сессионный режим мышления (default PRESERVE ROWS):**  
  TEMP — «черновик на всю работу в этом подключении». Пережил много `COMMIT`, умер при disconnect.

- **Транзакционный режим мышления (DROP / DELETE ROWS):**  
  TEMP привязан к границам транзакции сильнее:
  - `ON COMMIT DROP` — «временная таблица на одну транзакцию»;
  - `ON COMMIT DELETE ROWS` — «каркас таблицы на сессию, данные только внутри транзакции».

### Примеры (копипаста)

**A. PRESERVE ROWS (default) — stage на всю сессию**

```sql
BEGIN;
CREATE TEMP TABLE tmp_preserve AS
SELECT customer_id, amount
FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01'
DISTRIBUTED BY (customer_id)
ON COMMIT PRESERVE ROWS;
ANALYZE tmp_preserve;
COMMIT;

-- таблица ЖИВА после COMMIT
SELECT count(*) FROM tmp_preserve;

-- в другом окле psql (другая сессия) этого объекта НЕТ
```

**B. DELETE ROWS — каркас живёт, данные после COMMIT пустые**

```sql
BEGIN;
CREATE TEMP TABLE tmp_del (
    customer_id int,
    amount numeric
) DISTRIBUTED BY (customer_id)
ON COMMIT DELETE ROWS;

INSERT INTO tmp_del VALUES (1, 10.0);
SELECT count(*) FROM tmp_del;   -- 1
COMMIT;

SELECT count(*) FROM tmp_del;   -- 0  (таблица есть, строк нет)
\d tmp_del                      -- relation ещё существует
```

**C. DROP — после COMMIT таблицы нет**

```sql
BEGIN;
CREATE TEMP TABLE tmp_drop AS
SELECT 1 AS x
DISTRIBUTED BY (x)
ON COMMIT DROP;
SELECT * FROM tmp_drop;         -- ok внутри транзакции
COMMIT;

SELECT * FROM tmp_drop;         -- ERROR: relation "tmp_drop" does not exist
```

**D. ROLLBACK после CREATE**

```sql
BEGIN;
CREATE TEMP TABLE tmp_rb AS SELECT 1 AS x DISTRIBUTED BY (x);
ROLLBACK;
SELECT * FROM tmp_rb;           -- не существует (CREATE откатили)
```

Демо-скрипт: [`lesson03-temp-on-commit-lifecycle.sql`](../../../../labs/greenplum-625/examples/lesson03-temp-on-commit-lifecycle.sql).

---

## Когда TEMP Удаляется (Чеклист)

| Событие | PRESERVE | DELETE ROWS | DROP |
|---|---|---|---|
| `COMMIT` | живёт | строки → 0 | **удалена** |
| `ROLLBACK` (после CREATE в той же txn) | CREATE откатан | CREATE откатан | CREATE откатан |
| Явный `DROP TABLE tmp` | удалена | удалена | — |
| Конец сессии (disconnect) | **удалена** | **удалена** | уже нет |
| `pg_terminate_backend(pid)` | **удалена** | **удалена** | — |
| Падение backend / timeout idle | **удалена** | **удалена** | — |

TEMP **не** переживает reconnect. Новый `psql` = новая сессия = новый пустой `pg_temp_*`.

---

## Как Понять, Что TEMP Ещё Существует

### 1) В той же сессии (самый простой способ)

```sql
\dt                       -- список; TEMP часто помечены как temporary
\d tmp_preserve           -- описание, если имя помните
SELECT to_regclass('tmp_preserve');   -- oid или NULL
```

### 2) Каталог Greenplum / PostgreSQL lineage

```sql
-- Ваш временный schema
SELECT pg_my_temp_schema()::regnamespace AS my_temp;

-- Все TEMP этой сессии
SELECT
    n.nspname,
    c.relname,
    c.relpersistence,                 -- 't' = temporary
    c.relkind,
    c.reltuples,                      -- оценка rows (после ANALYZE точнее)
    pg_relation_filepath(c.oid) AS filepath,
    pg_size_pretty(pg_relation_size(c.oid)) AS size_qd_view
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.oid = pg_my_temp_schema()
ORDER BY c.relname;
```

Ключи каталога:

| Поле | Смысл |
|---|---|
| `pg_namespace.nspname = pg_temp_<N>` | Временный schema сессии |
| `pg_class.relpersistence = 't'` | Временная relation |
| `pg_toast_temp_<N>` | Toast для широких значений TEMP |
| `pg_relation_filepath` | `base/<dboid>/t_<relfilenode>` |

### 3) Видит ли «чужая» сессия?

Обычно **нет** в смысле использования.  
Суперпользователь может увидеть чужие `pg_temp_%` в `pg_namespace`, но это не «общая таблица для join из другого окна».

```sql
-- обзор временных schema (часто только у суперюзера информативно)
SELECT nspname
FROM pg_namespace
WHERE nspname LIKE 'pg_temp%'
ORDER BY 1;
```

### 4) Файлы на сегментах (ops)

```sql
SELECT pg_relation_filepath('tmp_preserve'::regclass);
-- пример: base/12812/t_16465
```

На сегментах ищите `t_<relfilenode>` под `base/<dboid>/`.  
На master часто **0 bytes** (placeholder); байты — на QE.

---

## Зачем TEMP В Тяжёлом OLAP

`TEMP` создаёт *новый physical stage* с собственной кардинальностью, `DISTRIBUTED BY`, `ANALYZE` и явным lifecycle в сессии. CTE этого контракта не даёт надёжно.

## Как Создаётся (паттерн урока)

```sql
CREATE TEMP TABLE tmp_stage AS
SELECT ...
DISTRIBUTED BY (join_key);
-- ON COMMIT PRESERVE ROWS подразумевается

ANALYZE tmp_stage;
```

Особенности GPDB: TEMP распределённая; `DISTRIBUTED BY` должен совпадать со следующим join; before/after при фиксированном `SET optimizer`.

## Где Живёт TEMP (Каталог + QD/QE)

1. **Namespace:** `pg_temp_NNN` (+ `pg_toast_temp_NNN`), session-local.
2. **Catalog:** `pg_class` / `pg_attribute`, `relpersistence = 't'`.
3. **Filepath:** `pg_relation_filepath` → `base/<dboid>/t_<relfilenode>`.
4. **QD:** часто 0-byte placeholder.
5. **QE:** реальные байты по distribution key.

### Живой Снимок `greenplum-625`

```text
nspname=pg_temp_787  relname=tmp_fs_demo  filepath=base/12812/t_16465

/data/master/gpsne-1/base/12812/t_16465   0 bytes
/data/data1/gpsne0/base/12812/t_16465     1146880 bytes
/data/data2/gpsne1/base/12812/t_16465     1212416 bytes
```

Артефакты: `lessons/lesson-03/artifacts/temp-fs/`, скрин `lessons/lesson-03/artifacts/plan-screens/temp-relfilenode-fs.png`.  
`pgsql_tmp` при создании TEMP **пуст**.

## Spill / Workfiles

```text
<datadir>/base/pgsql_tmp/pgsql_tmp_Sort_<slice>_<pid>.0
```

Демо:

```sql
SET optimizer = off;
SET statement_mem = '8MB';
EXPLAIN ANALYZE
SELECT customer_id, product_id, amount, sale_date
FROM tmp_spill_fuel
ORDER BY amount DESC, customer_id, product_id, sale_date;
```

План: `Sort Method: external merge Disk: 34592kB`, `Memory used: 8192kB`, `Memory wanted: 58688kB`.

Рост FS (poll): `pgsql_tmp_Sort_*.0` ~0.4MB → ~17MB на сегмент, после query cleanup.

Скрин: `lessons/lesson-03/artifacts/plan-screens/spill-pgsql_tmp-growth.png`.

GUC: `statement_mem`, `max_statement_mem`, `gp_workfile_limit_*`, `gp_workfile_compression`. На GP6 `work_mem` deprecated.

## Код (якоря)

| Тема | Путь |
|---|---|
| Temp namespace | https://github.com/greenplum-db/gpdb-archive/blob/main/src/backend/catalog/namespace.c |
| Storage | https://github.com/greenplum-db/gpdb-archive/tree/main/src/backend/storage |
| Workfile manager | https://github.com/greenplum-db/gpdb-archive/tree/main/src/backend/utils/workfile_manager |
| Docs spill | https://techdocs.broadcom.com/us/en/vmware-tanzu/data-solutions/tanzu-greenplum/6/greenplum-database/admin_guide-query-topics-spill-files.html |

## Плюсы / Минусы

**Плюсы:** grain + distribution; ANALYZE; reuse в сессии; доказуемый rewrite.  
**Минусы:** double IO; диск на всех сегментах; catalog overhead; риск без ANALYZE / неверного DISTRIBUTED BY.

## Когда Хорошо / Плохо

**Хорошо:** узкое окно; grain под join; повтор stage; стабилизация плана.  
**Плохо:** весь fact; нет ANALYZE; distribution мимо join; рой мелких TEMP; игнор spill.

## Evidence Pack

1. before/after `EXPLAIN` при том же `optimizer`;
2. `pg_relation_filepath` / размеры `t_*`;
3. при spill — `external merge Disk` + `pgsql_tmp_Sort_*`;
4. для lifecycle — доказательство `ON COMMIT` режимом (PRESERVE / DELETE / DROP) + catalog query.
