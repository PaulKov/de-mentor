import fs from "node:fs";
import path from "node:path";
import { CORE_SLIDE_COUNT, SLIDES } from "./content.mjs";

/**
 * Build a deterministic Google Slides API migration plan for Lesson 04.
 *
 * The input is the full connector response captured while the published deck
 * still has its original 42-slide structure. The output deliberately splits
 * native slide creation, ordered block moves and deletion of superseded slides
 * so a caller can perform structural readbacks between irreversible phases.
 * This script only prepares requests; it never performs network writes.
 */

const POSITION_SCALE = 0.75;
const FONT_SCALE = 0.75;
const C = {
  bg: "#F7F7F4",
  panel: "#FFFFFF",
  panel2: "#EFEEE8",
  text: "#202123",
  muted: "#6E6E68",
  line: "#D8D7D0",
  green: "#10A37F",
  blue: "#2F6FED",
  red: "#B42318",
  orange: "#E25A1C",
  dark: "#1F2428",
};

function rgb(hex) {
  const value = hex.replace("#", "");
  return {
    red: Number.parseInt(value.slice(0, 2), 16) / 255,
    green: Number.parseInt(value.slice(2, 4), 16) / 255,
    blue: Number.parseInt(value.slice(4, 6), 16) / 255,
  };
}

function scaled(value) {
  return value * POSITION_SCALE;
}

function textOf(element) {
  return (element.shape?.text?.textElements ?? [])
    .map((item) => item.textRun?.content ?? "")
    .join("")
    .trim();
}

class NativeSlidesBuilder {
  constructor({ layoutId }) {
    this.layoutId = layoutId;
    this.requests = [];
    this.serial = 0;
  }

  objectId(pageId, role) {
    this.serial += 1;
    return `${pageId}_${role}_${String(this.serial).padStart(4, "0")}`;
  }

  addSlide(pageId) {
    this.requests.push({
      createSlide: {
        objectId: pageId,
        slideLayoutReference: { layoutId: this.layoutId },
      },
    });
    this.requests.push({
      updatePageProperties: {
        objectId: pageId,
        pageProperties: {
          pageBackgroundFill: { solidFill: { color: { rgbColor: rgb(C.bg) }, alpha: 1 } },
        },
        fields: "pageBackgroundFill",
      },
    });
  }

  elementProperties(pageId, position) {
    return {
      pageObjectId: pageId,
      size: {
        width: { magnitude: scaled(position.width), unit: "PT" },
        height: { magnitude: scaled(position.height), unit: "PT" },
      },
      transform: {
        scaleX: 1,
        scaleY: 1,
        translateX: scaled(position.left),
        translateY: scaled(position.top),
        unit: "PT",
      },
    };
  }

  addShape(pageId, shapeType, position, fill = "none", line = "none", role = "shape") {
    const objectId = this.objectId(pageId, role);
    this.requests.push({
      createShape: {
        objectId,
        shapeType,
        elementProperties: this.elementProperties(pageId, position),
      },
    });
    const shapeProperties = {
      shapeBackgroundFill: fill === "none"
        ? { propertyState: "NOT_RENDERED" }
        : { solidFill: { color: { rgbColor: rgb(fill) }, alpha: 1 } },
      outline: line === "none"
        ? { propertyState: "NOT_RENDERED" }
        : {
            outlineFill: { solidFill: { color: { rgbColor: rgb(line) }, alpha: 1 } },
            weight: { magnitude: 0.75, unit: "PT" },
            dashStyle: "SOLID",
          },
      contentAlignment: "TOP",
    };
    this.requests.push({
      updateShapeProperties: {
        objectId,
        shapeProperties,
        fields: "shapeBackgroundFill,outline,contentAlignment",
      },
    });
    return objectId;
  }

