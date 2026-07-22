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
| `lesson03-class-demo.sql` | Seed + worked TEMP на **class view** — только урок, не копировать в сдачу |
| `solutions/lesson03-reference-rewrite.sql` | Mentor-only эталон |

**Graded target (обязательный baseline):** `lesson03.v_homework_brand_region`  
(March × brand × region; filters `segment IN ('smb','mid')`, `category <> 'security'`).

**Class-demo view (не graded):** `lesson03.v_heavy_olap_monolith` (Feb × category) — для урока/workbook.

## Подготовка (таймер ещё не идёт)

```bash
python3 mentor-lab.py doctor --full
python3 mentor-lab.py up greenplum-625
python3 mentor-lab.py seed greenplum-625 --profile lesson03 --scale small
# Principal stress (локально ~2M rows): --scale principal
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

### Task 1 — Baseline (graded view)

- Зафиксируй `SET optimizer = on|off` для всего rewrite-доказательства (не менять mid-flight).
- `EXPLAIN ANALYZE` на **`lesson03.v_homework_brand_region`** (не на class-demo monolith).
- Найди critical path / Motion / join sides; учти skew (hot customers) и корреляцию region↔segment в dims.
- Challenge 1: конкретный estimate error **или** доказательство, что estimates адекватны и bottleneck в shape/Motion.

### Task 2 — A/B physical design (≥2 explored variants)

Исследуй **не меньше двух** кандидатов и зафиксируй оба в evidence (секция D):

| Candidate | Shape | Когда уместен |
| --- | --- | --- |
| **A** | ≤1 physical stage (или no-TEMP / pushdown-only) | shallow rewrite |
| **B** | multi-stage (обычно 2–3 TEMP / materialize) | когда A не снимает Motion/spill |

Хотя бы один explored вариант касается TEMP boundary: создать TEMP **или** аргументированно отвергнуть materialization.

Для **каждой** стадии выбранного production-кандидата заполни таблицу:

| Stage | Input rows | Output rows | Distribution | Storage | Next operator | Why materialization pays |
| --- | ---: | ---: | --- | --- | --- | --- |

Обоснуй grain, projection, `DISTRIBUTED BY`, необходимость `ANALYZE`, ожидаемый следующий оператор.  
Не утверждай «AOCO быстрее» без access-pattern evidence.

У production winner — **0–3** физические стадии.  
В `rewrite.sql` сдай **один** production candidate (A или B) — тот, что защищаешь e2e; A/B сравнение — в evidence.

### Task 3 — End-to-end proof

Сравни **полный pipeline**, не только final SELECT:

| Metric | Monolith (`v_homework_brand_region`) | Candidate A | Candidate B (winner or explored) |
| --- | ---: | ---: | ---: |
| Total pipeline time (median) |  |  |  |
| Planning / stages / final |  |  |  |
| Motion / spill / TEMP bytes |  |  |  |

Production decision обязателен: **merge / do not merge / needs larger-scale validation**  
(для `needs larger-scale` укажи, что дал `--scale principal` или почему small недостаточен).

### Task 4 — Correctness

- Двусторонний `EXCEPT ALL` vs **`v_homework_brand_region`** → оба diff = 0 (см. [templates/reconcile.sql](templates/reconcile.sql)).
- Counts (+ рекомендуется aggregate checksum).
- Residual risks **дополнительно** к reconciliation (не вместо).
- Challenge 4: два adversarial способа сломать grain «на глаз».

## Principal extension (отдельно, 3–5 часов)

Не входит в обязательный 90-минутный core:

- повтор на `--scale principal` и сравнение decision;
- ORCA/Legacy matrix с **явным** контрактом: frozen-input final SELECT **или** full e2e per optimizer;
- filepath TEMP / constrained spill;
- Optimizer Policy RFC (когда `optimizer=on|off`, evidence before merge, monitoring);
- raw `pg_statistic` slots;
- вопрос к Уроку 04 (WLM / kill-switch);
- Challenge 2 co-location proof (если использовал TEMP).

`v_star_join_orca_case` — demo join-space; не graded rewrite target.  
`v_heavy_olap_monolith` — class demo; не graded rewrite target.

## Deliverables

```text
lessons/lesson-03/submissions/
├── rewrite.sql          # production candidate (A или B)
├── reconcile.sql        # two-way EXCEPT ALL vs v_homework_brand_region
├── evidence.md          # секции A–J + A/B (см. template)
└── artifacts/           # планы, metrics.tsv (рекомендуется)
```

## Запрещено (hard reject)

- Сдавать rewrite на class-demo grain (`v_heavy_olap_monolith` / `tmp_lesson03_sales_*`) вместо graded view.
- Копировать `tmp_lesson03_sales_*` как «своё» решение без собственной архитектуры и e2e cost.
- Только один explored candidate без A/B сравнения в evidence.
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
