# Практика 09в. Падение между фиксацией FlowFile и commitSync

NiFi 2.12.0 принимает одно JSON-событие из Kafka 4.2.2. У процессора `ConsumeKafka` выставлено `Commit Offsets=true`. Соединение ведёт в остановленный процессор. Так можно открыть очередь и исследовать обе копии, прежде чем они попадут в обработку.

## Что сделать

Из корня курса запусти:

```sh
cd labs/nifi
python commit_window_lab.py --report window-run.json
```

Нужны Docker Compose и Python 3.9+. Отдельный узел `nifi-window` открывается на порту 28445. Основной NiFi и Kafka продолжают работать. Сценарий создаёт уникальный топик с одной партицией, устанавливает начальную позицию новой группы на пустом входе и один раз отправляет событие. ID группы NiFi и ссылка на интерфейс печатаются при запуске. Логин `student`, пароль `Practice-Only-2026`.

До запуска процессора встроенный отладчик JDK ставит точку останова в строке 157 метода `Kafka3ConsumerService.commit`. В исходниках именно здесь вызывается `consumer.commitSync(offsets)`. Приостановлен один поток исполнения, поэтому во время паузы можно читать REST API NiFi и спрашивать Kafka о позиции группы. Стек, UUID, содержимое очереди и offset проверяются **до** отправки контейнеру `SIGKILL`. [Код NiFi в версии стенда](https://github.com/apache/nifi/blob/rel/nifi-2.12.0/nifi-extension-bundles/nifi-kafka-bundle/nifi-kafka-service-shared/src/main/java/org/apache/nifi/kafka/service/consumer/Kafka3ConsumerService.java#L153-L159)

## Как читать протокол

Обозначь UUID, увиденный до аварии, буквой A, а впервые появившийся после повторного чтения — B. `CURRENT`, `END` и `LAG` относятся ко входу Kafka. [Снимки прогона](observed.json)

| Когда снято | CURRENT / END / LAG | Очередь NiFi |
| --- | --- | --- |
| В точке останова, до вызова Kafka | 0 / 1 / 1 | A |
| Контейнер завершился с кодом 137 | 0 / 1 / 1 | API выключен |
| NiFi восстановился, источник ещё остановлен | 0 / 1 / 1 | A |
| Источник снова прочитал вход и зафиксировал позицию | 1 / 1 / 0 | A и B |

Во всех доступных снимках сравни `event_id` в содержимом, а также `kafka.topic`, `kafka.partition`, `kafka.offset` в атрибутах. A сохранил UUID при восстановлении репозитория. B пришёл с тех же входных координат, но получил другой UUID при создании FlowFile. Для наблюдения напрямую открой группу по ссылке из отчёта, затем меню соединения → **List queue**. После опыта оба процессора остановлены, обе записи сохранены. Эту проверку можно повторять до запуска downstream.

На учебном узле `nifi.flowcontroller.autoResumeState=false`. Ручное включение источника отделяет восстановление очереди от повторного чтения. Восстанавливается тот же контейнер с теми же томами, брокер всё время работает. Единственная административная установка offset выполняется до появления входной записи. Этот опыт моделирует падение процесса при работающем диске.

## Кто двигает позицию

Работающий Kafka consumer продвигает локальную `position` после `poll()`. Для восстановления сохраняется отдельная позиция группы. Ниже три варианта того, кто инициирует её фиксацию.

| Кто читает | Кто определяет момент фиксации |
| --- | --- |
| Java consumer c `enable.auto.commit=true` | Клиентская библиотека периодически инициирует commit при работе потребителя. Про завершённость внешней операции знает приложение |
| NiFi с `Commit Offsets=true` | После успешной фиксации сессии `ConsumeKafka` вызывает сервис, который формирует позицию для каждой партиции и вызывает `commitSync` |
| Kafka Connect sink | Worker читает данные и передаёт batch в `SinkTask.put`. Перед commit вызывает `preCommit`. Реализация по умолчанию выполняет `flush` и возвращает позиции. Коннектор может вернуть только безопасно записанную позицию каждой партиции |

У sink-коннектора, пишущего в БД, возможен повтор, если БД уже зафиксировала изменение, а worker упал до сохранения позиции в Kafka. Идемпотентный ключ или транзакционный учёт обработанных событий позволяет пережить это окно. [KafkaConsumer](https://kafka.apache.org/42/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html) · [SinkTask](https://kafka.apache.org/42/javadoc/org/apache/kafka/connect/sink/SinkTask.html) · [WorkerSinkTask 4.2.2](https://github.com/apache/kafka/blob/4.2.2/connect/runtime/src/main/java/org/apache/kafka/connect/runtime/WorkerSinkTask.java#L397-L445)

## Физическая запись группы в Kafka

Каждая пара «топик, партиция» имеет собственную позицию для каждой группы. Координатор сохраняет обновления во внутреннем компактируемом топике `__consumer_offsets`. Ключ offset-записи содержит `group`, `topic`, `partition`. В значении формата v4 находятся `offset`, `leaderEpoch`, `metadata`, `commitTimestamp` и опциональный tagged field `topicId`. Историческое поле `expireTimestamp` относится только к v1. В одном физическом журнале также есть другие типы записей координатора. [Схема ключа](https://github.com/apache/kafka/blob/4.2.2/group-coordinator/src/main/resources/common/message/OffsetCommitKey.json) · [Схема значения](https://github.com/apache/kafka/blob/4.2.2/group-coordinator/src/main/resources/common/message/OffsetCommitValue.json)

Для обычного просмотра достаточно:

```powershell
$r = Get-Content -Raw ./window-run.json | ConvertFrom-Json
docker compose exec -T kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka:29092 --describe --group $r.group
```

Колонка `CURRENT-OFFSET` показывает сохранённую позицию. `LOG-END-OFFSET` берётся из состояния входной партиции. В данном опыте `LAG = LOG-END-OFFSET − CURRENT-OFFSET`. Ни lag, ни UUID FlowFile в значении offset-записи не хранятся.

В опубликованном прогоне ключом был `(window-586fba7f-a35, window.in.586fba7f-a35, 0)`. Обновления этого ключа попали в партицию **38 служебного топика**. Форматтер Kafka показал два значения v4. Первое было создано при начальной установке позиции, второе — после повторного чтения.

| offset | leaderEpoch | metadata | commitTimestamp, мс Unix |
| ---: | ---: | --- | ---: |
| 0 | -1 | пустая строка | 1795763170030 |
| 1 | -1 | пустая строка | 1795763227476 |

Прочитать журнал примера можно штатным форматтером. Фильтруй вывод по имени группы: одна партиция служебного топика содержит данные многих групп. Со временем compaction может удалить старое значение. Номер 38 относится к этому прогону. Координатор выбирает партицию по хешу имени группы и количеству партиций `__consumer_offsets`. [Реализация GroupCoordinatorService](https://github.com/apache/kafka/blob/4.2.2/group-coordinator/src/main/java/org/apache/kafka/coordinator/group/GroupCoordinatorService.java)

```powershell
docker compose exec -T kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka:29092 --topic __consumer_offsets --partition 38 --offset earliest --timeout-ms 3500 --command-property enable.auto.commit=false --formatter org.apache.kafka.tools.consumer.OffsetsMessageFormatter
```
