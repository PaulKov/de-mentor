import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide364(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[363]);
}
