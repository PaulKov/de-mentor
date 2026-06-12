import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide31(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "APPENDIX",
    "MPP-семейства: где цена архитектуры",
    "System taxonomy and next steps: SMP, MPP, EPP, lakehouse, HTAP переносят bottleneck в разные места."
  );
  card(ctx, slide, 60, 245, 520, 132, "SMP", "Простота и вертикальный масштаб.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "MPP", "Параллельная аналитика ценой distribution design и Motion.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "EPP / lakehouse", "Эластика и открытые форматы ценой cost, shuffle, metadata и governance.", C.green);
  card(ctx, slide, 650, 405, 520, 132, "Lesson 02", "Partitioning, statistics and incremental loads in MPP.", C.blue);

  return slide;
}
