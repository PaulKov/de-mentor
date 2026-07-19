# Урок 03 Implementation Plan

> **For agentic workers:** execute task-by-task; checkbox tracking optional after initial delivery.

**Goal:** Полный контур Урока 03 — декомпозиция и тюнинг тяжёлых запросов в MPP.

**Architecture:** Гибрид (сквозной OLAP case + deep-dives), паттерн Lesson 02 (route/manifest/runbooks/control plane), PPTX через `scripts/build_lesson03_pptx.py`.

**Tech Stack:** Python mentor-lab, declarative `.mjs` slides, python-pptx builder, Google Slides publish CLI.

## Global Constraints

- Контент на русском; устоявшиеся термины (`EXPLAIN`, AOCO, Motion) сохраняем.
- WLM/RCA вне scope → Урок 04.
- Google publish только в `pavelkov007@gmail.com`.

## Tasks

- [x] Design doc
- [x] SQL-lab + docs + deep-dives
- [x] Deck sources + PPTX builder
- [x] Route/catalog/runbooks/control plane
- [x] Tests
- [ ] Live Google Slides publish (blocked: нет `google_personal_refresh_token`)
- [ ] Commit + MR после publish URL
