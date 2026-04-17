# SVG Template Patterns

Parameterized SVG building blocks for agent architecture diagrams. Substitute
`{PLACEHOLDER}` values with actual names, colors, positions, and field lists.

## CRITICAL: Scope Reminder

This file supports SVG generation ONLY. Never use these patterns to modify
Python, JavaScript, or any source code file. The output is always a `.svg`.

---

## Layout Algorithm (MANDATORY — follow this, not intuition)

### Step 0: Constants

```
CANVAS_WIDTH  = 1400        # NEVER change this
CENTER_X      = 700         # All centered elements anchor here
LEFT_MARGIN   = 60          # Minimum left edge
RIGHT_MARGIN  = 60          # Minimum right edge
USABLE_WIDTH  = 1280        # CANVAS_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
```

### Step 1: Section 1 — Flow Node Positions

Place each flow node from top to bottom. Use these EXACT gaps:

```
Y_HEADER      = 50          # Section title baseline
Y_USER        = 120         # User node top-left Y
USER_H        = 80
GAP_1         = 80          # Between User bottom and Orchestrator top
Y_ORCH        = Y_USER + USER_H + GAP_1    # = 280
ORCH_H        = 100
GAP_2         = 80          # Between Orchestrator bottom and Router top
Y_ROUTER_TOP  = Y_ORCH + ORCH_H + GAP_2    # = 460
ROUTER_H      = 120         # Diamond is taller than it looks
Y_ROUTER_BOT  = Y_ROUTER_TOP + ROUTER_H    # = 580
```

Side agents (Planner, Drafter) are vertically centered on router:
```
ROUTER_CY     = Y_ROUTER_TOP + ROUTER_H/2
SIDE_AGENT_Y  = ROUTER_CY - SIDE_H/2
```

Bottom agents (Researchers) go below:
```
GAP_3         = 100         # Router bottom to researcher stack top
Y_RESEARCHERS = Y_ROUTER_BOT + GAP_3
RESEARCHER_STACK_H = 160    # 3 stacked rects + text
```

### Step 2: Arrow Label Positions (FORMULA, not guessing)

```
LABEL_Y = floor((SOURCE_BOTTOM + TARGET_TOP) / 2)
```

Verification: `LABEL_Y - SOURCE_BOTTOM >= 15` AND `TARGET_TOP - LABEL_Y >= 15`.
If either fails, increase the gap between the nodes.

For horizontal arrows (Router ↔ Side agents), place labels:
- Outgoing label: `Y = ARROW_Y - 10` (above the arrow line)
- Return label: `Y = ARROW_Y + 20` (below the arrow line)
- Never at `Y = ARROW_Y` (directly on the line)

### Step 3: Section 2 — Data Contracts Grid

```
SECTION2_DIVIDER_Y = Y_RESEARCHERS + RESEARCHER_STACK_H + 60
SECTION2_TITLE_Y   = SECTION2_DIVIDER_Y + 30

# Grid: 2 rows × 2 columns
GRID_GAP_H    = 40          # Horizontal gap between columns
GRID_GAP_V    = 30          # Vertical gap between rows
COL_WIDTH     = (USABLE_WIDTH - GRID_GAP_H) / 2    # ≈ 620px each
COL1_X        = LEFT_MARGIN
COL2_X        = LEFT_MARGIN + COL_WIDTH + GRID_GAP_H

ROW1_Y        = SECTION2_TITLE_Y + 40

# Calculate each box height: 36 (header) + 26 × field_count + 40 (footer)
ROW1_H        = max(BOX1_HEIGHT, BOX2_HEIGHT)       # align row bottoms
ROW2_Y        = ROW1_Y + ROW1_H + GRID_GAP_V
ROW2_H        = max(BOX3_HEIGHT, BOX4_HEIGHT)
```

**ROW 1**: AgentState (left) + Task/primary model (right)
**ROW 2**: Prompt Contracts (left) + Operational Safety (right)

