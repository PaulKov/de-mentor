import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide06(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Аналогия",
    "QD / QE / gang / slices: простая аналогия",
    "QD - диспетчер смены; QE - исполнители; gang - команда; slice - участок работы."
  );
  card(ctx, slide, 60, 245, 520, 132, "QD", "Query Dispatcher на coordinator: решает, что делать и кому отправить.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "QE", "Query Executor на segment: исполняет свою часть плана над локальными данными.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "gang", "Набор QE-процессов, которые синхронно исполняют slice на сегментах.", C.green);
  card(ctx, slide, 650, 405, 520, 132, "slice", "Фрагмент distributed plan; часто граница проходит около Motion.", C.blue);

  return slide;
}
