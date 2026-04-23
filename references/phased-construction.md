# Phased Construction — Mechanics Cookbook

This is the per-phase how-to for the construction workflow defined in
[../SKILL.md § Phase C](../SKILL.md). The main skill specifies *what* each
phase does and *why*; this document specifies *how* to execute each phase
in practice — commands, exact deliverables, good/bad examples, and the
specific failures to watch for.

Read this when you're actually building a diagram. Refer back to
[svg-template-patterns.md](svg-template-patterns.md) for XML building
blocks and [diagram-readability-guide.md](diagram-readability-guide.md)
for the general rules.

---

## The render gate (what every gate actually checks)

The automated hook at `~/.cursor/hooks/svg-render-gate/validate.py` runs
after every `.svg` write and produces a JSON report at
`<svg>.render-report.json` with this shape:

```json
{
  "status": "OK" | "XML_ERROR" | "BAD_BYTES" | "RENDER_FAILED",
  "svg_path": "/abs/path/to/file.svg",
  "png_path": "/abs/path/to/file.png",
  "xml_ok": true,
  "bad_bytes": [],
  "render_ok": true,
  "viewbox": {"width": 1440, "height": 1760},
  "file_size_bytes": 42831,
  "messages": ["..."]
}
```

After every write, read the report:

```bash
cat <svg>.render-report.json
```

Then open the PNG (`<svg>.png`) to do the visual check. **Status must be
`OK` and the PNG must match the phase's exit criteria before advancing.**

### Status codes

- `OK` — XML parses, no bad bytes, PNG rendered successfully.
- `XML_ERROR` — SVG does not parse. `messages` names the element/line.
  **Fix immediately**; no other check runs until XML is valid.
- `BAD_BYTES` — control chars or Windows-1252 garbage detected. `bad_bytes`
  lists them with byte offsets. Replace them with real UTF-8 glyphs
  (`→`, `—`, `·`, `✓`).
- `RENDER_FAILED` — XML is fine but `rsvg-convert` couldn't produce a PNG.
  `messages` has the rsvg error. Usually a malformed path spec, missing
  gradient reference, or circular `use`.

### Manual fallback (when the hook is missing)

If the hook didn't run (e.g. machine without the user-level setup), run
the same checks by hand:

```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('file.svg')"
xxd file.svg | grep -nE '\\x(9[0-9a-f]|1[0-4])' || echo "clean"
rsvg-convert -o file.png file.svg
open file.png  # or use a PNG viewer
```

---

## Phase 0 — Plan

**Produces**: a text-only coordinate plan. No SVG written.

### Deliverable — component inventory table

Write a table (markdown or scratch buffer) listing every component:

| Component | Band | x | y | w | h | Notes |
|---|---|---|---|---|---|---|
| driver.py | left-gutter | 60 | 260 | 220 | 110 | CLI entry |
| AsyncLogStream | spine | 580 | 260 | 280 | 130 | primary stage 1 |
| QueueA | spine | 580 | 450 | 280 | 60 | asyncio.Queue(maxsize=100) |
| AnomalyClassifier | spine | 580 | 590 | 280 | 150 | primary stage 3 |
| LiteLLM | right-gutter | 1020 | 615 | 260 | 120 | tool call |
| QueueB | spine | 580 | 810 | 280 | 60 | secondary queue |
| AlertManager | spine | 580 | 940 | 280 | 150 | primary stage 5 |
| JSON output | right-gutter | 1020 | 965 | 240 | 100 | file emission |
| Pydantic sidebar | left-gutter | 60 | 580 | 480 | 390 | reference panel |
| Legend | bottom-right | 1020 | 1600 | 360 | 140 | arrow line types |

### Deliverable — band & spine definitions

```
PRIMARY_AXIS = vertical
SPINE_X      = 720   # all spine-component centers at x=720
LEFT_GUTTER  = 60..540
RIGHT_GUTTER = 1000..1380
VIEWBOX_W    = 1440
VIEWBOX_H    = 1760  # estimated, will confirm in Phase 1
```

