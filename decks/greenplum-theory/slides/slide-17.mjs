import { C, slideBase, card } from "./shared.mjs";

export async function slide17(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "Итоги", "Что ученик должен унести с урока", "Если эти пять тезисов закрепились, первый урок выполнил свою работу.");
  card(ctx, slide, 120, 210, 470, 86, "1. Greenplum — не просто большой PostgreSQL.", "", C.blue);
  card(ctx, slide, 120, 320, 470, 86, "2. Distribution key — физическое решение.", "", C.green);
  card(ctx, slide, 120, 430, 470, 86, "3. Skew измеряется через gp_segment_id.", "", C.amber);
  card(ctx, slide, 690, 265, 470, 86, "4. Motion nodes показывают движение по сети.", "", C.violet);
  card(ctx, slide, 690, 375, 470, 86, "5. Фикс доказывается distribution и EXPLAIN.", "", C.red);
  return slide;
}
