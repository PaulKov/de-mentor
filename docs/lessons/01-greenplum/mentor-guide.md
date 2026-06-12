# Mentor Guide

## Главная Идея

Не пытайся дать всю теорию Greenplum за час. Первый урок должен сформировать правильный рефлекс: перед созданием таблицы в MPP-базе инженер обязан подумать о grain, ключах join, cardinality и распределении нагрузки по сегментам.

## Как Вести Урок

Используй презентацию `artifacts/greenplum-theory.pptx` вместе с поминутным presenter guide:

- deck source: `decks/greenplum-theory/slides`;
- facilitator guide: `decks/greenplum-theory/facilitator-guide.md`;
- deep dive: `docs/lessons/01-greenplum/deep-dives/master-segment-data-path.md`;
- практика ученика: `docs/lessons/01-greenplum/student-workbook.md`;
- автоматическая проверка: `python3 mentor-lab.py check greenplum`.

Презентация должна занимать не весь час, а примерно половину урока: 33 минуты на theory framing, 12 минут на hands-on diagnostics, затем incident/capstone/review. Подробный тайминг по каждому слайду находится в `facilitator-guide.md`.

Advanced track подключай только после базового цикла `skew -> EXPLAIN -> fix -> evidence`. Для сильного ученика используй appendix-слайды и три deep dive:

- `deep-dives/explain-plan-reading.md` - читать план по scan/local work/join/Motion/global work/Rows out;
- `deep-dives/physical-joins-in-mpp.md` - отличать локальный join algorithm от MPP data movement;
- `deep-dives/mpp-system-taxonomy.md` - сравнивать SMP, MPP, EPP, lakehouse и HTAP по bottleneck.

### 0-5 Минут: Контекст

Скажи ученику:

> Сегодня мы будем смотреть не на синтаксис SQL, а на физику выполнения запроса. Один и тот же SQL может быть нормальным в PostgreSQL и дорогим в Greenplum.

Проверь, что ученик понимает разницу между transactional workload и analytical workload.

Коротко обозначь классы систем:

- `SMP`: один большой сервер, общая память/storage, проще в эксплуатации, но масштабируется в основном вертикально;
- `MPP`: shared-nothing, много сегментов с собственными ресурсами, хорошо масштабируется горизонтально, но требует distribution design;
- `EPP / cloud elastic`: compute и storage часто масштабируются независимо, удобно для эластики, но требует контроля стоимости и движения данных.

Обязательно покажи разницу между control plane и data plane:

- master/coordinator отвечает за подключение, metadata, planning, dispatch и gather;
- QE на segments исполняют slices и читают локальные данные;
- Motion передает строки между QE через interconnect;
- для больших загрузок избегай master как data pipe: показывай `gpfdist`/external tables как parallel segment path.

### 5-15 Минут: Архитектура

Объясни через три роли:

- coordinator принимает SQL и строит план;
- segments хранят данные и выполняют работу;
- interconnect передает данные между сегментами.

Контрольный вопрос:

> Если таблица распределена по `customer_id`, где физически лежит строка конкретного клиента?

### 15-25 Минут: Distribution

Дай правило первого приближения:

> Хороший distribution key часто совпадает с частым join key, имеет высокую cardinality и равномерно распределяет строки.

Попроси ученика выбрать ключ для `orders`, `payments`, `customers`.

### 25-35 Минут: EXPLAIN

Сконцентрируйся на Motion:

- `Gather Motion` собирает результат;
- `Broadcast Motion` копирует данные на сегменты;
- `Redistribute Motion` перераспределяет данные по новому ключу.

Не уходи глубоко в optimizer. Цель - научить замечать "данные поехали по сети".

### 35-52 Минут: Практика

Пусть ученик выполняет workbook сам. Помогай вопросами:

- "Какой сегмент получил больше строк?"
- "Почему низкая cardinality плоха для distribution?"
- "Что изменилось в плане после исправления?"

### 52-58 Минут: Design Review

Дай мини-кейс:

> У нас есть заказы, клиенты, товары и платежи. Нужно построить факт продаж для ежедневной аналитики по регионам, товарам и способам оплаты. Какой grain, distribution key и partition key ты выберешь?

Оценивай не "правильный ответ", а качество аргументации.

## Частые Ошибки Ученика

- Выбирает `status` как distribution key, потому что по нему часто фильтруют.
- Думает, что primary key автоматически решает распределение.
- Игнорирует cardinality.
- Смотрит только на SQL и не смотрит на `EXPLAIN`.
- Путает `Hash Join` как локальный алгоритм с `Redistribute Motion` как сетевой ценой.
- Думает, что хороший distribution key делает локальными все joins.
- Называет MPP "просто масштабированным PostgreSQL" и не видит network как часть плана.
- Не отличает partitioning от distribution.

## Критерии Успеха

Урок прошел хорошо, если ученик своими словами объяснил:

- почему `DISTRIBUTED BY(status)` плох для факта;
- зачем смотреть `gp_segment_id`;
- почему Motion может быть дорогим;
- чем co-located join отличается от Broadcast/Redistribute join;
- почему `Rows out` и фактические строки важнее красивой формы SQL;
- когда нужен SMP, MPP, EPP/cloud или lakehouse;
- чем ключ распределения отличается от partition key.
