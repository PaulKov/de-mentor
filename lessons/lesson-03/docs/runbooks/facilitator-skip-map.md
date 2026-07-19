# Facilitator Skip-Map: Урок 03

Режиссура live-показа. Презентация (**439** в Google Slides) = урок + справочник + порталы возврата.  
**Не листать всё.** Старт: слайд **«Как смотреть эту презентацию»** (`nav-guide`).  
Ниже — три режима по **учебным** слайдам core (индексы в `CORE_SLIDES` / core PPTX *до* порталов).

> В Google Slides номера слайдов **другие** (порталы «Словарь/Appendix»).  
> Ориентир: **☰ Меню** → якоря этапов (`stage-problem`, `stage-plan`, …) и заголовки из таблиц.  
> Полный словарь в начале презентации — self-service; live открывайте **чипы «Термины»** или один слайд-якорь.

Связанные runbook: [simple-path](simple-path.md) · [deep-dive-path](deep-dive-path.md) · [mentor-guide](../mentor-guide.md)

---

## Легенда

| Метка | Значение |
| --- | --- |
| **LIVE** | Говорите / демо на проекторе |
| **FLASH** | ≤40 сек: тезис → дальше |
| **CLICK** | Не листать; открыть по вопросу ученика (чип термина / → Appendix) |
| **SKIP** | Не открывать в этом режиме |

---

## Сводка режимов

| Режим | Время | LIVE+FLASH (цель) | Что принципиально SKIP |
| --- | --- | --- | --- |
| **Core 60** | ~60 мин | **~28–32** слайда | Весь front-словарь 4–12; inline «Детали ·»; формулы AND; storage anatomy; кейсы 02–09 |
| **Core 90** | ~90 мин | **~44–48** слайдов | Advanced-формулы словаря; appendix; 6 из 9 кейсов (оставить меню) |
| **Full** | 120+ / homework | все **108** teaching + appendix | Порталы не «читать» — только клик↔возврат |

---

## Core 60 — обязательный путь (~30 слайдов)

**DoD занятия:** симптом → прочитать Motion/cardinality → TEMP rewrite → metrics + equivalence → checklist.

### Тайминг

