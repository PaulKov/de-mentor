# Capstone: Daily Marketplace Revenue Mart

## Scenario

You need to design a Greenplum mart for daily marketplace revenue analytics. The source events include orders, order items, customers, products, payments, and delivery events.

## Deliverables

1. Fact and dimension list.
2. Grain for each fact.
3. Distribution key for each large table.
4. Partition key for each fact.
5. Three validation SQL queries.
6. Risks and trade-offs.

## Required Defense

Use this format:

```text
Primary fact:
Grain:
Distribution key:
Why this key:
Partition key:
Most important joins:
Expected Motion risks:
Validation SQL:
Trade-offs:
```

## Strong Answer Signals

- Grain is defined before keys.
- Distribution is explained through join locality and cardinality.
- Partitioning is explained through time pruning and maintenance.
- Risks include skew, enterprise customers, late-arriving events, and stale stats.
- `EXPLAIN` is part of validation, not an afterthought.

