# Практики Apache NiFi

Открой [стенд](../../labs/nifi/README.md) и перейди в `labs/nifi` в терминале. Для ручных экспериментов создавай отдельные process groups на canvas. Записывай конкретные доказательства, например ID события, значение атрибута, строку SQL или вывод команды.

## 01. Первый поток

1. В корне canvas создай пустую группу `Practice 01`. Открой её двойным щелчком, перетащи **Processor**, найди `GenerateFlowFile`. Выбери `Text`, установи `Custom Text` в `{"event_id":"o-001"}`.
2. Добавь `UpdateAttribute` и создай динамическое поле `source.system=lab`. Соедини генератор с ним по **success**. Добавь `PutFile`, задай `Directory=/lab/output/practice01` и соедини с `UpdateAttribute`. Для `PutFile.success` отметь auto-terminate. Для `failure` создай связь с остановленным `UpdateAttribute`, чтобы удержать ошибку в очереди. В нём тоже отметь auto-terminate для success.
3. На генераторе выбери **Run Once**. Перед запуском второго процессора открой меню соединения и **List queue**. Изучи размер, атрибуты и содержимое. Затем запусти следующие процессоры и проверь файл через `docker compose exec -T nifi ls /lab/output/practice01`.
4. Открой **Data Provenance**. Найди события создания, изменения атрибутов и записи. Результат сдачи — путь одного FlowFile от очереди до файла, включая его UUID и `source.system`.

| Термин | Где искать | Роль |
| --- | --- | --- |
| Processor | Canvas, Configure, Bulletin | Стадия обработки |
| Connection | Canvas, List queue | Очередь, backpressure, expiration |
| Relationship | Настройки connection/processor | Именованный исход |
| Controller Service | Настройки Process Group | Переиспользуемое подключение, reader или writer |
| Parameter Context | Меню и привязка к группе | Значения окружения, выражение `#{name}` |
| Expression Language | Свойства с EL | Вычисление, например `${filename}`, согласно scope свойства |
| RecordPath | Record processors | Выбор поля записи, например `/event_id` |

## 02. JSON и JSONL

1. Сравни [массив JSON](../../labs/nifi/fixtures/orders.json), [валидный JSONL](../../labs/nifi/fixtures/orders.jsonl) и [JSONL с ошибкой](../../labs/nifi/fixtures/orders-bad.jsonl). JSONL сохраняет по значению JSON на строку. Для упражнения договоримся о UTF‑8, отдельных JSON объектах, отсутствии пустых строк и стабильном ключе.
2. Собери `GenerateFlowFile → ConvertRecord → PutFile`. В генератор скопируй правильный JSONL. Создай `JsonTreeReader` (Root Node, Infer Schema) и `JsonRecordSetWriter` (Output Grouping = Array). Включи их и укажи в ConvertRecord. Результат содержит массив из двух элементов и `record.count=2`. Переключи writer на **One Line Per Object**, повтори и сравни форму.
3. Передай битый JSONL. Для пакетной валидации направляй **failure** ConvertRecord в карантин. Для независимых строк поставь `SplitText` с `Line Split Count = 1` без header lines. Подключи **splits** к validation/parse. В одной ветке сохраняй валидные строки, в другой исходный фрагмент с `segment.original.filename` и `fragment.index`. Проверь, что случилось с третьей строкой.
4. Добавь пустой ID и `qty` как строку. Введи явную схему читателя или `ValidateJson` с object schema. При использовании `ValidateJson` для всего JSONL включи его режим newline-delimited JSON. Запиши отдельно синтаксическую ошибку, нарушение схемы и нарушение бизнес-правила.

