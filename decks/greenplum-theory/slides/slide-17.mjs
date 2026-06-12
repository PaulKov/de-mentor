import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide17(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Цикл",
    "Диагностический цикл",
    "Профессиональный Greenplum fix выглядит как evidence loop, а не как догадка."
  );
  card(ctx, slide, 60, 245, 520, 132, "1. Измерить", "gp_segment_id, row counts, EXPLAIN, runtime symptoms.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "2. Объяснить", "Связать skew/Motion/storage/statistics с физической причиной.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "3. Изменить и проверить", "Новый DDL или query shape плюс повторный evidence.", C.green);

  return slide;
}
