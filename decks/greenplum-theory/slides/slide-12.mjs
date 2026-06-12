import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide12(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Defaults",
    "Columnstore defaults: table / database / role / instance",
    "Columnstore включается явно; defaults помогают стандарту, но требуют дисциплины."
  );
  card(ctx, slide, 60, 245, 520, 132, "Table level", "WITH (appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1).", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Column level", "amount numeric(12,2) ENCODING (compresstype=zstd, compresslevel=3).", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Admin note", "Instance-level gpconfig показываем как production/admin snippet, не выполняем без необходимости.", C.green);

  codeBlock(ctx, slide, 60, 520, 1090, 130, "ALTER DATABASE mentor SET gp_default_storage_options =\n'appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1';\n\ngpconfig -c gp_default_storage_options \\\n  -v \"'appendoptimized=true, orientation=column, compresstype=zstd, compresslevel=1'\"", "SQL / CLI");
  return slide;
}
