# Diagram Readability Guide

Generalized principles for producing architecture SVG diagrams that stay readable
at a glance, survive iteration, and render cleanly in browsers and PNG exporters.
These rules were distilled from real diagram rework on pipeline systems
(producer/queue/consumer with LLM classifiers) and apply to any architecture SVG:
agent systems, data pipelines, microservices, request/response flows, etc.

Read this alongside
[svg-template-patterns.md](svg-template-patterns.md) (building blocks) and
[../SKILL.md](../SKILL.md) (interrogation + construction workflow).

---

## 1. Flow Direction Conventions (MANDATORY)

Direction carries meaning. Pick a convention and stick to it for the whole
diagram, otherwise the reader has to re-learn the rules in every region.

### Rule: Cross-group = vertical, intra-group = horizontal

- **Cross-group transitions (stage boundaries)** must flow **vertically**.
  Examples: `Producer → Queue`, `Queue → Consumer`, `Classifier → Alert Manager`.
  These are the "stages" of the pipeline and advancing down the page = advancing
  through the system.
- **Intra-group transitions (expansions inside a stage)** should flow
  **horizontally**. Examples: `driver.py → AsyncLogStream` (setup feeding the
  producer), `AnomalyClassifier ↔ LiteLLM` (tool call within classify stage),
  `AlertManager → JSON report` (output emission within consume stage).

### Why it works

- The eye scans top-to-bottom once to understand the pipeline's backbone.
- Horizontal branches read as "things attached to this stage" rather than new
  stages, which prevents the diagram from feeling like a spaghetti graph.

### Picking the opposite convention

Left-to-right is equally valid for wide/landscape diagrams (e.g. API request
flows). In that case invert the rule: **cross-group = horizontal, intra-group
= vertical**. The invariant is that primary progression and lateral detail
use orthogonal axes.

---

## 2. Center Spine & Alignment

Once you know the primary axis, lock the primary components onto a single
center line (the "spine").

- Calculate a single `SPINE_X` (or `SPINE_Y` for horizontal flows) and anchor
  every main-pipeline box to it via `box.center = SPINE_X`.
- Horizontal expansions branch **left or right** of the spine symmetrically if
  possible, or consistently on one side if the diagram is asymmetric.
- Reference panels (legends, model definitions, config cheat sheets) live
  **outside** the spine in dedicated gutters so they never cross it.

Consequence: every vertical cross-group arrow is a straight line with
`x1 == x2 == SPINE_X`. No dog-legs, no S-curves for primary flow.

---

## 3. Arrow Connection Rules

Broken or awkward arrows are the #1 readability killer. Every arrow must:

### 3.1 Start and end inside the source/target bounds

- `arrow.x1 >= source.x  AND  arrow.x1 <= source.x + source.width`
- Same for `y1`, `x2`, `y2` vs target.
- If the arrow starts outside the box, readers can't tell what it's coming from.

### 3.2 Prefer straight lines for primary flow

- Vertical primary arrows: `x1 == x2`. Horizontal primary arrows: `y1 == y2`.
- Use L-shaped (one 90° bend) routing for secondary arrows only, and never
  cross another primary arrow.

### 3.3 Differentiate line types visually

| Meaning | Stroke width | Dash | Marker |
|---|---|---|---|
| Primary data flow (cross-group) | 2.6–3.0px | solid | filled arrow |
| Secondary flow (intra-group) | 2.0–2.4px | solid | filled arrow |
| Relationship / nesting / "used by" | 1.6px | dashed (5 3) | thin arrow |
| Failure path / error flow | 2.0px | solid, red stroke | red arrow |
| Sentinel / control signal | 2.0px | dashed (2 4) | filled arrow |

The reader should be able to distinguish flow type without reading labels.

### 3.4 Pill-style labels, not floating text

Arrow labels should sit in a **pill** (rounded rect + text) placed on or
beside the arrow line, not as bare text that collides with other geometry.

```xml
<rect x="..." y="..." width="..." height="20" rx="10"
      fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
<text ... font-size="11" font-weight="600">put("drain batch")</text>
```

Pills can sit **on** the arrow (centered) or **beside** it. Never let a label
overlap a box border or another arrow.

---

## 4. Visual Hierarchy & Weight

Force the reader's eye to the primary path.

