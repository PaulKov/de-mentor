export const C = {
  bg: "#F7F7F4",
  panel: "#FFFFFF",
  panel2: "#EFEEE8",
  text: "#202123",
  muted: "#6E6E68",
  blue: "#2F6FED",
  green: "#10A37F",
  amber: "#B7791F",
  red: "#B42318",
  violet: "#6B5BD2",
  line: "#D8D7D0",
  softGreen: "#DFF5EC",
  softBlue: "#E8F0FE",
  softAmber: "#F6E7C8",
  softRed: "#F8DFDA",
};

export function slideBase(presentation, ctx, kicker, title, subtitle = "") {
  const slide = presentation.slides.add();
  ctx.addShape(slide, { x: 0, y: 0, width: ctx.W, height: ctx.H, fill: C.bg });
  ctx.addShape(slide, { x: 0, y: 0, width: ctx.W, height: 1, fill: C.line });
  ctx.addShape(slide, { x: 0, y: 719, width: ctx.W, height: 1, fill: C.line });
  ctx.addText(slide, {
    x: 48,
    y: 34,
    width: 360,
    height: 24,
    text: kicker.toUpperCase(),
    fontSize: 14,
    bold: true,
    color: C.green,
  });
  ctx.addText(slide, {
    x: 48,
    y: 70,
    width: 790,
    height: 96,
    text: title,
    fontSize: 38,
    bold: true,
    color: C.text,
    typeface: ctx.fonts.title,
  });
  if (subtitle) {
    ctx.addText(slide, {
      x: 50,
      y: 170,
      width: 740,
      height: 48,
      text: subtitle,
      fontSize: 19,
      color: C.muted,
    });
  }
  ctx.addText(slide, {
    x: 1108,
    y: 672,
    width: 118,
    height: 20,
    text: `Урок 01`,
    fontSize: 12,
    color: C.muted,
    align: "right",
  });
  return slide;
}

export function card(ctx, slide, x, y, width, height, title, body, color = C.blue) {
  ctx.addShape(slide, {
    x,
    y,
    width,
    height,
    fill: C.panel,
    radius: 8,
    line: { fill: C.line, width: 1, style: "solid" },
  });
  ctx.addShape(slide, { x: x + 18, y: y + 18, width: 42, height: 4, fill: color });
  ctx.addText(slide, {
    x: x + 22,
    y: y + 36,
    width: width - 40,
    height: 54,
    text: title,
    fontSize: 20,
    bold: true,
    color: C.text,
  });
  if (body) {
    ctx.addText(slide, {
      x: x + 22,
      y: y + 92,
      width: width - 42,
      height: Math.max(40, height - 112),
      text: body,
      fontSize: 15,
      color: C.muted,
    });
  }
}

export function pill(ctx, slide, x, y, width, text, color = C.blue) {
  ctx.addShape(slide, {
    x,
    y,
    width,
    height: 34,
    radius: 17,
    fill: "#FFFFFF",
    line: { fill: color, width: 1, style: "solid" },
  });
  ctx.addText(slide, {
    x,
    y: y + 7,
    width,
    height: 18,
    text,
    fontSize: 13,
    bold: true,
    color,
    align: "center",
  });
}

export function bar(ctx, slide, x, y, width, label, value, color) {
  ctx.addText(slide, { x, y: y - 28, width, height: 20, text: label, fontSize: 14, color: C.muted });
  ctx.addShape(slide, { x, y, width, height: 20, fill: "#E8E7E1", radius: 10 });
  ctx.addShape(slide, { x, y, width: Math.max(8, width * value), height: 20, fill: color, radius: 10 });
  ctx.addText(slide, {
    x: x + width + 12,
    y: y - 2,
    width: 82,
    height: 24,
    text: `${Math.round(value * 100)}%`,
    fontSize: 16,
    bold: true,
    color: C.text,
  });
}

export function codeBlock(ctx, slide, x, y, width, height, code, label = "SQL") {
  ctx.addShape(slide, {
    x,
    y,
    width,
    height,
    fill: "#FFFFFF",
    radius: 8,
    line: { fill: C.line, width: 1, style: "solid" },
  });
  ctx.addText(slide, { x: x + 18, y: y + 14, width: 120, height: 20, text: label, fontSize: 12, bold: true, color: C.green });
  ctx.addText(slide, {
    x: x + 18,
    y: y + 42,
    width: width - 36,
    height: height - 52,
    text: code,
    fontSize: 14,
    color: C.text,
    typeface: ctx.fonts.mono,
  });
}

export function connector(ctx, slide, x1, y1, x2, y2, color = C.line) {
  const width = Math.max(2, Math.abs(x2 - x1));
  const height = Math.max(2, Math.abs(y2 - y1));
  ctx.addShape(slide, {
    x: Math.min(x1, x2),
    y: Math.min(y1, y2),
    width,
    height,
    fill: "#00000000",
    line: { fill: color, width: 3, style: "solid" },
  });
}
