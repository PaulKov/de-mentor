import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide272(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[271]);
}
