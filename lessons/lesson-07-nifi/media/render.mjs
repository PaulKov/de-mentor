import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const sourceDir = path.dirname(fileURLToPath(import.meta.url));
const build = path.resolve(process.argv[2] ?? '');
const modules = process.env.NIFI_MEDIA_NODE_MODULES;
if (!process.argv[2] || !modules) throw new Error('Usage: node render.mjs BUILD_DIR; set NIFI_MEDIA_NODE_MODULES.');
const require = createRequire(path.join(modules, 'nifi-media-loader.cjs'));
const { Presentation, PresentationFile } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
await fs.mkdir(build, { recursive: true });

const sources = [
  'https://nifi.apache.org/nifi-docs/user-guide.html',
  'https://jsonlines.org/',
  'https://nifi.apache.org/components/org.apache.nifi.processors.jolt.JoltTransformJSON/',
  'https://kafka.apache.org/42/design/design/\nhttps://nifi.apache.org/components/org.apache.nifi.kafka.processors.ConsumeKafka/',
  'https://www.w3.org/TR/1999/REC-xpath-19991116/\nhttps://nifi.apache.org/components/org.apache.nifi.processors.standard.TransformXml/',
  'https://nifi.apache.org/components/org.apache.nifi.processors.groovyx.ExecuteGroovyScript/',
  'https://nifi.apache.org/components/org.apache.nifi.processors.standard.InvokeHTTP/\nhttps://nifi.apache.org/components/org.apache.nifi.processors.standard.ListFTP/',
  'https://nifi.apache.org/docs/nifi-docs/html/nifi-in-depth.html\nhttps://nifi.apache.org/nifi-docs/administration-guide.html',
  'https://kafka.apache.org/42/design/design/\nhttps://nifi.apache.org/components/org.apache.nifi.processors.standard.PutDatabaseRecord/',
  'https://nifi.apache.org/nifi-docs/user-guide.html\nhttps://nifi.apache.org/nifi-docs/administration-guide.html',
];

