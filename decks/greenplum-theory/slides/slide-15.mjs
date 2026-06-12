import { C, card, slideBase } from "./shared.mjs";

export async function slide15(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "Capstone", "Проектируем daily marketplace revenue mart", "Финальная задача проверяет архитектурное мышление, а не память команд.");
  card(ctx, slide, 80, 222, 250, 250, "Grain", "Что такое одна строка: день-клиент-продукт, order item или payment event?", C.blue);
  card(ctx, slide, 370, 222, 250, 250, "Distribution", "Какой ключ оптимизирует самые тяжелые joins и не создает skew?", C.green);
  card(ctx, slide, 660, 222, 250, 250, "Partitioning", "Какая дата помогает pruning, retention и reload strategy?", C.amber);
  card(ctx, slide, 950, 222, 250, 250, "Risks", "Enterprise-клиенты, late events, stale stats, меняющиеся query patterns.", C.red);
  return slide;
}
