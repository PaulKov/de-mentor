import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide17(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Partitioning intro",
    "Partitioning strategies: RANGE / LIST / HASH",
    "Partitioning режет logical table для pruning/retention; distribution размещает строки по сегментам."
  );
  card(ctx, slide, 60, 245, 350, 132, "PARTITION BY RANGE", "Даты/числа: pruning, retention, monthly/daily windows.", C.green);
  card(ctx, slide, 465, 245, 350, 132, "PARTITION BY LIST", "Конечные категории: region, source_system, tenant_group.", C.blue);
  card(ctx, slide, 870, 245, 300, 132, "PARTITION BY HASH", "Bucketization, когда нет естественного range/list. Не заменяет distribution.", C.amber);
  card(ctx, slide, 60, 405, 520, 132, "DEFAULT partition", "Safety net для unexpected values; без него out-of-range INSERT падает.", C.green);
  card(ctx, slide, 650, 405, 520, 132, "Не distribution", "Partition key не обязан быть distribution key; leaf partitions тоже распределены по segments.", C.blue);

  codeBlock(ctx, slide, 60, 560, 1090, 86, "DISTRIBUTED BY (customer_id) -- placement\nPARTITION BY RANGE (sale_date) -- pruning/retention\n-- no default partitioning: DEFAULT partition нужно объявить явно", "SQL");
  return slide;
}
