import { C, card, connector, slideBase } from "./shared.mjs";

export async function slide04(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Master / Coordinator",
    "Master не хранит данные, но может стать узким горлышком",
    "Он принимает клиентские подключения, держит metadata, строит план, dispatch-ит работу и собирает финальный результат."
  );

  card(ctx, slide, 64, 260, 230, 150, "Client", "SQL, COPY, BI, JDBC/ODBC.", C.violet);
  card(ctx, slide, 406, 225, 280, 220, "Master / QD", "Parse -> rewrite -> optimize -> dispatch -> gather. Хорош для control plane, плох как data pipe.", C.blue);
  card(ctx, slide, 820, 188, 220, 152, "Segment 0", "User data lives here.", C.green);
  card(ctx, slide, 820, 372, 220, 152, "Segment 1", "User data lives here.", C.green);

  connector(ctx, slide, 294, 334, 406, 334, C.blue);
  connector(ctx, slide, 686, 302, 820, 260, C.green);
  connector(ctx, slide, 686, 368, 820, 444, C.green);

  ctx.addText(slide, { x: 88, y: 510, width: 1060, height: 66, text: "Главный рефлекс: управление идет через master, тяжелые данные должны идти параллельно через segments.", fontSize: 27, bold: true, color: C.text, align: "center" });
  return slide;
}
