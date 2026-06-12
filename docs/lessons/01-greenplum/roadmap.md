# Roadmap Урока

```mermaid
flowchart LR
    A["Старт: зачем Greenplum"] --> B["MPP архитектура"]
    B --> C["Coordinator, segments, interconnect"]
    C --> D["Distribution key"]
    D --> E["Data skew"]
    E --> F["EXPLAIN и Motion"]
    F --> G["Практика: плохая модель"]
    G --> H["Исправление distribution"]
    H --> I["Мини design review"]
    I --> J["Домашка: витрина продаж"]
```

## Логика Переходов

1. Сначала показываем, что Greenplum физически распределяет данные.
2. Затем объясняем, что распределение влияет на план запроса.
3. После этого ученик сам создает проблему skew.
4. В финале он чинит модель и защищает решение как инженер.

