import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide178(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[177]);
}
