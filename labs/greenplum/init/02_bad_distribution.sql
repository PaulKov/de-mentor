CREATE OR REPLACE VIEW lesson01.v_fact_sales_bad_segment_distribution AS
SELECT
    gp_segment_id,
    count(*) AS rows_count,
    round(
        count(*) * 100.0 / sum(count(*)) OVER (),
        2
    ) AS rows_percent
FROM lesson01.fact_sales_bad
GROUP BY gp_segment_id;

CREATE OR REPLACE VIEW lesson01.v_fact_sales_bad_status_distribution AS
SELECT
    status,
    count(*) AS rows_count,
    round(
        count(*) * 100.0 / sum(count(*)) OVER (),
        2
    ) AS rows_percent
FROM lesson01.fact_sales_bad
GROUP BY status;

