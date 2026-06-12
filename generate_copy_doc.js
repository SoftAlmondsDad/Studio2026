const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  HeadingLevel, BorderStyle, LevelFormat
} = require('docx');
const fs = require('fs');

// ── Helpers ──────────────────────────────────────────────────────────────────

const ORANGE = "C04B00";
const DARK   = "1A1A1A";
const MUTED  = "666666";
const LIGHT_BG = "F5F0EB";

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, font: "Arial", size: 36, color: DARK })],
    spacing: { before: 480, after: 120 },
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, font: "Arial", size: 28, color: DARK })],
    spacing: { before: 360, after: 100 },
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, bold: true, font: "Arial", size: 22, color: DARK })],
    spacing: { before: 280, after: 80 },
  });
}

// Section banner — e.g. "── HERO SECTION ──"
function sectionBanner(label) {
  return new Paragraph({
    children: [new TextRun({ text: `──  ${label.toUpperCase()}  ──`, bold: true, font: "Arial", size: 20, color: ORANGE })],
    spacing: { before: 560, after: 160 },
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 6, color: ORANGE, space: 4 },
    },
  });
}

// Field label + value on same line
function field(label, value) {
  return new Paragraph({
    children: [
      new TextRun({ text: `${label}:  `, bold: true, font: "Arial", size: 20, color: MUTED }),
      new TextRun({ text: value, font: "Arial", size: 20, color: DARK }),
    ],
    spacing: { before: 60, after: 60 },
  });
}

// Body paragraph
function body(text, italic = false) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Arial", size: 20, color: DARK, italics: italic })],
    spacing: { before: 60, after: 120 },
  });
}

// Caption / note (smaller, muted)
function caption(text) {
  return new Paragraph({
    children: [new TextRun({ text: `[Image caption] ${text}`, font: "Arial", size: 18, color: MUTED, italics: true })],
    spacing: { before: 40, after: 100 },
  });
}

// Quote block with left border effect (indented + italic)
function quote(text) {
  return new Paragraph({
    children: [new TextRun({ text: `“${text}”`, font: "Arial", size: 20, color: ORANGE, italics: true })],
    spacing: { before: 120, after: 120 },
    indent: { left: 720 },
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: ORANGE, space: 12 } },
  });
}

// Callout box — shaded label + text
function calloutLabel(text) {
  return new Paragraph({
    children: [new TextRun({ text: text.toUpperCase(), bold: true, font: "Arial", size: 18, color: ORANGE })],
    spacing: { before: 200, after: 60 },
    indent: { left: 360 },
  });
}

function calloutBody(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Arial", size: 20, color: DARK })],
    spacing: { before: 40, after: 80 },
    indent: { left: 360 },
    border: { left: { style: BorderStyle.SINGLE, size: 8, color: ORANGE, space: 12 } },
  });
}

// Bullet item
function bullet(text, ref) {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    children: [new TextRun({ text, font: "Arial", size: 20, color: DARK })],
    spacing: { before: 40, after: 40 },
  });
}

// Timeline step header
function stepHeader(label, title) {
  return new Paragraph({
    children: [
      new TextRun({ text: `${label}  —  `, bold: true, font: "Arial", size: 20, color: ORANGE }),
      new TextRun({ text: title, bold: true, font: "Arial", size: 22, color: DARK }),
    ],
    spacing: { before: 300, after: 80 },
  });
}

// Showcase item
function showcaseItem(tag, title, caption_text) {
  return [
    new Paragraph({
      children: [
        new TextRun({ text: `[${tag}]  `, bold: true, font: "Arial", size: 18, color: ORANGE }),
        new TextRun({ text: title, bold: true, font: "Arial", size: 20, color: DARK }),
      ],
      spacing: { before: 160, after: 40 },
    }),
    new Paragraph({
      children: [new TextRun({ text: caption_text, font: "Arial", size: 18, color: MUTED, italics: true })],
      spacing: { before: 0, after: 60 },
      indent: { left: 360 },
    }),
  ];
}

