import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide421(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[420]);
}
