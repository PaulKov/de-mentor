import { C, codeBlock, slideBase } from "./shared.mjs";

export async function slide11(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "EXPLAIN", "Motion nodes — счет за сеть внутри запроса", "Ученику не нужно понимать весь optimizer сразу; сначала он должен видеть, где данные поехали.");
  codeBlock(ctx, slide, 78, 230, 535, 300, "-> Redistribute Motion 2:2\n   Hash Key: fact_sales_bad.customer_id\n   -> Seq Scan on fact_sales_bad\n\n-> Gather Motion 2:1\n   Merge Key: sum(amount)", "PLAN FRAGMENT");
  ctx.addText(slide, { x: 700, y: 230, width: 430, height: 52, text: "Правило чтения", fontSize: 30, bold: true, color: C.blue });
  ctx.addText(slide, { x: 700, y: 298, width: 440, height: 150, text: "Redistribute Motion значит, что строки не лежат там, где нужны для join или aggregate. Это не всегда плохо, но всегда должно быть осознанно.", fontSize: 22, color: C.text });
  ctx.addText(slide, { x: 700, y: 474, width: 430, height: 86, text: "Вопрос: может ли физическая модель убрать этот motion?", fontSize: 25, bold: true, color: C.amber });
  return slide;
}
