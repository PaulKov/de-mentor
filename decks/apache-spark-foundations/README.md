# Apache Spark foundations — Lesson 04

Исходники и инструкции для двух версий презентации четвёртой лекции:

- `apache-spark-foundations-core.pptx` — обязательное ядро, 26 слайдов / 60 минут;
- `apache-spark-foundations-theory.pptx` — полная версия, 42 слайда / 90 минут;
- `content.mjs` — единый источник содержания;
- `build_lesson04_pptx.mjs` — детерминированный сборщик editable PPTX;
- `facilitator-guide.md` — рекомендуемый темп, вопросы аудитории и skip map.

## Самостоятельная пересборка

Сборщик использует предоставляемый Codex runtime и `@oai/artifact-tool`. Он не
зависит от `python-pptx`, а весь текст, схемы и код остаются редактируемыми.

```bash
node build_lesson04_pptx.mjs core ../../lessons/lesson-04/artifacts/apache-spark-foundations-core.pptx
node build_lesson04_pptx.mjs full ../../lessons/lesson-04/artifacts/apache-spark-foundations-theory.pptx
```

Перед публикацией обязательны рендер всех слайдов, visual QA и проверка
переполнений. Источники для внешних утверждений записаны в speaker notes каждого
слайда в блоке `[Sources]`.

