export const C = {
  bg: "#F7F7F4",
  panel: "#FFFFFF",
  panel2: "#EFEEE8",
  text: "#202123",
  muted: "#6E6E68",
  green: "#10A37F",
  blue: "#2F6FED",
  amber: "#B7791F",
  red: "#B42318",
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
    width: 420,
    height: 24,
    text: kicker.toUpperCase(),
    fontSize: 14,
    bold: true,
    color: C.green,
  });
  ctx.addText(slide, {
    x: 48,
    y: 70,
    width: 860,
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
      width: 760,
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
    text: "Урок 02",
    fontSize: 12,
    color: C.muted,
    align: "right",
  });
  return slide;
}

export function card(ctx, slide, x, y, width, height, title, body, color = C.green) {
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
    width: width - 44,
    height: 52,
    text: title,
    fontSize: 20,
    bold: true,
    color: C.text,
  });
  ctx.addText(slide, {
    x: x + 22,
    y: y + 88,
    width: width - 44,
    height: height - 108,
    text: body,
    fontSize: 14,
    color: C.muted,
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
  ctx.addText(slide, { x: x + 18, y: y + 14, width: 160, height: 20, text: label, fontSize: 12, bold: true, color: C.green });
  ctx.addText(slide, {
    x: x + 18,
    y: y + 42,
    width: width - 36,
    height: height - 52,
    text: code,
    fontSize: 13,
    color: C.text,
    typeface: ctx.fonts.mono,
  });
}

export function flow(ctx, slide, items, y = 300) {
  const width = 176;
  const gap = 22;
  items.forEach((item, index) => {
    const x = 70 + index * (width + gap);
    card(ctx, slide, x, y, width, 196, item.title, item.body, item.color || C.green);
    if (index < items.length - 1) {
      ctx.addShape(slide, { x: x + width + 4, y: y + 94, width: gap - 8, height: 3, fill: C.line });
    }
  });
}

export function twoColumn(ctx, slide, left, right) {
  card(ctx, slide, 60, 250, 520, 290, left.title, left.body, left.color || C.green);
  card(ctx, slide, 650, 250, 520, 290, right.title, right.body, right.color || C.blue);
}

export function renderContentSlide(presentation, ctx, spec) {
  const slide = slideBase(presentation, ctx, spec.kicker, spec.title, spec.subtitle);
  if (spec.type === "code") {
    codeBlock(ctx, slide, 84, 260, 1060, 310, spec.code);
  } else if (spec.type === "two") {
    twoColumn(
      ctx,
      slide,
      { title: spec.left[0], body: spec.left[1], color: spec.left[2] },
      { title: spec.right[0], body: spec.right[1], color: spec.right[2] },
    );
  } else if (spec.type === "flow") {
    flow(
      ctx,
      slide,
      spec.flow.map(([title, body, color]) => ({ title, body, color })),
      300,
    );
  } else {
    const positions = [
      [60, 250],
      [650, 250],
      [60, 420],
      [650, 420],
    ];
    spec.cards.forEach(([title, body, color], index) => {
      const [x, y] = positions[index];
      card(ctx, slide, x, y, 520, 148, title, body, color);
    });
  }
  return slide;
}
