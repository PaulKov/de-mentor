import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide29(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "APPENDIX",
    "Storage internals and ALTER TABLE caveats",
    "Heap/AO/AOCO и ALTER TABLE storage changes требуют понимания rewrite, locks и maintenance window."
  );
  card(ctx, slide, 60, 245, 520, 132, "AOCO files", "Колонки хранятся отдельно, compression работает по column segments.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "ALTER caveat", "Смена storage может требовать rewrite и операционного окна.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Production checklist", "Объем данных, locks, stats, vacuum/analyze, rollback plan.", C.green);

  return slide;
}