  addText(pageId, text, position, options = {}) {
    const objectId = this.addShape(
      pageId,
      "TEXT_BOX",
      position,
      options.fill ?? "none",
      options.line ?? "none",
      options.role ?? "text",
    );
    this.requests.push({ insertText: { objectId, text, insertionIndex: 0 } });
    const rawSize = (options.fontSize ?? 22) * FONT_SCALE;
    const fontSize = options.allowSmall ? rawSize : Math.max(12, rawSize);
    this.requests.push({
      updateTextStyle: {
        objectId,
        textRange: { type: "ALL" },
        style: {
          fontFamily: options.fontFamily ?? "Arial",
          fontSize: { magnitude: fontSize, unit: "PT" },
          foregroundColor: { opaqueColor: { rgbColor: rgb(options.color ?? C.text) } },
          bold: options.bold ?? false,
        },
        fields: "fontFamily,fontSize,foregroundColor,bold",
      },
    });
    this.requests.push({
      updateParagraphStyle: {
        objectId,
        textRange: { type: "ALL" },
        style: {
          alignment: options.alignment === "center" ? "CENTER" : options.alignment === "right" ? "END" : "START",
          lineSpacing: 100,
          spaceAbove: { magnitude: 0, unit: "PT" },
          spaceBelow: { magnitude: 0, unit: "PT" },
        },
        fields: "alignment,lineSpacing,spaceAbove,spaceBelow",
      },
    });
    if (options.verticalAlignment === "middle") {
      this.requests.push({
        updateShapeProperties: {
          objectId,
          shapeProperties: { contentAlignment: "MIDDLE" },
          fields: "contentAlignment",
        },
      });
    }
    return objectId;
  }

  addRule(pageId, left, top, width, color = C.line, height = 2) {
    this.addShape(pageId, "RECTANGLE", { left, top, width, height }, color, "none", "rule");
  }

  addChrome(pageId, spec, index) {
    const isDeepDive = index > CORE_SLIDE_COUNT && index < 54;
    this.addText(pageId, spec.section ?? "LESSON 04", { left: 64, top: 34, width: 300, height: 28 }, {
      fontSize: 14,
      bold: true,
      color: isDeepDive ? C.blue : C.orange,
      allowSmall: true,
      role: "section",
    });
    this.addText(pageId, "DE / MENTOR", { left: 1040, top: 34, width: 176, height: 28 }, {
      fontSize: 13,
      bold: true,
      color: C.muted,
      alignment: "right",
      allowSmall: true,
      role: "brand",
    });
    this.addRule(pageId, 64, 68, 1152, C.line, 1);
    this.addText(pageId, String(index).padStart(2, "0"), { left: 1158, top: 674, width: 58, height: 22 }, {
      fontSize: 13,
      bold: true,
      color: C.muted,
      alignment: "right",
      allowSmall: true,
      role: "page_number",
    });
  }

  addTitle(pageId, title) {
    this.addText(pageId, title, { left: 64, top: 92, width: 1152, height: 96 }, {
      fontSize: 38,
      bold: true,
      role: "title",
    });
  }

  addBulletList(pageId, items, x, y, width, fontSize = 23, color = C.text, gap = 64) {
    items.forEach((item, index) => {
      this.addShape(pageId, "ELLIPSE", { left: x, top: y + index * gap + 9, width: 10, height: 10 }, C.orange, "none", "bullet");
      this.addText(pageId, item, { left: x + 28, top: y + index * gap, width: width - 28, height: gap - 4 }, {
        fontSize,
        color,
        role: "bullet_text",
      });
    });
  }

  renderTimeline(pageId, spec) {
    this.addTitle(pageId, spec.title);
    const count = spec.items.length;
    const width = count === 4 ? 258 : 344;
    const gap = count === 4 ? 28 : 44;
    this.addRule(pageId, 86, 310, 1080, C.line, 4);
    spec.items.forEach(([year, label, body], index) => {
      const left = 72 + index * (width + gap);
      this.addShape(pageId, "ELLIPSE", { left: left + 5, top: 294, width: 36, height: 36 }, index === count - 1 ? C.orange : C.blue, "none", "milestone");
      this.addText(pageId, year, { left, top: 226, width, height: 50 }, { fontSize: 29, bold: true, color: index === count - 1 ? C.orange : C.blue });
      this.addText(pageId, label, { left, top: 355, width, height: 64 }, { fontSize: 23, bold: true });
      this.addText(pageId, body, { left, top: 430, width, height: 105 }, { fontSize: 19, color: C.muted });
    });
  }

