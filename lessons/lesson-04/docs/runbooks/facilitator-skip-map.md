# Facilitator Skip-Map: Lesson 04

## Режимы

| Режим | Live slides | Demo | Цель |
| --- | ---: | --- | --- |
| Core 60 | 1–39 | core pipeline | history + mental model + first evidence |
| Deep 90 | 1–59 | core + MapReduce matrix + join A/B | execution/recovery/cost reasoning |
| Self-service | 1–66 | все examples | reference + readings + homework |

## Core 60

LIVE:

```text
1–16, 17–29, 30–36 вместе с demo, 37–39
```

SKIP:

```text
40–66
```

## Deep 90

LIVE:

```text
1–59
```

SKIP на проекторе:

```text
60–66 appendix
```

## Stop conditions

Оставайся в Core, если ученик:

- считает Spark persistent storage;
- путает executor и task;
- не находит action;
- не связывает shuffle со stage boundary;
- предлагает `collect()` как validation.

## Anti-patterns ведущего

- не показывать 66 слайдов за 60 минут;
- не начинать с Catalyst/AQE;
- не объяснять Spark фразой «всё в памяти»;
- не использовать Scala-фрагменты;
- не выдавать configuration checklist вместо mental model;
- не принимать «быстрее» без correctness proof.
