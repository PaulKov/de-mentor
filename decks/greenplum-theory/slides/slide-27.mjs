import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide27(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "APPENDIX",
    "Hash Join deep dive",
    "QE строит hash table на inner side и probe-ит outer side; memory pressure ведет к batching/workfiles."
  );
  card(ctx, slide, 60, 245, 520, 132, "Build side", "Обычно меньшая сторона. Ошибка оценок может привести к spill.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Probe side", "Большая сторона проходит через hash lookup локально на QE.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "MPP context", "Перед локальным Hash Join данные могли пройти Broadcast или Redistribute Motion.", C.green);

  return slide;
}