| Мин | Блок | Слайды (core #) | Режим |
| --- | ---: | --- | --- |
| 0–3 | Старт | title → **nav-guide** → toc | LIVE «Как смотреть»; кнопка **Core 60 →** |
| — | Словарь front | после toc | **SKIP** live (есть чипы / «Аа Словарь») |
| 2–10 | Проблема | **13–17** | LIVE |
| 10–28 | План | **18**, 19 FLASH, **20–21**, 22 FLASH, **23–29** | LIVE; **30–34 SKIP** (детали — CLICK с чипов) |
| 28–38 | Статистика lite | **35–36**, **40**, **43**, **50** | LIVE; 37–39,41–42,44–49,51–52 → SKIP/CLICK |
| — | Storage | 53–58 | **SKIP**; при вопросе — только **59** FLASH |
| 38–52 | Практика OLAP | **60–63**, **66–68** | LIVE; 64–65 FLASH или SKIP |
| — | Кейсы 01–09 | 69–104 | **SKIP** live (назвать: «меню в Меню → кейсы») |
| 52–60 | Закрепление | **105–107**, 108 FLASH | LIVE checklist + маршруты |

### Чеклист LIVE (Core 60) — скопировать ментору

```
[ ] 1  title (FLASH)
[ ] 2  toc · путь ученика
[ ] 13–17  проблема (gate → incident → data → SQL → baseline)
[ ] 18  stage-plan
[ ] 19  model (FLASH)
[ ] 20  MPP + чипы терминов
[ ] 21  method 1/2
[ ] 22  method 2/2 (FLASH)
[ ] 23  interactive 90 сек
[ ] 24–28  plan 1/5 … 5/5
[ ] 29  ORCA vs Legacy (осторожно)
[ ] 35–36  stage-stats + карта
[ ] 40  Equality / MCV (пример)
[ ] 43  Range / hist (пример, без deep)
[ ] 50  ANALYZE
[ ] 59  storage decision (только если спросили «Heap vs AOCO»)
[ ] 60–63  practice gate → CTE → TEMP → rewrite
[ ] 66–68  after plan → metrics → equivalence
[ ] 105–107  wrap + checklist + маршруты
```

**Демо SQL (минимум):** `SHOW optimizer` → baseline EXPLAIN → TEMP stages + ANALYZE → after EXPLAIN → `EXCEPT ALL` / metrics (`lesson03-e2e-case-metrics.sql`).

---

## Core 90 — расширенный путь (~45 слайдов)

Всё из Core 60 **плюс** блоки ниже. Не открывать appendix на проекторе, кроме одного осознанного jump.

### Добавки к Core 60

| Мин (ориентир) | Блок | Слайды | Режим |
| --- | --- | --- | --- |
| +3 | Словарь lite | **4**, **6**, **8**, **10** | FLASH (архитектура, sel, MCV/hist смысл). Формулы — CLICK |
| +4 | План: детали по запросу | **32** Motion и/или **33** ORCA | CLICK с чипа на 20/29; не листать 30–34 подряд |
| +6 | Статистика depth | **41** MCV смысл, **44** hist смысл, **46** SQL стенд, **49** шпаргалка | LIVE/FLASH; 42,45,47,48 — CLICK |
| +5 | Storage | **54**, **57** или **59** | LIVE decision + AOCO смысл; Heap/AO anatomy SKIP |
| +8 | Практика | **64–65** | FLASH cost/spill vs TEMP files |
| +12 | Кейсы (выбрать **2**) | см. ниже | LIVE титул+суть (+ план если успеваете) |

### Какие 2 кейса live (рекомендация)

| Приоритет | Кейс | Слайды | Зачем |
| --- | --- | --- | --- |
| 1 | **01** ORCA CE → NLJ | **70–71** (+73 если есть время) | Кардинальность → смена join |
| 2a | **03** SCD2 locus | **78–79** | Redistribute при «согласованном» join |
| 2b | **08** Autostats | **97–98** | ETL / ANALYZE после load |
| Остальные 02,04–07,09 | — | титулы в Меню | Homework / deep |

Итоговый размер Core 90: ≈ Core 60 (30) + словарь 4 + stats 4 + storage 2 + practice 2 + кейсы 4–6 ≈ **46**.

### Чеклист добавок (Core 90)

```
[ ] 4, 6, 8, 10  словарь lite (FLASH)
[ ] 32 или 33    Motion/ORCA detail (CLICK→LIVE 1 слайд)
[ ] 41, 44, 46, 49  MCV/hist/SQL/шпаргалка
[ ] 54 + 59      storage зачем + decision
[ ] 64–65        TEMP files vs spill / cost
[ ] 70–71        кейс 01
[ ] 78–79  или  97–98   второй кейс
```

---

## Full — справочник / deep / homework

| Слой | Что открывать | Когда |
| --- | --- | --- |
| Все teaching **1–108** | Self-study или 120+ мин с группой Principal | После Core 90 |
| Inline **Детали ·** 31–34, 38–39, 41–42, 44–45 | По чипам «Термины» | Вопрос «что такое MCV?» |
| Front словарь **4–12** | Полный проход | Дома / pre-read |
| Формулы **47–48**, Physical **51**, Fail **52** | Deep stats | Design review |
| Storage **55–58** | Anatomy lab | Со `lesson03-storage-heap-ao-aoco.sql` |
| Кейсы **все 01–09** | По одному за сессию или homework | SQL в `labs/…/lesson03-*.sql` |
| **Appendix** (после divider) | CE history, screenshots, ON COMMIT, star-join deep | Кнопка «→ Appendix» → портал → раздел → «← Вернуться» |

**Порталы** (сотни слайдов в full deck) никогда не «ведут» урок — только навигация.

---

## Карта этапов → якоря (Google Меню)

| Этап | Якорь | Core # gate |
| --- | --- | --- |
| Оглавление | `toc` | 2 |
| Словарь | `glossary` | 4 |
| 1 Проблема | `stage-problem` | 13 |
| 2 План | `stage-plan` | 18 |
| 3 Статистика | `stage-stats` | 35 |
| 4 Storage | `stage-storage` | 53 |
| 5 Практика | `stage-practice` | 60 |
| 6 Кейсы | `cases` | 69 |
| 7 Закрепление | `stage-wrap` | 105 |

---

## Анти-паттерны (не делать)

1. Листать front-словарь 9 слайдов вслух в Core 60.  
2. Читать подряд все «Детали ·» — они дублируют словарь **намеренно** для клика, не для показа.  
3. Открывать appendix «посмотреть что там» без вопроса — теряете 15+ минут.  
4. Гонять все 9 кейсов live — оставьте 1–2, остальное homework.  
5. Путать номер слайда в Google с номером из этой таблицы — используйте **заголовок / Меню**.

---

## Быстрый выбор режима

| Аудитория | Режим |
| --- | --- |
| Первый проход, mixed Senior | **Core 60** |
| Senior/Principal, уже видели EXPLAIN | **Core 90** |
| Self-service / RFC / повтор | **Full** + appendix jumps |
