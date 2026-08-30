# Live-практика Lesson 04: PySpark + Spark UI

Этот runbook — режиссёрский план для демонстрации на macOS из VS Code. Цель практики — не просто выполнить код, а провести ученика по цепочке доказательств:

```text
PySpark-код → physical plan → job/stages/tasks → runtime metrics → Parquet → reconciliation
```

## Готовность до прихода группы

1. Запусти в VS Code `Tasks: Run Task` → `Spark · Prepare stand`.
2. Убедись, что итог содержит все `PASS`, а master и два worker-а имеют статус `Up`.
3. Открой заранее:
   - Spark master UI: <http://localhost:18080>;
   - Spark worker 1: <http://localhost:18081>;
   - Spark worker 2: <http://localhost:18082>;
   - Google Slides: <https://docs.google.com/presentation/d/1U_u3cwqdCzz2oRoa_w5BT7btbLqUlBSou3rJe2YXni0/edit?usp=sharing>.
4. Не запускай одновременно Core и Deep: оба приложения используют порт `4040`.
5. Во время лекции не пересоздавай seed. Датасет уже детерминирован: `250 000` событий и `10 000` клиентов.

## Раскладка VS Code

Оставь только релевантные вкладки, в таком порядке:

1. `labs/spark/examples/lesson04_core_pipeline.py` — orchestration;
2. `labs/spark/mentor_spark_lab/schemas.py` — explicit schema;
3. `labs/spark/mentor_spark_lab/pipeline.py` — transformations и quality gates;
4. `labs/spark/examples/lesson04_deep_join.py` — A/B join experiment;
5. `lessons/lesson-04/docs/runbooks/live-practice.md` — этот сценарий;
6. `lessons/lesson-04/docs/runbooks/facilitator-skip-map.md` — аварийное сокращение.

Команды запускай через `Tasks: Run Task`: это исключает ошибки в длинных CLI-командах и передаёт Docker CLI в `PATH` интегрированного терминала.

Для интерактивных экспериментов открой `labs/spark/notebooks/` и запусти `Jupyter · Start server`. Одноразовое подключение kernel описано в [notebooks/README.md](../../../../labs/spark/notebooks/README.md). Notebook application UI работает на `14040`, поэтому не конфликтует с CLI demo на `4040`.

## Core-практика: 15 минут внутри маршрута Core 60

| Время | Действие ментора | Вопрос группе | Evidence |
| --- | --- | --- | --- |
| 00:00–02:00 | Покажи master UI и два worker-а | Где driver, а где executors? | 2 workers / 2 cores |
| 02:00–04:00 | Открой explicit schemas | Почему `inferSchema` — плохой production-контракт? | типы и nullability |
| 04:00–07:00 | Пройди `read → filter → join → groupBy → write` | Что lazy, а что запустит job? | transformations/actions |
| 07:00–09:00 | До запуска попроси предсказать план | Где ожидаем `Exchange`? Где безопасен broadcast? | гипотеза до измерения |
| 09:00–13:00 | Запусти `Spark · Core live (UI 5 min)` и смотри UI во время job | Какие границы stage создаёт shuffle? | formatted plan + UI `4040` |
| 13:00–14:00 | Сопоставь SQL / Stages в UI | Как связаны operator и shuffle metrics? | `Exchange`, read/write bytes |
| 14:00–15:00 | Покажи `PASS` и Parquet round-trip | Почему один успешный `show()` недостаточен? | counts + revenue reconciliation |

Пока приложение удерживается, открой <http://localhost:4040>. Иди по UI в порядке `Jobs → Stages → SQL → Executors`; не пытайся объяснить все поля сразу.

## Deep-dive: ещё 15 минут, маршрут 90

| Время | Действие ментора | Вопрос группе | Evidence |
| --- | --- | --- | --- |
| 00:00–03:00 | В `lesson04_deep_join.py` отключи auto-broadcast мысленно, не редактируя код | Какой join выберет Spark? | `SortMergeJoin` hypothesis |
| 03:00–06:00 | Запусти `Spark · Deep join live (UI 5 min)` | Сколько `Exchange` ожидаем слева и справа? | shuffle plan |
| 06:00–10:00 | Сравни планы `SHUFFLE_JOIN` и `BROADCAST_JOIN` | Что исчезло после broadcast hint? | 2-side shuffle vs broadcast |
| 10:00–13:00 | Сверь Stages/SQL metrics | Как доказать выигрыш, кроме времени на ноутбуке? | shuffle bytes / task count |
| 13:00–15:00 | Обсуди safety condition | Когда broadcast уронит executor/driver? | размер dimension + memory budget |

Главная формулировка для ученика: `broadcast` — не универсальная оптимизация; это решение, подтверждённое размером данных, memory budget и runtime metrics.

## Команды без VS Code Tasks

```bash
python3 mentor-lab.py student spark-foundations start --profile lesson04

python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_core_pipeline.py \
  -- --hold-seconds 300

python3 mentor-lab.py spark-submit spark \
  labs/spark/examples/lesson04_deep_join.py \
  -- --hold-seconds 300
```

## Что проговаривать во время ожидания job

- Сначала driver строит logical/physical plan; это ещё не обработка всего датасета.
- DAGScheduler режет job на stages, TaskScheduler назначает TaskSet на свободные
  executor slots; cluster manager к этому моменту уже выделил resources/executors.
- `action` создаёт job; shuffle-разрыв превращается в границу stages.
- `task` работает с partition, а не «со строкой» и не «с таблицей целиком».
- Python-код задаёт plan через PySpark API; основная DataFrame execution идёт в JVM executors.
- Время на локальном стенде не является production benchmark. Доказательство — сравнительный plan и runtime metrics при одинаковом входе.
- `cache()` ленив: первый action materialize partitions через BlockManager,
  следующий action reuse их; после эксперимента нужен `unpersist()`.

## Аварийный сценарий

| Симптом | Решение без потери учебной цели |
| --- | --- |
| `4040` не открывается | Убедись, что task ещё держит приложение; перезапусти с `--hold-seconds 300` |
| Master UI доступен, application не стартует | Выполни `Spark · Readiness check`, затем повтори demo |
| Не хватает времени | Покажи уже напечатанный formatted plan и `PASS`; сократи навигацию UI до `SQL → Details` |
| Интернет недоступен | PPTX и весь код локальны; Spark image и seed уже подготовлены |
| Случайно запущены две demo | Останови один терминал `Ctrl+C`, дождись освобождения `4040`, повтори нужный task |

## Критерий завершения практики

Практика закончена, когда ученик может без подсказки:

1. назвать SparkSession/SparkContext, driver, executor, partition, job, stage и task;
2. предсказать хотя бы один `Exchange` до запуска;
3. найти его в formatted plan и Spark UI;
4. объяснить, почему broadcast уменьшает shuffle и когда он опасен;
5. показать correctness evidence: input count, valid count, output count и revenue round-trip.
6. объяснить повторный lineage без cache и путь cache block на executor.

После занятия стенд останавливается через `Tasks: Run Task` → `Spark · Stop cluster`. Данные в `labs/spark/data/` сохраняются для следующего запуска.
