import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide367(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[366]);
}
