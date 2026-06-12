# Student Workbook

## Подготовка

macOS:

```bash
python3 mentor-lab.py up greenplum
python3 mentor-lab.py psql greenplum
```

Windows PowerShell:

```powershell
py mentor-lab.py up greenplum
py mentor-lab.py psql greenplum
```

Если нужно начать заново:

```bash
python3 mentor-lab.py reset greenplum
python3 mentor-lab.py up greenplum
```

## Задание 1: Осмотри Кластер

```sql
SELECT content, role, preferred_role, mode, status, hostname, port
FROM gp_segment_configuration
ORDER BY content, role;
```

Ответь:

- сколько сегментов участвует в хранении данных;
- какой узел принимает пользовательские подключения;
- почему в MPP-базе важна равномерность работы сегментов.

## Задание 2: Найди Skew

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_bad
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
```

Затем посмотри распределение по статусам:

```sql
SELECT status, count(*) AS rows_count
FROM lesson01.fact_sales_bad
GROUP BY status
ORDER BY rows_count DESC;
```

Ответь:

- почему распределение по `status` опасно;
- какой сегмент получил больше работы;
- какие поля лучше подходят для distribution key.

## Задание 3: Поймай Motion

```sql
EXPLAIN ANALYZE
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;
```

Найди в плане:

- `Redistribute Motion`;
- `Gather Motion`;
- строки, где optimizer двигает данные между сегментами.

## Задание 4: Сравни С Исправленной Таблицей

```sql
SELECT gp_segment_id, count(*) AS rows_count
FROM lesson01.fact_sales_good
GROUP BY gp_segment_id
ORDER BY gp_segment_id;
```

```sql
EXPLAIN ANALYZE
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;
```

Ответь:

- стало ли распределение ровнее;
- какой Motion исчез или стал дешевле;
- почему `customer_id` лучше для этого join.

## Задание 5: Мини Design Review

Спроектируй факт `fact_daily_sales`:

- grain;
- distribution key;
- partition key;
- основные dimensions;
- 2-3 риска модели.

Формат ответа:

```text
Grain:
Distribution key:
Partition key:
Dimensions:
Risks:
```

## Advanced Track: План, Joins, Архитектура

Эти задания включай, если базовые 5 заданий идут уверенно. Их можно дать как продолжение урока или домашнюю работу.

### Advanced 1: Прочитай План По Лестнице

```sql
EXPLAIN ANALYZE
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;
```

Заполни:

```text
Leaf scans:
Local work:
Join algorithm:
First Motion:
Rows out / actual row surprise:
Global work:
One-sentence RCA:
```

Подсказка:

```bash
python3 mentor-lab.py hint greenplum plan-reading
```

### Advanced 2: Физика Join В MPP

Сравни три join patterns:

```sql
-- A. Плохой distribution относительно customer_id
EXPLAIN
SELECT c.region, sum(f.amount)
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;

-- B. Хороший distribution относительно customer_id
EXPLAIN
SELECT c.region, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;

-- C. Хороший для customer_id, но не для product_id
EXPLAIN
SELECT p.category, sum(f.amount)
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_products AS p USING (product_id)
GROUP BY p.category;
```

Ответь:

- где join co-located;
- где нужен `Broadcast Motion`;
- где нужен `Redistribute Motion`;
- почему один distribution key не оптимизирует все joins одновременно.

Подсказка:

```bash
python3 mentor-lab.py hint greenplum physical-joins
```

### Advanced 3: Выбери Класс Системы

Для каждого сценария выбери `SMP`, `MPP`, `EPP/cloud`, `lakehouse` или `HTAP`:

1. 2 TB данных, один сильный сервер, команда маленькая, важна простота эксплуатации.
2. 200 TB фактов, стабильные nightly loads, тяжелые joins, предсказуемая BI-нагрузка.
3. Петабайтный data lake, Spark/Trino/ML, открытые форматы и много команд.
4. Operational workload с транзакциями и near-real-time аналитикой.

Формат ответа:

```text
Scenario:
System class:
Primary bottleneck:
Why not the alternatives:
```

Подсказка:

```bash
python3 mentor-lab.py hint greenplum mpp-systems
```
