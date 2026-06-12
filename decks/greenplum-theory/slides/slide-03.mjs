import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide03(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Позиционирование",
    "Greenplum vs sharded PostgreSQL",
    "Greenplum не sharded PostgreSQL: это MPP engine с единым SQL endpoint и distributed executor."
  );
  card(ctx, slide, 60, 245, 520, 132, "Sharded PostgreSQL", "Routing/fan-out часто живет во внешнем слое или в приложении; cross-shard join становится задачей системы вокруг БД.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Greenplum", "QD строит distributed plan, QE исполняют slices, Motion виден в EXPLAIN как часть плана.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Практический вывод", "Мы проектируем distribution, storage и bulk I/O как часть модели данных, а не как приложение сверху.", C.green);

  return slide;
}
