# SVG Template Patterns

Parameterized SVG building blocks for agent architecture diagrams. Substitute
`{PLACEHOLDER}` values with actual names, colors, positions, and field lists.

## Spacing & Readability Rules (MANDATORY)

These minimums prevent text overlap and mushed elements.

### Vertical Spacing

| Between | Minimum gap | Why |
|---|---|---|
| Flow nodes (agent → agent) | **80px** | Room for arrow + 2 label lines |
| Node bottom → arrow label | **25px** | Label needs clearance from box edge |
| Arrow label → next node top | **25px** | Label needs clearance from box edge |
| Multi-line labels | **22px** line-height | Prevents line merging at 13-14px font |
| Section divider → section title | **30px** | Title needs breathing room |
| Section title → first content | **35px** | Content needs separation from header |
| Model box fields | **26px** line-height | Monospace 14px needs 26px spacing |
| Model box footer separator → text | **18px** | Footer text needs padding |

### Horizontal Spacing

| Between | Minimum gap | Why |
|---|---|---|
| Side-by-side boxes (same row) | **40px** | Shadows overlap at < 30px |
| Relationship arrow + label | **70px** | Arrow (20px) + label (50px) needs room |
| Box edge → inner text | **20px** padding | Text must not touch border |

### Layout Strategy

- **Canvas width**: 1400px (not 1300px — the extra 100px prevents right-edge cramming)
- **Canvas height**: calculate as sum of sections + gaps, never guess
- **Section 2 (Data Contracts)**: use **2 rows of 2 boxes** instead of 4 across
  - Row 1: State model (left, ~380px) + primary data model (right, ~360px)
  - Row 2: Prompt Contracts (left, ~520px) + Operational Safety (right, ~460px)
  - Row gap: **30px** between rows
- **Section 3 (Classes)**: child class boxes need **30px** minimum gap between them
- **Arrow labels**: place at the **midpoint** between source and target, never overlapping either box

### Text Size Reference

| Element | Font size | Family | Weight |
|---|---|---|---|
| Section titles | 22px | system-ui | 700 |
| Agent node titles | 22px | system-ui | 700 |
| Agent subtitles | 14px | system-ui | 400 |
| Model box header | 16px | monospace | 700 |
| Model box fields | 14px | monospace | 400 |
| Model box footer | 11px | system-ui | 600 |
| Arrow labels | 13px | system-ui | 600 |
| Error annotations | 11px | system-ui | 600, fill #dc2626 |
| Inline comments | 12px | monospace | 400, fill #6b7280 |
| Tool badges | 13px | system-ui | 700 |

### Anti-Patterns

- **NEVER** place 4+ model boxes in a single row at 1300-1400px width
- **NEVER** use < 20px gap between side-by-side boxes
- **NEVER** use < 22px line-height for multi-line text at 13-14px font size
- **NEVER** place arrow labels at the same Y as box text inside the box
- **NEVER** use font-size 10px for anything — minimum readable size is 11px

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

Three offset rectangles to convey N parallel instances:

```xml
<g filter="url(#shadow)">
  <rect x="{X+30}" y="{Y}"    width="{W}" height="{H}" rx="20"
        fill="url(#{ROLE}Fill)" stroke="#475569" stroke-width="1.8"/>
  <rect x="{X+15}" y="{Y+20}" width="{W}" height="{H}" rx="20"
        fill="url(#{ROLE}Fill)" stroke="#475569" stroke-width="1.8"/>
  <rect x="{X}"    y="{Y+40}" width="{W}" height="{H}" rx="20"
        fill="url(#{ROLE}Fill)" stroke="#475569" stroke-width="1.8"/>
  <text x="{CX}" y="{TY}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="22" font-weight="700" fill="#1f2937">{AGENT_NAME}s</text>
  <text x="{CX}" y="{SY}" text-anchor="middle"
        font-family="system-ui, -apple-system, sans-serif"
        font-size="15" fill="#475569">Spawns exactly len({COLLECTION}) instances</text>
</g>
```

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

```xml
<line x1="50" y1="{Y}" x2="1250" y2="{Y}"
      stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="8 6"/>
<text x="650" y="{Y-10}" text-anchor="middle"
      font-family="system-ui, -apple-system, sans-serif"
      font-size="20" font-weight="700" fill="#64748b">{SECTION_TITLE}</text>
```

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
