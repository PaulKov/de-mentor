import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide24(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "APPENDIX",
    "APPENDIX: как читать EXPLAIN",
    "Лестница чтения плана: снизу вверх и от локальной работы к сетевой цене."
  );
  card(ctx, slide, 60, 245, 520, 132, "Leaf scans", "Какие таблицы читаем и сколько строк ожидаем.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Local work", "Filter, aggregate, Hash Join на QE.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Motion boundary", "Где появляется slice boundary и network movement.", C.green);
  card(ctx, slide, 650, 405, 520, 132, "Rows out", "Где actual сильно расходится с estimate.", C.blue);

  return slide;
}