NEVER put 3+ boxes in one row. ALWAYS 2×2.

### Step 4: Section 3 — Class Architecture

```
SECTION3_DIVIDER_Y = ROW2_Y + ROW2_H + 60
SECTION3_TITLE_Y   = SECTION3_DIVIDER_Y + 30

# Two-column layout: State+Notes on left, Classes on right
LEFT_COL_X    = LEFT_MARGIN
LEFT_COL_W    = 580
RIGHT_COL_X   = LEFT_COL_X + LEFT_COL_W + 60
RIGHT_COL_W   = USABLE_WIDTH - LEFT_COL_W - 60

STATE_BOX_Y   = SECTION3_TITLE_Y + 40
PARA_NOTE_Y   = STATE_BOX_Y + STATE_BOX_H + 40

BASE_CLASS_Y  = SECTION3_TITLE_Y + 40
INHERITANCE_BAR_Y = BASE_CLASS_Y + BASE_CLASS_H + 30
CHILDREN_Y    = INHERITANCE_BAR_Y + 50

# Distribute children evenly across right column
CHILD_GAP     = 60          # Between child class boxes (not 30)
```

### Step 5: Canvas Height

```
CANVAS_HEIGHT = CHILDREN_Y + CHILD_CLASS_H + 60   # 60px bottom padding
```

---

## Spacing & Readability Rules (MANDATORY)

### Vertical Spacing

| Between | Minimum gap | Why |
|---|---|---|
| Flow nodes (agent → agent) | **80px** | Room for arrow + 2 label lines |
| Node bottom → arrow label | **15px** | Label needs clearance from box edge |
| Arrow label → next node top | **15px** | Label needs clearance from box edge |
| Multi-line labels | **22px** line-height | Prevents line merging at 13-14px font |
| Section divider → section title | **30px** | Title needs breathing room |
| Section title → first content | **40px** | Content needs separation from header |
| Model box fields | **26px** line-height | Monospace 14px needs 26px spacing |
| Model box footer separator → text | **18px** | Footer text needs padding |

### Horizontal Spacing

| Between | Minimum gap | Why |
|---|---|---|
| Side-by-side boxes (same row) | **40px** | Shadows overlap at < 30px |
| Relationship arrow + label | **70px** | Arrow (20px) + label (50px) needs room |
| Box edge → inner text | **15px** padding | Text must not touch border |

### Text Size Reference

| Element | Font size | Line-height | Family | Weight |
|---|---|---|---|---|
| Section titles | 22px | n/a | system-ui | 700 |
| Agent node titles | 22px | n/a | system-ui | 700 |
| Agent subtitles | 15px | 22px | system-ui | 400 |
| Model box header | 16px | n/a | monospace | 700 |
| Model box fields | 14px | **26px** | monospace | 400 |
| Model box footer | 12px | n/a | system-ui | 600 |
| Arrow labels | 14px | 20px | system-ui | 600 |
| Error annotations | 12px | 18px | system-ui | 600, fill #dc2626 |
| Inline comments | 12px | 18px | monospace | 400, fill #6b7280 |
| Tool badges | 13px | n/a | system-ui | 700 |

### Anti-Patterns (if you do any of these, the output is WRONG)

- **NEVER** place 3+ model boxes in a single row at 1400px width
- **NEVER** use < 40px gap between side-by-side boxes
- **NEVER** use < 26px line-height for model fields at 14px font size
- **NEVER** place arrow labels at the same Y as text inside any box
- **NEVER** use font-size smaller than 11px for anything
- **NEVER** guess canvas height — always calculate from component positions
- **NEVER** modify `.py` or `.js` files — this skill outputs only `.svg`
- **NEVER** remove diagram elements because they don't exist in current code
- **NEVER** start or end an arrow outside the bounding box of its
  source/target — see [diagram-readability-guide.md §3.1](diagram-readability-guide.md)
