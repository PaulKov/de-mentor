import { C, card, slideBase } from "./shared.mjs";

export async function slide12(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "Диагностика", "Профессиональный цикл: evidence first", "Лучший урок учит не командам, а диагностическому мышлению.");
  card(ctx, slide, 80, 250, 250, 210, "Измерить", "Строки по сегментам, размер таблиц, свежесть statistics, row counts.", C.blue);
  card(ctx, slide, 370, 250, 250, 210, "Объяснить", "Найти Motion, тип join, фазы aggregate, форму scan.", C.amber);
  card(ctx, slide, 660, 250, 250, 210, "Изменить", "Поправить distribution, statistics, grain модели или форму запроса.", C.green);
  card(ctx, slide, 950, 250, 250, 210, "Проверить", "Сравнить proof objects, а не ощущения от выполнения.", C.violet);
  return slide;
}
