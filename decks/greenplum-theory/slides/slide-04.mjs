import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide04(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Топология",
    "Greenplum shared-nothing topology",
    "Coordinator принимает SQL, segments держат data plane, interconnect переносит строки между QE."
  );
  card(ctx, slide, 60, 245, 520, 132, "Coordinator / master", "Подключения, metadata, planning, dispatch, final gather.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Primary / mirror segments", "Локальное хранение и локальное исполнение. Mirror нужен для HA.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Interconnect", "Сеть становится частью query plan: Gather, Broadcast, Redistribute Motion.", C.green);

  return slide;
}
