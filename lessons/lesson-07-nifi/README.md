# Урок 07 · Apache NiFi с нуля

На синтетических заказах разберёшься, как NiFi принимает данные, проверяет формат, отправляет результат в Kafka и восстанавливает обработку после сбоя. Для начала достаточно уметь открыть терминал. Команды, JSON, Kafka, XML и Groovy разбираются по ходу.

[Презентация с заметками преподавателя](artifacts/apache-nifi-course.pptx) · [Стенд](../../labs/nifi/README.md) · [Воркбук](workbook.md) · [Карта компонентов](processor-map.md) · [Deep Dive](deep-dive.md) · [Итоговый проект](capstone.md)

## Основная часть

| № | Тема и результат | Материалы |
| --- | --- | --- |
| 01 | **Первый поток.** Canvas, FlowFile, processor, relationship, connection, Process Group, provenance | [Видео](artifacts/video/01-first-flow.mp4) · [Текст](media/01-first-flow.md) · [Практика](workbook.md#01-первый-поток) |
| 02 | **JSON и JSONL.** Границы сообщения, Record API, схема, повреждённая строка | [Видео](artifacts/video/02-jsonl.mp4) · [Текст](media/02-jsonl.md) · [Практика](workbook.md#02-json-и-jsonl) |
| 03 | **JOLT.** Преобразование вложенных заказов, индексы, null, пустые массивы | [Видео](artifacts/video/03-jolt.mp4) · [Текст](media/03-jolt.md) · [Практика](workbook.md#03-jolt-и-маршрутизация) |
| 04 | **Kafka.** Партиции, ключи, группы, offsets, публикация и чтение через NiFi | [Видео](artifacts/video/04-kafka.mp4) · [Текст](media/04-kafka.md) · [Практика](workbook.md#04-kafka-и-postgresql) |
| 05 | **XML, XPath и XSLT.** Namespace, выбор узлов, таблица стилей, SOAP Fault | [Видео](artifacts/video/05-xml.mp4) · [Текст](media/05-xml.md) · [Практика](workbook.md#05-xml-xpath-и-xslt) |
| 06 | **Groovy.** Чтение и обновление FlowFile, StreamCallback и маршрутизация ошибок | [Видео](artifacts/video/06-groovy.mp4) · [Текст](media/06-groovy.md) · [Практика](workbook.md#06-groovy) |
| 07 | **Интеграции.** REST, SOAP, FTP, SMB и PostgreSQL через JDBC | [Видео](artifacts/video/07-connectors.mp4) · [Текст](media/07-connectors.md) · [Практика](workbook.md#07-rest-soap-ftp-smb-и-jdbc) |

## Deep Dive

| № | Тема и результат | Материалы |
| --- | --- | --- |
| 08 | **Runtime и репозитории.** ProcessSession, content claims, backpressure, state, provenance, кластер | [Видео](artifacts/video/08-internals.mp4) · [Текст](media/08-internals.md) · [Разбор](deep-dive.md#08-runtime-и-репозитории) |
| 09 | **Гарантии доставки.** Kafka offsets, внешние транзакции, idempotency, fencing и replay | [Видео](artifacts/video/09-delivery.mp4) · [Текст](media/09-delivery.md) · [Разбор](deep-dive.md#09-гарантии-доставки) |
| 10 | **Эксплуатация.** Наблюдаемость, версионирование, инциденты и итоговый проект | [Видео](artifacts/video/10-operations.mp4) · [Текст](media/10-operations.md) · [Разбор](deep-dive.md#10-эксплуатация) |

Видео содержат русскую синтезированную озвучку и переключаемые субтитры. Отдельные [файлы SRT](artifacts/video/) лежат рядом с MP4. Если GitHub показывает ссылку на бинарный файл, скачай MP4 через **Raw** или **Download**.

Начни с видео 01 и запуска стенда. Затем повторяй практики по порядку. После блоков 04, 06 и 10 выполни [самопроверку](quiz.md). Сначала сформулируй ответ, потом открой ключ.

← [Весь курс](../README.md) · [Урок 06: Kafka, Flink и Iceberg](../lesson-06/)
