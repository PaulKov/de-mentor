# Карта компонентов NiFi

Начинай выбор с единицы обработки. Файл подходит для одной поставки. Record подходит для строки со схемой. Запись Kafka имеет собственные ключ, заголовки и позицию. Один FlowFile может включать весь файл либо несколько записей Kafka.

| Задача | Компоненты | Что проверять |
| --- | --- | --- |
| Простейший вход | GenerateFlowFile | Run Once и размер входа |
| Файлы | ListFile/FetchFile, ListFTP/FetchFTP, ListSmb/FetchSmb | Состояние листинга, права чтения и готовность файла |
| HTTP клиент | InvokeHTTP | Request и response relationships, timeout, retry budget |
| HTTP сервер | HandleHttpRequest/HandleHttpResponse с общим HTTP Context Map | Endpoint, correlation, timeout и число активных запросов |
| Kafka | PublishKafka, ConsumeKafka, Kafka Connection Service | Topic, key, consumer group, listener, security protocol и output strategy |
| База данных | ExecuteSQLRecord, PutDatabaseRecord, DBCPConnectionPool | Driver, URL, схема, transaction boundaries и batch |
| Атрибуты | UpdateAttribute, RouteOnAttribute | Expression Language scope, type coercion, unmatched |
| JSON | EvaluateJsonPath, JoltTransformJSON, ValidateJson | Контракт массива, валидность и предел размера |
| Record преобразования | ConvertRecord, UpdateRecord, QueryRecord, ValidateRecord | Schema Access Strategy и RecordPath |
| XML | EvaluateXPath, TransformXml | Namespace, синтаксис, совпадение шаблона и проверка выхода |
| Код | ExecuteGroovyScript | Успех, ошибки, ProcessSession и потребление памяти |
| Разбиение и сборка | SplitText, SplitRecord, MergeContent, MergeRecord | Размер, fragment metadata, timeout неполного пакета |
| Повторы | RetryFlowFile, named relationships | Лимит, backoff, идемпотентность, очередь после исчерпания |
| Отладка | Queue, Bulletins, Data Provenance | ID события, время, фактический downstream результат |
| Границы потоков | Process Group, Input Port, Output Port, Funnel | Входной контракт группы, связи, обратное давление |

**Scheduler.** Timer driven задаёт частоту опроса. Concurrent Tasks определяет одновременные запуски процессора, а не число Kafka partitions. Сверяй пределы внешней системы и порядок результатов. Для источников, которые должны выполняться на одном узле, проверь настройку запуска на Primary Node и поведение при смене узла.

**Конфигурация.** Параметры `#{kafka.bootstrap}` подставляют значение из Parameter Context. Expression Language `${filename}` вычисляет атрибут в поддерживаемом свойствах scope. RecordPath `/items[*]/sku` работает с содержимым record. Секреты помещай только в поддерживаемые sensitive параметры и свойства.

**Выбор инструмента.** NiFi подходит для приёма и доставки файлов, API и событий с управляемыми очередями. Kafka Connect подходит для типовых коннекторов Kafka с минимальной логикой. Flink подходит для stateful окон, join и расчётов по event time. В одном pipeline NiFi может принять неоднородный вход и нормализовать его, Kafka удерживает журнал, Flink рассчитывает потоковые производные. Когда одновременно требуются корректный ретрай и точная семантика внешней записи, сначала фиксируй границу каждого инструмента.

[Справочник компонентов NiFi](https://nifi.apache.org/components/) · [Руководство NiFi](https://nifi.apache.org/nifi-docs/user-guide.html) · [Kafka Connect](https://kafka.apache.org/documentation/#connect) · [Урок 06 про Flink](../lesson-06/)
