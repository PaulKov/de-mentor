# Deep-Dive: Временные Таблицы, `pg_temp` и Spill (Greenplum 6.25)

## Три Механизма (Не Путать)

| Механизм | Что это | Где на диске | Stats / distribution |
|---|---|---|---|
| **CTE / WITH** | Логическая форма запроса | Обычно нет своей relation | Нет гарантированного `ANALYZE` / `DISTRIBUTED BY` |
| **TEMP TABLE** | Явная session relation | `base/<dboid>/t_<relfilenode>` на QE | Да: `ANALYZE`, `DISTRIBUTED BY` |
| **Spill / workfiles** | Overflow Sort/Hash executor | `<datadir>/base/pgsql_tmp/pgsql_tmp_Sort_*` | Не relation; чистится после query |

Правило: «не было `CREATE TEMP` ⇒ не было диска» — **ложь**.

## Зачем TEMP В Тяжёлом OLAP

`TEMP` создаёт *новый physical stage* с собственной кардинальностью, `DISTRIBUTED BY`, `ANALYZE` и явным lifecycle в сессии. CTE этого контракта не даёт надёжно.

## Как Создаётся

```sql
CREATE TEMP TABLE tmp_stage AS
SELECT ...
DISTRIBUTED BY (join_key);

ANALYZE tmp_stage;
```

Lifecycle: `ON COMMIT PRESERVE ROWS` (default) / `DROP` / `DELETE ROWS`; конец сессии → drop `pg_temp_NNN`.

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

Артефакты: `artifacts/lesson03-temp-fs/`, скрин `artifacts/lesson03-plan-screens/temp-relfilenode-fs.png`.
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

Скрин: `artifacts/lesson03-plan-screens/spill-pgsql_tmp-growth.png`.

GUC: `statement_mem`, `max_statement_mem`, `gp_workfile_limit_*`, `gp_workfile_compression`. На GP6 `work_mem` deprecated.

## Код (`6X_STABLE`)

| Тема | Путь |
|---|---|
| Temp namespace | https://github.com/greenplum-db/gpdb/blob/6X_STABLE/src/backend/catalog/namespace.c |
| Storage | https://github.com/greenplum-db/gpdb/tree/6X_STABLE/src/backend/storage |
| Workfile manager | https://github.com/greenplum-db/gpdb/tree/6X_STABLE/src/backend/utils/workfile_manager |
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
3. при spill — `external merge Disk` + `pgsql_tmp_Sort_*`.
