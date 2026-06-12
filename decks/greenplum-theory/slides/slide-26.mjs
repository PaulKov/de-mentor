import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide26(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "APPENDIX",
    "Physical joins in MPP",
    "Hash Join - локальный алгоритм; co-located join/Broadcast/Redistribute - физика размещения."
  );
  card(ctx, slide, 60, 245, 520, 132, "co-located join", "Обе стороны уже распределены по join key: network минимален.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Broadcast side", "Маленькая dimension копируется на все segments.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Redistribute side", "Одна или обе стороны перекладываются по hash join key.", C.green);

  return slide;
}
