import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide08(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Interconnect",
    "Interconnect и Motion",
    "Motion - оператор движения строк между QE. Это не всегда ошибка, но всегда физическая цена."
  );
  card(ctx, slide, 60, 245, 520, 132, "Gather Motion", "Собрать результат на coordinator или consumer slice.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Broadcast Motion", "Разослать маленькую сторону join всем segments.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Redistribute Motion", "Переразложить строки по hash ключу для join/aggregate.", C.green);

  return slide;
}
