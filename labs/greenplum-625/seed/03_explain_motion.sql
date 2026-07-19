CREATE OR REPLACE VIEW lesson01.v_region_revenue_bad AS
SELECT
    c.region,
    count(*) AS orders_count,
    sum(f.amount) AS revenue
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_customers AS c USING (customer_id)
GROUP BY c.region;

CREATE OR REPLACE VIEW lesson01.v_category_revenue_bad AS
SELECT
    p.category,
    count(*) AS orders_count,
    sum(f.amount) AS revenue
FROM lesson01.fact_sales_bad AS f
JOIN lesson01.dim_products AS p USING (product_id)
GROUP BY p.category;

