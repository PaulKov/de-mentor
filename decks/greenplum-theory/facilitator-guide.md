# Facilitator Guide: Greenplum Theory Deck

Цель презентации - быстро собрать mental model: Greenplum как MPP-система, цена движения данных, QD/QE, storage, distribution, partitioning intro и доказательный подход к исправлениям.

Используй два маршрута:

- simple path: 60 минут, слайды 1-23, короткая практика и домашка.
- deep-dive path: 90-120 минут, simple path плюс appendix 24-30.

Связанные материалы:

- `docs/lessons/01-greenplum/runbooks/simple-path.md`
- `docs/lessons/01-greenplum/runbooks/deep-dive-path.md`
- `docs/lessons/01-greenplum/runbooks/homework-plan.md`
- `docs/lessons/01-greenplum/student-workbook.md`
- `labs/greenplum/examples/storage-and-partitioning.sql`

## Simple Path: 60-Минутный Маршрут

| Время | Слайд | Мин | Что сказать емко | Вопрос ученику | Практика / переход |
| --- | --- | ---: | --- | --- | --- |
| 00:00-02:00 | 1. Greenplum MPP: мышление дата инженера | 2 | Сегодня учимся думать не только SQL, но и физикой данных: где лежит строка, кто ее обрабатывает, поедет ли она по сети. | Чем аналитический запрос отличается от OLTP-запроса по нагрузке? | Переход к классам систем. |
| 02:00-05:00 | 2. SMP, MPP, EPP | 3 | SMP проще и вертикален, MPP shared-nothing и требует distribution, EPP/cloud добавляет эластику и cost/shuffle observability. | Где быстрее появится потолок: SMP или MPP? | Объясни, почему Greenplum ближе к MPP. |
| 05:00-08:00 | 3. Greenplum vs sharded PostgreSQL | 3 | Greenplum vs sharded PostgreSQL: Greenplum не sharded PostgreSQL, а единый SQL endpoint с distributed optimizer/executor/interconnect. | Кто в Greenplum строит distributed plan? | Показать QD/QE как native engine. |
| 08:00-10:00 | 4. Shared-nothing topology | 2 | Coordinator планирует и dispatch-ит; segments хранят и исполняют; interconnect передает строки. | Если строка на segment 1, может ли segment 0 обработать ее без движения? | Перейти к master. |
| 10:00-12:00 | 5. Master / coordinator для новичка | 2 | Master - control plane и final gather, но не место для больших bulk data потоков. | Почему master может стать bottleneck? | Развести control plane/data plane. |
| 12:00-15:00 | 6. QD / QE / gang / slices | 3 | Простая аналогия: QD - диспетчер, QE - исполнители, gang - команда, slice - участок работы. | Что такое gang простыми словами? | Подготовить QD/QE deep dive. |
| 15:00-18:00 | 7. QD/QE dispatch deep dive | 3 | QD режет plan на slices, выделяет gang, создает QueryDispatchDesc, QE исполняют slice. | Почему slice часто рядом с Motion? | Углубление только по готовности ученика. |
| 18:00-20:00 | 8. Interconnect и Motion | 2 | Motion показывает физическое движение строк: Gather, Broadcast, Redistribute. | Redistribute Motion - это всегда ошибка? | Перейти к bulk I/O. |
| 20:00-22:00 | 9. Bulk I/O paths | 2 | `gpfdist external table` позволяет segments читать параллельно; master остается control plane. | Почему не грузить терабайты через coordinator? | Перейти к storage. |
| 22:00-25:00 | 10. Heap vs AO row vs AOCO | 3 | Heap, AO row, AOCO column: row/mutable, append-heavy row, append-heavy columnar analytics. | Почему AOCO не исправит skew? | Открыть SQL demo. |
| 25:00-28:00 | 11. Heap vs AOCO DDL | 3 | Покажи `appendoptimized=true`, `orientation=column`, `\d+` и catalog checks. | Что проверяет `access_method`? | Выполнить `storage-and-partitioning.sql`. |
| 28:00-31:00 | 12. Columnstore defaults | 3 | gp_default_storage_options можно задать на database/role/instance level, но table/column explicit важнее для урока. | Почему instance-level gpconfig не выполняем без причины? | Перейти к distribution. |
| 31:00-34:00 | 13. Distribution key | 3 | Distribution key выбирается через cardinality, join locality и равномерность. | Почему `status` плохой ключ? | Запустить skew query. |
| 34:00-37:00 | 14. Skew через gp_segment_id | 3 | `gp_segment_id` превращает архитектурный спор в измерение. | Что будет, если один segment получил почти все строки? | Workbook task 2. |
| 37:00-40:00 | 15. EXPLAIN и Motion | 3 | Motion nodes - первый маркер MPP-цены в плане. | Что спросить, увидев Redistribute Motion? | Workbook task 3-4. |
| 40:00-42:00 | 16. Partitioning intro | 2 | partitioning intro: pruning/retention != distribution. `PARTITION BY RANGE (sale_date)` помогает датам, но не размещает строки по сегментам. | Почему partition key не равен distribution key? | Глубина переносится в Lesson 02. |
| 42:00-44:00 | 17. Диагностический цикл | 2 | Измерить, объяснить, изменить, проверить. Без evidence фикс остается догадкой. | Какой артефакт докажет skew? | Ученик работает руками. |
| 44:00-48:00 | 18. Practice checkpoint | 4 | Держи слайд как карту: skew -> EXPLAIN -> compare -> RCA. | Что ты уже доказал? | Выполнить workbook блоки. |
| 48:00-51:00 | 19. Incident mode | 3 | Теперь это не упражнение, а замедлившийся отчет и RCA. | Какие три гипотезы проверим первыми? | `mentor-lab.py incident start`. |
| 51:00-54:00 | 20. Fix and evidence | 3 | Фикс = physical change + повторный evidence. | Какие два запроса приложишь к RCA? | Сравнить bad/good table. |
| 54:00-56:00 | 21. Capstone mart design | 2 | Сначала grain, затем distribution, partitioning, storage и risks. | Какой grain у daily marketplace revenue? | Мини design review. |
| 56:00-57:00 | 22. Automation | 1 | CLI делает урок повторяемым: runbook, check, hint, grade, report. | Какая команда покажет homework route? | `mentor-lab.py runbook greenplum homework`. |
| 57:00-60:00 | 23. Что ученик должен унести | 3 | Greenplum = MPP; master control plane; segments data plane; skew измерим; Motion виден; фиксы доказываются. | Один принцип, который применишь в следующей модели? | Выдать `homework.md` и Lesson 02. |

