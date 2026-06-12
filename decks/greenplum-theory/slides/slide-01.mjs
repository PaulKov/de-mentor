import { C, slideBase, pill } from "./shared.mjs";

export async function slide01(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Теория Greenplum",
    "Greenplum MPP: мышление дата инженера",
    "Как думать о SQL, когда данные физически распределены по сегментам."
  );
  ctx.addShape(slide, { x: 760, y: 118, width: 390, height: 398, fill: C.panel, radius: 10, line: { fill: C.line, width: 1, style: "solid" } });
  ctx.addShape(slide, { x: 802, y: 160, width: 306, height: 116, fill: C.softGreen, radius: 10, line: { fill: C.softGreen, width: 0, style: "solid" } });
  await ctx.addLucideIcon(slide, { icon: "DatabaseZap", x: 880, y: 184, width: 84, height: 84, color: C.green, strokeWidth: 1.6 });
  await ctx.addLucideIcon(slide, { icon: "Network", x: 980, y: 184, width: 84, height: 84, color: C.blue, strokeWidth: 1.6 });
  pill(ctx, slide, 800, 336, 132, "SMP / MPP", C.green);
  pill(ctx, slide, 950, 336, 132, "Skew", C.amber);
  ctx.addText(slide, { x: 800, y: 398, width: 300, height: 74, text: "60 минут: модель -> практика -> incident -> capstone", fontSize: 19, bold: true, color: C.text, align: "center" });
  return slide;
}
