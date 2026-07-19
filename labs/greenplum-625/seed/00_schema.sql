DROP SCHEMA IF EXISTS lesson01 CASCADE;
CREATE SCHEMA lesson01;

CREATE TABLE lesson01.dim_customers (
    customer_id integer NOT NULL,
    customer_name text NOT NULL,
    region text NOT NULL,
    segment text NOT NULL,
    registered_at date NOT NULL
)
DISTRIBUTED BY (customer_id);

CREATE TABLE lesson01.dim_products (
    product_id integer NOT NULL,
    product_name text NOT NULL,
    category text NOT NULL,
    price numeric(12, 2) NOT NULL
)
DISTRIBUTED BY (product_id);

CREATE TABLE lesson01.fact_sales_bad (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    product_id integer NOT NULL,
    status text NOT NULL,
    sale_date date NOT NULL,
    amount numeric(12, 2) NOT NULL,
    loaded_at timestamp NOT NULL
)
DISTRIBUTED BY (status);

CREATE TABLE lesson01.fact_sales_good (
    sale_id bigint NOT NULL,
    customer_id integer NOT NULL,
    product_id integer NOT NULL,
    status text NOT NULL,
    sale_date date NOT NULL,
    amount numeric(12, 2) NOT NULL,
    loaded_at timestamp NOT NULL
)
DISTRIBUTED BY (customer_id);

