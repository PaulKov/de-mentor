#!/usr/bin/env python3
"""Build Lesson 03 PPTX and regenerate declarative slide sources.

Usage:
    python3 scripts/build_lesson03_pptx.py
"""

from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Pt


ROOT = Path(__file__).resolve().parents[1]
DECK_DIR = ROOT / "decks" / "greenplum-query-tuning-theory"
SLIDES_DIR = DECK_DIR / "slides"
PPTX_PATH = ROOT / "artifacts" / "lesson-03" / "greenplum-query-tuning-theory.pptx"

W, H = 12192000, 6858000  # 13.333" x 7.5" in EMUs
C = {
    "bg": RGBColor(0xF7, 0xF7, 0xF4),
    "panel": RGBColor(0xFF, 0xFF, 0xFF),
    "text": RGBColor(0x20, 0x21, 0x23),
    "muted": RGBColor(0x6E, 0x6E, 0x68),
    "green": RGBColor(0x10, 0xA3, 0x7F),
    "blue": RGBColor(0x2F, 0x6F, 0xED),
    "amber": RGBColor(0xB7, 0x79, 0x1F),
    "red": RGBColor(0xB4, 0x23, 0x18),
    "line": RGBColor(0xD8, 0xD7, 0xD0),
}
HEX = {
    "green": "#10A37F",
    "blue": "#2F6FED",
    "amber": "#B7791F",
    "red": "#B42318",
}


def inch(value: float) -> int:
    return int(value * 914400)


import sys

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
from lesson03_slide_specs import SLIDES


def _set_run(paragraph, text, *, size=18, bold=False, color=None, font="Calibri"):
    paragraph.text = text
    paragraph.font.size = Pt(size)
    paragraph.font.bold = bold
    paragraph.font.name = font
    paragraph.font.color.rgb = color or C["text"]


def _add_rect(slide, x, y, w, h, fill):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    return shape


def _add_round(slide, x, y, w, h, fill):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = C["line"]
    shape.adjustments[0] = 0.08
    return shape


def _add_text(slide, x, y, w, h, text, *, size=18, bold=False, color=None, align=PP_ALIGN.LEFT, font="Calibri"):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    _set_run(p, text, size=size, bold=bold, color=color, font=font)
    return box


def _card(slide, x, y, w, h, title, body, color_key, *, body_size: int = 13):
    _add_round(slide, x, y, w, h, C["panel"])
    _add_rect(slide, x + inch(0.2), y + inch(0.2), inch(0.45), inch(0.05), C[color_key])
    _add_text(slide, x + inch(0.22), y + inch(0.35), w - inch(0.4), inch(0.45), title, size=18, bold=True)
    _add_text(
        slide,
        x + inch(0.22),
        y + inch(0.85),
        w - inch(0.4),
        h - inch(1.05),
        body,
        size=body_size,
        color=C["muted"],
    )


def _slide_base(prs, spec):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_rect(slide, 0, 0, W, H, C["bg"])
    _add_rect(slide, 0, 0, W, inch(0.02), C["line"])
    _add_rect(slide, 0, H - inch(0.02), W, inch(0.02), C["line"])
    _add_text(slide, inch(0.55), inch(0.35), inch(4.5), inch(0.3), spec["kicker"].upper(), size=13, bold=True, color=C["green"])
    _add_text(slide, inch(0.55), inch(0.7), inch(11.5), inch(1.1), spec["title"], size=30, bold=True, font="Calibri")
    if spec.get("subtitle"):
        _add_text(slide, inch(0.55), inch(1.85), inch(11.2), inch(0.6), spec["subtitle"], size=16, color=C["muted"])
    _add_text(slide, inch(11.0), inch(7.05), inch(1.8), inch(0.3), "Урок 03", size=11, color=C["muted"], align=PP_ALIGN.RIGHT)
    return slide


def render_slide(prs, spec):
    slide = _slide_base(prs, spec)
    if spec["type"] == "code":
        label = "PLAN" if "Plan" in spec.get("kicker", "") or "Phases" in spec.get("kicker", "") else "SQL"
        font_size = 11 if len(spec["code"]) > 420 else 12
        _add_round(slide, inch(0.7), inch(2.55), inch(11.9), inch(4.0), C["panel"])
        _add_text(slide, inch(0.95), inch(2.7), inch(2), inch(0.3), label, size=12, bold=True, color=C["green"])
        _add_text(
            slide,
            inch(0.95),
            inch(3.05),
            inch(11.4),
            inch(3.2),
            spec["code"],
            size=font_size,
            font="Consolas",
        )
    elif spec["type"] == "image":
        image_path = ROOT / spec["image"]
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing plan screenshot: {image_path}")
        # Fit screenshot into content band under subtitle.
        left, top = inch(0.7), inch(2.5)
        max_w, max_h = inch(11.9), inch(4.2)
        slide.shapes.add_picture(str(image_path), left, top, width=max_w)
        # Cap height if the picture is taller than the band (python-pptx sets height proportionally).
        pic = slide.shapes[-1]
        if pic.height > max_h:
            ratio = max_h / pic.height
            pic.height = max_h
            pic.width = int(pic.width * ratio)
            pic.left = int((W - pic.width) / 2)
    elif spec["type"] == "two":
        left, right = spec["left"], spec["right"]
        _card(slide, inch(0.6), inch(2.7), inch(5.8), inch(3.5), left[0], left[1], left[2], body_size=12)
        _card(slide, inch(6.8), inch(2.7), inch(5.8), inch(3.5), right[0], right[1], right[2], body_size=12)
    elif spec["type"] == "flow":
        width = inch(2.05)
        gap = inch(0.25)
        y = inch(2.85)
        for index, (title, body, color_key) in enumerate(spec["flow"]):
            x = inch(0.55) + index * (width + gap)
            _card(slide, x, y, width, inch(3.3), title, body, color_key)
            if index < len(spec["flow"]) - 1:
                _add_rect(slide, x + width + inch(0.05), y + inch(1.5), gap - inch(0.1), inch(0.04), C["line"])
    else:
        positions = [
            (inch(0.6), inch(2.55)),
            (inch(6.8), inch(2.55)),
            (inch(0.6), inch(4.55)),
            (inch(6.8), inch(4.55)),
        ]
        long_bodies = any(len(body) > 90 for _, body, _ in spec["cards"])
        card_h = inch(1.85) if long_bodies else inch(1.65)
        body_size = 11 if long_bodies else 13
        for index, (title, body, color_key) in enumerate(spec["cards"]):
            x, y = positions[index]
            _card(slide, x, y, inch(5.8), card_h, title, body, color_key, body_size=body_size)
    return slide