// ── Document ─────────────────────────────────────────────────────────────────

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: DARK },
        paragraph: { spacing: { before: 480, after: 120 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: DARK },
        paragraph: { spacing: { before: 360, after: 100 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: DARK },
        paragraph: { spacing: { before: 280, after: 80 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets-a",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
      },
      {
        reference: "bullets-b",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
      },
      {
        reference: "bullets-c",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    children: [

      // ── Title Page ──
      new Paragraph({
        children: [new TextRun({ text: "Gavin Koch-Schulte", bold: true, font: "Arial", size: 52, color: DARK })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 1440, after: 240 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Studio Final Project — Website Copy", font: "Arial", size: 28, color: MUTED })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 240 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Architecture & 3D Design  |  2025–26", font: "Arial", size: 22, color: MUTED })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 1440 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "This document contains all copy for the studio project website, organized by section for easy editing and updating. Each section heading corresponds directly to a section on the website.", font: "Arial", size: 20, color: MUTED, italics: true })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 0 },
        border: {
          top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 6 },
          bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 6 },
        },
      }),

      // ── NAVIGATION ──
      sectionBanner("Navigation"),
      h2("Site Navigation"),
      field("Logo / Brand", "Gavin."),
      field("Nav Links", "About  |  The Project  |  Journey  |  Showcase"),

      // ── HERO ──
      sectionBanner("Hero Section"),
      h2("Hero — Page Header"),
      field("Tag / Badge", "Studio Final Project · 2025–26"),
      field("Main Headline", "Building the Future, One Model at a Time"),
      body("An exploration of how technology and emerging digital tools are transforming the way buildings are designed, visualized, and brought to life."),
      field("Label", "Subheading / Intro Text"),
      new Paragraph({ spacing: { before: 120, after: 60 }, children: [new TextRun({ text: "Meta Labels", bold: true, font: "Arial", size: 20, color: MUTED })] }),
      field("Student", "Gavin Koch-Schulte"),
      field("Medium", "Blender · 3D Print"),
      field("Discipline", "Architectural Design"),

      // ── ABOUT ──
      sectionBanner("About Section"),
      h2("About Gavin"),
      field("Section Label", "About"),
      field("Headline", "A builder since day one."),
      new Paragraph({ spacing: { before: 160, after: 60 }, children: [new TextRun({ text: "Body Copy", bold: true, font: "Arial", size: 20, color: MUTED })] }),
      body("Gavin Koch-Schulte has always been drawn to creating spaces. Long before studio class, he was designing elaborate homes and entire cities — first in Minecraft, then in Roblox, always pushing to make the worlds he imagined feel real."),
      body("When his passion for architecture met the tools that real designers actually use, something clicked. Studio class became the opportunity to stop building for fun and start building with purpose — learning the same workflows that professional architects depend on."),
      body("What started as a curiosity became a semester-long investigation into how technology is changing who gets to design buildings, and how well they can design them."),
      new Paragraph({ spacing: { before: 160, after: 60 }, children: [new TextRun({ text: "Stats / Callout Numbers", bold: true, font: "Arial", size: 20, color: MUTED })] }),
      field("Stat 1", "3 Buildings Modelled"),
      field("Stat 2", "1 Real Site Designed"),
      field("Stat 3", "1 Architect Consulted"),
      field("Stat 4", "∞ Hours in Blender"),
      caption("123 Bannatyne Ave, Winnipeg — the real building that inspired Gavin’s most detailed model"),

      // ── THE PROJECT ──
      sectionBanner("The Project Section"),
      h2("The Project"),
      field("Section Label", "The Project"),
      field("Headline", "Design buildings. Think like an architect."),
      new Paragraph({ spacing: { before: 160, after: 60 }, children: [new TextRun({ text: "Body Copy", bold: true, font: "Arial", size: 20, color: MUTED })] }),
      body("The project began with a simple question: can a student with no formal training in architecture learn to design real buildings using the same software professionals use? The answer turned out to be: yes — with the right tools and the right guidance."),
      body("Gavin set out to create a series of increasingly complex 3D models, culminating in designing a real building for a real site — a vacant downtown Winnipeg parking lot his father’s company was looking to develop."),
      calloutLabel("Central Idea"),
      calloutBody("“How important technology and emerging tools are in good design, and how they are making it more accessible.”"),

      new Paragraph({ spacing: { before: 200, after: 60 }, children: [new TextRun({ text: "Project Goals (3 Cards)", bold: true, font: "Arial", size: 20, color: MUTED })] }),
      h3("Goal 01 — Master a professional 3D tool"),
      body("Learn Blender from scratch — the same software used by game studios, film production houses, and increasingly, architecture firms worldwide."),
      h3("Goal 02 — Model a real Winnipeg building"),
      body("Recreate 123 Bannatyne Ave in precise 3D detail — matching the real building’s windows, facades, and ornamental stonework."),
      h3("Goal 03 — Design an original building"),
      body("Apply the architectural process from scratch on a real site — working with city constraints, topographic data, and a professional architect."),

      // ── THE JOURNEY ──
      sectionBanner("The Journey Section (Timeline)"),
      h2("The Journey"),
      field("Section Label", "The Journey"),
      field("Headline", "From Minecraft to the real thing."),
      body("The path from hobbyist builder to architectural modeller wasn’t straight — it was full of frustration, discovery, and the gradual realization that professional tools open doors that toys never could."),

      stepHeader("START", "It started with blocks"),
      body("Gavin has been building homes and cities in Minecraft since he was young — designing elaborate structures, recreating landmarks, and imagining entire skylines. He moved to Roblox for more creative control, but eventually hit a ceiling: these were tools for games, not for the real world."),
      quote("I started using Roblox to make buildings and models but then felt it was too childish and not something that real architects and designers use to make real buildings."),
      caption("Minecraft recreation"),

      stepHeader("STEP 2", "Discovering Blender"),
      body("After exploring Fusion 360 (which didn’t run well on his computer and was trial-only), Gavin landed on Blender — the same software his brother uses for game assets. He started with the classic beginner project: the Blender donut tutorial."),
      body("At first, Blender was deeply frustrating. Things that took seconds in Minecraft took hours in Blender. But then something shifted — the detail and repeatability of the tool started to reveal itself, and what once felt like an obstacle became a superpower."),
      caption("First Blender project — the classic donut"),

      stepHeader("STEP 3", "The Leaning Tower of Pisa"),
      body("The first building Gavin made start-to-finish for the studio project was the Leaning Tower of Pisa. It was a strategic choice: abundant reference images online, detailed tutorials available, and iconic enough to reveal whether his model was accurate at a glance."),
      body("The challenge — and the lesson — was discovering how difficult it was to add colour and texture inside Blender compared to simpler tools like Roblox. The geometry was one thing; making it look like the real building was another skill entirely."),

      stepHeader("STEP 4", "123 Bannatyne — a real Winnipeg building"),
      body("The next level: model an actual existing building in Winnipeg — one his father’s company had just purchased. 123 Bannatyne Ave is a three-storey heritage brick building downtown, with arched windows, ornamental cornices, and distinctive wall bump-outs."),
      body("This was far harder than the Tower of Pisa. Every time Gavin would check his model against photos of the real building, he’d notice something he’d missed. “I would always see things I missed every time I would check.” But the result — a 3D model that matched the real building’s windows, proportions, and facade details — was genuinely impressive."),

      stepHeader("FINAL", "Designing from scratch — with a real architect"),
      body("For the final project, Gavin wanted to follow the same process real architects use. The site: a downtown Winnipeg parking lot that his father’s company was looking to develop into an apartment building."),
      body("Gavin met with Sean, an architect from AtLrg Architects, who showed him how the design process actually works — introducing city topographic maps, underground utility lines, and all the constraints that shape what can and can’t be built on a site."),
      calloutLabel("What the architect revealed"),
      calloutBody("Real architectural design isn’t just aesthetics — it’s navigating an invisible network of constraints that determine where, how high, and how wide you can build. Each constraint changed the shape of the building."),
      new Paragraph({ spacing: { before: 140, after: 60 }, indent: { left: 360 }, children: [new TextRun({ text: "Constraints:", bold: true, font: "Arial", size: 20, color: DARK })] }),
      bullet("Driveway access requirements", "bullets-a"),
      bullet("Underground service lines", "bullets-a"),
      bullet("Sidewalk setbacks", "bullets-a"),
      bullet("Parking minimums", "bullets-a"),
      bullet("Building height limits", "bullets-a"),
      bullet("City utility corridors", "bullets-a"),
      caption("City topographic map — underground utilities & site constraints"),

      // ── SHOWCASE ──
      sectionBanner("Showcase Section"),
      h2("Showcase / Creative Accomplishments"),
      field("Section Label", "Showcase"),
      field("Headline", "Creative Accomplishments"),
      body("From the first donut to a 3D-printed city model — a full view of what was built across the semester."),

      new Paragraph({ spacing: { before: 200, after: 60 }, children: [new TextRun({ text: "Showcase Items (Grid)", bold: true, font: "Arial", size: 20, color: MUTED })] }),
      ...showcaseItem("Final Project", "3D-Printed Winnipeg City Model", "Physical massing studies for the exChange site, 3D printed in orange and placed in a full model of downtown Winnipeg"),
      ...showcaseItem("Heritage Building", "123 Bannatyne Ave", "Precise Blender recreation of Winnipeg’s heritage brick building"),
      ...showcaseItem("Reference", "The Real Building", "The actual 123 Bannatyne Ave — matched window by window in 3D"),
      ...showcaseItem("Landmark", "Tower of Pisa", "First major Blender build — base colonnade detail"),
      ...showcaseItem("Landmark", "Tower of Pisa", "Upper colonnade ring — intricate arch repetition"),
      ...showcaseItem("Site Analysis", "exChange Site Topo", "City topographic data used in the real design process"),

      new Paragraph({ spacing: { before: 200, after: 60 }, children: [new TextRun({ text: "Capstone Feature Card", bold: true, font: "Arial", size: 20, color: MUTED })] }),
      field("Tag", "Capstone Achievement"),
      h3("From Digital Model to Physical Reality"),
      body("The culmination of the project wasn’t just a Blender file — it was a physically 3D-printed massing model, placed on a full-scale 3D print of downtown Winnipeg. The orange models represent different design options for the exChange site, embedded in their real-world urban context."),
      body("This is the same process professional architecture firms use when presenting early design options to clients and city planners."),
      new Paragraph({ spacing: { before: 100, after: 60 }, children: [new TextRun({ text: "Feature List:", bold: true, font: "Arial", size: 20, color: DARK })] }),
      bullet("Multiple massing options designed and compared", "bullets-b"),
      bullet("Printed at 1:500 scale to match the city base model", "bullets-b"),
      bullet("Constraints from real city maps factored into every option", "bullets-b"),
      bullet("Presented in context of surrounding Winnipeg downtown", "bullets-b"),

      // ── FOOTER ──
      sectionBanner("Footer"),
      h2("Footer"),
      field("Brand / Logo Text", "Gavin."),
      field("Centre Text", "Studio Final Project — 2025–26"),
      field("Right Text", "Gavin Koch-Schulte  |  Architecture & 3D Design"),

    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  const outPath = "C:/Users/frank/Documents/Gavins Files/Gavin Studio Project/Gavin_Studio_Website_Copy.docx";
  fs.writeFileSync(outPath, buffer);
  console.log("Written:", outPath);
}).catch(err => { console.error(err); process.exit(1); });
