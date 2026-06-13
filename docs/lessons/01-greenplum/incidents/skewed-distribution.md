# Инцидент: Перекошенное Распределение

## Название

Отчет по выручке marketplace стал медленным.

## Симптомы

- Запрос по region стал медленнее после выкладки новой fact-таблицы.
- В `EXPLAIN` появился `Redistribute Motion`.
- Распределение строк показывает, что один segment делает большую часть работы.
- Fact-таблица была распределена по `status`.

## Миссия

Найди root cause и подготовь короткий RCA с evidence.

## Подготовка

```bash
python3 mentor-lab.py seed greenplum --profile skewed
python3 mentor-lab.py check greenplum
```

## Evidence Для Сбора

```sql
SELECT *
FROM lesson01.v_fact_sales_bad_segment_distribution
ORDER BY gp_segment_id;
```

```sql
EXPLAIN
SELECT c.region, count(*) AS orders_count, sum(f.amount) AS revenue
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region
ORDER BY revenue DESC;
```

## Критерии Приемки

- Показано распределение строк по segments для плохой fact-таблицы.
- `status` определен как low-cardinality distribution key.
- В плане показан `Redistribute Motion`.
- Предложен `customer_id` как distribution key для этого join pattern.
- Описаны остаточные риски и validation steps.
