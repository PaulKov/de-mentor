import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide57(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[56]);
}
