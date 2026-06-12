import { C, bar, slideBase } from "./shared.mjs";

export async function slide10(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "Доказательство", "Skew видно до production-инцидента", "Проверка `gp_segment_id` превращает архитектурную гипотезу в измеримый факт.");
  ctx.addText(slide, { x: 96, y: 230, width: 430, height: 34, text: "Плохо: DISTRIBUTED BY(status)", fontSize: 24, bold: true, color: C.red });
  bar(ctx, slide, 100, 312, 380, "Segment 0", 0.01, C.red);
  bar(ctx, slide, 100, 402, 380, "Segment 1", 0.99, C.red);
  ctx.addText(slide, { x: 710, y: 230, width: 430, height: 34, text: "Лучше: BY(customer_id)", fontSize: 24, bold: true, color: C.green });
  bar(ctx, slide, 714, 312, 380, "Segment 0", 0.501, C.green);
  bar(ctx, slide, 714, 402, 380, "Segment 1", 0.499, C.green);
  ctx.addText(slide, { x: 250, y: 548, width: 780, height: 70, text: "Оптимизатору легче помогать, когда физическая модель не мешает.", fontSize: 26, bold: true, color: C.text, align: "center" });
  return slide;
}
