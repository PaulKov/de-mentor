import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide11(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Практика",
    "Docker lab cluster passport",
    "Перед командами фиксируем, какой Greenplum мы смотрим: 1 coordinator + 2 primary segments в одном Docker service."
  );

  card(ctx, slide, 60, 245, 350, 150, "Container", "image: woblerr/greenplum:7.1.0\nservice: greenplum\nport: 15432 -> 5432", C.green);
  card(ctx, slide, 465, 245, 350, 150, "Topology", "1 coordinator/master\n2 primary segments\n0 mirrors, 1 segment host", C.blue);
  card(ctx, slide, 870, 245, 300, 150, "Resources", "CPU/RAM limits не заданы в compose: используются лимиты Docker Desktop/Engine.", C.amber);

  codeBlock(
    ctx,
    slide,
    60,
    435,
    1090,
    170,
    "\\i /mentor-lab/examples/cluster-inspection.sql\n\n-- anchors inside the script:\nSELECT ... FROM gp_segment_configuration;\nSELECT ... FROM pg_settings WHERE name IN (...);\nSELECT ... FROM gp_toolkit.gp_disk_free;",
    "SQL"
  );

  return slide;
}
