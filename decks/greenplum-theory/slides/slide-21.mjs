import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide21(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Capstone",
    "Capstone mart design",
    "Факт проектируется от grain и workload, а не от любимой DDL-опции."
  );
  card(ctx, slide, 60, 245, 520, 132, "Grain", "Одна строка что означает? order, order item, daily customer aggregate?", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Physical design", "Distribution для joins, partitioning для date pruning/retention, storage для scans.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Risk register", "Skew, late facts, stats after load, hot partitions, huge final gather.", C.green);

  return slide;
}
