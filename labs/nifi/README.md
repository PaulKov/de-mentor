# Стенд de-mentor для Apache NiFi

Учебный автономный контур на синтетических заказах. Нужны Docker Compose, Linux containers, Python 3 и около 4 ГБ доступной памяти для этого контура. Версии основных компонентов — NiFi 2.12.0, Kafka 4.2.2 и PostgreSQL 17.

## Запуск

Из корня репозитория:

```sh
cd labs/nifi
docker compose up -d --build --wait --wait-timeout 240
docker compose exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:29092 --create --if-not-exists --topic nifi.orders.v1 --partitions 3 --replication-factor 1
python bootstrap.py --run-once
python bootstrap.py --formats --run-once
docker compose ps
```

Если команда в твоей системе называется `python3`, используй её вместо `python`. Bootstrap повторно использует созданные группы. С флагом `--run-once` он запускает генераторы один раз. При открытии [NiFi UI](https://localhost:28443/nifi/) браузер может спросить подтверждение для учебного самоподписанного сертификата. Логин **student**, пароль **Practice-Only-2026**.

| Сервис | Адрес из NiFi | Адрес с хоста |
| --- | --- | --- |
| NiFi | `https://nifi:8443` | [Интерфейс](https://localhost:28443/nifi/) |
| Kafka | `kafka:29092` | `localhost:39092` |
| PostgreSQL | `jdbc:postgresql://postgres:5432/integration` | `localhost:35432` |
| REST и SOAP | `http://mock-api:8080` | [Заказы](http://localhost:28090/orders) |
| FTP | `ftp:2121` | Подключай из NiFi |
| SMB | `smb:445`, share `incoming` | Подключай из NiFi |

PostgreSQL использует `student` / `practice-only-db`, FTP и SMB — `student` / `practice-only-files`. Реквизиты предназначены для этого контура. Опубликованные порты привязаны к loopback. Одноброкерный Kafka и одновузловый NiFi помогают воспроизвести семантику потока и ошибки без настройки кластера.

## Проверка

```sh
docker compose exec -T postgres psql -U student -d integration -c "SELECT event_id, customer_id FROM integration_events ORDER BY event_id"
docker compose exec -T kafka /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server kafka:29092 --topic nifi.orders.v1
docker compose exec -T nifi ls -l /lab/output/transformed
```

**Lab 01 · Kafka and PostgreSQL.** После первого прогона БД содержит `o-101 / c-1` и `o-102 / NULL`. Во второй запуск топик получает повтор, а бизнес ключи таблицы остаются прежними. В starter flow весь массив JSON идёт одним Kafka сообщением.

**Lab 02 · XML and Groovy.** Один файл содержит `<normalized-order id="o-101" …>` с двумя позициями, второй содержит `{"event_id":"o-101","qty":2}`. Для просмотра содержимого используй provenance или `docker compose exec -T nifi sh -c 'cat /lab/output/transformed/*'`.

### Пауза и восстановление

[Практика 09. Одно начисление при повторной доставке](points/README.md) запускает отдельный NiFi, завершает его после коммита PostgreSQL и проверяет по смещениям Kafka, UUID FlowFile и балансу три вида повтора.

[Практика 09б. Kafka → NiFi → Kafka](kafka-replay/README.md) проверяет, что прочитает потребитель с `read_committed` после падения NiFi между выходной публикацией и фиксацией входной позиции.

[Практика 09в. Очередь NiFi и commitSync](commit-window/README.md) останавливает поток в точке вызова Kafka и позволяет увидеть в очереди восстановленный и заново созданный FlowFile.

```sh
docker compose stop
docker compose up -d --wait
```

Named volumes сохраняют настройки NiFi, очереди, локальное state, Kafka и БД. Для fault drill останавливай конкретный сервис, затем возвращай его. Для изолированного повторного чтения задай отдельный consumer group и отдельную таблицу или каталог результатов.

[Вернуться к уроку 07](../../lessons/lesson-07-nifi/)
