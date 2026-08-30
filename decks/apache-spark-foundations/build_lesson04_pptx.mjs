import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { CORE_SLIDE_COUNT, FULL_SLIDE_COUNT, SLIDES } from "./content.mjs";

const SIZE = { width: 1280, height: 720 };
const C = {
  bg: "#F7F7F4",
  panel: "#FFFFFF",
  panel2: "#EFEEE8",
  text: "#202123",
  muted: "#6E6E68",
  line: "#D8D7D0",
  green: "#10A37F",
  blue: "#2F6FED",
  amber: "#B7791F",
  red: "#B42318",
  orange: "#E25A1C",
  dark: "#1F2428",
};
const FONT = "Aptos";
const MONO = "Aptos Mono";
const APPENDIX_SLIDE_NUMBER = SLIDES.findIndex((spec) => spec.section === "APPENDIX") + 1;

function addShape(slide, geometry, position, fill = "none", line = "none", name = undefined) {
  return slide.shapes.add({
    geometry,
    name,
    position,
    fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 },
  });
}

function addText(slide, text, position, options = {}) {
  const shape = addShape(slide, "textbox", position, options.fill ?? "none", options.line ?? "none", options.name);
  shape.text = text;
  shape.text.style = {
    fontFamily: options.fontFamily ?? FONT,
    fontSize: options.fontSize ?? 22,
    color: options.color ?? C.text,
    bold: options.bold ?? false,
    alignment: options.alignment ?? "left",
    verticalAlignment: options.verticalAlignment ?? "top",
    wrap: true,
  };
  return shape;
}

function addRule(slide, left, top, width, color = C.line, height = 2) {
  return addShape(slide, "rect", { left, top, width, height }, color, "none");
}

function addChrome(slide, spec, index) {
  const isDeepDive = index > CORE_SLIDE_COUNT && index < APPENDIX_SLIDE_NUMBER;
  addText(slide, spec.section ?? "LESSON 04", { left: 64, top: 34, width: 300, height: 28 }, {
    fontSize: 14, bold: true, color: isDeepDive ? C.blue : C.orange,
  });
  addText(slide, "DE / MENTOR", { left: 1040, top: 34, width: 176, height: 28 }, {
    fontSize: 13, bold: true, color: C.muted, alignment: "right",
  });
  addRule(slide, 64, 68, 1152, C.line, 1);
  addText(slide, String(index).padStart(2, "0"), { left: 1158, top: 674, width: 58, height: 22 }, {
    fontSize: 13, bold: true, color: C.muted, alignment: "right",
  });
}

function addTitle(slide, title) {
  addText(slide, title, { left: 64, top: 92, width: 1152, height: 96 }, {
    fontSize: 38, bold: true, color: C.text,
  });
}

function addNotes(slide, spec, index) {
  const sources = spec.sources?.length ? spec.sources.map((source) => `- ${source}`).join("\n") : "- No external sources; original instructional synthesis.";
  const notes = `Slide ${index}. ${spec.title}\n\nFacilitator cue: ask learners to explain the slide in their own words before revealing the next one.\n\n[Sources]\n${sources}\n[/Sources]`;
  slide.speakerNotes.textFrame.setText(notes);
  slide.speakerNotes.setVisible(true);
}

function addBulletList(slide, items, x, y, width, fontSize = 23, color = C.text, gap = 64) {
  items.forEach((item, i) => {
    addShape(slide, "ellipse", { left: x, top: y + i * gap + 9, width: 10, height: 10 }, C.orange, "none");
    addText(slide, item, { left: x + 28, top: y + i * gap, width: width - 28, height: gap - 4 }, { fontSize, color });
  });
}