  renderMatrix(pageId, spec) {
    this.addTitle(pageId, spec.title);
    const x = 240;
    const columnWidth = 236;
    spec.columns.forEach((column, index) => {
      this.addText(pageId, column, { left: x + index * columnWidth, top: 218, width: columnWidth - 10, height: 42 }, {
        fontSize: 22,
        bold: true,
        color: index === 3 ? C.orange : C.blue,
        alignment: "center",
      });
    });
    spec.rows.forEach((row, rowIndex) => {
      const top = 282 + rowIndex * 72;
      this.addText(pageId, row[0], { left: 72, top, width: 150, height: 40 }, { fontSize: 20, bold: true });
      row.slice(1).forEach((value, columnIndex) => {
        this.addText(pageId, value, { left: x + columnIndex * columnWidth, top, width: columnWidth - 10, height: 52 }, {
          fontSize: 18,
          color: C.muted,
          alignment: "center",
        });
      });
      this.addRule(pageId, 72, top + 56, 1110, C.line, 1);
    });
  }

  renderGlossary(pageId, spec) {
    this.addTitle(pageId, spec.title);
    spec.terms.forEach(([term, meaning], index) => {
      const column = index % 2;
      const row = Math.floor(index / 2);
      const left = column === 0 ? 72 : 660;
      const top = 210 + row * 96;
      this.addText(pageId, term, { left, top, width: 200, height: 38 }, { fontSize: 24, bold: true, color: column === 0 ? C.blue : C.orange });
      this.addText(pageId, meaning, { left: left + 205, top: top + 2, width: 310, height: 58 }, { fontSize: 18, color: C.muted });
    });
  }

  renderOutcomes(pageId, spec) {
    this.addTitle(pageId, spec.title);
    spec.items.forEach(([number, label, body], index) => {
      const top = 218 + index * 102;
      this.addText(pageId, number, { left: 74, top, width: 70, height: 54 }, { fontSize: 35, bold: true, color: C.orange });
      this.addText(pageId, label, { left: 166, top, width: 220, height: 34 }, { fontSize: 25, bold: true });
      this.addText(pageId, body, { left: 420, top: top + 2, width: 720, height: 58 }, { fontSize: 22, color: C.muted });
      if (index < spec.items.length - 1) this.addRule(pageId, 166, top + 71, 974, C.line, 1);
    });
  }

  renderFlow(pageId, spec) {
    this.addTitle(pageId, spec.title);
    spec.items.forEach(([label, body], index) => {
      const left = 72 + index * 290;
      if (index < spec.items.length - 1) {
        this.addText(pageId, "→", { left: left + 235, top: 326, width: 55, height: 48 }, { fontSize: 36, bold: true, color: C.orange, alignment: "center" });
      }
      const terminal = index === spec.items.length - 1;
      this.addShape(pageId, "ROUND_RECTANGLE", { left, top: 260, width: 230, height: 180 }, terminal ? C.dark : C.panel, terminal ? "none" : C.line, "flow_card");
      this.addText(pageId, label, { left: left + 22, top: 302, width: 186, height: 45 }, { fontSize: 25, bold: true, color: terminal ? C.orange : C.text, alignment: "center" });
      this.addText(pageId, body, { left: left + 22, top: 365, width: 186, height: 52 }, { fontSize: 18, color: terminal ? C.panel : C.muted, alignment: "center" });
    });
    this.addText(pageId, spec.callout, { left: 100, top: 505, width: 1080, height: 70 }, { fontSize: 23, bold: true, color: C.orange, alignment: "center" });
  }