### Checklist before leaving Phase 0

- [ ] Every component in the planned diagram is in the table.
- [ ] Every spine component has `x + w/2 == SPINE_X`.
- [ ] No two components in the same band overlap.
- [ ] Gutter components are outside `SPINE_X ± max_spine_width/2 + 80px`.
- [ ] Estimated `VIEWBOX_H` = `max(y + h) + 60` bottom padding.

No render needed at Phase 0 — no SVG exists yet.

---

## Phase 1 — Scaffold

**Produces**: an SVG where every component is a plain rounded rect with a
single centered title. No fills (beyond a neutral white), no chips, no
fields, no arrows.

### Scaffold component template

```xml
<g>
  <rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="12"
        fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="{X + W/2}" y="{Y + H/2 + 5}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="16" font-weight="600" fill="#1f2937">{NAME}</text>
</g>
```

Use the exact `(x, y, w, h)` from the Phase 0 table. Do not deviate.

### Do not add yet

- Gradients, shadow filters, gradient fills
- Component fields / chips / inline annotations
- Arrows or arrow markers
- Section-band badges, stage numbers, legend

Add `<defs>` for arrow markers and shadow if you wish — they're reused
later — but do not apply them in Phase 1.

### Render gate — what to look for

After save, read the render report:

```bash
cat <file>.svg.render-report.json
```

Open the PNG. Verify:

- [ ] `status == "OK"`
- [ ] Every spine component is visually vertically aligned (same x-center).
- [ ] No component overlaps another.
- [ ] Gutters look like gutters — clearly separated from the spine.
- [ ] `viewBox` fits all content. No clipping at edges. No empty canyons.
- [ ] `VIEWBOX_H` prediction from Phase 0 is within ±40px of what looks
      right. If badly off, fix the plan before moving on.

### Good vs bad Phase 1 renders

**Good**: pencil-sketch feel — grey boxes, centered names, obvious spine
going top-to-bottom, gutter panels offset left/right.

**Bad** (fix before Phase 2):
- Two spine components share a y-range → collision.
- Gutter component visually reads as "part of the spine".
- Canvas has 200px of empty space below the last component.
- A component is cut off at the right edge.

### Exit gate

Fix any render issue at the layout level. Do not advance to Phase 2 on top
of a broken scaffold.

---

## Phase 2 — Fill (one component at a time)

**Produces**: a fully-detailed SVG, built one component per edit.

### The per-component loop

For each component in the Phase 0 inventory:

