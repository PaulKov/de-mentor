# Финальная Задача: Daily Marketplace Revenue Mart

## Сценарий

Нужно спроектировать витрину Greenplum для ежедневной аналитики выручки marketplace. Источники: orders, order items, customers, products, payments и delivery events.

Цель задачи - не написать максимум DDL, а защитить физический дизайн: grain, distribution, partitioning, storage и проверку через evidence.

## Что Сдать

1. Список fact-таблиц и dimensions.
2. Grain для каждого факта.
3. Distribution key для каждой большой таблицы.
4. Partition key для каждого факта или объяснение, почему partitioning пока не нужен.
5. Три validation SQL-запроса.
6. Риски и trade-offs.

## Формат Защиты

Используй такой шаблон:

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

Поля в шаблоне оставлены на английском как рабочий evidence-формат: его удобно вставлять в issue, PR или review comment без перевода технических меток.

## Признаки Сильного Ответа

- Grain описан до выбора ключей.
- Distribution объяснен через join locality и cardinality.
- Partitioning объяснен через time pruning и maintenance.
- Риски включают skew, enterprise customers, late-arriving events и stale stats.
- `EXPLAIN` входит в validation, а не добавляется после решения.