- **NEVER** use a horizontal line + text as a section-band label; use a
  rounded rect badge instead — horizontal lines cross primary arrows
- **NEVER** reuse a colour for two different roles (e.g. red for both
  "failure" and "classification = CRITICAL")
- **NEVER** skip the render-and-inspect loop — many layout bugs are only
  visible in the rendered PNG, not in the source

For the full generalized readability ruleset (flow conventions, density,
content discipline, iteration loop, pre-ship checklist) see
[diagram-readability-guide.md](diagram-readability-guide.md).

## Defs Block (Always Include)

```xml
<defs>
  <!-- Role-based gradient: copy and rename id per agent role -->
  <linearGradient id="{ROLE}Fill" x1="0%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="{LIGHT_COLOR}"/>
    <stop offset="100%" stop-color="{DARK_COLOR}"/>
  </linearGradient>

  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#1f2937" flood-opacity="0.12"/>
  </filter>

  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="8" markerHeight="8" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569"/>
  </marker>
</defs>

<rect width="100%" height="100%" fill="#fafbfc"/>
```

### Standard Gradient Palette

| Role | Gradient ID | Light stop | Dark stop | Stroke | Title fill |
|---|---|---|---|---|---|
| User | userFill | #eef7ff | #d8ecff | #2b6cb0 | #1e3a5f |
| Orchestrator | orchFill | #e8f0fe | #cfe0ff | #1a73e8 | #174ea6 |
| Router | routerFill | #ccfbf1 | #99f6e4 | #0d9488 | #0f766e |
| Planner | plannerFill | #f3e8ff | #e5d5ff | #7c3aed | #5b21b6 |
| Researcher | researcherFill | #e6f4ea | #d7f0dd | #16a34a | #14532d |
| Writer/Drafter | drafterFill | #fff8f1 | #ffedd5 | #d97706 | #9a3412 |
| Extra 1 | indigoFill | #e8eaf6 | #c5cae9 | #3f51b5 | #1a237e |
| Extra 2 | pinkFill | #fce4ec | #f8bbd0 | #e91e63 | #880e4f |
| Extra 3 | cyanFill | #e0f7fa | #b2ebf2 | #00bcd4 | #006064 |

---

## Agent Node Template

Rounded rectangle with gradient fill, title, and subtitle.

```xml
<g filter="url(#shadow)">
  <rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="20"
        fill="url(#{ROLE}Fill)" stroke="{STROKE}" stroke-width="2.4"/>
  <text x="{CX}" y="{TY}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="22" font-weight="700" fill="{TITLE_FILL}">{AGENT_NAME}</text>
  <text x="{CX}" y="{SY}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="15" fill="#334155">{SUBTITLE}</text>
</g>
```

Parameters:
- `{X}, {Y}`: top-left position
- `{W}`: width (typically 280-300)
- `{H}`: height (typically 80-120)
- `{CX}`: center X = X + W/2
- `{TY}`: title Y = Y + H*0.4
- `{SY}`: subtitle Y = TY + 28

### With Tool Badge

Append inside the `<g>` after subtitle:

```xml
<rect x="{BX}" y="{BY}" width="{BW}" height="26" rx="13"
      fill="#ffffff" stroke="#34a853" stroke-width="1.6"/>
<text x="{BCX}" y="{BTY}" text-anchor="middle"
      font-family="system-ui, -apple-system, sans-serif"
      font-size="13" font-weight="700" fill="#1f6f43">Only tool: {TOOL_NAME}</text>
```

---

## Router Diamond Template

```xml
<g filter="url(#shadow)">
  <polygon points="{CX},{TOP} {RIGHT},{CY} {CX},{BOT} {LEFT},{CY}"
           fill="url(#routerFill)" stroke="#0d9488" stroke-width="2.4"/>
  <text x="{CX}" y="{CY-5}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="22" font-weight="700" fill="#0f766e">Router</text>
  <text x="{CX}" y="{CY+20}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="14" fill="#0f766e">{ROUTING_LOGIC}</text>
</g>
```

