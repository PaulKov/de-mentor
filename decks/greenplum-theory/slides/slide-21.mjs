import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide21(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Appendix",
    "Hash Join deep dive",
    "Внутри QE Hash Join строит hash table на inner side и probe-ит outer side; при нехватке memory появляются batches/workfiles."
  );

  codeBlock(ctx, slide, 72, 236, 525, 300, `Hash Join:
  build inner hash table
  for each outer tuple:
    compute hash
    scan bucket
    evaluate join qual
  if memory pressure:
    split into batches
    spill hashvalue + MinimalTuple`, "EXECUTOR SHAPE");

  card(ctx, slide, 650, 236, 245, 170, "Build side", "Меньшая сторона обычно лучше для hash table.", C.green);
  card(ctx, slide, 940, 236, 245, 150, "Spill", "Workfiles означают, что join вышел за memory budget.", C.red);
  card(ctx, slide, 650, 430, 535, 106, "Source anchors", "nodeHashjoin.c state machine; ExecHashJoinSaveTuple пишет hash value + MinimalTuple.", C.violet);

  ctx.addText(slide, { x: 152, y: 608, width: 960, height: 34, text: "MPP вопрос сверху: была ли data movement цена до того, как QE начал локальный Hash Join?", fontSize: 18, bold: true, color: C.text, align: "center" });
  return slide;
}
