# Apache Spark foundations — Lesson 04

Исходники и инструкции для двух версий презентации четвёртой лекции:

- `apache-spark-foundations-core.pptx` — обязательное ядро, 39 слайдов / 60 минут;
- `apache-spark-foundations-theory.pptx` — полная версия, 66 слайдов / 90 минут;
- `content.mjs` — единый источник содержания;
- `build_lesson04_pptx.mjs` — детерминированный сборщик editable PPTX;
- `build_google_slides_requests.mjs` — детерминированный план нативного обновления
  опубликованной Google Slides с 60 до 66 слайдов;
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

Исторический блок намеренно различает исходную модель 3V и более поздние
неунифицированные расширения 6V/10V. Principal-блок сравнивает Spark и
MapReduce по execution graph, materialization, recovery, workload fit и полной
стоимости эксплуатации, а не по мифу «disk против RAM».

## Нативная миграция Google Slides

Сборщик запросов не пишет в Google сам и рассчитан на безопасный workflow с
промежуточным readback:

```bash
node build_google_slides_requests.mjs raw-template.json update-plan.json
```

Применяйте `creationChunks` последовательно, затем перечитайте структуру и
убедитесь, что созданы все `createdSlideIds`. После этого примените каждый
элемент `positionBatches` отдельным batch update и проверьте точный порядок
`deliveredSlideIds`. `deleteRequests` пуст: обновление сохраняет все 60
существующих слайдов и добавляет шесть новых. После финального readback
обязательны issue checker и полный PDF-рендер всех 66 слайдов.
