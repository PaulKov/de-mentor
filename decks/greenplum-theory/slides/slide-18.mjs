import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide18(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Practice",
    "Practice checkpoint",
    "Ученик сам проходит skew -> EXPLAIN -> comparison -> short RCA."
  );
  card(ctx, slide, 60, 245, 520, 132, "Что делает ученик", "Запускает workbook, ищет skew, читает Motion, сравнивает bad/good fact.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Что делает ментор", "Задает вопросы и просит доказывать каждый вывод SQL-артефактом.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Критерий", "Ученик может назвать root cause и validation query.", C.green);

  return slide;
}