  renderArchitecture(pageId, spec) {
    this.addTitle(pageId, spec.title);
    this.addRule(pageId, 270, 341, 740, C.line, 4);
    [435, 692, 949].forEach((left) => this.addText(pageId, "→", { left, top: 314, width: 54, height: 50 }, { fontSize: 34, bold: true, color: C.orange, alignment: "center" }));
    spec.nodes.forEach(([label, body], index) => {
      const left = 72 + index * 290;
      this.addShape(pageId, "ROUND_RECTANGLE", { left, top: 245, width: 230, height: 190 }, index === 0 ? C.dark : C.panel, index === 0 ? "none" : C.line, "architecture_node");
      this.addText(pageId, label, { left: left + 24, top: 278, width: 182, height: 36 }, { fontSize: 23, bold: true, color: index === 0 ? C.orange : C.blue, alignment: "center" });
      this.addText(pageId, body, { left: left + 24, top: 338, width: 182, height: 70 }, { fontSize: 18, color: index === 0 ? C.panel : C.muted, alignment: "center" });
    });
    this.addText(pageId, spec.caption, { left: 105, top: 500, width: 1070, height: 70 }, { fontSize: 22, color: C.muted, alignment: "center" });
  }

  renderCompare(pageId, spec) {
    this.addTitle(pageId, spec.title);
    [spec.left, spec.right].forEach((column, index) => {
      const left = index === 0 ? 72 : 672;
      this.addText(pageId, column.label.toUpperCase(), { left, top: 222, width: 500, height: 30 }, { fontSize: 16, bold: true, color: index === 0 ? C.muted : C.orange, allowSmall: true });
      this.addText(pageId, column.headline, { left, top: 278, width: 500, height: 92 }, { fontSize: 31, bold: true });
      this.addBulletList(pageId, column.bullets, left, 397, 500, 21, C.text, 62);
    });
    this.addRule(pageId, 632, 214, 2, C.line, 390);
  }

  renderChecklist(pageId, spec) {
    this.addTitle(pageId, spec.title);
    spec.groups.forEach(([label, body], index) => {
      const top = 210 + index * 82;
      this.addShape(pageId, "ELLIPSE", { left: 72, top: top + 6, width: 30, height: 30 }, index < 4 ? C.green : C.orange, "none", "check_circle");
      this.addText(pageId, "✓", { left: 72, top: top + 4, width: 30, height: 30 }, { fontSize: 18, bold: true, color: C.panel, alignment: "center" });
      this.addText(pageId, label, { left: 132, top, width: 230, height: 38 }, { fontSize: 25, bold: true });
      this.addText(pageId, body, { left: 390, top: top + 2, width: 760, height: 38 }, { fontSize: 21, color: C.muted });
      this.addRule(pageId, 132, top + 56, 1018, C.line, 1);
    });
  }

  renderLayers(pageId, spec) {
    this.addTitle(pageId, spec.title);
    spec.rows.forEach(([label, example, meaning], index) => {
      const top = 220 + index * 94;
      this.addText(pageId, label, { left: 72, top, width: 185, height: 52 }, { fontSize: 25, bold: true, color: index === spec.rows.length - 1 ? C.orange : C.blue });
      this.addText(pageId, example, { left: 286, top, width: 430, height: 52 }, { fontSize: 22, bold: true });
      this.addText(pageId, meaning, { left: 760, top, width: 400, height: 52 }, { fontSize: 20, color: C.muted });
      this.addRule(pageId, 72, top + 66, 1088, C.line, 1);
    });
  }

