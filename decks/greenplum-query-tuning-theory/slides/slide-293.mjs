import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide293(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[292]);
}
