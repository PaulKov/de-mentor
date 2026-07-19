import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide370(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[369]);
}