  renderArchitectureCompare(pageId, spec) {
    this.addTitle(pageId, spec.title);
    [spec.left, spec.right].forEach((column, columnIndex) => {
      const left = columnIndex === 0 ? 72 : 672;
      this.addText(pageId, column.label.toUpperCase(), { left, top: 208, width: 500, height: 28 }, { fontSize: 16, bold: true, color: columnIndex === 0 ? C.muted : C.orange, allowSmall: true });
      for (let index = 0; index < column.nodes.length - 1; index += 1) {
        this.addText(pageId, "↓", { left: left + 220, top: 304 + index * 80, width: 60, height: 30 }, { fontSize: 22, bold: true, color: C.orange, alignment: "center" });
      }
      column.nodes.forEach(([label, body], index) => {
        const top = 246 + index * 80;
        const terminal = index === column.nodes.length - 1;
        this.addShape(pageId, "ROUND_RECTANGLE", { left, top, width: 500, height: 62 }, terminal ? C.dark : C.panel, terminal ? "none" : C.line, "architecture_compare_node");
        this.addText(pageId, label, { left: left + 22, top: top + 16, width: 190, height: 30 }, { fontSize: 20, bold: true, color: terminal ? C.orange : C.text });
        this.addText(pageId, body, { left: left + 220, top: top + 16, width: 255, height: 30 }, { fontSize: 17, color: terminal ? C.panel : C.muted, alignment: "right" });
      });
    });
    this.addRule(pageId, 632, 205, 2, C.line, 380);
    this.addText(pageId, spec.callout, { left: 96, top: 590, width: 1088, height: 52 }, { fontSize: 20, bold: true, color: C.orange, alignment: "center" });
  }

  renderPipelineCompare(pageId, spec) {
    this.addTitle(pageId, spec.title);
    [spec.left, spec.right].forEach((lane, laneIndex) => {
      const top = laneIndex === 0 ? 256 : 438;
      const darkTokens = new Set(["HDFS", "shuffle"]);
      this.addText(pageId, lane.label.toUpperCase(), { left: 72, top: top - 48, width: 420, height: 30 }, { fontSize: 17, bold: true, color: laneIndex === 0 ? C.muted : C.orange });
      lane.steps.forEach((step, index) => {
        const left = 72 + index * 158;
        if (index < lane.steps.length - 1) this.addText(pageId, "→", { left: left + 112, top: top + 20, width: 46, height: 34 }, { fontSize: 24, bold: true, color: C.orange, alignment: "center" });
        const highlighted = darkTokens.has(step);
        this.addShape(pageId, "ROUND_RECTANGLE", { left, top, width: 112, height: 70 }, highlighted ? C.dark : C.panel, highlighted ? "none" : C.line, "pipeline_node");
        this.addText(pageId, step, { left: left + 8, top: top + 21, width: 96, height: 30 }, { fontSize: 16, bold: true, color: highlighted ? C.orange : C.text, alignment: "center", allowSmall: true });
      });
      this.addText(pageId, lane.note, { left: 72, top: top + 86, width: 1100, height: 34 }, { fontSize: 17, color: C.muted });
    });
    this.addText(pageId, spec.callout, { left: 96, top: 610, width: 1088, height: 42 }, { fontSize: 20, bold: true, color: C.orange, alignment: "center" });
  }

  renderComparisonMatrix(pageId, spec) {
    this.addTitle(pageId, spec.title);
    const columnX = [300, 560, 820];
    const columnWidth = [240, 240, 360];
    spec.columns.forEach((column, index) => {
      this.addText(pageId, column, { left: columnX[index], top: 210, width: columnWidth[index] - 12, height: 40 }, { fontSize: 19, bold: true, color: index === 2 ? C.orange : C.blue, alignment: "center" });
    });
    spec.rows.forEach((row, rowIndex) => {
      const top = 265 + rowIndex * 58;
      if (rowIndex % 2 === 0) this.addShape(pageId, "RECTANGLE", { left: 64, top: top - 3, width: 1120, height: 53 }, C.panel2, "none", "matrix_band");
      this.addText(pageId, row[0], { left: 72, top: top + 7, width: 210, height: 38 }, { fontSize: 17, bold: true });
      row.slice(1).forEach((value, columnIndex) => {
        this.addText(pageId, value, { left: columnX[columnIndex], top: top + 4, width: columnWidth[columnIndex] - 12, height: 44 }, { fontSize: 16, color: columnIndex === 2 ? C.text : C.muted, alignment: "center", verticalAlignment: "middle" });
      });
      this.addRule(pageId, 64, top + 51, 1120, C.line, 1);
    });
  }

