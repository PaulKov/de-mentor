# Greenplum Cheat Sheet

## CLI

```bash
python3 mentor-lab.py list
python3 mentor-lab.py info greenplum
python3 mentor-lab.py lesson greenplum
python3 mentor-lab.py teach greenplum simple --stage 1
python3 mentor-lab.py hint greenplum skew-investigation
python3 mentor-lab.py hint greenplum plan-reading
python3 mentor-lab.py hint greenplum physical-joins
python3 mentor-lab.py hint greenplum physical-joins --level 2
python3 mentor-lab.py hint greenplum mpp-systems
python3 mentor-lab.py assessment greenplum pre
python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join
python3 mentor-lab.py tuning greenplum list
python3 mentor-lab.py submit greenplum advanced-joins
python3 mentor-lab.py evidence greenplum collect redistribute-join --output submissions/redistribute-join.md
python3 mentor-lab.py homework greenplum check --submission submissions/homework.md
python3 mentor-lab.py review greenplum --submission submissions/advanced-joins.md
python3 mentor-lab.py cockpit greenplum
python3 mentor-lab.py certificate greenplum
python3 mentor-lab.py up greenplum
python3 mentor-lab.py status greenplum
python3 mentor-lab.py check greenplum
python3 mentor-lab.py grade greenplum
python3 mentor-lab.py report greenplum
python3 mentor-lab.py incident list greenplum
python3 mentor-lab.py incident start greenplum skew-investigation
python3 mentor-lab.py incident start greenplum slow-product-analytics
python3 mentor-lab.py psql greenplum
python3 mentor-lab.py logs greenplum
python3 mentor-lab.py down greenplum
python3 mentor-lab.py reset greenplum
```

## Подключение

Через CLI:

```bash
python3 mentor-lab.py psql greenplum
```

Если локальный `psql` установлен:

```bash
psql -h localhost -p 15432 -U gpadmin -d mentor
```

Пароль: `gparray`.

## Сегменты

```sql
SELECT content, role, preferred_role, mode, status, hostname, port
FROM gp_segment_configuration
ORDER BY content, role;
```

## Распределение Строк

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_bad
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
```

## Создание Таблицы

```sql
CREATE TABLE lesson01.example_orders (
    order_id bigint,
    customer_id bigint,
    order_date date,
    amount numeric(12, 2)
)
DISTRIBUTED BY (customer_id);
```

## EXPLAIN

```sql
EXPLAIN
SELECT *
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id);
```

```sql
EXPLAIN ANALYZE
SELECT c.region, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;
```

## Motion Nodes

| Node | Что значит |
|---|---|
| `Gather Motion` | Собрать результат с сегментов на coordinator |
| `Broadcast Motion` | Разослать набор строк на все сегменты |
| `Redistribute Motion` | Перераспределить строки по новому hash key |

## Быстрые Правила

- Distribution key должен иметь высокую cardinality.
- Частый join key - хороший кандидат, если он равномерный.
- Низкокардинальные поля вроде `status`, `gender`, `flag` почти всегда опасны.
- Partitioning отвечает за pruning и управление данными, distribution - за физическое размещение строк по сегментам.
- `EXPLAIN` нужен до того, как таблица выросла до терабайтов.
