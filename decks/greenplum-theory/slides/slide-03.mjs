import { C, slideBase, card, connector } from "./shared.mjs";

export async function slide03(presentation, ctx) {
  const slide = slideBase(presentation, ctx, "Архитектура", "Greenplum = MPP / shared-nothing", "Coordinator строит план, segments выполняют работу, interconnect переносит данные.");
  card(ctx, slide, 92, 280, 250, 170, "Клиент", "psql, BI-инструмент или приложение отправляет SQL.", C.violet);
  card(ctx, slide, 480, 240, 300, 185, "Coordinator", "Парсит SQL, строит план, отправляет work units на сегменты.", C.blue);
  card(ctx, slide, 910, 174, 220, 152, "Segment 0", "Локальная часть данных и работы.", C.green);
  card(ctx, slide, 910, 344, 220, 152, "Segment 1", "Локальная часть данных и работы.", C.green);
  connector(ctx, slide, 344, 350, 480, 330, C.blue);
  connector(ctx, slide, 780, 310, 910, 240, C.green);
  connector(ctx, slide, 780, 340, 910, 410, C.green);
  ctx.addText(slide, { x: 470, y: 530, width: 620, height: 64, text: "Сеть становится частью query plan.", fontSize: 31, bold: true, color: C.amber, align: "center" });
  return slide;
}
