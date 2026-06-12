import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide20(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Appendix",
    "Broadcast vs Redistribute",
    "Движение данных выбирается не по красоте SQL, а по размеру сторон, locus и join key."
  );

  card(ctx, slide, 68, 232, 300, 185, "co-located join", "Обе стороны уже распределены по join key. Лучший случай для больших таблиц.", C.green);
  card(ctx, slide, 416, 232, 300, 185, "Broadcast Motion", "Маленькая сторона копируется на все segments. Хорошо после сильного фильтра.", C.blue);
  card(ctx, slide, 764, 232, 300, 185, "Redistribute Motion", "Строки хэшируются по новому key и едут segment-to-segment.", C.amber);

  codeBlock(ctx, slide, 165, 465, 910, 132, `if both sides distributed by join_key -> co-located
else if one side is small after filters -> Broadcast Motion
else -> Redistribute Motion one or both sides`, "JOIN ROUTE");
  return slide;
}
