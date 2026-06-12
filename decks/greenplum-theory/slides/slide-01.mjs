import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide01(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Теория Greenplum",
    "Greenplum MPP: мышление дата инженера",
    "Первый урок: от системной карты до skew, Motion, storage и доказательного RCA."
  );
  card(ctx, slide, 60, 245, 520, 132, "Маршрут", "60 минут: теория -> SQL practice -> incident -> capstone.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Главный навык", "Думать не только запросом, но и физикой размещения данных.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Фокус", "Coordinator, segments, interconnect, distribution, EXPLAIN.", C.green);

  return slide;
}
