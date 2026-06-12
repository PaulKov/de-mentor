import { C, card, codeBlock, slideBase } from "./shared.mjs";

export async function slide05(presentation, ctx) {
  const slide = slideBase(
    presentation,
    ctx,
    "Новичку",
    "Master / coordinator простыми словами",
    "Master - диспетчер и точка входа, но не место, через которое должны течь все большие данные."
  );
  card(ctx, slide, 60, 245, 520, 132, "Что делает", "Парсит SQL, смотрит metadata, строит план, отправляет работу сегментам, возвращает результат клиенту.", C.green);
  card(ctx, slide, 650, 245, 520, 132, "Почему узкое место", "Слишком много подключений, metadata work, planning, dispatch или final gather создают очередь на coordinator.", C.blue);
  card(ctx, slide, 60, 405, 520, 132, "Правило урока", "Control plane через master; большие scans/joins/load должны максимально оставаться на segments.", C.green);

  return slide;
}
