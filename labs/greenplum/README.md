# Greenplum Lab

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

Первый запуск может занять несколько минут: контейнер поднимает Greenplum и выполняет SQL-файлы из `labs/greenplum/init`.

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

## Data Profiles

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
