import { C, card, slideBase } from "./shared.mjs";

export async function slide22(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Appendix",
    "MPP-семейства: где цена архитектуры",
    "Сильный инженер выбирает не модную систему, а bottleneck, который готов контролировать."
  );

  card(ctx, slide, 56, 230, 210, 220, "SMP", "Простота и vertical scale. Цена: предел одного сервера.", C.blue);
  card(ctx, slide, 296, 230, 210, 220, "MPP", "Shared-nothing scan/join scale-out. Цена: skew, Motion, distribution.", C.green);
  card(ctx, slide, 536, 230, 210, 220, "EPP/cloud", "Elastic compute/storage. Цена: remote IO, shuffle, cost governance.", C.amber);
  card(ctx, slide, 776, 230, 210, 220, "Lakehouse", "Open storage + engines. Цена: metadata, small files, compaction.", C.violet);
  card(ctx, slide, 1016, 230, 210, 220, "HTAP", "Transactions + distributed SQL. Цена: consensus и OLAP-scan trade-offs.", C.red);

  ctx.addText(slide, {
    x: 150,
    y: 548,
    width: 980,
    height: 60,
    text: "Контрольный вопрос: где твоя система платит за движение данных - внутри сети MPP, в object storage, в shuffle engine или в одном сервере?",
    fontSize: 22,
    bold: true,
    color: C.text,
    align: "center",
  });
  return slide;
}
