import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide07(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Deep dive",
    "QD/QE dispatch deep dive",
    "Plan режется на slices; slice исполняется gang-процессами; QueryDispatchDesc создается на QD и уезжает на QE."
  );
  card(ctx, slide, 60, 245, 520, 132, "Что важно новичку", "Не нужно читать C-код в первый час; важно понимать, что distributed plan - нативная часть Greenplum.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Где глубина", "Source anchors: cdbdisp_query.c, execUtils.c, nodeMotion.c.", C.blue);

  codeBlock(ctx, slide, 60, 520, 1090, 130, "QD: parse -> rewrite -> optimize -> slice table\nQD: allocate gang -> build QueryDispatchDesc\nQD -> QE: dispatch MPPEXEC payload\nQE: receive plan fragment -> execute slice -> send tuples via Motion", "SQL / CLI");
  return slide;
}