function renderHero(slide, spec) {
  addShape(slide, "rect", { left: 0, top: 0, width: 1280, height: 720 }, C.dark, "none");
  addShape(slide, "rect", { left: 0, top: 0, width: 20, height: 720 }, C.orange, "none");
  addText(slide, spec.section, { left: 72, top: 70, width: 400, height: 30 }, { fontSize: 16, bold: true, color: C.orange });
  addText(slide, spec.title, { left: 72, top: 176, width: 870, height: 230 }, { fontSize: 62, bold: true, color: C.panel });
  addText(slide, spec.subtitle, { left: 76, top: 438, width: 800, height: 70 }, { fontSize: 25, color: "#D6D9DC" });
  addRule(slide, 76, 550, 160, C.orange, 5);
  addText(slide, spec.meta, { left: 76, top: 580, width: 650, height: 34 }, { fontSize: 18, bold: true, color: "#D6D9DC" });
  addText(slide, "PYSPARK", { left: 956, top: 564, width: 230, height: 60 }, { fontSize: 28, bold: true, color: C.orange, alignment: "right" });
}

function renderIncident(slide, spec) {
  addTitle(slide, spec.title);
  addText(slide, spec.lead, { left: 64, top: 205, width: 690, height: 60 }, { fontSize: 31, bold: true, color: C.red });
  addBulletList(slide, spec.bullets, 72, 300, 690, 24, C.text, 72);
  addShape(slide, "roundRect", { left: 800, top: 208, width: 386, height: 338 }, C.dark, "none");
  addText(slide, "SLA", { left: 840, top: 245, width: 150, height: 58 }, { fontSize: 46, bold: true, color: C.panel });
  addText(slide, "18 min", { left: 840, top: 325, width: 290, height: 85 }, { fontSize: 58, bold: true, color: C.orange });
  addText(slide, spec.callout, { left: 840, top: 430, width: 300, height: 92 }, { fontSize: 21, color: "#E5E7EB" });
}

function renderOutcomes(slide, spec) {
  addTitle(slide, spec.title);
  spec.items.forEach(([number, label, body], i) => {
    const y = 218 + i * 102;
    addText(slide, number, { left: 74, top: y, width: 70, height: 54 }, { fontSize: 35, bold: true, color: C.orange });
    addText(slide, label, { left: 166, top: y, width: 220, height: 34 }, { fontSize: 25, bold: true });
    addText(slide, body, { left: 420, top: y + 2, width: 720, height: 58 }, { fontSize: 22, color: C.muted });
    if (i < spec.items.length - 1) addRule(slide, 166, y + 71, 974, C.line, 1);
  });
}

function renderStatement(slide, spec) {
  addTitle(slide, spec.title);
  addText(slide, `“${spec.statement}”`, { left: 72, top: 220, width: 1050, height: 164 }, { fontSize: 37, bold: true, color: C.dark });
  addRule(slide, 72, 410, 150, C.orange, 5);
  spec.axes.forEach((axis, i) => {
    const left = 72 + i * 218;
    addText(slide, axis.toUpperCase(), { left, top: 452, width: 190, height: 36 }, { fontSize: 17, bold: true, color: i === 0 ? C.orange : C.muted });
  });
  addText(slide, spec.footerNote, { left: 72, top: 544, width: 950, height: 58 }, { fontSize: 22, color: C.muted });
}

function renderTimeline(slide, spec) {
  addTitle(slide, spec.title);
  const count = spec.items.length;
  const width = count === 4 ? 258 : 344;
  const gap = count === 4 ? 28 : 44;
  addRule(slide, 86, 310, 1080, C.line, 4);
  spec.items.forEach(([year, label, body], i) => {
    const left = 72 + i * (width + gap);
    addShape(slide, "ellipse", { left: left + 5, top: 294, width: 36, height: 36 }, i === count - 1 ? C.orange : C.blue, "none");
    addText(slide, year, { left, top: 226, width, height: 50 }, { fontSize: 29, bold: true, color: i === count - 1 ? C.orange : C.blue });
    addText(slide, label, { left, top: 355, width, height: 64 }, { fontSize: 23, bold: true });
    addText(slide, body, { left, top: 430, width, height: 105 }, { fontSize: 19, color: C.muted });
  });
}