- **Stroke-width hierarchy**: primary pipeline arrows should be visibly thicker
  than helper arrows (e.g. 3.0 vs 2.0). The ratio must be perceptible at
  100% zoom.
- **Box fill hierarchy**: main pipeline boxes use gradient fills with
  coloured borders; reference/context boxes use flat white with dashed or
  muted borders.
- **Border style signals role**:
  - Solid coloured border → part of the pipeline.
  - Dashed grey border → reference / legend / context panel.
  - Double border or shadow filter → "entry point" (driver, user, CLI).

---

## 5. Color Semantics

Assign one role per colour and keep it for the life of the diagram.

- Pick roles up front: e.g. producer = blue, queue = teal, classifier
  = purple, consumer = amber, output = green, failure = red.
- When a box represents a *classification* or *enum value* (e.g. CRITICAL /
  WARNING / INFO), use a consistent palette of chips with matching colours so
  the same label always looks identical everywhere it appears.
- Never reuse the failure colour (red) for a non-failure concept. Red always
  = error or warning.
- If you run out of canonical roles, cycle through indigo, pink, cyan, lime
  but never reassign an earlier role.

---

## 6. Spacing & Density Management

Diagrams read worse when crowded, not better. The fix for "too much info" is
almost never "shrink the fonts" — it is "add space and split into sub-regions".

### 6.1 Minimum gaps

| Between | Minimum | Why |
|---|---|---|
| Two primary pipeline boxes (cross-group, along spine) | 110px | Room for arrow + pill label + breathing gap |
| Node bottom → arrow label centre | 25px | Label must not kiss the box |
| Arrow label centre → next node top | 25px | Same as above |
| Main spine → reference panel gutter | 80px | Keeps gutter visually separate |
| Box inner text → box border | 18px | Text must not touch the frame |
| Adjacent pills / chips on the same line | 8px | Avoid chip-merging illusion |

### 6.2 When it feels congested

Don't compress. Instead:

1. Remove decorative boxes (e.g. "at a glance" summaries) once their content
   is covered by the main diagram.
2. Widen the canvas rather than shrinking the content.
3. Move long textual notes into a dedicated reference panel in a gutter.
4. Split a single overloaded box into two aligned sub-boxes.

### 6.3 Grow the canvas

- It is **always acceptable** to raise `viewBox` height/width to fit content
  comfortably. Pixel-budget is cheap; cognitive budget is not.
- After any layout change, recompute canvas size from actual component bounds,
  never leave old dimensions that clip content.

---

## 7. Typography

Small text in architecture diagrams is a bug.

| Element | Font size | Family | Weight | Notes |
|---|---|---|---|---|
| Main box titles | 20–22px | system-ui | 700 | Use title case |
| Secondary titles (class/module names) | 16–18px | JetBrains Mono / monospace | 700 | Monospace for code identifiers |
| Field/method lines | 13–14px | monospace | 400 | 22–26px line-height |
| Pill labels on arrows | 11–12px | system-ui | 600 | Letter-spacing 0.5px |
| Section band labels (`INGEST · PRODUCER GROUP`) | 12–13px | system-ui | 700 | Letter-spacing 1.5–2px, uppercase |
| Inline comments / footnotes | 11–12px | system-ui | 500 | Muted fill `#64748b` / `#6b7280` |
| Warnings / annotations | 11–12px | system-ui | 700 | Red fill `#dc2626` |

Rules:
- Never go below **11px** for anything that must be read.
- Use monospace for code identifiers (function names, type names, module paths)
  — it signals "this is literal code", not prose.
- Add **letter-spacing 1.5–2px** and uppercase to small section-band labels so
  they read as structural headers instead of body text.

---

## 8. Content Discipline (Be Specific)

A diagram that says `retry logic: yes` is useless. Replace generic statements
with concrete values drawn from the codebase.

### Good content, with evidence

- `MAX_RETRIES = 3, backoff = 0.5s × 2^n`
- `Semaphore(limit=5)` inside the classifier box
- `response_format = LLMClassificationResponse` next to the LLM arrow
- `model = "azure/gpt-4.1", temperature = 0.1` on the LLM tool box
- `asyncio.Queue(maxsize=100)` on the queue box
- Exact method list: `_classify_and_forward`, `_parse_response`,
  `_build_report`, `_save_report`, `_print_summary`
- Exact field list with types and defaults from the real Pydantic model

