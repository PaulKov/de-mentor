import { C, card, slideBase } from "./shared.mjs";

export async function slide16(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "Автоматизация", "Лаборатория оценивает evidence, а не уверенность", "Команды превращают урок в self-service тренажер и дают ментору отчет.");
  card(ctx, slide, 85, 238, 330, 250, "Цикл ученика", "lesson -> seed -> investigate -> check -> hint -> retry", C.blue);
  card(ctx, slide, 475, 238, 330, 250, "Цикл ментора", "grade -> report -> rubric -> next actions -> homework focus", C.green);
  card(ctx, slide, 865, 238, 330, 250, "Цикл платформы", "Та же CLI-форма позже расширяется на Postgres, ClickHouse, HDFS и Spark.", C.violet);
  return slide;
}