  renderSources(pageId, spec) {
    this.addTitle(pageId, spec.title);
    this.addText(pageId, "EVIDENCE CHAIN", { left: 72, top: 214, width: 430, height: 32 }, { fontSize: 16, bold: true, color: C.orange, allowSmall: true });
    this.addBulletList(pageId, spec.actions, 72, 280, 600, 22, C.text, 70);
    this.addText(pageId, "МАТЕРИАЛЫ", { left: 742, top: 214, width: 430, height: 32 }, { fontSize: 16, bold: true, color: C.blue, allowSmall: true });
    spec.links.forEach(([label, link], index) => {
      const top = 280 + index * 78;
      this.addText(pageId, label, { left: 742, top, width: 420, height: 32 }, { fontSize: 22, bold: true });
      this.addText(pageId, link, { left: 742, top: top + 35, width: 420, height: 30 }, { fontSize: 16, color: C.muted, allowSmall: true });
    });
  }

  render(pageId, spec, index) {
    this.addSlide(pageId);
    this.addChrome(pageId, spec, index);
    const renderers = {
      timeline: this.renderTimeline,
      matrix: this.renderMatrix,
      glossary: this.renderGlossary,
      outcomes: this.renderOutcomes,
      flow: this.renderFlow,
      architecture: this.renderArchitecture,
      compare: this.renderCompare,
      checklist: this.renderChecklist,
      layers: this.renderLayers,
      architectureCompare: this.renderArchitectureCompare,
      pipelineCompare: this.renderPipelineCompare,
      comparisonMatrix: this.renderComparisonMatrix,
      sources: this.renderSources,
    };
    const renderer = renderers[spec.type];
    if (!renderer) throw new Error(`No native Google Slides renderer for ${spec.type}`);
    renderer.call(this, pageId, spec);
  }
}

function renumberExistingSlides(rawPresentation, deliveredSlideIds) {
  const slideById = new Map(rawPresentation.slides.map((slide) => [slide.objectId, slide]));
  const requests = [];
  deliveredSlideIds.forEach((slideId, index) => {
    if (!/^p\d+$/.test(slideId) || ["p1", "p27", "p37"].includes(slideId)) return;
    const slide = slideById.get(slideId);
    if (!slide) throw new Error(`Existing slide not found: ${slideId}`);
    const oldNumber = Number.parseInt(slideId.slice(1), 10);
    const pageNumber = slide.pageElements.find((element) => textOf(element) === String(oldNumber).padStart(2, "0"));
    if (!pageNumber) throw new Error(`Page number shape not found on ${slideId}`);
    const nextNumber = String(index + 1).padStart(2, "0");
    requests.push(
      { deleteText: { objectId: pageNumber.objectId, textRange: { type: "ALL" } } },
      { insertText: { objectId: pageNumber.objectId, text: nextNumber, insertionIndex: 0 } },
      {
        updateTextStyle: {
          objectId: pageNumber.objectId,
          textRange: { type: "ALL" },
          style: {
            fontFamily: "Arial",
            fontSize: { magnitude: 9.75, unit: "PT" },
            foregroundColor: { opaqueColor: { rgbColor: rgb(C.muted) } },
            bold: true,
          },
          fields: "fontFamily,fontSize,foregroundColor,bold",
        },
      },
      {
        updateParagraphStyle: {
          objectId: pageNumber.objectId,
          textRange: { type: "ALL" },
          style: { alignment: "END" },
          fields: "alignment",
        },
      },
    );
  });
  return requests;
}

