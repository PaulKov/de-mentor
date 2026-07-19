import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide213(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[212]);
}