function renderCompare(slide, spec) {
  addTitle(slide, spec.title);
  [spec.left, spec.right].forEach((column, i) => {
    const left = i === 0 ? 72 : 672;
    addText(slide, column.label.toUpperCase(), { left, top: 222, width: 500, height: 30 }, { fontSize: 16, bold: true, color: i === 0 ? C.muted : C.orange });
    addText(slide, column.headline, { left, top: 278, width: 500, height: 92 }, { fontSize: 31, bold: true, color: C.dark });
    addBulletList(slide, column.bullets, left, 397, 500, 21, C.text, 62);
  });
  addRule(slide, 632, 214, 2, C.line, 390);
}

function renderBoundary(slide, spec) {
  addTitle(slide, spec.title);
  addText(slide, "ENGINE", { left: 72, top: 218, width: 500, height: 32 }, { fontSize: 17, bold: true, color: C.green });
  addText(slide, "НЕ ENGINE", { left: 672, top: 218, width: 500, height: 32 }, { fontSize: 17, bold: true, color: C.red });
  addRule(slide, 632, 215, 2, C.line, 390);
  addBulletList(slide, spec.inside, 72, 282, 500, 23, C.text, 70);
  addBulletList(slide, spec.outside, 672, 282, 500, 23, C.text, 70);
}

function renderDecision(slide, spec) {
  addTitle(slide, spec.title);
  addText(slide, spec.question, { left: 170, top: 220, width: 940, height: 70 }, { fontSize: 30, bold: true, alignment: "center" });
  spec.paths.forEach(([answer, headline, body], i) => {
    const left = i === 0 ? 110 : 670;
    addShape(slide, "roundRect", { left, top: 340, width: 500, height: 220 }, i === 0 ? C.panel2 : C.dark, i === 0 ? C.line : "none");
    addText(slide, answer.toUpperCase(), { left: left + 34, top: 370, width: 430, height: 28 }, { fontSize: 16, bold: true, color: i === 0 ? C.muted : C.orange });
    addText(slide, headline, { left: left + 34, top: 420, width: 430, height: 54 }, { fontSize: 28, bold: true, color: i === 0 ? C.text : C.panel });
    addText(slide, body, { left: left + 34, top: 490, width: 430, height: 54 }, { fontSize: 19, color: i === 0 ? C.muted : "#D6D9DC" });
  });
}

function renderArchitecture(slide, spec) {
  addTitle(slide, spec.title);
  addRule(slide, 270, 341, 740, C.line, 4);
  addText(slide, "→", { left: 435, top: 314, width: 54, height: 50 }, { fontSize: 34, bold: true, color: C.orange, alignment: "center" });
  addText(slide, "→", { left: 692, top: 314, width: 54, height: 50 }, { fontSize: 34, bold: true, color: C.orange, alignment: "center" });
  addText(slide, "→", { left: 949, top: 314, width: 54, height: 50 }, { fontSize: 34, bold: true, color: C.orange, alignment: "center" });
  spec.nodes.forEach(([label, body], i) => {
    const left = 72 + i * 290;
    addShape(slide, "roundRect", { left, top: 245, width: 230, height: 190 }, i === 0 ? C.dark : C.panel, i === 0 ? "none" : C.line);
    addText(slide, label, { left: left + 24, top: 278, width: 182, height: 36 }, { fontSize: 23, bold: true, color: i === 0 ? C.orange : C.blue, alignment: "center" });
    addText(slide, body, { left: left + 24, top: 338, width: 182, height: 70 }, { fontSize: 18, color: i === 0 ? C.panel : C.muted, alignment: "center" });
  });
  addText(slide, spec.caption, { left: 105, top: 500, width: 1070, height: 70 }, { fontSize: 22, color: C.muted, alignment: "center" });
}

