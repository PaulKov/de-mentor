import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide17(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Partitioning intro",
    "Partitioning intro: pruning/retention != distribution",
    "Partitioning режет таблицу внутри logical table; distribution размещает строки по сегментам."
  );
  card(ctx, slide, 60, 245, 520, 132, "Pruning", "Фильтр по sale_date может читать только нужные partitions.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Retention", "Старые partitions можно удалять/архивировать операционно.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Не distribution", "Partition key не обязан быть distribution key.", C.green);

  codeBlock(ctx, slide, 60, 520, 1090, 130, "CREATE TABLE lesson01.fact_sales_partition_good (...)\nDISTRIBUTED BY (customer_id)\nPARTITION BY RANGE (sale_date)\n(START (DATE '2026-01-01') END (DATE '2026-04-01') EVERY (INTERVAL '1 month'));", "SQL / CLI");
  return slide;
}
