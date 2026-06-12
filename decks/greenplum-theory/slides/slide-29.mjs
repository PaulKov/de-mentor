import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide29(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "APPENDIX",
    "QD/QE internals with source anchors",
    "Глубина для любопытного ученика: source anchors без превращения урока в чтение C-кода."
  );
  card(ctx, slide, 60, 245, 520, 132, "cdbdisp_query.c", "Dispatch path: QD готовит и отправляет plan payload на QE.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "nodeMotion.c", "Motion executor обрабатывает send/receive tuple flow между slices.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "nodeHashjoin.c / joinpath.c", "Локальный Hash Join и optimizer choices отдельно от CdbPathLocus.", C.green);

  return slide;
}
