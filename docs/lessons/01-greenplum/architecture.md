# Карта Архитектуры Greenplum

## Ментальная Модель MPP

```mermaid
flowchart TB
    Client["Клиент / psql"] --> Coord["Coordinator"]
    Coord --> Plan["Optimizer строит параллельный план"]
    Plan --> S0["Segment 0"]
    Plan --> S1["Segment 1"]
    S0 <--> Interconnect["Interconnect"]
    S1 <--> Interconnect
    S0 --> Gather["Gather Motion"]
    S1 --> Gather
    Gather --> Coord
```

Главная идея: coordinator управляет запросом, а данные и основная работа живут на segments. Любое движение строк между segments видно в плане как `Motion`.

## Distribution И Локальность Join

```mermaid
flowchart LR
    FactBad["fact_sales_bad<br/>DISTRIBUTED BY status"] --> Motion["Redistribute Motion<br/>by customer_id"]
    Motion --> JoinBad["Join with dim_customers"]
    DimCustomers["dim_customers<br/>DISTRIBUTED BY customer_id"] --> JoinBad

    FactGood["fact_sales_good<br/>DISTRIBUTED BY customer_id"] --> JoinGood["Co-located join"]
    DimCustomers2["dim_customers<br/>DISTRIBUTED BY customer_id"] --> JoinGood
```

`DISTRIBUTED BY` отвечает за физическое размещение строк. Если большая fact-таблица и dimension-таблица распределены по ключу частого join, Greenplum может выполнить join локально на segments и уменьшить сетевое движение.

## Что Смотреть В EXPLAIN

| Фрагмент плана | Как читать |
|---|---|
| `Seq Scan on fact_sales_bad` | Каждый segment читает свою локальную часть таблицы. |
| `Redistribute Motion` | Строки переезжают через interconnect по новому hash key. |
| `Broadcast Motion` | Один input копируется на все segments. |
| `Gather Motion` | Финальные строки собираются на coordinator. |

## Архитектурная Эвристика

1. Сначала определи grain.
2. Найди самые большие fact-таблицы.
3. Выпиши частые joins и фильтры.
4. Проверь cardinality и риск skew.
5. Выбери distribution key под равномерность и join locality.
6. Выбери partition key отдельно под pruning и retention.
7. Подтверди решение через `EXPLAIN` и распределение строк по segments.
