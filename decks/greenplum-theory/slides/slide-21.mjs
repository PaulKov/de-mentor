import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide21(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Evidence",
    "Fix and evidence",
    "Фикс без проверки - мнение. Фикс с повторным EXPLAIN и skew check - инженерное решение."
  );
  card(ctx, slide, 60, 245, 520, 132, "До", "DISTRIBUTED BY(status), skew, Redistribute Motion.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "После", "DISTRIBUTED BY(customer_id), ровнее gp_segment_id, дешевле движение.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Доказываем", "Скрин/вывод SQL, короткая интерпретация, оставшийся риск.", C.green);

  return slide;
}
