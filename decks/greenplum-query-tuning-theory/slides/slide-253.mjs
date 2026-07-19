import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide253(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[252]);
}
