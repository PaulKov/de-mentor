# Homework Plan: Урок 03

## Что Сделать Ученику

1. Прогнать SQL-lab.
2. Снять before plan монолита.
3. Написать собственный TEMP rewrite (можно улучшить lab-паттерн).
4. Снять after plan.
5. Приложить `pg_stats` evidence.
6. Описать residual risk.

## Менторский Review

Смотри [rubric.md](../rubric.md). Красные флаги:

- нет before/after;
- TEMP без `ANALYZE`;
- `DISTRIBUTED RANDOMLY` на промежуточном join stage без обоснования;
- «AOCO быстрее» без access pattern.