[JsonTreeReader](https://nifi.apache.org/components/org.apache.nifi.json.JsonTreeReader/) · [JsonRecordSetWriter](https://nifi.apache.org/components/org.apache.nifi.json.JsonRecordSetWriter/) · [SplitText](https://nifi.apache.org/components/org.apache.nifi.processors.standard.SplitText/) · [ValidateJson](https://nifi.apache.org/components/org.apache.nifi.processors.standard.ValidateJson/)

## 03. JOLT и маршрутизация

В **Lab 01** открой **2 Normalize JSON**. Режим Chain, спецификация [orders.jolt.json](../../labs/nifi/fixtures/orders.jolt.json). Скопируй генератор и JoltTransformJSON в свою группу и подключи две очереди к остановленным процессорам, чтобы сравнить **success** и **failure**.

1. Запусти только `shift`, затем верни `default` и объясни, откуда появляется `items: []`.
2. Проследи путь одного `sku`. В `[&4].items[&1].sku` первый индекс указывает на заказ, второй на позицию. Замени один индекс в копии спецификации и сравни выход двух заказов.
3. Прогони таблицу входов.

| Вход | Требование |
| --- | --- |
| Первый заказ с двумя позициями | Две позиции сохраняют порядок |
| Второй заказ без клиента | Сохранён `event_id`, `items=[]`. Реши, должен ли появляться `customer_id:null` |
| `lines` отсутствует, пуст, равен null или имеет одну позицию | Опиши разрешённые формы |
| `lines` стал объектом | Явный отказ либо задокументированное приведение к массиву |
| Битый JSON | `failure` и сохранённый исходник |
| Количество `"2"` вместо `2` | Явное приведение или отказ |

Вынеси небольшой ключ с `EvaluateJsonPath`, затем используй `RouteOnAttribute`. Для одиночного объекта задай `Destination=flowfile-attribute` и dynamic property `order.id=$.event_id`. Добавь ветку для пустого или отсутствующего ключа. Сравни выход с эталонным JSON деревом, игнорируя пробелы и порядок полей.

## 04. Kafka и PostgreSQL

В **Lab 01** просмотри `Lab Kafka`, `PublishKafka`, `ConsumeKafka` и `5 UPSERT orders`. Топик `nifi.orders.v1`, три partitions, группа `nifi-orders-db-v1`, таблица `integration_events`.

```sh
docker compose exec -T kafka /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server kafka:29092 --topic nifi.orders.v1
docker compose exec -T kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka:29092 --describe --group nifi-orders-db-v1
docker compose exec -T postgres psql -U student -d integration -c "SELECT event_id, customer_id, first_seen_at FROM integration_events ORDER BY event_id"
```

1. Запиши исходную картину. Дважды запусти генератор. Сравни позицию брокера, сообщения и бизнес ID. Transaction markers занимают offsets, поэтому разница смещений и число payload могут отличаться.
2. Останови только `5 UPSERT orders`, подай следующий образец. Проследи, как consumer и очередь прогрессируют без изменения БД. Возобнови sink и дождись освобождения очереди.
3. Для публикации по одному заказу раздели массив и вынеси ключ в атрибут либо настрой record mode у PublishKafka. Добавь события с одинаковыми и разными ключами и проверь placement и порядок. Уникальность защищай в PostgreSQL.
4. Создай отдельный consumer group с `earliest` и записью результата в файл. Сверь диапазон прочитанных offsets. У прежней группы `earliest` не сбрасывает подходящую сохранённую позицию.
5. Для fault drill отправь в учебный topic битый JSON. Проверь карантин `/lab/output/quarantine` и результат в таблице.

## 05. XML, XPath и XSLT

В **Lab 02 · XML and Groovy** выполни **Run Once** на **Seed XML**. В **Apply stylesheet** указан `/lab/fixtures/order.xsl`, Secure Processing включён.

1. Сравни [XML](../../labs/nifi/fixtures/order.xml) и [XSLT](../../labs/nifi/fixtures/order.xsl). Свяжи `o` с `urn:lab:orders`. `/o:Order/o:Id` даёт `o-101`, а `/o:Order/o:Customer/@id` даёт `c-1`.
2. Проверь `normalized-order` и две позиции. Поменяй префикс XML, сохранив URI. Затем поменяй URI и выясни, как отсутствие ожидаемого корня обнаружить отдельной валидацией.
3. Прогони отсутствующий `Customer`, пустой `Id`, повторяющиеся `Line` и повреждённый синтаксис. Зафиксируй ошибку парсинга и отдельно валидный XML с неправильным бизнес-содержимым. Для реального контракта сверяй политику внешних ресурсов и лимиты парсера.
4. Прочитай [синтетический IDoc](../../labs/nifi/fixtures/idoc.xml). Сохрани ведущие нули `DOCNUM`, обработай повторяющиеся позиции как коллекцию.

## 06. Groovy

Запусти **Seed JSON**, затем открой [normalize.groovy](../../labs/nifi/fixtures/normalize.groovy). Выход — `{"event_id":"o-101","qty":2}`. `session.get()` возвращает вход, `StreamCallback` читает и пишет контент, `session.transfer()` передаёт FlowFile по выбранной ветке.

1. Прогони `{"event_id":"   "}`, `{"event_id":42}`, `{}` и невалидный JSON. Ожидается failure и `lab.error=invalid_json_or_event_id`. Проверь исходные байты в `/lab/output/transform-errors`.
2. Добавь проверку `qty` как положительного целого числа. Сравни `1`, `1.5`, `"1"`, `0` и отсутствующее поле. Согласуй действие для каждого.
3. Выдели ошибку данных из обработки сбоев I/O. Укажи, какая ошибка допускает повтор, какую нужно показать оператору, а для какой достаточно quarantine. Объясни, как размер входа и concurrent tasks влияют на heap.

## 07. REST, SOAP, FTP, SMB и JDBC

| Источник | Сборка | Проверка |
| --- | --- | --- |
| REST | `GenerateFlowFile → InvokeHTTP → RouteOnAttribute` | `http://mock-api:8080/orders?case=429&run=a`, `503`, `400`, `timeout`, `malformed`, `empty`. Для повторной серии 429/503 используй новый `run` |
| SOAP | `GenerateFlowFile → InvokeHTTP POST → XML validation` | Из [WSDL](../../labs/nifi/fixtures/order.wsdl) возьми action и binding. Используй [envelope](../../labs/nifi/fixtures/soap-request.xml). Сравни `/soap`, `?case=fault`, `?case=fault200` |
| FTP | `ListFTP → FetchFTP → PutFile` | `ftp:2121`, passive mode, путь `/`. Сравни размер и hash, перезапусти листинг |
| SMB | `ListSmb → FetchSmb → PutFile` | `smb:445`, `incoming`. Сравни листинг и успешное чтение |
| JDBC | `ExecuteSQLRecord` с DBCP и Record Writer | Прочитай `source_orders`. Выборка по `(updated_at,id)` должна сохранять обе записи с одинаковым timestamp |

Для REST сохрани status, `Retry-After`, число попыток и класс ошибки. Для FTP/SMB сравни имя, хеш, размер и состояние листинга. Для JDBC проверь пустой диапазон, совпадающий timestamp и имитацию позднего commit.

## 09. Начисление баллов при повторной доставке

Пройди [опыт с аварией после коммита PostgreSQL](../../labs/nifi/points/README.md). По отчёту найди две попытки с одинаковым UUID FlowFile, затем две попытки с одинаковым Kafka offset и разными UUID. Объясни, какую запись в БД проверяет обработчик перед начислением и почему перемотка Kafka не откатывает баланс.
