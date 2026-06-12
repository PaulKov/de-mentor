# Greenplum Architecture Map

## MPP Mental Model

```mermaid
flowchart TB
    Client["Client / psql"] --> Coord["Coordinator"]
    Coord --> Plan["Optimizer builds parallel plan"]
    Plan --> S0["Segment 0"]
    Plan --> S1["Segment 1"]
    S0 <--> Interconnect["Interconnect"]
    S1 <--> Interconnect
    S0 --> Gather["Gather Motion"]
    S1 --> Gather
    Gather --> Coord
```

## Distribution And Join Locality

```mermaid
flowchart LR
    FactBad["fact_sales_bad<br/>DISTRIBUTED BY status"] --> Motion["Redistribute Motion<br/>by customer_id"]
    Motion --> JoinBad["Join with dim_customers"]
    DimCustomers["dim_customers<br/>DISTRIBUTED BY customer_id"] --> JoinBad

    FactGood["fact_sales_good<br/>DISTRIBUTED BY customer_id"] --> JoinGood["Colocated join"]
    DimCustomers2["dim_customers<br/>DISTRIBUTED BY customer_id"] --> JoinGood
```

## What To Look For In EXPLAIN

| Plan fragment | Interpretation |
|---|---|
| `Seq Scan on fact_sales_bad` | Each segment scans its local slice. |
| `Redistribute Motion` | Rows move across the interconnect by a new hash key. |
| `Broadcast Motion` | A relation is copied to every segment. |
| `Gather Motion` | Final rows return to coordinator. |

## Architect's Heuristic

1. Define grain.
2. Identify largest facts.
3. List frequent joins.
4. Check cardinality and skew risk.
5. Choose distribution key.
6. Choose partition key separately.
7. Validate with `EXPLAIN` and segment distribution.

