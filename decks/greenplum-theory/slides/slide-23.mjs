import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide23(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Summary",
    "Что ученик должен унести с урока",
    "Одна страница mental model перед домашкой."
  );
  card(ctx, slide, 60, 245, 520, 132, "Greenplum = MPP", "Coordinator планирует, segments исполняют, interconnect двигает строки.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Физика важна", "Distribution, skew, Motion и storage влияют на тот же SQL сильнее, чем кажется.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Доказательность", "Каждый fix подтверждаем skew check, EXPLAIN и коротким RCA.", C.green);

  return slide;
}
