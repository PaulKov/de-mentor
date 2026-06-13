# Partitioning Strategies In Greenplum

Этот deep dive нужен как мост между первым уроком и `Lesson 02: Partitioning, statistics and incremental loads in MPP`. В первом уроке достаточно показать идею, но у ментора должен быть готовый профессиональный слой глубины: стратегии, defaults, catalog checks, maintenance и типовые ловушки.

Runnable SQL:

```sql
\i /mentor-lab/examples/partitioning-strategies.sql
```

## Самая Короткая Модель

```text
Distribution key -> на каком segment живет строка.
Partition key    -> в какой logical child table попадает строка.
```

Partition key не равен distribution key. Один и тот же leaf partition в Greenplum все равно распределен по segments через `DISTRIBUTED BY`. Поэтому partitioning помогает pruning/retention/maintenance, а distribution помогает parallel placement, join locality и skew control.

## RANGE / LIST / HASH

| Стратегия | Когда выбирать | Пример ключа | Сильная сторона | Риск |
| --- | --- | --- | --- | --- |
| `PARTITION BY RANGE` | Факты с временными фильтрами и retention. | `sale_date`, `event_date`, `business_dt`. | Partition pruning и быстрое удаление старых периодов. | Слишком много мелких partitions увеличивают planning/maintenance overhead. |
| `PARTITION BY LIST` | Небольшой конечный набор бизнес-категорий. | `region`, `tenant_group`, `source_system`. | Простая изоляция lifecycle или hot/cold categories. | Новое значение уйдет в `DEFAULT` partition или получит out-of-range INSERT error. |
| `PARTITION BY HASH` | Нужны стабильные buckets без естественного range/list. | `tenant_id`, `customer_id`, synthetic bucket. | Ровнее buckets для maintenance или parallel local operations. | Не помогает date pruning и retention по времени. |

Greenplum 7 поддерживает modern declarative partitioning, включая `RANGE`, `LIST` и `HASH`. Для Greenplum 6 и legacy scripts часто встречается classic syntax, но в учебном Docker-стенде `woblerr/greenplum:7.1.0` используем modern syntax.

## Defaults

Важно проговорить defaults явно:

- no default partitioning: таблица не становится partitioned сама по себе;
- `DEFAULT partition` не создается автоматически, его нужно объявить явно;
- если нет matching partition и нет `DEFAULT partition`, out-of-range INSERT будет отвергнут;
- слишком широкий `DEFAULT partition` полезен как safety net, но опасен как мусорный бак для неучтенных значений;
- новые будущие периоды не появляются автоматически: их добавляют DDL/automation, например `ATTACH PARTITION` или `CREATE TABLE ... PARTITION OF`;
- для date facts стартовое правило: monthly partitions для средних объемов, daily partitions только если есть реальная нагрузка, retention или SLA на pruning.

## RANGE Example

```sql
CREATE TABLE lesson01.partition_range_demo (
    sale_id bigint,
    customer_id integer,
    sale_date date,
    amount numeric(12, 2)
)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date);

CREATE TABLE lesson01.partition_range_demo_2026_01
    PARTITION OF lesson01.partition_range_demo
    FOR VALUES FROM (DATE '2026-01-01') TO (DATE '2026-02-01');

CREATE TABLE lesson01.partition_range_demo_default
    PARTITION OF lesson01.partition_range_demo
    DEFAULT;
```

Вопрос ученику:

> Почему `sale_date` хороший partition key, но не обязательно хороший distribution key?

Ожидаемый ответ:

> `sale_date` хорошо режет отчеты и retention. Но для join locality и равномерности чаще нужен `customer_id`, `order_id` или другой высококардинальный join key.

## LIST Example

```sql
CREATE TABLE lesson01.partition_list_demo (
    sale_id bigint,
    customer_id integer,
    sale_date date,
    region text,
    amount numeric(12, 2)
)
DISTRIBUTED BY (customer_id)
PARTITION BY LIST (region);

CREATE TABLE lesson01.partition_list_demo_capitals
    PARTITION OF lesson01.partition_list_demo
    FOR VALUES IN ('Moscow', 'Saint Petersburg');

CREATE TABLE lesson01.partition_list_demo_default
    PARTITION OF lesson01.partition_list_demo
    DEFAULT;
```

LIST хорош, когда бизнес-категория управляемая. Если values часто меняются, LIST быстро превращается в ручную операционную нагрузку.

## HASH Example

```sql
CREATE TABLE lesson01.partition_hash_demo (
    sale_id bigint,
    customer_id integer,
    sale_date date,
    amount numeric(12, 2)
)
DISTRIBUTED BY (customer_id)
PARTITION BY HASH (customer_id);

CREATE TABLE lesson01.partition_hash_demo_p0
    PARTITION OF lesson01.partition_hash_demo
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```

HASH partitioning не заменяет distribution. Это partitioning внутри logical table, а физическое размещение строк по segment все равно определяется `DISTRIBUTED BY`.

## Multi-Level

