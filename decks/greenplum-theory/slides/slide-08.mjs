import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide08(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Table storage",
    "Heap, AO row, AOCO column: когда что выбирать",
    "В Greenplum columnstore - это append-optimized column-oriented table, а не отдельная магия поверх heap."
  );

  card(ctx, slide, 62, 230, 310, 190, "Heap", "Row-oriented storage по умолчанию. Подходит для небольших mutable tables, staging, частых точечных изменений.", C.blue);
  card(ctx, slide, 485, 230, 310, 190, "AO row", "Append-optimized row. Хорош для batch insert и широких scans, когда часто читается почти вся строка.", C.green);
  card(ctx, slide, 908, 230, 310, 190, "AOCO column", "Column-oriented AO. Сильный вариант для OLAP: меньше I/O по выбранным колонкам, эффективнее compression.", C.amber);

  codeBlock(ctx, slide, 138, 456, 1010, 150, `WITH (appendoptimized=true, orientation=column,
      compresstype=zstd, compresslevel=1, blocksize=32768)

-- column-level:
amount numeric ENCODING (compresstype=zstd, compresslevel=3)`, "STORAGE OPTIONS");

  ctx.addText(slide, { x: 150, y: 620, width: 980, height: 42, text: "Правило: heap для mutable/малого, AO/AOCO для больших аналитических фактов и партиций; storage model меняется через rebuild.", fontSize: 16, bold: true, color: C.text, align: "center" });
  return slide;
}