function renderArchitectureCompare(slide, spec) {
  addTitle(slide, spec.title);
  [spec.left, spec.right].forEach((column, columnIndex) => {
    const left = columnIndex === 0 ? 72 : 672;
    const accent = columnIndex === 0 ? C.muted : C.orange;
    addText(slide, column.label.toUpperCase(), { left, top: 208, width: 500, height: 28 }, {
      fontSize: 16, bold: true, color: accent,
    });
    for (let i = 0; i < column.nodes.length - 1; i += 1) {
      addText(slide, "↓", { left: left + 220, top: 304 + i * 80, width: 60, height: 30 }, {
        fontSize: 22, bold: true, color: C.orange, alignment: "center",
      });
    }
    column.nodes.forEach(([label, body], i) => {
      const top = 246 + i * 80;
      const isTerminal = i === column.nodes.length - 1;
      addShape(slide, "roundRect", { left, top, width: 500, height: 62 }, isTerminal ? C.dark : C.panel, isTerminal ? "none" : C.line);
      addText(slide, label, { left: left + 22, top: top + 16, width: 190, height: 30 }, {
        fontSize: 20, bold: true, color: isTerminal ? C.orange : C.text,
      });
      addText(slide, body, { left: left + 220, top: top + 16, width: 255, height: 30 }, {
        fontSize: 17, color: isTerminal ? C.panel : C.muted, alignment: "right",
      });
    });
  });
  addRule(slide, 632, 205, 2, C.line, 380);
  addText(slide, spec.callout, { left: 96, top: 590, width: 1088, height: 52 }, {
    fontSize: 20, bold: true, color: C.orange, alignment: "center",
  });
}

function renderPipelineCompare(slide, spec) {
  addTitle(slide, spec.title);
  [spec.left, spec.right].forEach((lane, laneIndex) => {
    const top = laneIndex === 0 ? 256 : 438;
    const darkTokens = new Set(["HDFS", "shuffle"]);
    addText(slide, lane.label.toUpperCase(), { left: 72, top: top - 48, width: 420, height: 30 }, {
      fontSize: 17, bold: true, color: laneIndex === 0 ? C.muted : C.orange,
    });
    lane.steps.forEach((step, i) => {
      const left = 72 + i * 158;
      if (i < lane.steps.length - 1) {
        addText(slide, "→", { left: left + 112, top: top + 20, width: 46, height: 34 }, {
          fontSize: 24, bold: true, color: C.orange, alignment: "center",
        });
      }
      const highlighted = darkTokens.has(step);
      addShape(slide, "roundRect", { left, top, width: 112, height: 70 }, highlighted ? C.dark : C.panel, highlighted ? "none" : C.line);
      addText(slide, step, { left: left + 8, top: top + 21, width: 96, height: 30 }, {
        fontSize: 16, bold: true, color: highlighted ? C.orange : C.text, alignment: "center",
      });
    });
    addText(slide, lane.note, { left: 72, top: top + 86, width: 1100, height: 34 }, {
      fontSize: 17, color: C.muted,
    });
  });
  addText(slide, spec.callout, { left: 96, top: 610, width: 1088, height: 42 }, {
    fontSize: 20, bold: true, color: C.orange, alignment: "center",
  });
}

function renderPartition(slide, spec) {
  addTitle(slide, spec.title);
  spec.partitions.forEach((partition, i) => {
    const left = 72 + i * 136;
    addShape(slide, "roundRect", { left, top: 240, width: 110, height: 76 }, i % 2 === 0 ? C.orange : C.blue, "none");
    addText(slide, partition, { left, top: 259, width: 110, height: 34 }, { fontSize: 22, bold: true, color: C.panel, alignment: "center" });
  });
  spec.workers.forEach((worker, i) => {
    const left = 92 + i * 278;
    addText(slide, "↓", { left, top: 330, width: 72, height: 48 }, { fontSize: 30, color: C.muted, alignment: "center" });
    addShape(slide, "roundRect", { left, top: 395, width: 236, height: 88 }, C.panel, C.line);
    addText(slide, worker, { left, top: 423, width: 236, height: 32 }, { fontSize: 22, bold: true, alignment: "center" });
  });
  addText(slide, spec.rule, { left: 98, top: 545, width: 1084, height: 58 }, { fontSize: 22, bold: true, color: C.orange, alignment: "center" });
}