Diamond geometry: TOP = CY - 60, BOT = CY + 60, LEFT = CX - 120, RIGHT = CX + 120.

---

## Stacked Boxes (Parallel Agents)

Three offset rectangles to convey N parallel instances. The offsets MUST be
large enough (20px each axis) so the stacking is visually obvious.

```xml
<g filter="url(#shadow)">
  <!-- Back rect (highest, rightmost) -->
  <rect x="{X+40}" y="{Y}"    width="{W}" height="{H}" rx="20"
        fill="url(#{ROLE}Fill)" stroke="#475569" stroke-width="1.8"/>
  <!-- Middle rect -->
  <rect x="{X+20}" y="{Y+20}" width="{W}" height="{H}" rx="20"
        fill="url(#{ROLE}Fill)" stroke="#475569" stroke-width="1.8"/>
  <!-- Front rect (lowest, leftmost — text goes on this one) -->
  <rect x="{X}"    y="{Y+40}" width="{W}" height="{H}" rx="20"
        fill="url(#{ROLE}Fill)" stroke="#475569" stroke-width="1.8"/>
  <!-- Text anchored to FRONT rect center -->
  <text x="{X + W/2}" y="{Y+40 + H*0.4}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="22" font-weight="700" fill="#1f2937">{AGENT_NAME}s</text>
  <text x="{X + W/2}" y="{Y+40 + H*0.4 + 28}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="15" fill="#475569">Spawns exactly len({COLLECTION}) instances</text>
</g>
```

**Stack total height** = H + 40 (the Y offset of the front rect).
Use this when calculating gaps to the next element below.

---

## Model Definition Box

White rectangle with colored header band, monospace fields, and annotation footer.

```xml
<g filter="url(#shadow)">
  <!-- Box body -->
  <rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="8"
        fill="#ffffff" stroke="{BORDER}" stroke-width="2"/>
  <!-- Header band -->
  <rect x="{X}" y="{Y}" width="{W}" height="34" rx="8"
        fill="{HEADER_BG}"/>
  <path d="M {X} {Y+34} L {X+W} {Y+34}" stroke="{BORDER}" stroke-width="1.5"/>
  <!-- Model name -->
  <text x="{CX}" y="{Y+23}" text-anchor="middle"
        font-family="monospace" font-size="16" font-weight="700"
        fill="{TITLE_FILL}">{MODEL_NAME}</text>

  <!-- Fields (repeat, incrementing FY by 22 per field) -->
  <text x="{X+15}" y="{FY}" font-family="monospace" font-size="13"
        fill="#1f2937">{FIELD_NAME}: {FIELD_TYPE}</text>
  <!-- Optional red annotation inline -->
  <text x="{X+W-50}" y="{FY}"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="11" font-weight="700" fill="#dc2626">← {ANNOTATION}</text>

  <!-- Footer separator -->
  <path d="M {X} {FOOTER_Y} L {X+W} {FOOTER_Y}" stroke="#e5e7eb" stroke-width="1"/>
  <!-- Footer note -->
  <text x="{X+15}" y="{FOOTER_Y+19}"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="12" fill="#6b7280">{FOOTER_TEXT}</text>
</g>
```

### Height Calculation

`H = 34 (header) + 22 * field_count + 12 (padding) + 40 (footer area)`

### Color Presets for Model Boxes

| Model role | Border | Header BG | Title fill |
|---|---|---|---|
| Input/Task model | #7c3aed (purple) | #f3e8ff | #5b21b6 |
| Result model | #16a34a (green) | #dcfce7 | #14532d |
| Output/Report model | #d97706 (amber) | #fef3c7 | #78350f |
| Config/Settings | #6b7280 (gray) | #f1f5f9 | #374151 |

---

## Prompt Contracts Box

