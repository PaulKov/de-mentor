# Домашка: Урок 03 — Query Tuning Evidence Pack

Стенд: `greenplum-625` (Greenplum 6.25).  
База: **`mentor`**. Схема: **`lesson03`**.

Уровень по умолчанию: **Senior core** (после зелёного `check`).  
**Principal extension** — отдельный трек (не обязан влезать в 90 минут).

Цель: не «переписать SQL красивее», а **выбрать и доказать** физическую стратегию (включая решение **не внедрять** rewrite).

Шаблоны: [templates/evidence.md](templates/evidence.md) · [templates/reconcile.sql](templates/reconcile.sql).

## Важно: нет готового ответа в seed

| Файл | Назначение |
| --- | --- |
| `lesson03-homework-seed.sql` | Schema / data / views — **для homework** |
| `lesson03-class-demo.sql` | Seed + worked TEMP — **только урок**, не копировать в сдачу |
| `solutions/lesson03-reference-rewrite.sql` | Mentor-only эталон |

## Подготовка (таймер ещё не идёт)

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py psql greenplum-625
```

```sql
\conninfo
-- ожидаешь dbname=mentor
\i /mentor-lab/examples/lesson03-homework-seed.sql
```

**Таймер Senior core начинается после зелёного `check`**, не с `docker pull`.

## Senior core (~90–120 минут)

### Task 1 — Baseline

- Зафиксируй `SET optimizer = on|off` для всего rewrite-доказательства (не менять mid-flight).
- `EXPLAIN ANALYZE` на `lesson03.v_heavy_olap_monolith`.
- Найди critical path / Motion / join sides.
- Challenge 1: конкретный estimate error **или** доказательство, что estimates адекватны и bottleneck в shape/Motion.

### Task 2 — Physical design (0–3 стадии)

Спроектируй **от 0 до 3** физических стадий.  
Хотя бы один explored вариант касается TEMP boundary: создать TEMP **или** аргументированно отвергнуть materialization.

Для каждой стадии заполни таблицу (секция D):

| Stage | Input rows | Output rows | Distribution | Storage | Next operator | Why materialization pays |
| --- | ---: | ---: | --- | --- | --- | --- |

Обоснуй grain, projection, `DISTRIBUTED BY`, необходимость `ANALYZE`, ожидаемый следующий оператор.  
Не утверждай «AOCO быстрее» без access-pattern evidence.

### Task 3 — End-to-end proof

Сравни **полный pipeline**, не только final SELECT:

| Metric | Monolith | Candidate |
| --- | ---: | ---: |
| Total pipeline time (median) |  |  |
| Planning / stages / final |  |  |
| Motion / spill / TEMP bytes |  |  |

Production decision обязателен: **merge / do not merge / needs larger-scale validation**.

### Task 4 — Correctness

- Двусторонний `EXCEPT ALL` → оба diff = 0 (см. [templates/reconcile.sql](templates/reconcile.sql)).
- Counts (+ рекомендуется aggregate checksum).
- Residual risks **дополнительно** к reconciliation (не вместо).
- Challenge 4: два adversarial способа сломать grain «на глаз».

## Principal extension (отдельно, 3–5 часов)

Не входит в обязательный 90-минутный core:

- ORCA/Legacy matrix с **явным** контрактом: frozen-input final SELECT **или** full e2e per optimizer;
- filepath TEMP / constrained spill;
- Optimizer Policy RFC (когда `optimizer=on|off`, evidence before merge, monitoring);
- raw `pg_statistic` slots;
- вопрос к Уроку 05 (WLM / kill-switch);
- Challenge 2 co-location proof (если использовал TEMP).

`v_star_join_orca_case` — demo join-space; не основной graded rewrite target.

## Deliverables

```text
lessons/lesson-03/submissions/
├── rewrite.sql          # твой pipeline (или «no TEMP» + обоснование)
├── reconcile.sql        # two-way EXCEPT ALL
├── evidence.md          # секции A–J (см. template)
└── artifacts/           # планы, metrics.tsv (рекомендуется)
```

## Запрещено (hard reject)

- Копировать `tmp_lesson03_sales_*` / class-demo как «своё» решение без собственной архитектуры и e2e cost.
- Менять `optimizer` между baseline и candidate rewrite proof.
- Менять business grain без явного residual risk **и** без прохождения reconcile.
- Заменять reconciliation описанием residual risk.
- Работать в БД `postgres` вместо `mentor`.
- CTE-only «магический кеш» без proof materialize/TEMP или без доказанного отказа от TEMP.

## Самопроверка

```bash
python3 mentor-lab.py check greenplum-625
python3 mentor-lab.py homework greenplum-625 check \
  --submission lessons/lesson-03/submissions
python3 mentor-lab.py student greenplum-query-tuning homework
```

Mechanical checker проверяет gates и структуру. Reasoning / качество гипотез — human review по [rubric.md](rubric.md).
