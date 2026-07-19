# Deep-Dive: Legacy Postgres Planner vs GPORCA (Greenplum 6.25)

## Pipeline Оптимизации

```text
SQL
 → Parse
 → Rewrite (views/rules)
 → Optimize   ← сюда входят Legacy или GPORCA
 → Dispatch (QD → gangs / slices)
 → Execute (QE + Motion + Gather)
```

На Greenplum 6.25 выбор оптимизатора:

```sql
SHOW optimizer;     -- on = GPORCA, off = Legacy
SET optimizer = on;
SET optimizer = off;
```

## Legacy Postgres Planner

### Как работает

- Строит path trees в духе PostgreSQL (`joinpath`, `costsize`, `selfuncs`).
- Greenplum добавляет Motion/distribution через `cdbpath` / locus.
- Поиск join order ограничен эвристиками и локальным DP.

### Плюсы

- Предсказуем на простых/средних запросах.
- Быстрее planning time на коротком SQL.
- Надёжный fallback, когда ORCA не может построить план.
- Проще объяснить Senior’у через привычную PostgreSQL модель.

### Минусы

- Слабее на many-join star/snowflake.
- Чаще локально-оптимальный порядок joins.
- Меньше глобальных transform (agg pull-up, сложные CTE-сценарии).

### Когда эффективен

- 1–3 joins, локальные aggregates.
- Операционные/простые reporting queries.
- Когда ORCA даёт нестабильный/дорогой planning без выигрыша runtime.

## GPORCA (Pivotal Optimizer)

### Как работает

- Cascades-style: memo groups + transformation rules (xforms).
- Distribution/Motion — first-class citizens costing model.
- Исследует большее пространство эквивалентных планов.

### Плюсы

- Сильнее на сложных OLAP с многими joins.
- Лучше учитывает стоимость redistribute/broadcast.
- Часто находит лучший global join order.

### Минусы

- Дороже planning.
- Возможны feature gaps → fallback в Legacy.
- Сложнее debug (нужны status/minidump).
- Иногда «красивый» plan хуже на фактических stats.

### Когда эффективен

- Star/snowflake с 4+ joins.
- Сложные CTE/подзапросы, где важен reorder.
- Когда Motion cost доминирует и нужен distribution-aware search.

## Демо На Стенде `greenplum-625`

```bash
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py psql greenplum-625
```

```sql
\i /mentor-lab/examples/lesson03-optimizer-legacy-vs-orca.sql
```

Сравнивайте:

1. маркер Optimizer status / Settings;
2. порядок joins;
3. типы Motion и их положение относительно фильтров;
4. planning time vs runtime (через `EXPLAIN ANALYZE` на контролируемом окне).

## Практическое Правило

1. Зафиксируйте `SET optimizer`.
2. Снимите before plan.
3. Исправьте stats/TEMP/distribution, если estimates врут.
4. Только потом меняйте optimizer или SQL shape.
5. В production policy явно документируйте default `optimizer` для ETL/BI ролей.
