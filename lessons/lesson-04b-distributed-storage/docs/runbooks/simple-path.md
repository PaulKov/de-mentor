# Simple path — 90 минут

Этот маршрут даёт основу перед Iceberg. Если есть 90 минут, не пытайся заучить каждую настройку Ceph: сосредоточься на contract, data path и failure domain.

## 1. Контракт (15 минут)

Прочитай разделы 1–2 [internals](../deep-dives/distributed-storage-internals.md). Для directory, database volume и Iceberg warehouse заполни storage contract в [workbook](../student-workbook.md). Объясни, почему mount S3 не автоматически равен POSIX.

## 2. Три архитектуры (25 минут)

Разбери диаграммы HDFS, Ceph и SeaweedFS. Для каждой обозначь:

- component, который знает namespace/metadata;
- component, который знает placement;
- кто передает payload bytes;
- как обнаруживается disk/node failure;
- как возвращается нужная избыточность.

## 3. Локальная S3 лабораторная (25 минут)

Проверь bucket list, создай уникальный `storage-lesson/<guid>/probe.txt`, выполни HEAD/GET/LIST, открой filer UI и удали только свой object key. Сохрани результаты. Не удаляй bucket/volume.

## 4. Выбор и recap (25 минут)

Посмотри [decision matrix](../decision-matrix.md), выбери case B или C из workbook, назови один первый выбор и две альтернативы. Ответь:

1. Почему формула replica/EC ничего не говорит о latency до измерения?
2. Чем S3 key отличается от path directory?
3. Что добавляет Iceberg поверх object storage?
4. Что не проверил локальный Compose?

Продолжи в [Lesson 05: Iceberg](../../../lesson-05/README.md).
