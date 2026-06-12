import { C, card, slideBase } from "./shared.mjs";

export async function slide13(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "Incident mode", "Отчет по выручке marketplace замедлился", "Ученик играет роль инженера, который должен дать RCA, а не просто выполнить SQL.");
  card(ctx, slide, 80, 230, 330, 250, "Симптомы", "Запрос по регионам замедлился. EXPLAIN показывает Redistribute Motion. Один сегмент делает почти всю работу.", C.red);
  card(ctx, slide, 475, 230, 330, 250, "Миссия", "Доказать или отвергнуть skew, non-colocated join и stale statistics. Предложить physical design fix.", C.amber);
  card(ctx, slide, 870, 230, 330, 250, "Артефакт", "Короткий RCA: evidence, root cause, fix, validation query, remaining risk.", C.green);
  return slide;
}
