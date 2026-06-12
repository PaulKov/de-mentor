# Домашняя Работа

## Кейс

Компания собирает события интернет-магазина:

- `orders`
- `order_items`
- `customers`
- `products`
- `payments`
- `delivery_events`

Нужно спроектировать аналитический слой для ежедневной отчетности:

- выручка по дням;
- выручка по регионам;
- топ товаров;
- конверсия успешных оплат;
- задержки доставки.

## Что Нужно Сдать

1. Список фактов и измерений.
2. Grain каждого факта.
3. Distribution key для каждой большой таблицы.
4. Partition key для фактов.
5. 3 SQL-запроса для проверки качества модели.
6. 3 риска и как ты их проверишь.

## Шаблон Ответа

```text
Fact tables:

Dimension tables:

Fact grain:

Distribution strategy:

Partition strategy:

Quality checks:

Risks:
```

## Критерии Приемки

Работа засчитывается, если:

- grain описан до выбора ключей;
- distribution key выбран с аргументацией по cardinality и join pattern;
- partition key не смешан с distribution key;
- есть проверка skew;
- есть хотя бы один запрос с `EXPLAIN`.

