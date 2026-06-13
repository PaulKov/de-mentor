# Лабораторный Стенд Greenplum

Локальный Greenplum-стенд для первого урока по MPP, distribution key, skew и Motion nodes.

## Требования

- Docker Desktop.
- Python 3.9+.
- Файл `mentor-lab.py` из корня репозитория.

## Запуск

```bash
python3 mentor-lab.py up greenplum
python3 mentor-lab.py status greenplum
python3 mentor-lab.py psql greenplum
```

На Windows используй `py mentor-lab.py ...` вместо `python3 mentor-lab.py ...`.

Первый запуск может занять несколько минут: контейнер поднимает Greenplum и выполняет SQL-файлы из [init scripts](https://github.com/PaulKov/de-mentor/tree/master/labs/greenplum/init).

## Подключение

Рекомендуемый способ:

```bash
python3 mentor-lab.py psql greenplum
```

Альтернативно, если локальный `psql` уже установлен:

```bash
psql -h localhost -p 15432 -U gpadmin -d mentor
```

Пароль: `gparray`.

## Паспорт Docker-Кластера

Compose поднимает учебный single-container Greenplum:

| Параметр | Значение |
| --- | --- |
| Docker service | `greenplum` |
| Container hostname | `greenplum` |
| Image | `woblerr/greenplum:7.1.0` |
| Database | `mentor` |
| User / password | `gpadmin` / `gparray` |
| Published port | `15432:5432` |
| Data volume | `greenplum-data` |
| Init scripts | [init scripts](https://github.com/PaulKov/de-mentor/tree/master/labs/greenplum/init) -> `/docker-entrypoint-initdb.d` |
| Examples | [SQL examples](https://github.com/PaulKov/de-mentor/tree/master/labs/greenplum/examples) -> `/mentor-lab/examples` |

Фактическая topology внутри Greenplum:

- `1 coordinator/master`: `content = -1`, порт `5432` внутри контейнера;
- `2 primary segments`: `content = 0` и `content = 1`, порты `6000` и `6001`;
- `0 mirror segments`: HA отключен, чтобы стенд был легким;
- `1 segment host`: все segment instances живут в одном Docker container/hostname `greenplum`.

CPU/RAM limits в `docker-compose.yml` **не заданы**. Это значит, что контейнер использует лимиты Docker Desktop/Engine. В Greenplum можно посмотреть memory-related настройки executor'а, но не полную физическую квоту Docker VM.

Быстрая проверка через SQL:

```bash
python3 mentor-lab.py psql greenplum
```

```sql
\i /mentor-lab/examples/cluster-inspection.sql
```

Ключевые SQL-запросы из скрипта:

```sql
SELECT content, role, preferred_role, mode, status, hostname, address, port, datadir
FROM gp_segment_configuration
ORDER BY content, role;

SELECT name, setting, unit
FROM pg_settings
WHERE name IN (
    'gp_resource_manager',
    'gp_vmem_protect_limit',
    'max_connections',
    'shared_buffers',
    'statement_mem',
    'work_mem'
)
ORDER BY name;

SELECT dfsegment, dfhostname, dfdevice, pg_size_pretty(dfspace::bigint * 1024) AS free_space
FROM gp_toolkit.gp_disk_free
ORDER BY dfsegment;
```

Ожидаемые ориентиры для текущего образа:

- `gp_segment_configuration`: 1 master row и 2 primary segment rows;
- `gp_vmem_protect_limit`: `8192`;
- `statement_mem`: `128000 kB`;
- `work_mem`: `32768 kB`;
- `shared_buffers`: `4000` blocks по `32kB`, примерно 125 MB;
- disk free зависит от Docker VM и volume, смотри `gp_toolkit.gp_disk_free`.

Проверка Docker-level ресурсов снаружи Greenplum:

```bash
docker inspect greenplum-greenplum-1 \
  --format 'NanoCpus={{.HostConfig.NanoCpus}} Memory={{.HostConfig.Memory}} CpuQuota={{.HostConfig.CpuQuota}}'

docker stats greenplum-greenplum-1 --no-stream
docker system df
docker volume inspect greenplum_greenplum-data
```

Если `NanoCpus=0`, `Memory=0`, `CpuQuota=0`, значит compose не ограничивает CPU/RAM на уровне container runtime.

## Monitoring SQL

Для более полного production-style осмотра кластера используй:

```sql
\i /mentor-lab/examples/cluster-monitoring.sql
```

Скрипт покрывает:

- topology и health через `gp_segment_configuration`;
- problem segments: `status <> 'u'`, `mode <> 's'`, `role <> preferred_role`;
- segments per host и список segment ids через `STRING_AGG(content::text, ',' ORDER BY content)`;
- disk free через `gp_toolkit.gp_disk_free`;
- resource groups через `gp_toolkit.gp_resgroup_status_per_segment`, если view доступна;
- skew helpers через `gp_segment_id`, `gp_toolkit.gp_skew_coefficients`, `gp_toolkit.gp_skew_idle_fractions`;
- служебные псевдо/system-поля: `gp_segment_id`, `tableoid`, `ctid`, `xmin`, `xmax`, `cmin`, `cmax`;
- segment-local helpers: `gp_dist_random`, `gp_execution_segment`, если доступны в версии кластера;
- CLI snippets для `gpstate -s`, `gpstate -m`, `gpstate -c`, `gpstate -e`.

## Partitioning Strategies SQL

Для отдельного deep-dive по стратегиям partitioning:

```sql
\i /mentor-lab/examples/partitioning-strategies.sql
```

Скрипт создает runnable-примеры:

- `PARTITION BY RANGE (sale_date)` для date pruning и retention;
- `PARTITION BY LIST (region)` для конечного набора бизнес-категорий;
- `PARTITION BY HASH (customer_id)` для bucketization;
- `DEFAULT partition` для unexpected values;
- multi-level пример: RANGE по дате, затем LIST по региону.

Как смотреть партиции и сколько их в GP:

```sql
SELECT *
FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);

WITH roots AS (
    SELECT n.nspname AS schema_name, c.relname AS table_name, c.oid AS root_oid
    FROM pg_class AS c
    JOIN pg_namespace AS n ON n.oid = c.relnamespace
    WHERE n.nspname = 'lesson01'
      AND c.relname LIKE 'partition_%_demo'
)
SELECT
    roots.schema_name,
    roots.table_name,
    COUNT(*) FILTER (WHERE tree.isleaf) AS leaf_partitions
FROM roots
CROSS JOIN LATERAL pg_partition_tree(roots.root_oid) AS tree
GROUP BY roots.schema_name, roots.table_name
ORDER BY roots.table_name;

SELECT *
FROM gp_toolkit.gp_partitions
WHERE schemaname = 'lesson01';
```

Maintenance snippets в скрипте включают `ATTACH PARTITION`, `DETACH PARTITION`, `DROP` старой retention partition и пояснение про out-of-range INSERT без default partition.

## Переинициализация

Init scripts выполняются только при пустом data volume. Если нужно пересоздать учебные данные:

```bash
python3 mentor-lab.py reset greenplum
python3 mentor-lab.py up greenplum
```

## Что Создается

- база `mentor`;
- схема `lesson01`;
- измерения `dim_customers`, `dim_products`;
- факт `fact_sales_bad`, распределенный по низкокардинальному `status`;
- факт `fact_sales_good`, распределенный по `customer_id`;
- helper views для проверки skew.

## Диагностика

```bash
python3 mentor-lab.py logs greenplum
python3 mentor-lab.py config greenplum
python3 mentor-lab.py up greenplum --dry-run
python3 mentor-lab.py check greenplum
```

## Профили Данных

```bash
python3 mentor-lab.py seed greenplum --profile skewed
python3 mentor-lab.py seed greenplum --profile balanced
python3 mentor-lab.py seed greenplum --profile enterprise
python3 mentor-lab.py seed greenplum --profile late-facts
python3 mentor-lab.py seed greenplum --profile bad-statistics
python3 mentor-lab.py seed greenplum --profile bad-partitioning
python3 mentor-lab.py seed greenplum --profile wide-aoco
python3 mentor-lab.py seed greenplum --profile small-dimension-broadcast
```

- `skewed` - основной incident profile с перекосом распределения.
- `balanced` - baseline для сравнения планов.
- `enterprise` - профиль, где несколько крупных клиентов доминируют в выручке.
- `late-facts` - late arriving facts для incremental load discussion.
- `bad-statistics` - intentionally stale statistics drill.
- `bad-partitioning` - mart layout для pruning discussion.
- `wide-aoco` - AOCO column storage drill.
- `small-dimension-broadcast` - маленькая dimension для Broadcast Motion analysis.

## Academy Loop

```bash
python3 mentor-lab.py assessment greenplum pre
python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join
python3 mentor-lab.py tuning greenplum list
python3 mentor-lab.py cockpit greenplum
python3 mentor-lab.py certificate greenplum
```
