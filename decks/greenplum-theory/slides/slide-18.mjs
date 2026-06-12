import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide18(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Appendix",
    "APPENDIX: как читать EXPLAIN",
    "План читается как физический маршрут данных: scan -> local work -> join -> Motion -> global work."
  );

  codeBlock(ctx, slide, 70, 236, 500, 318, `plan-reading ladder:
1. leaf scans
2. filters + cardinality
3. join algorithm
4. Motion / slice boundary
5. final aggregate / gather
6. Rows out vs estimates
7. one-sentence RCA`, "READING ORDER");

  card(ctx, slide, 625, 232, 250, 176, "Motion", "Граница data movement/slice. Спроси: почему строки едут?", C.blue);
  card(ctx, slide, 915, 232, 250, 176, "Rows out", "Фактический поток строк: где оценка неожиданно поменяла масштаб?", C.green);
  card(ctx, slide, 625, 438, 540, 140, "RCA sentence", "План дорогой, потому что <node> двигает или строит <rows> из-за <distribution/join/skew reason>.", C.amber);
  return slide;
}