function renderFlow(slide, spec) {
  addTitle(slide, spec.title);
  spec.items.forEach(([label, body], i) => {
    const left = 72 + i * 290;
    if (i < spec.items.length - 1) addText(slide, "→", { left: left + 235, top: 326, width: 55, height: 48 }, { fontSize: 36, bold: true, color: C.orange, alignment: "center" });
    addShape(slide, "roundRect", { left, top: 260, width: 230, height: 180 }, i === spec.items.length - 1 ? C.dark : C.panel, i === spec.items.length - 1 ? "none" : C.line);
    addText(slide, label, { left: left + 22, top: 302, width: 186, height: 45 }, { fontSize: 25, bold: true, color: i === spec.items.length - 1 ? C.orange : C.text, alignment: "center" });
    addText(slide, body, { left: left + 22, top: 365, width: 186, height: 52 }, { fontSize: 18, color: i === spec.items.length - 1 ? C.panel : C.muted, alignment: "center" });
  });
  addText(slide, spec.callout, { left: 100, top: 505, width: 1080, height: 70 }, { fontSize: 23, bold: true, color: C.orange, alignment: "center" });
}

function renderLayers(slide, spec) {
  addTitle(slide, spec.title);
  spec.rows.forEach(([label, example, meaning], i) => {
    const y = 220 + i * 94;
    addText(slide, label, { left: 72, top: y, width: 185, height: 52 }, { fontSize: 25, bold: true, color: i === spec.rows.length - 1 ? C.orange : C.blue });
    addText(slide, example, { left: 286, top: y, width: 430, height: 52 }, { fontSize: 22, bold: true });
    addText(slide, meaning, { left: 760, top: y, width: 400, height: 52 }, { fontSize: 20, color: C.muted });
    addRule(slide, 72, y + 66, 1088, C.line, 1);
  });
}

function renderShuffle(slide, spec) {
  addTitle(slide, spec.title);
  spec.before.forEach((item, i) => {
    const y = 226 + i * 72;
    addShape(slide, "roundRect", { left: 72, top: y, width: 250, height: 52 }, C.panel, C.line);
    addText(slide, item, { left: 92, top: y + 10, width: 210, height: 30 }, { fontSize: 19, bold: true });
  });
  addText(slide, "SHUFFLE", { left: 470, top: 292, width: 300, height: 70 }, { fontSize: 38, bold: true, color: C.orange, alignment: "center" });
  addText(slide, spec.triggers.join("  ·  "), { left: 394, top: 380, width: 450, height: 60 }, { fontSize: 18, color: C.muted, alignment: "center" });
  spec.after.forEach((item, i) => {
    const y = 226 + i * (288 / Math.max(1, spec.after.length - 1));
    addShape(slide, "roundRect", { left: 920, top: y, width: 250, height: 52 }, C.dark, "none");
    addText(slide, item, { left: 940, top: y + 10, width: 210, height: 30 }, { fontSize: 19, bold: true, color: C.panel });
  });
  addText(slide, spec.warning, { left: 150, top: 574, width: 980, height: 50 }, { fontSize: 22, bold: true, color: C.red, alignment: "center" });
}

function renderCase(slide, spec) {
  addTitle(slide, spec.title);
  const blocks = [
    ["INPUT", spec.input, 72, C.panel],
    ["OUTPUT", spec.output, 468, C.dark],
    ["CONSTRAINTS", spec.constraints, 864, C.panel2],
  ];
  blocks.forEach(([label, items, left, fill], i) => {
    addShape(slide, "roundRect", { left, top: 232, width: 340, height: 310 }, fill, fill === C.panel ? C.line : "none");
    addText(slide, label, { left: left + 28, top: 265, width: 284, height: 30 }, { fontSize: 16, bold: true, color: i === 1 ? C.orange : C.muted });
    addText(slide, items.join("\n\n"), { left: left + 28, top: 330, width: 284, height: 182 }, { fontSize: 21, bold: i === 1, color: i === 1 ? C.panel : C.text, alignment: "left" });
  });
}

