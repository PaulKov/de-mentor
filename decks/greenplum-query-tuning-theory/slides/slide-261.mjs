import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide261(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[260]);
}
