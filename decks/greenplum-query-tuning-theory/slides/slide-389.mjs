import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide389(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[388]);
}
