DROP TABLE IF EXISTS lesson01.fact_sales_wide_aoco;

CREATE TABLE lesson01.fact_sales_wide_aoco (
    sale_id bigint,
    customer_id integer,
    product_id integer,
    sale_date date,
    amount numeric(12, 2),
    payload_01 text,
    payload_02 text,
    payload_03 text
)
WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=3)
DISTRIBUTED BY (customer_id);

INSERT INTO lesson01.fact_sales_wide_aoco
SELECT
    sale_id,
    customer_id,
    product_id,
    sale_date,
    amount,
    repeat('segment-friendly-column-data-', 2),
    repeat('rarely-read-wide-attribute-', 2),
    repeat('compression-demo-', 3)
FROM lesson01.fact_sales_good
LIMIT 10000;

ANALYZE lesson01.fact_sales_wide_aoco;
