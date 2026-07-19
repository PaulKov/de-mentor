CREATE OR REPLACE VIEW lesson01.v_fact_sales_good_segment_distribution AS
SELECT
    gp_segment_id,
    count(*) AS rows_count,
    round(
        count(*) * 100.0 / sum(count(*)) OVER (),
        2
    ) AS rows_percent
FROM lesson01.fact_sales_good
GROUP BY gp_segment_id;

CREATE OR REPLACE VIEW lesson01.v_region_revenue_good AS
SELECT
    c.region,
    count(*) AS orders_count,
    sum(f.amount) AS revenue
FROM lesson01.fact_sales_good AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;

