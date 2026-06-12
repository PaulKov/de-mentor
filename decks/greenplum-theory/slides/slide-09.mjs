import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide09(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Bulk I/O",
    "Bulk I/O paths",
    "Для больших загрузок держим master в control plane и даем segments читать/писать параллельно."
  );
  card(ctx, slide, 60, 245, 520, 132, "COPY через client", "Просто для малых объемов, но поток легко становится центральной трубой.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "gpfdist external table", "Segments читают файлы параллельно как HTTP clients; throughput растет вместе с segments.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Production habit", "Для bulk load заранее думай про parallel path, формат, compression, network и error handling.", C.green);

  return slide;
}
