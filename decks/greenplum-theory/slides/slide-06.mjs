import { C, card, codeBlock, connector, slideBase } from "./shared.mjs";

export async function slide06(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Interconnect",
    "Как данные едут между сегментами",
    "Motion node выбирает route, сериализует tuple в TupleChunks и отправляет их через interconnect."
  );

  card(ctx, slide, 58, 228, 210, 176, "Sender QE", "ExecProcNode дает tuple из child plan.", C.green);
  card(ctx, slide, 356, 228, 250, 176, "Motion", "GATHER -> route 0; BROADCAST -> all; HASH -> evalHashKey.", C.blue);
  card(ctx, slide, 704, 228, 250, 176, "Interconnect", "Packet = header + one or more serialized TupleChunks.", C.amber);
  card(ctx, slide, 1032, 228, 190, 176, "Receiver QE", "RecvTupleFrom собирает MinimalTuple.", C.violet);

  connector(ctx, slide, 268, 314, 356, 314, C.green);
  connector(ctx, slide, 606, 314, 704, 314, C.blue);
  connector(ctx, slide, 954, 314, 1032, 314, C.amber);

  codeBlock(ctx, slide, 100, 446, 1040, 150, `if motion == HASH:
  targetRoute = evalHashKey(distribution_expr)
elif motion == BROADCAST:
  targetRoute = all_receivers
SendTuple(motionID, slot, targetRoute) -> TupleChunks -> packet -> RecvTupleFrom(...)`, "MOTION ROUTING");

  ctx.addText(slide, { x: 116, y: 614, width: 1000, height: 44, text: "Важно: Redistribute Motion идет segment-to-segment; master не должен становиться промежуточной трубой для каждой строки.", fontSize: 17, bold: true, color: C.text, align: "center" });
  return slide;
}