function renderCode(slide, spec) {
  addTitle(slide, spec.title);
  addShape(slide, "roundRect", { left: 64, top: 210, width: 755, height: 390 }, C.dark, "none");
  addText(slide, spec.code, { left: 92, top: 238, width: 700, height: 340 }, { fontSize: 17, fontFamily: MONO, color: "#E6EDF3" });
  addText(slide, "WHY", { left: 870, top: 226, width: 290, height: 30 }, { fontSize: 16, bold: true, color: C.orange });
  addBulletList(slide, spec.takeaways, 870, 290, 320, 20, C.text, 86);
}

function renderEvidence(slide, spec) {
  addTitle(slide, spec.title);
  spec.steps.forEach(([number, action, evidence], i) => {
    const left = 64 + i * 292;
    const numbered = /^\d+$/.test(number);
    addText(slide, number, { left, top: 224, width: numbered ? 80 : 248, height: 62 }, {
      fontSize: numbered ? 42 : 26, bold: true, color: C.orange,
    });
    addText(slide, action, { left, top: 320, width: 248, height: 92 }, { fontSize: numbered ? 21 : 24, bold: true });
    addRule(slide, left, 438, 190, i === spec.steps.length - 1 ? C.orange : C.line, 4);
    addText(slide, evidence, { left, top: 478, width: 248, height: 92 }, { fontSize: 20, color: C.muted });
  });
}

function renderPlan(slide, spec) {
  addTitle(slide, spec.title);
  addShape(slide, "roundRect", { left: 64, top: 210, width: 760, height: 375 }, C.dark, "none");
  addText(slide, spec.code, { left: 90, top: 238, width: 708, height: 320 }, { fontSize: 17, fontFamily: MONO, color: "#E6EDF3" });
  spec.highlights.forEach((item, i) => {
    addText(slide, item, { left: 870, top: 238 + i * 78, width: 300, height: 52 }, { fontSize: 24, bold: true, color: i === 0 ? C.orange : C.blue });
  });
  addText(slide, spec.interpretation, { left: 870, top: 488, width: 310, height: 100 }, { fontSize: 20, color: C.muted });
}

function renderUi(slide, spec) {
  addTitle(slide, spec.title);
  spec.tabs.forEach(([label, body], i) => {
    const left = 72 + i * 286;
    addShape(slide, "roundRect", { left, top: 242, width: 250, height: 250 }, i === 2 ? C.dark : C.panel, i === 2 ? "none" : C.line);
    addText(slide, label, { left: left + 26, top: 282, width: 198, height: 44 }, { fontSize: 27, bold: true, color: i === 2 ? C.orange : C.blue, alignment: "center" });
    addText(slide, body, { left: left + 26, top: 360, width: 198, height: 95 }, { fontSize: 20, color: i === 2 ? C.panel : C.muted, alignment: "center" });
  });
  addText(slide, spec.callout, { left: 120, top: 545, width: 1040, height: 54 }, { fontSize: 22, bold: true, color: C.orange, alignment: "center" });
}

function renderExit(slide, spec) {
  addTitle(slide, spec.title);
  spec.questions.forEach((question, i) => {
    const left = i % 2 === 0 ? 72 : 652;
    const top = i < 2 ? 225 : 390;
    addText(slide, `0${i + 1}`, { left, top, width: 70, height: 48 }, { fontSize: 31, bold: true, color: C.orange });
    addText(slide, question, { left: left + 82, top, width: 450, height: 95 }, { fontSize: 23, bold: true });
  });
  addShape(slide, "roundRect", { left: 115, top: 565, width: 1050, height: 60 }, C.dark, "none");
  addText(slide, spec.next, { left: 145, top: 581, width: 990, height: 32 }, { fontSize: 19, bold: true, color: C.panel, alignment: "center" });
}

