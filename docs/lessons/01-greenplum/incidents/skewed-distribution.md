# Incident: Skewed Distribution

## Title

Marketplace revenue report became slow.

## Symptoms

- Query by region became slower after a new fact table deployment.
- `EXPLAIN` contains `Redistribute Motion`.
- Segment distribution shows one segment doing most work.
- The fact table was distributed by `status`.

## Mission

Find the root cause and produce a short RCA with evidence.

## Setup

```bash
python3 mentor-lab.py seed greenplum --profile skewed
python3 mentor-lab.py check greenplum
```

## Evidence To Collect

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

## Acceptance Criteria

- Show segment distribution for the bad fact table.
- Identify `status` as low-cardinality distribution key.
- Show `Redistribute Motion` in the plan.
- Propose `customer_id` distribution for this join pattern.
- Explain remaining risks and validation steps.

