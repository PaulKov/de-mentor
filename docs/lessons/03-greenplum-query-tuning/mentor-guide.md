# План Ментора: Урок 03 (Greenplum 6.25)

Тема: декомпозиция и тюнинг тяжёлых запросов в MPP — optimizer (Legacy vs GPORCA), статистика, storage, TEMP/spill.

## Перед Уроком (T−30 … T−10)

```bash
cd ~/Projects/de-mentor   # или ваш clone

python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py runbook greenplum-query-tuning simple
```

x86_64:

```bash
GREENPLUM_625_IMAGE=andruche/greenplum:6.25.3-slim-amd64 \
  python3 mentor-lab.py up greenplum-625
```

Открой материалы:

- [Google Slides](https://docs.google.com/presentation/d/1e5vpqatw6ccgeZF0PWLLWMzIqkb4SODE-IwKxrSyqB8/edit?usp=sharing) (65 слайдов)
- PPTX: `artifacts/greenplum-query-tuning-theory.pptx`
- [Simple path](runbooks/simple-path.md) · [Deep path](runbooks/deep-dive-path.md)
- [Workbook](student-workbook.md) · [Homework](homework.md) · [Cheat-sheet](cheat-sheet.md)
- Deep-dives: [optimizer](deep-dives/optimizer-legacy-vs-orca.md), [stats](deep-dives/pg-statistic-internals.md), [TEMP/spill](deep-dives/temp-tables-and-spill.md), [storage](deep-dives/storage-physical-layout.md)

Прогони сам один раз: ORCA vs Legacy, `pg_stats`, TEMP `t_*`, spill (опционально deep).

## Как Подключиться К Greenplum В Docker

| Поле | Значение |
| --- | --- |
| Lab | `greenplum-625` |
| Host port | **15436** → container `5432` |
| User | `gpadmin` |
| Database | `postgres` |
| Password | обычно не нужна для local peer/trust в этом образе; если клиент спросит — пустая / смотри образ |
| Container | `greenplum-625-greenplum-625-1` (имя от compose) |

### Способ A — удобный (рекомендуется)

```bash
python3 mentor-lab.py psql greenplum-625
```

### Способ B — psql с хоста

```bash
psql "host=127.0.0.1 port=15436 dbname=postgres user=gpadmin"
```

### Способ C — shell внутри контейнера

```bash
docker ps --format '{{.Names}}' | grep greenplum-625

docker exec -it -u gpadmin greenplum-625-greenplum-625-1 bash -lc '
  source /usr/local/gpdb/greenplum_path.sh
  export USER=gpadmin
  psql -d postgres
'
```

Проверка:

```sql
SELECT version();
SHOW optimizer;
\dn lesson03
SELECT count(*) FROM lesson03.fact_sales;
```

Seed SQL в контейнере смонтирован в `/mentor-lab/examples/`:

```sql
\i /mentor-lab/examples/lesson03-olap-decomposition-tuning.sql
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
```

## Демо: Где Лежат Файлы Таблиц (Для Экрана)

Карта сегментов на стенде:

| Role | content | datadir |
| --- | --- | --- |
| master (QD) | -1 | `/data/master/gpsne-1` |
| primary seg0 | 0 | `/data/data1/gpsne0` |
| primary seg1 | 1 | `/data/data2/gpsne1` |

### 1) Из SQL — filepath relation

```sql
-- Обычная таблица lesson03
SELECT c.relname,
       c.relkind,
       pg_relation_filepath(c.oid) AS filepath,
       pg_size_pretty(pg_relation_size(c.oid)) AS size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'lesson03'
ORDER BY pg_relation_size(c.oid) DESC;

-- На сегментах (размеры/пути могут отличаться)
SELECT gp_segment_id,
       pg_relation_filepath('lesson03.fact_sales'::regclass) AS filepath,
       pg_relation_size('lesson03.fact_sales'::regclass) AS bytes
FROM gp_dist_random('gp_id');
```

`filepath` вида `base/<dboid>/<relfilenode>` — относительно **datadir сегмента**.

### 2) С хоста — ls на сегментах

```bash
# Узнать OID/filepath из psql, затем:
docker exec -u gpadmin greenplum-625-greenplum-625-1 bash -lc '
  source /usr/local/gpdb/greenplum_path.sh
  export USER=gpadmin
  psql -d postgres -c "SELECT content, datadir FROM gp_segment_configuration ORDER BY 1;"
  echo "=== example fact_sales files (подставьте свой relfilenode) ==="
  # типичный вид: /data/data1/gpsne0/base/<dboid>/<filenode>
  find /data/data1/gpsne0/base /data/data2/gpsne1/base -maxdepth 2 -type f 2>/dev/null | head
'
```

Практика на демо:

1. Покажи `pg_relation_filepath('lesson03.dim_customer')`.
2. `ls -la` этот файл на **seg0 и seg1** — размеры разные (distribution).
3. На master часто меньше данных / другой размер — QD не хранит весь fact.

### 3) TEMP TABLE — префикс `t_`

```sql
CREATE TEMP TABLE tmp_demo AS
SELECT * FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01' AND sale_date < DATE '2026-03-01'
DISTRIBUTED BY (customer_id);

SELECT n.nspname, c.relname, c.relpersistence,
       pg_relation_filepath(c.oid) AS filepath
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relname = 'tmp_demo';
-- filepath ≈ base/<dboid>/t_<relfilenode>
```

Пока сессия жива:

```bash
docker exec -u gpadmin greenplum-625-greenplum-625-1 bash -lc '
  find /data -type f -name "t_*" -ls
'
```

Важно для ученика: **TEMP ≠ `pgsql_tmp/`**. TEMP — relation `t_*` в `base/<dboid>/`. Spill Sort/Hash — `base/pgsql_tmp/pgsql_tmp_Sort_*`.

### 4) Spill (опционально, deep)

В **той же** сессии psql после CTAS+INSERT amplify:

```sql
SET optimizer = off;
SET statement_mem = '8MB';
EXPLAIN ANALYZE
SELECT customer_id, amount FROM tmp_spill_fuel  -- заранее наполненный TEMP
ORDER BY amount;
-- ищите: Sort Method: external merge  Disk: …
```

Параллельно в другом терминале:

```bash
docker exec -u gpadmin greenplum-625-greenplum-625-1 bash -lc '
  watch -n 0.2 "du -sh /data/*/gpsne*/base/pgsql_tmp; find /data -path \"*/pgsql_tmp/pgsql_tmp_Sort*\" -ls 2>/dev/null | head"
'
```

Готовые скрины: `artifacts/lesson03-temp-fs/`, `artifacts/lesson03-plan-screens/temp-*.png`, `spill-*.png`.

---

## Главная Линия Объяснения

1. **Словарь** — GUC, QD/QE, star-join, MCV/histogram, TEMP≠spill.
2. **Pipeline** — parse → rewrite → optimize → dispatch → execute.
3. **Optimize fork** — `SET optimizer` выбирает GPORCA или Legacy; доказываем EXPLAIN.
4. **Star-join** — fact + dims; почему ORCA часто сильнее.
5. **Stats** — hist/MCV → selectivity → rows; когда stats не спасают.
6. **TEMP** — physical stage + FS `t_*` + rewrite proof.
7. **Handoff** — homework evidence checklist.

## Тайминг Simple (60 минут)

| Время | Слайды | Фокус | Вопрос ученику | Что показать руками |
| --- | --- | --- | --- | --- |
| 0–6 | 1–4 | Glossary | Что такое GUC `optimizer`? Star vs snowflake? | Слайды словаря; не уходи в код |
| 6–12 | 5–8 | Стенд + pipeline | Где в EXPLAIN видны slices? | `up/check/seed`; `SHOW optimizer` |
| 12–24 | 9–25 | Optimize + star + plan trees | Чем маркер GPORCA ≠ Legacy? | `SET optimizer on/off` + `v_star_join_orca_case` |
| 24–32 | 26–35 | Case + Motion + estimates alarm | Какой Motion дороже? | Monolith EXPLAIN; найти Redistribute |
| 32–44 | 36–48 | **Stats deep** | Чем equi-depth hist ≠ MCV? | `pg_stats`, `EXPLAIN ANALYZE` rows vs actual |
| 44–56 | 49–62 | Storage + TEMP FS/spill | Где TEMP vs `pgsql_tmp_Sort_*`? | `pg_relation_filepath` + `find t_*` |
| 56–60 | 63–65 | Proof + homework | Какой evidence обязателен? | Checklist домашки |

CLI во время урока:

```bash
python3 mentor-lab.py runbook greenplum-query-tuning simple
python3 mentor-lab.py teach greenplum-query-tuning simple --stage 1   # если используете teach
```

## Тайминг Deep (90–120 минут)

Добавь к simple:

| Блок | Слайды / материал | Демо |
| --- | --- | --- |
| Code map GPDB | слайды code map + [optimizer deep-dive](deep-dives/optimizer-legacy-vs-orca.md) | Открыть ссылки `6X_STABLE` |
| Stats slots | [pg-statistic-internals](deep-dives/pg-statistic-internals.md) | `pg_statistic` stakind 1/2; `SET STATISTICS` |
| Stats fail → TEMP | слайды Stats fail / fix | Коррелированный join; затем TEMP rewrite |
| Spill FS | [temp-tables-and-spill](deep-dives/temp-tables-and-spill.md) | `statement_mem=8MB` + `watch` pgsql_tmp |
| Design review | финал | Ученик защищает rewrite как mini-RFC |

```bash
python3 mentor-lab.py runbook greenplum-query-tuning deep
```

## Что Показать В Greenplum (Скрипт Демо)

### Блок A — Optimizer

```sql
SHOW optimizer;

SET optimizer = on;
EXPLAIN
SELECT * FROM lesson03.v_star_join_orca_case
ORDER BY revenue DESC LIMIT 5;
-- маркер: Optimizer: Pivotal Optimizer (GPORCA)

SET optimizer = off;
EXPLAIN
SELECT * FROM lesson03.v_star_join_orca_case
ORDER BY revenue DESC LIMIT 5;
-- маркер: Optimizer: Postgres query optimizer
```

Сравни: join order, положение Redistribute, число slices.

### Блок B — Статистика

```sql
SHOW default_statistics_target;  -- 100

SELECT attname, n_distinct,
       left(most_common_vals::text, 60) AS mcv,
       left(most_common_freqs::text, 40) AS mcf,
       array_length(histogram_bounds, 1) AS hist_n
FROM pg_stats
WHERE schemaname = 'lesson03'
  AND tablename IN ('fact_sales', 'dim_customer')
ORDER BY tablename, attname;

-- Хорошая оценка (MCV)
EXPLAIN ANALYZE
SELECT count(*) FROM lesson03.dim_customer WHERE segment = 'enterprise';

-- Range / hist или MCV дат
EXPLAIN ANALYZE
SELECT count(*) FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01';

-- Где независимость уже врёт (~10%+)
EXPLAIN ANALYZE
SELECT count(*)
FROM lesson03.fact_sales f
JOIN lesson03.dim_customer c ON c.customer_id = f.customer_id
WHERE c.segment = 'test'
  AND f.sale_date >= DATE '2026-02-01';
```

Говори вслух: **сначала `rows` vs `actual`, потом ANALYZE / SET STATISTICS / TEMP**.

### Блок C — TEMP rewrite + FS

```sql
SET optimizer = on;  -- зафиксировали GUC

CREATE TEMP TABLE tmp_sales_feb AS
SELECT customer_id, product_id, amount
FROM lesson03.fact_sales
WHERE sale_date >= DATE '2026-02-01'
  AND sale_date < DATE '2026-03-01'
DISTRIBUTED BY (customer_id);

ANALYZE tmp_sales_feb;

SELECT n.nspname, pg_relation_filepath(c.oid),
       pg_size_pretty(pg_total_relation_size(c.oid))
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relname = 'tmp_sales_feb';

EXPLAIN
SELECT c.region, d.category, sum(t.amount)
FROM tmp_sales_feb t
JOIN lesson03.dim_customer c ON c.customer_id = t.customer_id
JOIN lesson03.dim_product d ON d.product_id = t.product_id
WHERE c.segment <> 'test'
GROUP BY c.region, d.category;
```

В другом терминале — `find … -name 't_*' -ls` (см. выше).

Сравни с монолитом:

```sql
EXPLAIN SELECT * FROM lesson03.v_heavy_olap_monolith;
```

## Вопросы Ученику

- Что такое GUC `optimizer` и кто строит plan при `on` / `off`?
- Чем star-join отличается от snowflake?
- Как в EXPLAIN отличить GPORCA от Legacy?
- Чем equi-depth histogram отличается от MCV? Когда hist = NULL?
- Почему `AND` двух фильтров часто врёт даже при свежем ANALYZE?
- Почему на GP 6.25 нет `CREATE STATISTICS` и чем заменяем?
- Где на диске TEMP TABLE и где spill?
- Зачем `ANALYZE` сразу после наполнения TEMP?
- Какой evidence обязателен в домашке?

## Ожидаемые Ответы

- GUC = параметр сервера; `optimizer=on` → GPORCA, `off` → Legacy на QD.
- Star = fact + dims по FK; snowflake = dims нормализованы дальше.
- Маркеры: `Pivotal Optimizer (GPORCA)` vs `Postgres query optimizer`.
- Histogram — границы корзин равной плотности для range; MCV — частые значения+freqs для `=`; hist NULL если весь NDV в MCV.
- Модель независимости `s1·s2`; корреляция/many-join → misestimate.
- На GP6: `SET STATISTICS` + rewrite + TEMP stage (+ ANALYZE).
- TEMP → `base/<dboid>/t_*` на QE; spill → `pgsql_tmp/pgsql_tmp_Sort_*`.
- Без ANALYZE следующий plan по TEMP врёт cardinality.
- Before/after EXPLAIN при том же optimizer, stats snippet, TEMP+distribution, residual risk.

## Как Проверять На Уроке

Ученик готов дальше, если:

- расшифровывает GUC / star-join / MCV / TEMP≠spill без подсказки;
- сравнивает ORCA vs Legacy на одном SQL и говорит про Motion/join order;
- показывает `rows` vs `actual` и читает `pg_stats`;
- делает TEMP с `DISTRIBUTED BY` + `ANALYZE` и объясняет FS `t_*`;
- не предлагает AOCO как фикс плохого plan.

## Что Не Делать

- Не уводи в полный WLM — Урок 04.
- Не принимай rewrite без before/after EXPLAIN и без `SET optimizer`.
- Не предлагай AOCO как универсальный фикс.
- Не произноси аббревиатуры без словаря.
- Не говори «просто ANALYZE», не показав misestimate.

## Handoff В Конце

```bash
python3 mentor-lab.py student greenplum-query-tuning homework
python3 mentor-lab.py runbook greenplum-query-tuning homework
```

Домашка: [homework.md](homework.md).  
Критерии: [rubric.md](rubric.md).

Скажи ученику:

> Evidence pack: (1) before/after EXPLAIN при фиксированном optimizer, (2) кусок pg_stats / ANALYZE, (3) TEMP + DISTRIBUTED BY, (4) residual risk. Без плана rewrite не засчитывается.