### Bad content

- "Retries on failure" (how many? backoff type?)
- "Calls LLM" (which model? provider? structured output?)
- "Saves report" (JSON? where? named how?)

### Rule of thumb

Every piece of text on the diagram should survive the question "so what?" and
"says who?". If it cannot, replace it with a constant, config value, function
name, or type signature pulled from source.

---

## 9. Labels, Badges, Chips, and Stage Numbers

Use dedicated label primitives instead of free-floating text.

### 9.1 Section band badges, not underlines

When you need to label a horizontal band of the diagram (e.g.
`INGEST · PRODUCER GROUP`), use a **rounded rectangle badge** with the label
inside it, not a horizontal line + text.

Rationale: horizontal lines drawn across the canvas will cross vertical
primary arrows and visually sever them. Badges sit beside the spine and stay
out of the way.

```xml
<rect x="60" y="{Y}" width="280" height="28" rx="14"
      fill="#eef2ff" stroke="#6366f1" stroke-width="1.5"/>
<text x="200" y="{Y+19}" text-anchor="middle"
      font-family="system-ui" font-size="12" font-weight="700"
      letter-spacing="2" fill="#4338ca">INGEST · PRODUCER GROUP</text>
```

### 9.2 Stage numbers on the spine

For pipelines, place a **circled number** adjacent to each primary stage
(1, 2, 3, ...). Readers instantly know the order without tracing arrows.

```xml
<circle cx="{CX}" cy="{CY}" r="14" fill="#6366f1"/>
<text x="{CX}" y="{CY+5}" text-anchor="middle"
      font-family="system-ui" font-size="14" font-weight="700"
      fill="#ffffff">3</text>
```

### 9.3 Inline chips for nested concepts

