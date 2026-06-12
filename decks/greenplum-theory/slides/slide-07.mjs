import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide07(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Bulk I/O",
    "Через master или напрямую на segments",
    "Для маленьких загрузок удобно идти через client/COPY; для больших потоков нужен parallel segment data path."
  );

  card(ctx, slide, 68, 228, 330, 212, "COPY через client/QD", "Client stream приходит на coordinator. QD dispatch-ит COPY на QEs и прокидывает данные дальше. Просто, но master/client network становятся узким местом.", C.red);
  card(ctx, slide, 474, 228, 330, 212, "gpfdist external table", "gpfdist - HTTP server. Каждый segment подключается сам, читает/пишет поток параллельно, master держит metadata и план.", C.green);
  card(ctx, slide, 880, 228, 330, 212, "PXF / writable external", "Та же идея data-plane bypass: segments работают с внешним storage или сервисом напрямую, когда protocol это поддерживает.", C.blue);

  codeBlock(ctx, slide, 172, 466, 940, 130, `CREATE EXTERNAL TABLE stg_sales (...)
LOCATION ('gpfdist://loader-host:8081/sales.csv')
FORMAT 'CSV' (HEADER)
DISTRIBUTED BY (customer_id);`, "PARALLEL LOAD");

  ctx.addText(slide, { x: 110, y: 620, width: 1040, height: 32, text: "gpfdist protocol v1: messages F/O/L/D/E; optional X-GP-ZSTD path exists when built with ZSTD support.", fontSize: 16, color: C.muted, align: "center" });
  return slide;
}
