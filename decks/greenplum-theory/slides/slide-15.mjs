import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide15(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Skew",
    "Skew через gp_segment_id",
    "gp_segment_id превращает догадки про распределение в измеримое evidence."
  );
  card(ctx, slide, 60, 245, 520, 132, "Симптом", "Один segment получил непропорционально много строк.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Причина", "Часто низкая cardinality distribution key: status, region, flag.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Фикс", "Распределить большой fact по высококардинальному join key.", C.green);

  codeBlock(ctx, slide, 60, 520, 1090, 130, "SELECT gp_segment_id, count(*) AS rows_count\nFROM lesson01.fact_sales_bad\nGROUP BY gp_segment_id\nORDER BY gp_segment_id;", "SQL / CLI");
  return slide;
}