Concepts that belong inside a larger component (e.g. `Semaphore`, `retry`,
`fallback` inside the classifier's LLM box) should render as **small
coloured chips** inside the parent box rather than as separate diagram
elements. Chips say "this is a property of the parent", not "this is another
stage".

```xml
<rect x="..." y="..." width="78" height="20" rx="10"
      fill="#fef3c7" stroke="#d97706" stroke-width="1"/>
<text ... font-size="11" font-weight="700" fill="#92400e">Semaphore(5)</text>
```

### 9.4 Classification pills

Enum values (e.g. `CRITICAL`, `WARNING`, `INFO`, `NORMAL`) should render as
a consistent row of coloured pills so the same label is instantly
recognisable wherever it appears.

---

## 10. Legends (when needed)

Add a compact legend panel whenever the diagram uses:

- More than 2 arrow line types (solid/dashed/red/sentinel).
- More than 4 role colours.
- Custom symbols (circled numbers, chips, badges).

Legend lives in a gutter, uses a dashed grey border (signalling "reference, not
pipeline"), and lists every visual convention exactly once.

---

## 11. Iteration Loop (render → inspect → fix)

SVGs that look correct in code frequently render poorly. Treat every layout
change as a hypothesis and verify it.

### Required loop

1. Modify the SVG source.
2. Validate well-formed XML:
   ```bash
   python -c "import xml.etree.ElementTree as ET; ET.parse('<file>.svg')"
   ```
3. Render to PNG so you can see what the browser will see:
   ```bash
   rsvg-convert -o <file>.png <file>.svg   # preferred
   # or: magick <file>.svg <file>.png
   ```
4. Inspect the PNG. Specifically check:
   - Every arrow starts **inside** its source box and ends **inside** its
     target box.
   - No pill/label overlaps a box border or another pill.
   - Section band labels do **not** cross any primary arrow.
   - No text is clipped at a box edge.
   - `viewBox` dimensions fit the content — no whitespace canyons, no
     cropped elements at the edges.
5. If any issue found, go to step 1. Do not hand off a diagram that hasn't
   survived at least one render cycle.

### Common problems caught by this loop

- Arrow origin outside the producer box (e.g. `x1 = 670` but box is
  `x = 730..980`).
- Horizontal section divider line crossing a vertical spine arrow, visually
  severing the pipeline.
- Reference panel pushed outside `viewBox` because canvas wasn't recomputed
  after adding content.
- Labels readable in the source but microscopic in the rendered PNG.

---

## 12. Technical Hygiene

### 12.1 XML correctness

- File must parse with `xml.etree.ElementTree` with no errors.
- Every element is properly nested and closed.
- No stray CDATA, no broken entities.

### 12.2 Unicode / character integrity

Architecture diagrams often pick up corrupted bytes from copy-paste
(`0x92` Windows-1252 right-single-quote becoming visible garbage, or
`0x14` DC4 control character appearing inside text).

- Check the raw bytes periodically:
  ```bash
  xxd <file>.svg | grep -nE '\\\\x(9[0-9a-f]|1[0-4])'
  ```
- Replace with real UTF-8 glyphs: `→`, `—`, `·`, `✓`, `✗`.
- Never keep control characters (bytes `0x00–0x1F` other than tab/newline).

### 12.3 viewBox discipline

- `viewBox` must match actual content extent. Recompute after every major
  layout change.
- Prefer `viewBox` + no explicit `width`/`height` on the root `<svg>` — this
  lets consumers scale freely without distortion.
- If you must set width/height, keep them proportional to `viewBox`.

### 12.4 Font fallback

Always specify a system fallback list, never a single exotic font:

```
font-family="JetBrains Mono, 'Fira Code', Menlo, Consolas, monospace"
font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
```

---

## 13. Anti-Patterns (if you see any of these, fix them)

- Arrow originates or terminates outside the bounding box of its source/target.
- Primary flow uses curves or multiple bends where a straight line is possible.
- Section-title text sits on a horizontal line that cuts across a primary arrow.
- Same colour used for two different roles (e.g. red for both "failure" and
  "classification = CRITICAL").
- Font-size below 11px anywhere.
- Three or more sibling boxes crammed in a single row at 1400px width when a
  2-row layout would fit.
- "At a glance" or summary boxes that duplicate info already shown elsewhere
  in the diagram.
- Generic labels (`retry`, `call LLM`, `store`) where concrete values
  (`retries = 3`, `model = azure/gpt-4.1`, `asyncio.Queue(maxsize=100)`) are
  known.
- `viewBox` dimensions left at stale values after adding/removing components.
- Skipping the render-and-inspect loop and shipping directly from code.

---

## 14. Pre-Ship Checklist

Before declaring a diagram done:

**Flow & layout**
- [ ] Every cross-group transition is a straight line along the primary axis.
- [ ] Every intra-group transition is on the perpendicular axis and stays
      inside its owning band.
- [ ] All primary-pipeline boxes share a single spine coordinate.
- [ ] No arrow starts or ends outside the bounds of its source/target.
- [ ] Section band labels use rect badges, not horizontal lines that cross
      arrows.

**Visual hierarchy**
- [ ] Primary arrows are measurably thicker than secondary arrows.
- [ ] Dashed lines are used only for references/relationships, never for
      primary flow.
- [ ] Each colour maps to exactly one role.

**Content**
- [ ] Every factual claim on the diagram is backed by a real constant,
      config value, type name, or function name from source.
- [ ] Enum values render as consistent pills everywhere they appear.
- [ ] Inline chips used for properties-of-a-parent, not for new stages.
- [ ] Stage numbers (or equivalent ordering hint) present for pipelines.

**Readability**
- [ ] No font size below 11px.
- [ ] Monospace used for code identifiers, sans-serif for prose.
- [ ] Minimum gaps respected (see §6.1 and [svg-template-patterns.md](svg-template-patterns.md)).
- [ ] No label overlaps any box border or other label.

**Hygiene**
- [ ] XML parses without errors.
- [ ] No corrupted bytes / control characters in source.
- [ ] `viewBox` matches actual content extent.
- [ ] Rendered PNG reviewed and matches intent.

---

## 15. Quick Reference Card

| Want to show | Use |
|---|---|
| The backbone of a pipeline | Vertical straight arrows, thick stroke, spine alignment |
| A helper/tool used by one stage | Horizontal arrow, thinner stroke, kept inside the stage's band |
| A property of a component | Inline chip inside the parent box |
| An ordering of stages | Circled stage numbers on the spine |
| A data contract | Model definition box in a gutter, dashed relationship arrows |
| A failure or exception path | Red solid arrow with red pill label |
| A control signal (sentinel, shutdown) | Dashed arrow, small pill label |
| An enum / classification | Consistent row of coloured pills |
| A section boundary | Rounded rect badge beside the spine (not a horizontal line) |
| A reference / legend | Gutter panel with dashed grey border |