## Deep-Dive Path: Appendix 24-30

Appendix не обязателен для первого часа. Открывай его, если ученик уверенно прошел базовый цикл и задает вопросы про optimizer, executor и storage internals.

| Слайд | Мин | Когда включать | Что сказать емко | Практика |
| --- | ---: | --- | --- | --- |
| 24. APPENDIX: как читать EXPLAIN | 6 | Ученик видит Motion, но теряется в плане. | План читаем как маршрут: scans -> local work -> join -> Motion -> global work -> Rows out. | Заполнить ladder в `student-workbook.md`. |
| 25. Physical joins in MPP | 6 | Ученик говорит "там Hash Join" как полный ответ. | Hash Join - локальный алгоритм; co-located join, Broadcast и Redistribute - data movement axis. | Сравнить customer_id и product_id joins. |
| 26. Broadcast vs Redistribute | 5 | Нужно объяснить маленькую dimension vs большой fact. | Broadcast хорош для маленькой стороны после фильтров; Redistribute - цена несовпадения ключей. | Назвать, какую сторону дешевле двигать. |
| 27. Hash Join deep dive | 5 | Ученик готов к executor-level деталям. | QE строит hash table на inner side, probe-ит outer side, при memory pressure идут batches/workfiles. | Найти build/probe risk. |
| 28. QD/QE internals with source anchors | 6 | Нужна глубина по QD/QE без чтения всего C-кода. | Source anchors: `cdbdisp_query.c`, `nodeMotion.c`, `nodeHashjoin.c`, `joinpath.c`, `CdbPathLocus`. | Связать slice/gang/Motion с планом. |
| 29. Storage internals and ALTER TABLE caveats | 5 | Ученик спрашивает про AOCO и ALTER. | Storage change может требовать rewrite, locks, stats и maintenance window. | Составить production checklist. |
| 30. MPP-семейства: где цена архитектуры | 5 | Ученик спрашивает, почему не ClickHouse/Snowflake/Spark/Postgres. | Каждый класс систем переносит bottleneck: CPU, network Motion, remote storage, shuffle, metadata, cost. | Выбрать SMP/MPP/EPP/lakehouse/HTAP для 3 сценариев. |

## Мини-Шпаргалка По SMP / MPP / EPP

| Тип | Простое объяснение | Сильная сторона | Ограничение |
| --- | --- | --- | --- |
| SMP | Один большой сервер, общие CPU/memory/storage. | Простота и предсказуемость. | Вертикальный потолок. |
| Shared-disk | Несколько compute-узлов, общий storage. | Единый набор данных. | Storage/network contention. |
| MPP | Shared-nothing, каждый узел хранит и обрабатывает свою часть. | Горизонтальная аналитика. | Требует distribution design и контроля Motion/skew. |
| EPP / cloud elastic | Эластичная параллельная обработка с отделением compute/storage. | Масштабирование и гибкость. | Стоимость, shuffle, metadata и governance. |

`EPP` не такой универсальный академический термин, как `SMP` и `MPP`; используй его как удобный ярлык для cloud elastic DWH-подходов.

## Presenter Notes

- Не читай слайды дословно: один слайд = один главный тезис и один вопрос.
- На слайдах 6-8 держи глубину управляемой: analogies first, QD/QE deep dive only if ученик готов.
- На слайдах 10-12 произнеси точную формулу: `Heap, AO row, AOCO column`.
- На слайде 16 явно скажи: partitioning intro сегодня, deep partitioning lab на Lesson 02.
- Если время проседает, сократи appendix до ссылок на `deep-dive path`, но не выкидывай практику и homework handoff.
