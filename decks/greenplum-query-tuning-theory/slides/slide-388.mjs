import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide388(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[387]);
}
