# Facilitator guide — Apache Spark foundations

## Тайминг

| Блок | Слайды | Время | Результат |
| --- | ---: | ---: | --- |
| Big Data: термин, 3V и причины | 1–8 | 15 мин | Отличает workload constraint от ярлыка размера и не принимает 10V за стандарт |
| MapReduce → Spark: история и версии | 9–16 | 13 мин | Объясняет исходную боль iterative/reuse и ключевые вехи Spark 0.x–4.2 |
| Модель исполнения | 17–25 | 14 мин | Связывает application, driver, executor, partition, job, stage и task |
| PySpark pipeline и plan | 26–32 | 10 мин | Читает DataFrame-код и находит Exchange / join strategy в плане |
| Spark UI, evidence и exit | 33–35 | 8 мин | Формулирует проверяемую гипотезу производительности |
| Spark vs MapReduce principal block | 36–44 | +15 мин | Сравнивает graph, materialization, recovery и workload fit |
| Execution internals | 45–53 | +15 мин | Объясняет Catalyst, shuffle, Python/JVM boundary, AQE и skew |
| Appendix | 54–60 | по запросу | Получает справочные материалы, чтение и переход к практике |

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

## Skip map

Если остаётся 45 минут, сократите 5–8 до тезиса 3V, пропустите 14–16 и 32,
затем проведите 35 как обязательную проверку понимания. Если остаётся 30 минут,
используйте 2, 4, 9–12, 17–25, 27, 30–31 и 35. Deep dive не заменяет core: к нему
переходят только после корректного
объяснения цепочки `DataFrame → plan → job → stage → task`.
