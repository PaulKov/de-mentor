import { slides } from "./content.mjs";
import { renderContentSlide } from "./shared.mjs";

export async function slide285(presentation, ctx) {
  return renderContentSlide(presentation, ctx, slides[284]);
}