function chunkRequests(requests, chunkSize = 180) {
  const chunks = [];
  for (let index = 0; index < requests.length; index += chunkSize) {
    chunks.push(requests.slice(index, index + chunkSize));
  }
  return chunks;
}

function main() {
  const [rawTemplatePath, outputPath] = process.argv.slice(2);
  if (!rawTemplatePath || !outputPath) {
    throw new Error("Usage: build_google_slides_requests.mjs <raw-template.json> <output.json>");
  }
  const wrapper = JSON.parse(fs.readFileSync(rawTemplatePath, "utf8"));
  const presentation = wrapper.structuredContent;
  if (!presentation?.slides || !presentation?.layouts) throw new Error("Invalid raw presentation wrapper");
  const layoutId = presentation.layouts[0]?.objectId;
  if (!layoutId) throw new Error("No layout available in source presentation");

  const builder = new NativeSlidesBuilder({ layoutId });
  const newSlideNumbers = [
    ...Array.from({ length: 12 }, (_, index) => index + 5),
    ...Array.from({ length: 8 }, (_, index) => index + 37),
    59,
  ];
  const newSlideIds = new Map(newSlideNumbers.map((number) => [number, `spark60_s${String(number).padStart(2, "0")}`]));
  newSlideNumbers.forEach((number) => builder.render(newSlideIds.get(number), SLIDES[number - 1], number));

  const deliveredSlideIds = [
    "p1", "p2", "p3", "p4",
    ...Array.from({ length: 12 }, (_, index) => newSlideIds.get(index + 5)),
    ...Array.from({ length: 19 }, (_, index) => `p${index + 8}`),
    "p27",
    ...Array.from({ length: 8 }, (_, index) => newSlideIds.get(index + 37)),
    ...Array.from({ length: 9 }, (_, index) => `p${index + 28}`),
    ...Array.from({ length: 5 }, (_, index) => `p${index + 37}`),
    newSlideIds.get(59),
    "p42",
  ];
  if (deliveredSlideIds.length !== 60 || new Set(deliveredSlideIds).size !== 60) {
    throw new Error("Delivered slide order must contain exactly 60 unique IDs");
  }

  const compatibilityRequests = [
    ...renumberExistingSlides(presentation, deliveredSlideIds),
    {
      replaceAllText: {
        containsText: {
          text: "Разбираем Catalyst, shuffle, Python/JVM boundary, AQE и skew",
          matchCase: true,
        },
        replaceText: "Spark vs MapReduce на principal-уровне, затем Catalyst, shuffle, Python/JVM boundary, AQE и skew",
        pageObjectIds: ["p27"],
      },
    },
  ];
  const creationRequests = [...builder.requests, ...compatibilityRequests];
  const output = {
    migration: "lesson-04-google-slides-42-to-60",
    presentationId: presentation.presentationId,
    sourceRevisionId: presentation.revisionId,
    createdSlideIds: [...newSlideIds.values()],
    deliveredSlideIds,
    creationChunks: chunkRequests(creationRequests),
    positionBatches: [
      [{
        updateSlidesPosition: {
          slideObjectIds: Array.from({ length: 12 }, (_, index) => newSlideIds.get(index + 5)),
          insertionIndex: 4,
        },
      }],
      [{
        updateSlidesPosition: {
          slideObjectIds: Array.from({ length: 8 }, (_, index) => newSlideIds.get(index + 37)),
          insertionIndex: 39,
        },
      }],
      [{
        updateSlidesPosition: {
          slideObjectIds: [newSlideIds.get(59)],
          insertionIndex: 61,
        },
      }],
    ],
    deleteRequests: ["p5", "p6", "p7"].map((objectId) => ({ deleteObject: { objectId } })),
  };
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`);
  console.log(JSON.stringify({
    outputPath,
    newSlides: newSlideNumbers.length,
    deliveredSlides: deliveredSlideIds.length,
    creationRequests: creationRequests.length,
    creationChunks: output.creationChunks.length,
  }, null, 2));
}

main();