Multi-level схема нужна редко на первом уроке, но полезно показать идею:

```sql
CREATE TABLE lesson01.partition_multilevel_demo (...)
DISTRIBUTED BY (customer_id)
PARTITION BY RANGE (sale_date);

CREATE TABLE lesson01.partition_multilevel_demo_2026_01
    PARTITION OF lesson01.partition_multilevel_demo
    FOR VALUES FROM (DATE '2026-01-01') TO (DATE '2026-02-01')
    PARTITION BY LIST (region);
```

Правило: не делай multi-level partitioning только потому, что можешь. Сначала докажи, что есть query pruning, retention или operational boundary, которые окупают сложность.

## Как Смотреть Партиции И Сколько Их В GP

Самый понятный способ для Greenplum 7:

```sql
SELECT
    tree.level,
    tree.isleaf,
    tree.relid::regclass AS relation_name,
    tree.parentrelid::regclass AS parent_relation
FROM pg_partition_tree('lesson01.partition_range_demo'::regclass) AS tree
ORDER BY tree.level, relation_name::text;
```

Подсчет leaf partitions по всем demo tables:

```sql
WITH roots AS (
    SELECT n.nspname AS schema_name, c.relname AS table_name, c.oid AS root_oid
    FROM pg_class AS c
    JOIN pg_namespace AS n ON n.oid = c.relnamespace
    WHERE n.nspname = 'lesson01'
      AND c.relname LIKE 'partition_%_demo'
)
SELECT
    roots.schema_name,
    roots.table_name,
    COUNT(*) FILTER (WHERE tree.isleaf) AS leaf_partitions,
    COUNT(*) FILTER (WHERE NOT tree.isleaf) AS internal_partition_nodes,
    MAX(tree.level) AS max_partition_level
FROM roots
CROSS JOIN LATERAL pg_partition_tree(roots.root_oid) AS tree
GROUP BY roots.schema_name, roots.table_name
ORDER BY roots.table_name;
```

Greenplum compatibility view:

```sql
SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson01'
ORDER BY schemaname, tablename, partitionlevel, partitiontablename;
```

`gp_toolkit.gp_partitions` показывает leaf partitions. Это удобно для operational inventory: сколько partitions в базе, какие таблицы разрослись, где есть слишком глубокая иерархия.

## Как Проверять Pruning

```sql
EXPLAIN
SELECT sum(amount)
FROM lesson01.partition_range_demo
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';
```

Смотри, сколько child partitions попало в план. Если фильтр не содержит partition key или выражение мешает pruning, Greenplum может читать больше partitions.

Bad pattern:

```sql
WHERE date_trunc('month', sale_date) = DATE '2026-02-01'
```

Better pattern:

```sql
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01'
```

## Maintenance

Примеры maintenance-команд, которые полезно показать как snippets:

```sql
-- ATTACH PARTITION
ALTER TABLE lesson01.partition_range_demo
    ATTACH PARTITION lesson01.partition_range_demo_2026_04
    FOR VALUES FROM (DATE '2026-04-01') TO (DATE '2026-05-01');

-- DETACH PARTITION
ALTER TABLE lesson01.partition_range_demo
    DETACH PARTITION lesson01.partition_range_demo_2026_01;

-- DROP old retention partition
DROP TABLE lesson01.partition_range_demo_2026_01;
```

На первом уроке это не главный hands-on, но ученик должен понять: partitioning ценен не только скоростью чтения, но и lifecycle operations.

## Mentor Questions

1. Почему `PARTITION BY RANGE (sale_date)` не гарантирует равномерность по segments?
2. Когда `DEFAULT partition` полезен, а когда опасен?
3. Как посчитать leaf_partitions по всем таблицам в схеме?
4. Почему HASH partitioning не заменяет `DISTRIBUTED BY`?
5. Что произойдет при out-of-range INSERT без default partition?

## Acceptance

Ученик понял тему, если может:

- выбрать RANGE/LIST/HASH по workload;
- объяснить no default partitioning и роль `DEFAULT partition`;
- выполнить `pg_partition_tree`;
- найти partitions через `gp_toolkit.gp_partitions`;
- посчитать `leaf_partitions`;
- объяснить, почему partition key не равен distribution key;
- назвать хотя бы один maintenance сценарий: `ATTACH PARTITION`, `DETACH PARTITION`, retention drop.

## Sources

- [Greenplum 7 Partitioning Large Tables](https://techdocs.broadcom.com/us/en/vmware-tanzu/data-solutions/tanzu-greenplum/7/greenplum-database/admin_guide-ddl-ddl-partition.html)
- [Greenplum 7 gp_toolkit Administrative Schema](https://techdocs.broadcom.com/us/en/vmware-tanzu/data-solutions/tanzu-greenplum/7/greenplum-database/ref_guide-gp_toolkit.html)
- [Greenplum 7 partitioning catalog migration notes](https://techdocs.broadcom.com/us/en/vmware-tanzu/data-solutions/tanzu-greenplum/7/greenplum-database/install_guide-migrate-classic-partitioning.html)
