import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide13(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Distribution",
    "Distribution key",
    "Ключ распределения решает, где физически лежит строка и какие joins станут локальными."
  );
  card(ctx, slide, 60, 245, 520, 132, "Хороший ключ", "Высокая cardinality, равномерность, совпадение с частым join key.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Плохой ключ", "Низкая cardinality, skew, один segment делает почти всю работу.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Не то же самое", "Distribution key не равен primary key и не равен partition key.", C.green);

  return slide;
}
