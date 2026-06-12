DROP TABLE IF EXISTS lesson01.dim_product_focus;

CREATE TABLE lesson01.dim_product_focus (
    product_id integer NOT NULL,
    category text NOT NULL,
    campaign text NOT NULL
)
DISTRIBUTED REPLICATED;

INSERT INTO lesson01.dim_product_focus
SELECT
    product_id,
    category,
    'focus_campaign'
FROM lesson01.dim_products
WHERE product_id <= 20;

ANALYZE lesson01.dim_product_focus;
