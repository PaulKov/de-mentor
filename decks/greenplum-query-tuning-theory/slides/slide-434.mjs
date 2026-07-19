import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide434(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[433]);
}