```xml
<g filter="url(#shadow)">
  <rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="8"
        fill="#ffffff" stroke="#0d9488" stroke-width="2"/>
  <rect x="{X}" y="{Y}" width="{W}" height="32" rx="8" fill="#ccfbf1"/>
  <path d="M {X} {Y+32} L {X+W} {Y+32}" stroke="#0d9488" stroke-width="1.5"/>
  <text x="{CX}" y="{Y+22}" text-anchor="middle"
        font-family="monospace" font-size="16" font-weight="700"
        fill="#0f766e">Prompt Contracts</text>

  <!-- One line per agent (increment by 22) -->
  <text x="{X+15}" y="{LY}" font-family="monospace" font-size="12"
        fill="#374151">{AGENT} → {OUTPUT_FORMAT}</text>
  <!-- Hallucination prevention (red) -->
  <text x="{X+15}" y="{LY}" font-family="monospace" font-size="12"
        font-weight="600" fill="#dc2626">         → must NOT invent data</text>
</g>
```

---

## Operational Safety Box

```xml
<g filter="url(#shadow)">
  <rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="8"
        fill="#ffffff" stroke="#ef4444" stroke-width="2"/>
  <rect x="{X}" y="{Y}" width="{W}" height="32" rx="8" fill="#fef2f2"/>
  <path d="M {X} {Y+32} L {X+W} {Y+32}" stroke="#ef4444" stroke-width="1.5"/>
  <text x="{CX}" y="{Y+22}" text-anchor="middle"
        font-family="monospace" font-size="16" font-weight="700"
        fill="#991b1b">Operational Safety</text>

  <!-- Items (increment by 22) -->
  <text x="{X+15}" y="{LY}" font-family="monospace" font-size="12"
        fill="#1f2937">MAX_ITERATIONS = {N} (loop cap)</text>
  <text x="{X+15}" y="{LY+22}" font-family="monospace" font-size="12"
        fill="#1f2937">LLM retry: {N}× {STRATEGY}</text>
  <text x="{X+15}" y="{LY+44}" font-family="monospace" font-size="12"
        fill="#1f2937">Empty LLM response → error + retry</text>

  <!-- Separator + gitignore -->
  <path d="M {X} {SEP_Y} L {X+W} {SEP_Y}" stroke="#e5e7eb" stroke-width="1"/>
  <text x="{X+15}" y="{SEP_Y+17}" font-family="monospace" font-size="11"
        fill="#6b7280">.gitignore: {ARTIFACTS}</text>
</g>
```

---

## Arrow Patterns

### Solid Flow Arrow (between agents)

```xml
<g stroke="#475569" stroke-width="2.6" fill="none"
   stroke-linecap="round" marker-end="url(#arrow)">
  <path d="M {X1} {Y1} L {X2} {Y2}"/>
</g>
<!-- Label -->
<text x="{LX}" y="{LY}" text-anchor="{ANCHOR}"
      font-family="system-ui, -apple-system, sans-serif"
      font-size="14" font-weight="600" fill="#4b5563">{LABEL}</text>
```

### Dashed Relationship Arrow (model → model)

```xml
<path d="M {X1} {Y1} L {X2} {Y2}"
      stroke="{COLOR}" stroke-width="1.6" stroke-dasharray="5 3"
      fill="none" marker-end="url(#arrow)"/>
<text x="{LX}" y="{LY}"
      font-family="system-ui, -apple-system, sans-serif"
      font-size="10" fill="{COLOR}" font-weight="600">{RELATIONSHIP}</text>
```

### Failure Annotation on Arrow

```xml
<text x="{LX}" y="{LY}" text-anchor="middle"
      font-family="system-ui, -apple-system, sans-serif"
      font-size="12" fill="#9a3412">{FAILURE_TEXT}</text>
```

---

## Section Divider

Use `x2 = CANVAS_WIDTH - LEFT_MARGIN` and `text x = CENTER_X`:

