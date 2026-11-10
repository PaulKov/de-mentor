# Homework plan

Рекомендуемый объём: 4–6 часов.

| Этап | Оценка | Выход |
|---|---:|---|
| Повторить deep dives и архитектурное задание | 45 мин | схема source → state → checkpoint → sink commit |
| Запустить SQL lab и собрать метрики | 45 мин | evidence с Job ID, offsets, checkpoint, snapshots |
| Recovery drill | 45–75 мин | failure timeline и восстановленное состояние |
| Спроектировать watermark/late policy | 30 мин | timestamp data contract и policy |
| Заполнить retention/SLO/monitoring matrix | 45 мин | production operations plan |
| Сравнить Java/DataStream/SQL/PyFlink | 30–60 мин | API comparison + два code samples |
| Review и cleanup | 30 мин | согласованный submission, стенд оставлен без опасного reset |

Не объединяй доказательство correctness и performance. Сначала выровняй события и expected output, затем измеряй throughput, checkpoint latency и commit delay.
