import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide32(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "APPENDIX",
    "Partition catalog: как смотреть и считать",
    "В Greenplum 7 основной быстрый путь - pg_partition_tree; compatibility view - gp_toolkit.gp_partitions."
  );
  card(ctx, slide, 60, 245, 520, 132, "pg_partition_tree", "Показывает root/internal/leaf nodes, level и parent relation для partitioned table.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "gp_toolkit.gp_partitions", "Удобный inventory leaf partitions в базе и совместимость с legacy pg_partitions-подходом.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "leaf partitions", "Считаем именно leaf partitions: они физически держат данные и участвуют в pruning.", C.green);
  card(ctx, slide, 650, 405, 520, 132, "Maintenance", "ATTACH PARTITION, DETACH PARTITION, retention DROP; проверять DEFAULT partition и out-of-range INSERT.", C.blue);

  codeBlock(
    ctx,
    slide,
    60,
    560,
    1090,
    92,
    "SELECT * FROM pg_partition_tree('lesson01.partition_range_demo'::regclass);\nSELECT * FROM gp_toolkit.gp_partitions WHERE schemaname = 'lesson01';\n-- COUNT(*) FILTER (WHERE isleaf) AS leaf_partitions",
    "SQL"
  );
  return slide;
}
