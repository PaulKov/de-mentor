# Facilitator skip-map

| Время | Если отстаём | Что обязательно сохранить |
| ---: | --- | --- |
| 15 мин | дать схему Kafka→Flink→Iceberg | четыре координаты (offset/checkpoint/event time/watermark) |
| 30 мин | показать готовый topic | offset initializer vs checkpoint recovery |
| 45 мин | пропустить повторный publish | watermark / late event tradeoff |
| 60 мин | пропустить UI deep inspection | минимум один completed checkpoint ID и snapshot ID |
| 80 мин | fault drill оставить как мини-лекцию | failure windows до/после completed checkpoint |
| 90 мин | сократить debrief | checkpoint success ≠ Iceberg commit success |

Если classpath/Compose не готов: переключиться на чтение lab SQL и sequence diagrams из deep dives, затем отложить live fault drill. Не выдумывать operational evidence, если job фактически не запускался.
