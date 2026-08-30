# Facilitator guide — Apache Spark foundations

## Тайминг

| Блок | Слайды | Время | Результат |
| --- | ---: | ---: | --- |
| Big Data: термин, 3V и причины | 1–8 | 15 мин | Отличает workload constraint от ярлыка размера и не принимает 10V за стандарт |
| MapReduce → Spark: история и версии | 9–16 | 13 мин | Объясняет исходную боль iterative/reuse и ключевые вехи Spark 0.x–4.2 |
| Модель исполнения | 17–29 | 14 мин | Связывает API/context, scheduler flow, lazy/cache, job, stage и task |
| PySpark pipeline и plan | 30–36 | 10 мин | Читает DataFrame-код и находит Exchange / join strategy в плане |
| Spark UI, evidence и exit | 37–39 | 8 мин | Формулирует проверяемую гипотезу производительности |
| Spark vs MapReduce + scheduler | 40–49 | +15 мин | Сравнивает graph/recovery и объясняет scheduler stack |
| Execution + cache internals | 50–59 | +15 мин | Объясняет Catalyst, shuffle, BlockManager, AQE и skew |
| Appendix | 60–66 | по запросу | Получает справочные материалы, чтение и переход к практике |

## Рекомендуемый ритм

Каждые 7–10 минут просите участника предсказать следующий элемент execution
model. После слайда с физическим планом дайте 60 секунд на самостоятельный поиск
`Exchange` и стратегии join. Не показывайте Spark UI как экскурсию по вкладкам:
всегда начинайте с вопроса и ожидаемого evidence.

## Контрольные вопросы

1. Где заканчивается ответственность cluster manager и начинается Spark?
2. Почему action создаёт job, а shuffle — новую stage?
3. Почему обычный Python UDF ограничивает возможности Catalyst?
4. Чем в плане отличаются `SortMergeJoin` и `BroadcastHashJoin`?
5. Какие метрики в UI подтвердят skew?
6. Почему утверждение «Spark — MapReduce в RAM» архитектурно неполно?
7. При каком workload разница между Spark и MapReduce будет мала?
8. Кто назначает task на executor slot и что в этот момент делает cluster manager?
9. Почему `cache()` ничего не вычисляет до первого action?

## Skip map

Если остаётся 45 минут, сократите 5–8 до тезиса 3V, пропустите 14–16 и 36,
затем проведите 39 как обязательную проверку понимания. Если остаётся 30 минут,
используйте 2, 4, 9–12, 17–29, 31, 34–35 и 39. Deep dive не заменяет core: к нему
переходят только после корректного
объяснения цепочки `DataFrame → plan → job → stage → task`.
