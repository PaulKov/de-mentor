import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide20(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Incident",
    "Incident mode",
    "Теперь это не упражнение, а замедлившийся отчет и короткий RCA для бизнеса."
  );
  card(ctx, slide, 60, 245, 520, 132, "Симптом", "Отчет по выручке стал медленнее после новой fact table.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Гипотезы", "Skew, non-colocated join, missing statistics, плохой storage/load path.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Артефакт", "RCA: symptom -> evidence -> root cause -> fix -> validation.", C.green);

  return slide;
}
