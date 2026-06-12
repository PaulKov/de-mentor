import { C, codeBlock, slideBase } from "./shared.mjs";

export async function slide14(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "Паттерн фикса", "Исправляем модель и доказываем эффект", "Профессиональный ответ содержит DDL и validation evidence.");
  codeBlock(ctx, slide, 72, 230, 520, 292, "CREATE TABLE fact_sales_good (...)\nDISTRIBUTED BY (customer_id);\n\nSELECT gp_segment_id, count(*)\nFROM fact_sales_good\nGROUP BY gp_segment_id;", "DDL + CHECK");
  codeBlock(ctx, slide, 668, 230, 520, 292, "EXPLAIN\nSELECT c.region, sum(f.amount)\nFROM fact_sales_good f\nJOIN dim_customers c USING(customer_id)\nGROUP BY c.region;", "PLAN CHECK");
  ctx.addText(slide, { x: 210, y: 558, width: 850, height: 76, text: "Фикс не завершен, пока не измерены distribution и форма плана.", fontSize: 27, bold: true, color: C.green, align: "center" });
  return slide;
}
