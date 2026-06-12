import { C, card, slideBase } from "./shared.mjs";

export async function slide19(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Appendix",
    "Physical joins in MPP",
    "Join algorithm и data movement - разные оси. В MPP нужно уметь назвать обе."
  );

  card(ctx, slide, 86, 235, 300, 220, "Algorithm axis", "Hash Join, Nested Loop, Merge Join отвечают на вопрос: как один QE соединяет строки локально.", C.green);
  card(ctx, slide, 490, 235, 300, 220, "Locus axis", "co-located join, Broadcast Motion, Redistribute Motion отвечают: где строки должны оказаться.", C.blue);
  card(ctx, slide, 894, 235, 300, 220, "MPP answer", "Полный ответ: Hash Join после Redistribute Motion из-за несовпадения distribution и join key.", C.amber);

  ctx.addText(slide, {
    x: 120,
    y: 540,
    width: 1040,
    height: 76,
    text: "Нельзя говорить только `Hash Join`. Нужно объяснить data movement, build side, skew и возможный spill.",
    fontSize: 22,
    bold: true,
    color: C.text,
    align: "center",
  });
  return slide;
}