function renderDivider(slide, spec) {
  addShape(slide, "rect", { left: 0, top: 0, width: 1280, height: 720 }, C.dark, "none");
  addText(slide, spec.section, { left: 72, top: 90, width: 500, height: 36 }, { fontSize: 17, bold: true, color: C.orange });
  addRule(slide, 72, 180, 165, C.orange, 5);
  addText(slide, spec.title, { left: 72, top: 244, width: 1000, height: 135 }, { fontSize: 58, bold: true, color: C.panel });
  addText(slide, spec.subtitle, { left: 76, top: 430, width: 850, height: 80 }, { fontSize: 25, color: "#D6D9DC" });
}

function renderChecklist(slide, spec) {
  addTitle(slide, spec.title);
  spec.groups.forEach(([label, body], i) => {
    const y = 210 + i * 82;
    addShape(slide, "ellipse", { left: 72, top: y + 6, width: 30, height: 30 }, i < 4 ? C.green : C.orange, "none");
    addText(slide, "✓", { left: 72, top: y + 4, width: 30, height: 30 }, { fontSize: 18, bold: true, color: C.panel, alignment: "center" });
    addText(slide, label, { left: 132, top: y, width: 230, height: 38 }, { fontSize: 25, bold: true });
    addText(slide, body, { left: 390, top: y + 2, width: 760, height: 38 }, { fontSize: 21, color: C.muted });
    addRule(slide, 132, y + 56, 1018, C.line, 1);
  });
}

function renderGlossary(slide, spec) {
  addTitle(slide, spec.title);
  spec.terms.forEach(([term, meaning], i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const left = col === 0 ? 72 : 660;
    const top = 210 + row * 96;
    addText(slide, term, { left, top, width: 200, height: 38 }, { fontSize: 24, bold: true, color: col === 0 ? C.blue : C.orange });
    addText(slide, meaning, { left: left + 205, top: top + 2, width: 310, height: 58 }, { fontSize: 18, color: C.muted });
  });
}

function renderMatrix(slide, spec) {
  addTitle(slide, spec.title);
  const x = 240;
  const colWidth = 236;
  spec.columns.forEach((column, i) => {
    addText(slide, column, { left: x + i * colWidth, top: 218, width: colWidth - 10, height: 42 }, { fontSize: 22, bold: true, color: i === 3 ? C.orange : C.blue, alignment: "center" });
  });
  spec.rows.forEach((row, i) => {
    const y = 282 + i * 72;
    addText(slide, row[0], { left: 72, top: y, width: 150, height: 40 }, { fontSize: 20, bold: true });
    row.slice(1).forEach((value, j) => {
      addText(slide, value, { left: x + j * colWidth, top: y, width: colWidth - 10, height: 52 }, { fontSize: 18, color: C.muted, alignment: "center" });
    });
    addRule(slide, 72, y + 56, 1110, C.line, 1);
  });
}

function renderComparisonMatrix(slide, spec) {
  addTitle(slide, spec.title);
  const labelX = 72;
  const columnX = [300, 560, 820];
  const columnWidth = [240, 240, 360];
  spec.columns.forEach((column, i) => {
    addText(slide, column, { left: columnX[i], top: 210, width: columnWidth[i] - 12, height: 40 }, {
      fontSize: 19, bold: true, color: i === 2 ? C.orange : C.blue, alignment: "center",
    });
  });
  spec.rows.forEach((row, rowIndex) => {
    const top = 265 + rowIndex * 58;
    if (rowIndex % 2 === 0) {
      addShape(slide, "rect", { left: 64, top: top - 3, width: 1120, height: 53 }, C.panel2, "none");
    }
    addText(slide, row[0], { left: labelX, top: top + 7, width: 210, height: 38 }, {
      fontSize: 17, bold: true,
    });
    row.slice(1).forEach((value, columnIndex) => {
      addText(slide, value, { left: columnX[columnIndex], top: top + 4, width: columnWidth[columnIndex] - 12, height: 44 }, {
        fontSize: 15, color: columnIndex === 2 ? C.text : C.muted, alignment: "center", verticalAlignment: "middle",
      });
    });
    addRule(slide, 64, top + 51, 1120, C.line, 1);
  });
}

