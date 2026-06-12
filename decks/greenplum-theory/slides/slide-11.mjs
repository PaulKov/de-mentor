import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide11(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Runnable DDL",
    "Heap vs AOCO: runnable DDL + catalog checks",
    "Демо живет в labs/greenplum/examples/storage-and-partitioning.sql."
  );
  card(ctx, slide, 60, 245, 520, 132, "Проверяем", "Heap/AO/AOCO видны через psql \\d+ и catalog checks.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Не путаем", "Storage ускоряет scan/compression, но не заменяет distribution key.", C.blue);

  codeBlock(ctx, slide, 60, 520, 1090, 130, "CREATE TABLE lesson01.storage_aoco_demo (...)\nWITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1)\nDISTRIBUTED BY (customer_id);\n\n\\d+ lesson01.storage_aoco_demo\nSELECT c.relname, am.amname AS access_method FROM pg_class c LEFT JOIN pg_am am ON am.oid = c.relam WHERE c.relname LIKE 'storage_%_demo';", "SQL / CLI");
  return slide;
}
