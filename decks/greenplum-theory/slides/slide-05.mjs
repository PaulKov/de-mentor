import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide05(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "QD/QE deep dive",
    "Как план уезжает с QD на QE",
    "Внутри Greenplum план режется на slices, исполняется gangs-процессами, а dispatch payload сериализуется."
  );

  codeBlock(ctx, slide, 68, 226, 585, 338, `QD:
  PlannedStmt -> SliceTable
  allocate gang per executable slice
  serializeNode(plan)              -- binary tree
  serializeNode(QueryDispatchDesc) -- params, slice table, context
  dispatch MPPEXEC to QEs

QE:
  deserializeNode(payload)
  install slice table
  execute assigned slice`, "QD/QE ALGORITHM");

  card(ctx, slide, 716, 218, 405, 108, "Slice", "Единица исполнения между Motion nodes. Root slice часто остается на QD.", C.blue);
  card(ctx, slide, 716, 344, 405, 108, "Gang", "Группа QE-процессов на сегментах, исполняющая slice параллельно.", C.green);
  card(ctx, slide, 716, 466, 405, 122, "Compression", "ZSTD для plan payload, если GPDB собран с libzstd; иначе binary serialization.", C.amber);

  ctx.addText(slide, { x: 88, y: 612, width: 1040, height: 34, text: "Source anchors: cdbdisp_query.c, cdbsrlz.c, execdesc.h", fontSize: 16, color: C.muted, align: "center" });
  return slide;
}
