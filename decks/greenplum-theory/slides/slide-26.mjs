import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide26(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "APPENDIX",
    "Broadcast vs Redistribute",
    "Выбор data movement зависит от размера сторон после фильтров и ключей распределения."
  );
  card(ctx, slide, 60, 245, 520, 132, "Broadcast", "Хорош, когда broadcast-side реально мала. Плох для большой dimension/fact.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Redistribute", "Нормальная цена несовпадения distribution и join key, но может стать дорогой.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Вопрос ученику", "Что дешевле: разослать 10k строк или переразложить 50M строк?", C.green);

  return slide;
}
