import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide10(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Storage",
    "Heap vs AO row vs AOCO: концепт",
    "Heap vs AO row vs AOCO - выбор под workload, scan pattern и частоту изменений."
  );
  card(ctx, slide, 60, 245, 520, 132, "Heap", "Row storage по умолчанию, удобен для small/mutable tables.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "AO row", "Append-optimized row storage для append-heavy аналитики, когда читаем много колонок.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "AOCO", "Append-optimized column storage: column pruning и compression для широких фактов.", C.green);

  return slide;
}
