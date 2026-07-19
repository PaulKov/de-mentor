import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide284(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[283]);
}