```xml
<line x1="60" y1="{Y}" x2="1340" y2="{Y}"
      stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="8 6"/>
<text x="700" y="{Y+30}" text-anchor="middle"
      font-family="system-ui, -apple-system, sans-serif"
      font-size="22" font-weight="700" fill="#64748b">{SECTION_TITLE}</text>
```

Title goes 30px BELOW the divider line (not above or on it).

---

## UML Class Box

```xml
<g filter="url(#shadow)">
  <!-- Body -->
  <rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="8"
        fill="#ffffff" stroke="{BORDER}" stroke-width="2"/>
  <!-- Header band -->
  <rect x="{X}" y="{Y}" width="{W}" height="40" rx="8" fill="{HEADER_BG}"/>
  <path d="M {X} {Y+40} L {X+W} {Y+40}" stroke="{BORDER}" stroke-width="2"/>
  <!-- Class name -->
  <text x="{CX}" y="{Y+26}" text-anchor="middle"
        font-family="monospace" font-size="18" font-weight="700"
        fill="{TITLE_FILL}">{CLASS_NAME}</text>

  <!-- Fields (increment by 20) -->
  <text x="{X+15}" y="{FY}" font-family="monospace" font-size="14"
        font-weight="700" fill="#1f2937">+ {FIELD}: {TYPE}</text>
  <text x="{X+15}" y="{FY+20}" font-family="monospace" font-size="12"
        fill="#6b7280">  {DESCRIPTION}</text>

  <!-- Methods separator (dashed) -->
  <path d="M {X} {MY} L {X+W} {MY}" stroke="{BORDER}"
        stroke-width="1" stroke-dasharray="4"/>
  <!-- Methods -->
  <text x="{X+15}" y="{MY+20}" font-family="monospace" font-size="14"
        fill="#1f2937">+ {METHOD}(state)</text>
</g>
```

### Inheritance Connector

Hollow triangle pointing UP to parent class:

```xml
<g stroke="#9ca3af" stroke-width="2" fill="none">
  <path d="M {CHILD_CX} {CHILD_TOP} L {CHILD_CX} {JOIN_Y}"/>
  <path d="M {LEFT_CX} {JOIN_Y} L {RIGHT_CX} {JOIN_Y}"/>
  <path d="M {PARENT_CX} {JOIN_Y} L {PARENT_CX} {PARENT_BOT}"/>
</g>
<polygon points="{PARENT_CX-10},{PARENT_BOT} {PARENT_CX},{PARENT_BOT-10} {PARENT_CX+10},{PARENT_BOT}"
         fill="#ffffff" stroke="#9ca3af" stroke-width="2"/>
```

---

## Async/Parallelization Note Box

```xml
<g filter="url(#shadow)">
  <rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="8"
        fill="#f0fdf4" stroke="#059669" stroke-width="2"/>
  <text x="{CX}" y="{Y+25}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="16" font-weight="700" fill="#064e3b">{TITLE}</text>
  <text x="{CX}" y="{Y+48}" text-anchor="middle"
        font-family="monospace" font-size="14" fill="#047857">{CODE_LINE_1}</text>
  <text x="{CX}" y="{Y+68}" text-anchor="middle"
        font-family="monospace" font-size="14" fill="#047857">{CODE_LINE_2}</text>
  <text x="{CX}" y="{Y+90}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="13" fill="#047857">{ANNOTATION}</text>
</g>
```

---

## Timing Proof Annotation

Add to the parallelization note box or as a standalone annotation:

```xml
<text x="{X}" y="{Y}" font-family="monospace" font-size="12"
      fill="#047857">Timing: log f"[{id}] start={start:.2f} end={end:.2f} duration={ms}ms"</text>
<text x="{X}" y="{Y+18}" font-family="monospace" font-size="12"
      fill="#047857">Orchestrator logs total_pipeline_ms after gather completes</text>
```
