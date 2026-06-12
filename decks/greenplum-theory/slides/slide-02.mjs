import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide02(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Карта систем",
    "SMP, MPP, EPP: где живет узкое место",
    "SMP / Shared-disk / MPP / EPP дают разные компромиссы по простоте, масштабу и цене сети."
  );
  card(ctx, slide, 60, 245, 520, 132, "SMP", "Один большой сервер, общая память/storage. Простота, но вертикальный потолок.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Shared-disk", "Несколько compute-узлов, общее хранилище. Единые данные, но storage contention.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "MPP", "Shared-nothing: сегменты хранят свои данные и параллельно исполняют запросы.", C.green);
  card(ctx, slide, 650, 405, 520, 132, "EPP / cloud elastic", "Compute и storage часто масштабируются независимо; цена и shuffle требуют контроля.", C.blue);

  return slide;
}
