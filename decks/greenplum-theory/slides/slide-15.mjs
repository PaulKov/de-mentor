import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide15(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Plan reading",
    "EXPLAIN и Motion",
    "Первый взгляд новичка в Greenplum-плане: где данные едут по сети."
  );
  card(ctx, slide, 60, 245, 520, 132, "Redistribute Motion", "Данные перекладываются по новому ключу. Часто join key не совпал с distribution key.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Broadcast Motion", "Маленькая таблица копируется на все сегменты. Хорошо только если она действительно маленькая.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Gather Motion", "Финальная сборка результата. Нормально, но может стать bottleneck для огромного output.", C.green);

  return slide;
}