const episodes = [];
for (const [index, filename] of (await fs.readdir(sourceDir)).filter(name => /^\d\d-.*\.md$/.test(name)).sort().entries()) {
  const raw = await fs.readFile(path.join(sourceDir, filename), 'utf8');
  const [header, ...sections] = raw.replaceAll('\r\n', '\n').trim().split(/^## /m);
  if (!sections.length || !header.startsWith('# ')) throw new Error(`Invalid episode: ${filename}`);
  episodes.push({
    slug: filename.slice(0, -3),
    title: header.trim().slice(2),
    source: sources[index],
    scenes: sections.map(section => {
      const lines = section.trim().split('\n');
      const title = lines.shift();
      return {
        title,
        points: lines.filter(line => line.startsWith('- ')).map(line => line.slice(2)),
        code: section.match(/```[^\n]*\n([\s\S]*?)```/)?.[1].trimEnd(),
        narration: lines.filter(line => line.startsWith('> ')).map(line => line.slice(2)).join(' '),
      };
    }),
  });
}

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
// Layout and palette follow decks/apache-spark-foundations/build_lesson04_pptx.mjs.
const ink = '#202123';
const muted = '#6E6E68';
const paper = '#F7F7F4';
const line = '#D8D7D0';
const orange = '#E25A1C';
const blue = '#2F6FED';
const dark = '#1F2428';
const white = '#FFFFFF';

function rule(slide, left, top, width, height, fill) {
  slide.shapes.add({ geometry: 'rect', position: { left, top, width, height }, fill,
    line: { fill: 'none', width: 0 } });
}

function label(slide, value, left, top, width, height, fontSize, options = {}) {
  const shape = slide.shapes.add({
    name: options.name || value.slice(0, 55),
    geometry: 'textbox',
    position: { left, top, width, height },
    fill: options.fill ?? 'none',
    line: { fill: 'none', width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    typeface: options.font ?? 'Aptos',
    fontSize, color: options.color ?? ink, bold: options.bold ?? false,
    alignment: options.alignment ?? 'left', verticalAlignment: 'top',
    insets: options.insets ?? 0, wrap: 'square', autoFit: 'none',
  };
}

const cover = presentation.slides.add();
cover.background.fill = dark;
rule(cover, 0, 0, 20, 720, orange);
label(cover, 'LESSON 07', 72, 70, 400, 30, 16, { color: orange, bold: true });
label(cover, 'Apache NiFi\nИнтеграция данных с нуля', 72, 176, 1050, 230, 62, { color: white, bold: true });
label(cover, 'JSONL, JOLT, Kafka, XML, XSLT и Groovy', 76, 438, 850, 70, 25, { color: '#D6D9DC' });
rule(cover, 76, 550, 160, 5, orange);
label(cover, 'Основная часть и Deep Dive', 76, 580, 650, 34, 18, { color: '#D6D9DC', bold: true });
label(cover, 'DE / MENTOR', 956, 564, 230, 60, 28, { color: orange, bold: true, alignment: 'right' });
cover.speakerNotes.text = 'Курс de-mentor. Основная часть, практики и Deep Dive показывают путь синтетического заказа от входа до базы.';
const coverImage = await presentation.export({ slide: cover, format: 'png', scale: 1 });
await fs.writeFile(path.join(build, 'cover.png'), new Uint8Array(await coverImage.arrayBuffer()));

for (const [moduleIndex, episode] of episodes.entries()) {
  const number = String(moduleIndex + 1).padStart(2, '0');
  for (const [sceneIndex, scene] of episode.scenes.entries()) {
    if (!scene.points.length || !scene.narration) throw new Error(`Empty content: ${episode.slug}/${scene.title}`);
    const slide = presentation.slides.add();
    slide.background.fill = paper;
    const topic = sceneIndex === 0 ? episode.title.replace(/^Deep Dive · /, '') : scene.title;
    label(slide, `${number}  ${moduleIndex < 7 ? 'ОСНОВНАЯ ЧАСТЬ' : 'DEEP DIVE'}`, 64, 34, 300, 28, 14,
      { color: moduleIndex < 7 ? orange : blue, bold: true });
    label(slide, 'DE / MENTOR', 1040, 34, 176, 28, 13, { bold: true, color: muted, alignment: 'right' });
    rule(slide, 64, 68, 1152, 1, line);
    label(slide, topic, 64, 92, 1152, 96, 38, { bold: true });
    label(slide, String(presentation.slides.items.length).padStart(2, '0'), 1158, 674, 58, 22, 13,
      { color: muted, bold: true, alignment: 'right' });
    const compact = Boolean(scene.code);
    const left = compact ? 776 : 72;
    for (const [pointIndex, point] of scene.points.entries()) {
      const y = 244 + pointIndex * (compact ? 75 : 74);
      slide.shapes.add({
        geometry: 'ellipse', position: { left, top: y + 9, width: 9, height: 9 },
        fill: orange, line: { fill: 'none', width: 0 },
      });
      label(slide, point, left + 28, y, compact ? 398 : 1080, compact ? 70 : 64, compact ? 24 : 30);
    }
    if (scene.code) {
      label(slide, scene.code, 72, 218, 646, 306, 21,
        { color: '#E6EDF3', fill: dark, font: 'Consolas', insets: { left: 20, right: 18, top: 22, bottom: 10 } });
    }
    slide.speakerNotes.text = `${scene.narration}\n\n${episode.source}`;
    scene.image = `${episode.slug}-${sceneIndex + 1}.png`;
    const frame = await presentation.export({ slide, format: 'png', scale: 1 });
    await fs.writeFile(path.join(build, scene.image), new Uint8Array(await frame.arrayBuffer()));
  }
  console.log(`Rendered ${episode.slug}`);
}

const deck = await PresentationFile.exportPptx(presentation);
await deck.save(path.join(build, 'nifi-course-draft.pptx'));
await fs.writeFile(path.join(build, 'episodes.json'), JSON.stringify(episodes, null, 2), 'utf8');
