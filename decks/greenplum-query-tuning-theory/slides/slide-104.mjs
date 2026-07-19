import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide104(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[103]);
}
