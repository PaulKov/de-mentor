import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide23(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Automation",
    "Automation",
    "CLI делает урок повторяемым для ментора и ученика на macOS и Windows."
  );
  card(ctx, slide, 60, 245, 520, 132, "Student UX", "up/status/psql/reset без локального psql.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Mentor UX", "runbook, hints, grading, incident, report.", C.blue);

  codeBlock(ctx, slide, 60, 520, 1090, 130, "python3 mentor-lab.py runbook greenplum simple\npython3 mentor-lab.py runbook greenplum deep\npython3 mentor-lab.py runbook greenplum homework\npython3 mentor-lab.py check greenplum", "SQL / CLI");
  return slide;
}
