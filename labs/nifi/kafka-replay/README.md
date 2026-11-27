# Практика 09б. Одна запись на входе Kafka и две на выходе

Что увидит читатель, если Kafka успела зафиксировать результат, а NiFi упал? Проверим это на одном брокере Kafka 4.2.2 и двух штатных процессорах NiFi 2.12.0. У каждого топика одна партиция. Во входной топик один раз отправляется JSON с уникальным `event_id` и полем `points: 100`.

| Компонент | Настройка | Что проверяем |
| --- | --- | --- |
| ConsumeKafka | `Commit Offsets=false`, отдельная группа | Сохранённую позицию группы на брокере |
| PublishKafka | `Transactions Enabled=true`, `acks=all` | Видимость результата после фиксации транзакции |
| PublishKafka | `FlowFile Attribute Header Pattern` пропускает `kafka.topic`, `kafka.partition`, `kafka.offset` и `uuid` | Происхождение каждой выходной записи |
| Независимый читатель | `read_committed`, прямое чтение партиции 0 с начала | Количество доступных приложению записей |

## Запуск

Из корня курса выполни команды ниже. Нужны Docker Compose и Python 3.9+. Сценарий использует выделенный узел NiFi из практики с баллами. PostgreSQL служит только для блокировки от одновременного запуска двух аварийных опытов. Данные проходят по маршруту Kafka → NiFi → Kafka.

```sh
cd labs/nifi
python kafka_replay_lab.py --report replay-run.json
```

Каждый запуск создаёт свою группу NiFi, пару топиков и входную группу Kafka. Начальная позиция группы задаётся равной 0 **на пустом топике**. После отправки события сценарий больше не меняет offset административными командами. Он ждёт первой записи с `read_committed`, завершает только контейнер `nifi-points` через `SIGKILL`, проверяет код выхода 137 и читает Kafka при выключенном NiFi. Затем запускает тот же контейнер с его томами и снимает показания до и после штатной остановки процессоров. Ссылка на группу NiFi выводится в терминал.

## Разбор измерений

В сохранённом прогоне входная партиция содержала одну запись на offset 0. Во всех строках `CURRENT`, `END` и `LAG` относятся к **входной** группе. Последний столбец показывает offsets **выходной** партиции, которые вернул независимый читатель. [Полный протокол прогона](observed.json)

| Снимок | CURRENT | END | LAG | Видимые выходные offsets |
| --- | ---: | ---: | ---: | --- |
| Первая публикация зафиксирована | 0 | 1 | 1 | 0 |
| NiFi остановлен аварийно | 0 | 1 | 1 | 0 |
| NiFi восстановился | 0 | 1 | 1 | 0, 2 |
| Процессоры штатно остановлены | 1 | 1 | 0 | 0, 2 |

1. На первом снимке позиция работающего consumer уже продвинулась после чтения. Одновременно брокер хранит для восстановления группы значение 0. Оно обозначает **следующий offset для чтения**. Сохранённая позиция 1 означала бы, что группа перешла за единственную входную запись.
2. После падения новый consumer получил партицию и прочитал ту же запись. Две выходные записи несут одинаковые `event_id` и заголовки исходных topic/partition/offset. Разные `uuid` показывают, что через прямое соединение двух процессоров прошли два разных FlowFile.
3. Физический журнал выхода содержит данные на 0 и 2, а на 1 и 3 стоят служебные маркеры `COMMIT`. Обе транзакции состоялись. Читателю с `read_committed` доступны оба результата.
4. При штатной остановке consumer вернул партицию группе. В этом прогоне NiFi записал в журнале `Committed offsets during rebalance` для входного offset 1. Поэтому в конце можно одновременно увидеть нулевой lag и два результата. При `SIGKILL` процесс не смог выполнить этот обработчик. [Обработчик отзыва партиций в NiFi 2.12.0](https://github.com/apache/nifi/blob/rel/nifi-2.12.0/nifi-extension-bundles/nifi-kafka-bundle/nifi-kafka-service-shared/src/main/java/org/apache/nifi/kafka/service/consumer/Kafka3ConsumerService.java#L98-L142)

## Самостоятельная проверка

Команды PowerShell читают идентификаторы из отчёта. Для сохранённого примера подставь `./kafka-replay/observed.json`. Чтение по `--partition` позволяет осматривать данные, не вступая во входную группу NiFi.

```powershell
$r = Get-Content -Raw ./replay-run.json | ConvertFrom-Json
$bin = '/opt/kafka/bin'
$broker = 'kafka:29092'
docker compose exec -T kafka "$bin/kafka-consumer-groups.sh" --bootstrap-server $broker --describe --group $r.group
docker compose exec -T kafka "$bin/kafka-console-consumer.sh" --bootstrap-server $broker --topic $r.input_topic --partition 0 --offset earliest --isolation-level read_committed --timeout-ms 4000 --formatter-property print.offset=true
docker compose exec -T kafka "$bin/kafka-console-consumer.sh" --bootstrap-server $broker --topic $r.output_topic --partition 0 --offset earliest --isolation-level read_committed --timeout-ms 4000 --formatter-property print.offset=true --formatter-property print.headers=true
```

Оба читателя завершаются по тайм-ауту без новых записей. В этой версии CLI пишет `TimeoutException`, затем число прочитанных сообщений. Для короткого учебного топика с одним сегментом можно увидеть и служебные записи на самом брокере.

```powershell
$segment = "/var/lib/kafka/data/$($r.output_topic)-0/00000000000000000000.log"
docker compose exec -T kafka "$bin/kafka-dump-log.sh" --files $segment --deep-iteration --print-data-log
```

## Где проходит граница exactly-once

В NiFi 2.12.0 обычный commit после приёма зависит от флага `Commit Offsets`. Выходной producer вызывает `commitTransaction()`. В момент первого выходного коммита мы независимо измерили, что сохранённый входной offset всё ещё равен 0. Идемпотентность Kafka producer защищает от сетевых повторов отправки. Повторная обработка входа после рестарта стала новой публикацией. [ConsumeKafka](https://github.com/apache/nifi/blob/rel/nifi-2.12.0/nifi-extension-bundles/nifi-kafka-bundle/nifi-kafka-processors/src/main/java/org/apache/nifi/kafka/processors/ConsumeKafka.java#L631-L645) · [Транзакционный producer NiFi](https://github.com/apache/nifi/blob/rel/nifi-2.12.0/nifi-extension-bundles/nifi-kafka-bundle/nifi-kafka-service-shared/src/main/java/org/apache/nifi/kafka/service/producer/transaction/KafkaTransactionalProducerWrapper.java#L45-L61) · [KafkaProducer API](https://kafka.apache.org/42/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html)

Для атомарного Kafka → Kafka в одном кластере приложение может в одной транзакции отправить результат и вызвать `sendOffsetsToTransaction` с позицией следующей входной записи и метаданными той же группы, а затем вызвать `commitTransaction()`. Если транзакция завершилась, читатель видит результат, и группа продолжает с 1. Если она была прервана, результат этой попытки скрыт от `read_committed`, а вход 0 доступен для повторной обработки. [Контракт Kafka producer](https://kafka.apache.org/42/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html#sendOffsetsToTransaction(java.util.Map,org.apache.kafka.clients.consumer.ConsumerGroupMetadata))

**Для самопроверки.** Как по двум заголовкам отличить восстановление того же FlowFile от повторного чтения входа? Как узнать, куда делся выходной offset 1? Почему одного снимка `LAG=0`, сделанного после остановки процессоров, недостаточно для вывода об exactly-once?