def write_shared_mjs() -> None:
    shared = (ROOT / "decks" / "greenplum-partitioning-theory" / "slides" / "shared.mjs").read_text(encoding="utf-8")
    shared = shared.replace("Урок 02", "Урок 03")
    # Image slides are PPTX-primary; web deck falls back to a path caption.
    shared = shared.replace(
        '  if (spec.type === "code") {\n    codeBlock(ctx, slide, 84, 260, 1060, 310, spec.code);',
        '  if (spec.type === "image") {\n'
        '    codeBlock(ctx, slide, 84, 260, 1060, 310,\n'
        '      "Скрин EXPLAIN (см. PPTX / artifacts):\\n" + (spec.image || ""));\n'
        '  } else if (spec.type === "code") {\n'
        '    codeBlock(ctx, slide, 84, 260, 1060, 310, spec.code);',
    )
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    (SLIDES_DIR / "shared.mjs").write_text(shared, encoding="utf-8")


def write_content_mjs() -> None:
    def color_expr(key: str) -> str:
        return f"C.{key}"

    chunks = ["import { C } from \"./shared.mjs\";", "", "export const slides = ["]
    for spec in SLIDES:
        chunks.append("  {")
        chunks.append(f'    kicker: {json.dumps(spec["kicker"], ensure_ascii=False)},')
        chunks.append(f'    title: {json.dumps(spec["title"], ensure_ascii=False)},')
        chunks.append(f'    subtitle: {json.dumps(spec.get("subtitle", ""), ensure_ascii=False)},')
        chunks.append(f'    type: {json.dumps(spec["type"], ensure_ascii=False)},')
        if spec["type"] == "code":
            chunks.append(f'    code: {json.dumps(spec["code"], ensure_ascii=False)},')
        elif spec["type"] == "image":
            chunks.append(f'    image: {json.dumps(spec["image"], ensure_ascii=False)},')
        elif spec["type"] == "two":
            left = spec["left"]
            right = spec["right"]
            chunks.append(
                f'    left: [{json.dumps(left[0], ensure_ascii=False)}, {json.dumps(left[1], ensure_ascii=False)}, {color_expr(left[2])}],'
            )
            chunks.append(
                f'    right: [{json.dumps(right[0], ensure_ascii=False)}, {json.dumps(right[1], ensure_ascii=False)}, {color_expr(right[2])}],'
            )
        elif spec["type"] == "flow":
            chunks.append("    flow: [")
            for title, body, color_key in spec["flow"]:
                chunks.append(
                    f'      [{json.dumps(title, ensure_ascii=False)}, {json.dumps(body, ensure_ascii=False)}, {color_expr(color_key)}],'
                )
            chunks.append("    ],")
        else:
            chunks.append("    cards: [")
            for title, body, color_key in spec["cards"]:
                chunks.append(
                    f'      [{json.dumps(title, ensure_ascii=False)}, {json.dumps(body, ensure_ascii=False)}, {color_expr(color_key)}],'
                )
            chunks.append("    ],")
        chunks.append("  },")
    chunks.append("];")
    chunks.append("")
    (SLIDES_DIR / "content.mjs").write_text("\n".join(chunks), encoding="utf-8")


def write_slide_modules() -> None:
    SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    for stale in SLIDES_DIR.glob("slide-*.mjs"):
        stale.unlink()
    for index in range(1, len(SLIDES) + 1):
        name = f"slide-{index:02d}.mjs"
        fn = f"slide{index:02d}"
        body = (
            'import { slides } from "./content.mjs";\n'
            'import { renderContentSlide } from "./shared.mjs";\n\n'
            f"export async function {fn}(presentation, ctx) {{\n"
            f"  return renderContentSlide(presentation, ctx, slides[{index - 1}]);\n"
            "}\n"
        )
        (SLIDES_DIR / name).write_text(body, encoding="utf-8")


def build_pptx() -> None:
    prs = Presentation()
    prs.slide_width = Emu(W)
    prs.slide_height = Emu(H)
    for spec in SLIDES:
        render_slide(prs, spec)
    PPTX_PATH.parent.mkdir(parents=True, exist_ok=True)
    prs.save(PPTX_PATH)


def main() -> None:
    write_shared_mjs()
    write_content_mjs()
    write_slide_modules()
    build_pptx()
    print(f"Wrote {len(SLIDES)} slides to {PPTX_PATH}")
    print(f"Wrote sources under {SLIDES_DIR}")


if __name__ == "__main__":
    main()
