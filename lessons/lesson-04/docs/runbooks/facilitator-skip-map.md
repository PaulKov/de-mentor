# Facilitator Skip-Map: Lesson 04

## Режимы

| Режим | Live slides | Demo | Цель |
| --- | ---: | --- | --- |
| Core 60 | 1–26 | core pipeline | mental model + first evidence |
| Deep 90 | 1–36 | core + join A/B | plan/shuffle/join reasoning |
| Self-service | 1–42 | все examples | reference + homework |

## Core 60

LIVE:

```text
1–16, 17–23 вместе с demo, 24–26
```

SKIP:

```text
27–42
```

## Deep 90

LIVE:

```text
1–36
```

SKIP на проекторе:

```text
37–42 appendix
```

## Stop conditions

Оставайся в Core, если ученик:

- считает Spark persistent storage;
- путает executor и task;
- не находит action;
- не связывает shuffle со stage boundary;
- предлагает `collect()` как validation.

## Anti-patterns ведущего

- не показывать 42 слайда за 60 минут;
- не начинать с Catalyst/AQE;
- не объяснять Spark фразой «всё в памяти»;
- не использовать Scala-фрагменты;
- не выдавать configuration checklist вместо mental model;
- не принимать «быстрее» без correctness proof.
