import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide237(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[236]);
}