1. Pick the component.
2. Replace its Phase 1 scaffold block with the fully detailed version:
   - Gradient fill from the role palette
     ([svg-template-patterns.md § Standard Gradient Palette](svg-template-patterns.md#standard-gradient-palette)).
   - Stroke colour matching the role.
   - Title, subtitle, field list, inline chips, annotations.
   - Shadow filter if the component is a primary pipeline stage.
3. **Save the file.**
4. Read the render report. Open the PNG.
5. Visually verify just that component:
   - [ ] Text does not overflow the box.
   - [ ] Chips are aligned and do not overlap each other.
   - [ ] Colours match the role in the palette.
   - [ ] The component has not encroached into neighbouring components.
   - [ ] Inner text padding ≥ 18px from any border.
6. Fix anything wrong, re-save, re-render.
7. When the component is clean, move to the next.

### Ordering within Phase 2

Fill in this order (prevents compounding layout issues):

1. **Primary-pipeline spine components**, top to bottom (biggest first —
   they're most likely to have typography issues).
2. **Tool / helper components** in gutters.
3. **Reference panels** (Pydantic models, config cheat sheets).
4. **Legend placeholder** (leave content for Phase 4).

### Forbidden in Phase 2

- Adding arrows (those come in Phase 3).
- Adding section-band badges (those come in Phase 4).
- Editing two components in one save — breaks failure localization.

### Common Phase 2 failures

| Symptom in PNG | Cause | Fix |
|---|---|---|
| Title text overflows right edge | Component `w` was undersized for the title | Grow `w` in Phase 0 table, re-scaffold, return here |
| Field line merges with next | Line-height < 22px at 14px font | Use 26px line-height for 14px monospace |
| Chip runs off box | Chip width + x-offset > component width | Shrink chip label or move to next row |
| Gradient washes out text | Dark gradient stop + dark text fill | Use the palette's prescribed title fill colour |
| Two chips visually touching | Chip-to-chip gap < 8px | Increase inter-chip gap |

### Exit gate

Every component has its full content and its own clean render. The overall
diagram looks finished **except for arrows and polish**.

---

## Phase 3 — Connect flows

**Produces**: arrows between finalized box positions, with pill labels.

### Why Phase 3 comes after Phase 2

Because Phase 2 froze every `(x, y, w, h)`, Phase 3 can guarantee arrow
integrity deterministically:

- An arrow from component `A` to component `B` has
  `x1 = A.cx, y1 = A.y + A.h` (bottom-center exit) and
  `x2 = B.cx, y2 = B.y` (top-center entry) for a vertical primary flow.
- No guessing. No rework.

### Arrow drawing order

1. **Primary (cross-group) arrows** along the spine — straight vertical
   lines, stroke-width 2.6–3.0, solid, filled arrow marker.
2. **Secondary (intra-group) arrows** — perpendicular to the spine,
   stroke-width 2.0–2.4, solid. Keep them inside the owning band.
3. **Relationship / reference arrows** — dashed (5 3), stroke-width 1.6,
   thin arrow marker.
4. **Failure / sentinel arrows** — red stroke for failure, dashed (2 4)
   for sentinels.

### Arrow geometry formula (vertical diagrams)

For a primary arrow from spine component `A` (top) to `B` (bottom):

```
ARROW_X1 = ARROW_X2 = SPINE_X
ARROW_Y1 = A.y + A.h          # bottom edge of A
ARROW_Y2 = B.y                # top edge of B
LABEL_CY = (ARROW_Y1 + ARROW_Y2) / 2
```

Pill label centered at `(SPINE_X, LABEL_CY)`:

```xml
<g>
  <rect x="{SPINE_X - pill_w/2}" y="{LABEL_CY - 12}"
        width="{pill_w}" height="24" rx="12"
        fill="#ffffff" stroke="#94a3b8" stroke-width="1"/>
  <text x="{SPINE_X}" y="{LABEL_CY + 5}" text-anchor="middle"
        font-family="system-ui" font-size="12" font-weight="600"
        fill="#475569">{LABEL}</text>
</g>
```

### Secondary arrow formula (horizontal, inside a band)

For a helper arrow from primary `P` to tool `T` to the right:

```
ARROW_Y1 = ARROW_Y2 = P.cy     # horizontal line at P's vertical center
ARROW_X1 = P.x + P.w           # P's right edge
ARROW_X2 = T.x                 # T's left edge
LABEL_CX = (ARROW_X1 + ARROW_X2) / 2
LABEL_CY = ARROW_Y1 - 14       # pill above the arrow
```

### Render gate — arrow integrity

After save, verify **for every arrow**:

- [ ] `x1` is within `[source.x, source.x + source.w]`.
- [ ] `y1` is within `[source.y, source.y + source.h]`.
- [ ] `x2` is within `[target.x, target.x + target.w]`.
- [ ] `y2` is within `[target.y, target.y + target.h]`.
- [ ] Primary arrows are straight lines (`x1 == x2` or `y1 == y2`).
- [ ] No primary arrow is crossed by any other line.
- [ ] Every pill label centers on its arrow with no overlap on component
      borders or other pills.

### Common Phase 3 failures

| Symptom in PNG | Cause | Fix |
|---|---|---|
| Arrow "floats" disconnected from source | `x1`/`y1` computed from wrong component bounds | Recompute from Phase 0 table; never eyeball |
| Primary arrow dog-legs | Source and target `cx` differ | Re-align both to `SPINE_X` in Phase 0/2 |
| Pill overlaps box border | `LABEL_CY` too close to source/target edge | Grow the inter-component gap to ≥ 110px |
| Two pills touch | Two adjacent labels computed independently | Offset one vertically or widen the gap |
| Arrow head hidden under a component | Arrow `y2` extends past target's top edge | Stop at `target.y`, not `target.y + 5` |

### Exit gate

All arrows in place, every endpoint inside its component bounds, no pill
overlaps, render clean.

---

## Phase 4 — Polish

**Produces**: structural labels, stage numbers, legend, final typography.

### What gets added in Phase 4

1. **Section-band badges** — rounded rect pills beside the spine, one per
   band (e.g. `INGEST · PRODUCER GROUP`, `CLASSIFY · STRUCTURED JSON`,
   `CONSUME · ALERT · REPORT`).
2. **Circled stage numbers** (if pipeline has ≥ 3 stages) — one per
   primary spine component, touching the left edge of the component.
3. **Legend panel** — populate the placeholder from Phase 2 with the
   arrow line-type key and role colour key.
4. **Typography micro-adjustments** — letter-spacing on section labels,
   monospace on code identifiers, muted fills for footnotes.

### Section-band badge placement

Badges live **beside** the spine in the left gutter, vertically centered
on the band they label. Never as a horizontal line spanning the canvas
— that would cross primary arrows.

```xml
<rect x="60" y="{BAND_CY - 14}" width="280" height="28" rx="14"
      fill="#eef2ff" stroke="#6366f1" stroke-width="1.5"/>
<text x="200" y="{BAND_CY + 5}" text-anchor="middle"
      font-family="system-ui" font-size="12" font-weight="700"
      letter-spacing="2" fill="#4338ca">INGEST · PRODUCER GROUP</text>
```

### Stage number placement

```xml
<circle cx="{SPINE_X - component.w/2 - 24}" cy="{component.cy}" r="14"
        fill="#6366f1"/>
<text x="{SPINE_X - component.w/2 - 24}" y="{component.cy + 5}"
      text-anchor="middle" font-family="system-ui"
      font-size="14" font-weight="700" fill="#ffffff">{N}</text>
```

### Render gate — regression check

Phase 4 is the easiest place to accidentally regress earlier work. Verify:

- [ ] `status == "OK"`.
- [ ] No badge crosses any primary arrow.
- [ ] No stage-number circle overlaps the component it labels.
- [ ] Legend does not overlap any other element.
- [ ] Letter-spacing adjustments did not push any label off its pill.

### Exit gate — Quality Checklist

Run the full Quality Checklist from `SKILL.md`. Every item must pass
before declaring the diagram complete.

---

## Backtracking rules

If a later phase uncovers a bug introduced in an earlier phase:

- **Phase 4 finds a Phase 3 bug**: fix in Phase 3 section, re-render,
  re-do Phase 4 from scratch.
- **Phase 3 finds a Phase 2 bug**: fix the component in Phase 2, re-render,
  then restart Phase 3 (arrow coordinates may have shifted).
- **Phase 2 finds a Phase 0 bug**: go back to the coordinate table, fix
  it, re-scaffold in Phase 1, then resume Phase 2.

Never patch forward. Fix where the bug belongs and re-enter from there.

---

## Budget guide (not hard limits)

| Phase | Typical time for a 10-component diagram |
|---|---|
| Phase 0 — Plan | 10–15 min |
| Phase 1 — Scaffold | 5 min |
| Phase 2 — Fill | 3–5 min per component = 30–50 min |
| Phase 3 — Connect | 10–15 min |
| Phase 4 — Polish | 10 min |

If you find yourself 2× over budget on any phase, stop and reassess: you
are probably skipping a render gate or patching forward instead of
backtracking.
