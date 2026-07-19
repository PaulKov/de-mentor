import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide292(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[291]);
}
