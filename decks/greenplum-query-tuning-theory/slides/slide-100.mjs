import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide100(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[99]);
}