function renderSources(slide, spec) {
  addTitle(slide, spec.title);
  addText(slide, "EVIDENCE CHAIN", { left: 72, top: 214, width: 430, height: 32 }, { fontSize: 16, bold: true, color: C.orange });
  addBulletList(slide, spec.actions, 72, 280, 600, 22, C.text, 70);
  addText(slide, "МАТЕРИАЛЫ", { left: 742, top: 214, width: 430, height: 32 }, { fontSize: 16, bold: true, color: C.blue });
  spec.links.forEach(([label, link], i) => {
    const y = 280 + i * 78;
    addText(slide, label, { left: 742, top: y, width: 420, height: 32 }, { fontSize: 22, bold: true });
    addText(slide, link, { left: 742, top: y + 35, width: 420, height: 30 }, { fontSize: 16, color: C.muted });
  });
}

const RENDERERS = {
  hero: renderHero,
  incident: renderIncident,
  outcomes: renderOutcomes,
  statement: renderStatement,
  timeline: renderTimeline,
  compare: renderCompare,
  boundary: renderBoundary,
  decision: renderDecision,
  architecture: renderArchitecture,
  architectureCompare: renderArchitectureCompare,
  pipelineCompare: renderPipelineCompare,
  partition: renderPartition,
  flow: renderFlow,
  layers: renderLayers,
  shuffle: renderShuffle,
  case: renderCase,
  code: renderCode,
  evidence: renderEvidence,
  plan: renderPlan,
  ui: renderUi,
  exit: renderExit,
  divider: renderDivider,
  checklist: renderChecklist,
  glossary: renderGlossary,
  matrix: renderMatrix,
  comparisonMatrix: renderComparisonMatrix,
  sources: renderSources,
};

export async function buildDeck({ count, outputPath, renderDir }) {
  if (![CORE_SLIDE_COUNT, FULL_SLIDE_COUNT].includes(count)) {
    throw new Error(`Unsupported slide count: ${count}`);
  }
  const presentation = Presentation.create({ slideSize: SIZE });
  for (const [zeroIndex, spec] of SLIDES.slice(0, count).entries()) {
    const slide = presentation.slides.add();
    slide.background.fill = C.bg;
    const index = zeroIndex + 1;
    if (!["hero", "divider"].includes(spec.type)) addChrome(slide, spec, index);
    const renderer = RENDERERS[spec.type];
    if (!renderer) throw new Error(`No renderer for slide type: ${spec.type}`);
    renderer(slide, spec);
    addNotes(slide, spec, index);
  }
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(outputPath);
  if (renderDir) {
    await fs.mkdir(renderDir, { recursive: true });
    for (const [index, slide] of presentation.slides.items.entries()) {
      const blob = await presentation.export({ slide, format: "png", scale: 1 });
      const bytes = new Uint8Array(await blob.arrayBuffer());
      await fs.writeFile(path.join(renderDir, `slide-${String(index + 1).padStart(2, "0")}.png`), bytes);
    }
    const montage = await presentation.export({ format: "webp", montage: true, scale: 1 });
    await fs.writeFile(path.join(renderDir, "montage.webp"), new Uint8Array(await montage.arrayBuffer()));
  }
}

async function main() {
  const [mode, outputPath, renderDir] = process.argv.slice(2);
  const count = mode === "core" ? CORE_SLIDE_COUNT : FULL_SLIDE_COUNT;
  if (!outputPath) throw new Error("Usage: build_lesson04_pptx.mjs <core|full> <output.pptx> [render-dir]");
  await buildDeck({ count, outputPath: path.resolve(outputPath), renderDir: renderDir ? path.resolve(renderDir) : undefined });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
