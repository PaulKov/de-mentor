import { C, card, slideBase } from "./shared.mjs";

export async function slide09(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "Distribution", "Distribution key — физическое архитектурное решение", "Хороший ключ распределяет строки ровно и делает частые joins локальными.");
  card(ctx, slide, 86, 238, 310, 250, "1. Cardinality", "Много разных значений. Поля вроде status, flag, gender опасны для больших фактов.", C.red);
  card(ctx, slide, 485, 238, 310, 250, "2. Join locality", "Если fact и dimension распределены по одному ключу, join может пройти без Redistribute Motion.", C.blue);
  card(ctx, slide, 884, 238, 310, 250, "3. Workload fit", "Нет универсального ключа. Выбор защищается через grain, query patterns и риски.", C.green);
  return slide;
}
