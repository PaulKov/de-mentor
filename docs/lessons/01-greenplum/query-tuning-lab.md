# Query Tuning Lab

Этот блок используется после базового урока или как домашний мини-экзамен. Цель - научить ученика объяснять план и выбирать фикс, а не угадывать DDL.

## Запуск

```bash
python3 mentor-lab.py tuning greenplum list
python3 mentor-lab.py tuning greenplum show redistribute-join
python3 mentor-lab.py analyze-plan greenplum --query bad_customer_join
python3 mentor-lab.py visualize-plan greenplum --query bad_customer_join --sample --format mermaid
python3 mentor-lab.py diagnostics greenplum show segment-skew
python3 mentor-lab.py scenario greenplum start --difficulty medium --seed 42 --dry-run
python3 mentor-lab.py submit greenplum query-tuning
python3 mentor-lab.py adaptive-review greenplum --submission submissions/query-tuning.md
```

## Tasks

| Task | Навык | Что доказать |
|---|---|---|
| `missing-statistics` | Statistics literacy | Estimates/Rows out меняются после `ANALYZE`. |
| `redistribute-join` | Join locality | `Redistribute Motion` связан с несовпадением distribution и join key. |
| `bad-partitioning` | Partition pruning | Partition key должен совпадать с retention/pruning workload. |
| `large-gather` | Coordinator bottleneck | Большой `Gather Motion` нужно уменьшать локальным aggregate/filter. |
| `storage-model-choice` | Storage design | Heap/AO/AOCO выбирается по workload, не вместо distribution. |

## Visual And Runtime Diagnostics

Для максимального вовлечения сначала проси ученика объяснить план текстом, затем показать тот же план визуально:

```bash
python3 mentor-lab.py visualize-plan greenplum --query product_join --sample --format html --output artifacts/product-plan.html
```

После визуального шага ученик должен подтвердить гипотезу runtime evidence:

```bash
python3 mentor-lab.py diagnostics greenplum list
python3 mentor-lab.py diagnostics greenplum show table-statistics
python3 mentor-lab.py diagnostics greenplum run segment-skew
```

## Data Profiles

```bash
python3 mentor-lab.py seed greenplum --profile late-facts
python3 mentor-lab.py seed greenplum --profile bad-statistics
python3 mentor-lab.py seed greenplum --profile bad-partitioning
python3 mentor-lab.py seed greenplum --profile wide-aoco
python3 mentor-lab.py seed greenplum --profile small-dimension-broadcast
```

## Expected Submission

Ученик сдает markdown:

```text
Symptom:
Plan evidence:
Physical cause:
Change:
Validation:
Residual risk:
```
