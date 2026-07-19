import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide51(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[50]);
}
