---
name: build-agent-architecture-svg
description: >-
  Generate production-quality SVG architecture diagrams for agent systems.
  Interrogates the user about agents, state, tools, data models, prompt
  contracts, and operational safety, then produces a fully-specced three-section
  SVG. Use when designing agent systems, drawing architecture diagrams, building
  multi-agent flows, or before any multi-file agent implementation.
---

# Build Agent Architecture SVG

Interactive skill that produces zero-ambiguity SVG architecture diagrams for
single-agent, multi-agent, and hierarchical agent systems. The diagram serves
as Cursor context so generated code has no integration bugs.

---

## HARD CONSTRAINTS (read these FIRST, before anything else)

### Constraint 1: SVG FILES ONLY — NEVER MODIFY CODE

This skill produces **ONLY `.svg` files**. You MUST NOT:

- Edit, create, or modify any `.py`, `.js`, `.ts`, or other source code file
- Add retry logic, loop caps, or any feature to source code
- "Fix" code to match the diagram — the diagram is the SPEC, code comes later

If the diagram shows `MAX_ITERATIONS = 10` but `driver.py` has no loop cap,
that is CORRECT — the diagram is the design, not documentation of existing code.

**Violation check**: Before calling Write/StrReplace, verify the file path ends
in `.svg`. If it does not, STOP.

### Constraint 2: DIAGRAM = INTENDED ARCHITECTURE, NOT EXISTING CODE

The SVG represents what the system SHOULD look like, not what `state.py` or
any current file contains. Do NOT:

- Read source files and then remove diagram elements that "don't exist in code yet"
- Simplify the diagram to match a partial implementation
- Replace typed models (like `ResearchResult`) with `str` because that's what the code has

**The diagram drives the code, not the other way around.**

### Constraint 3: NO THINKING LOOPS

Do NOT output multiple "I'm now focusing on..." or "I'm now determining..."
paragraphs. Read the skill, gather the information, compute coordinates, write
the SVG. One planning paragraph maximum, then act.

---

## Scope

| System type | Example |
|---|---|
| Single agent (tool loop) | ReAct agent with tool registry |
| Multi-agent (orchestrated) | Planner → Researcher → Writer with central router |
| Hierarchical | Supervisor spawning sub-agent teams |

## The Cardinal Rule

> **Every box that appears in an arrow label must have its own definition box.**
> If a data type crosses an arrow or appears inside another model, it needs a box.

When this rule holds, Cursor has zero decisions to make about data shapes.

---

## Diagram Readability Principles (apply on every diagram)

Full details and rationale in
[references/diagram-readability-guide.md](references/diagram-readability-guide.md).
The principles below are non-negotiable and must be respected during
construction and review.

### Flow direction convention

- **Cross-group transitions (stage boundaries) flow along the primary axis.**
  For vertical diagrams: cross-group = top→bottom straight lines.
  For horizontal diagrams: cross-group = left→right straight lines.
- **Intra-group transitions (expansions inside a stage) flow on the
  perpendicular axis.** Helpers like `driver → stream`, `classifier ↔ LLM`,
  or `alert_manager → JSON` branch sideways and stay inside their owning band.
- Lock all primary-pipeline boxes to a single `SPINE_X` (or `SPINE_Y`) so every
  cross-group arrow is a straight line with `x1 == x2` (or `y1 == y2`).

### Arrow integrity

- Every arrow must start inside the source box bounds and end inside the
  target box bounds. No arrow may originate from or point into empty space.
- Primary flow arrows are straight. Use a single 90° bend for secondary
  arrows only. Never cross a primary arrow.
- Distinguish line types by stroke width + dash pattern, not just colour:
  primary (2.6–3.0px solid) > secondary (2.0–2.4px solid) > relationship
  (1.6px dashed).

### Labels and bands

- Arrow labels live in pill-shaped rects, not as bare floating text.
- Section-band labels use rounded-rect badges beside the spine. **Never** use
  a horizontal line + text as a band label — it will cross primary arrows
  and visually sever the pipeline.
- Use circled stage numbers (1, 2, 3, ...) on the spine for pipelines with
  more than two stages.
- Properties of a component (e.g. `Semaphore(5)`, `retries=3`) render as
  inline chips inside the parent box, not as separate diagram elements.

### Density management

- If a diagram feels crowded, **grow the canvas** or **split regions**. Do
  not shrink fonts below 11px.
- Minimum gap between primary pipeline boxes along the spine: **110px**.
- Minimum gap between spine and reference-panel gutter: **80px**.
- Inner text padding: **18px** from any box border.

### Content discipline

- Prefer concrete constants and type names over generic verbs. Pull values
  directly from source code (`MAX_RETRIES = 3`, `model = "azure/gpt-4.1"`,
  `asyncio.Queue(maxsize=100)`, `response_format = LLMClassificationResponse`).
- Every text element must survive the questions "so what?" and "says who?".

---

## Phase A: Structured Interrogation

Use AskQuestion for blocks 1-2. Use conversational follow-ups for blocks 3-6
since they depend on agent count and complexity.

### Block 1 — System Overview

Ask via AskQuestion:

1. **Architecture type**: single tool-loop / multi-agent orchestrated / hierarchical
2. **Agent count and names**: list each agent with a one-line role
3. **Coordination**: single orchestrator / multiple coordinators / peer-to-peer

### Block 2 — State Architecture

Ask via AskQuestion:

1. **State model**: global unified state / per-agent isolated state / hybrid
2. **State fields**: list field names and types for the shared state
3. **Write ownership**: which agent writes which state fields?

### Block 3 — Per-Agent Deep Dive

For EACH agent named in Block 1, ask conversationally:

- Does it call an LLM? Which model/provider?
- Does it have tools? List each: `name → what it does`
- Shared tool pool or dedicated tools per agent?
- What data model does it consume (input)?
- What data model does it produce (output)?
- Failure handling: retry with backoff? error field on result? propagate exception?

### Block 4 — Data Models

For every model that crosses an agent boundary:

- Field name, type, default value, is it Optional?
- Nesting: which models contain which? (e.g. `Task.result: Optional[ResearchResult]`)
- Literal/enum fields: what are the allowed values?
- Which fields are `None` until a specific agent populates them?

### Block 5 — Prompt Contracts

For each LLM-calling agent:

- What output format does the prompt demand? (JSON, markdown, free text)
- Output constraints? (max items, required sections, field names)
- Grounding rules? (cite sources, use task_id, must-not-invent)
- Hallucination prevention? (only use provided data, no external knowledge)

### Block 6 — Operational Safety

- MAX_ITERATIONS or loop cap for orchestrator?
- LLM retry strategy: count, backoff type, empty response handling?
- Concurrency: asyncio.gather, thread pool, sequential?
- Timing: duration fields on models? log format for proving concurrency?
- Runtime artifacts for .gitignore?

---

## Phase B: Refinement Checklist

After gathering all answers, summarize the full system design back to the user,
then ask these verification questions:

1. "Does every arrow label have a defined model box?"
2. "Are failure paths annotated on every arrow?"
3. "Is there a timing proof mechanism showing logged durations?"
4. "Does every Optional field say when it gets populated?"

Iterate until the user confirms. Then generate the SVG.

---

## SVG Structure: Three Sections

### Section 1 — Message Flow

The happy-path and failure-path flow between agents.

Elements to draw:
- **Agent nodes**: rounded rects with gradient fills, title + subtitle
- **Router diamond**: if orchestrator uses a routing function
- **Directional arrows**: solid lines with labels showing what data flows
- **Parallel agents**: stacked boxes (offset rects) for fan-out instances
- **Tool badges**: small rounded rect inside agent node listing tools
- **Model preview boxes**: placed near producing agent, showing key fields
- **Failure annotations**: red text on arrows showing what happens on error

Key rules:
- Every arrow has a label saying what data structure flows on it
- Failure path annotated on every arrow that can fail
- Parallel execution shown with stacked boxes + "spawns N instances" note
- "Always runs" annotation on any agent that must execute even if upstream fails

### Section 2 — Data Contracts & Operational Safety

Separated from Section 1 by a dashed line with section title.

Elements to draw:
- **Model definition boxes**: white rect with colored header band, monospace
  field list (name: type = default), separator line, annotation footer
- **Prompt Contracts box** (teal border): one line per LLM-calling agent
  stating output format, constraints, and grounding rules
- **Operational Safety box** (red border): MAX_ITERATIONS, retry strategy,
  empty response handling, timing log format, .gitignore artifacts
- **Relationship connectors**: dashed arrows between models showing nesting
  (e.g. "contains", "used in X.field")

Key rules:
- Every model referenced in Section 1 arrows MUST have a definition box here
- Every Optional field has a red annotation: "None until X populates it"
- Prompt contracts include at least one hallucination prevention rule

### Section 3 — Class Architecture

Separated by a dashed line with section title.

Elements to draw:
- **State model box**: UML-style with all fields and descriptions
- **BaseAgent class**: fields + abstract methods
- **Concrete agent classes**: inheriting from BaseAgent, showing overrides
- **Inheritance lines**: with hollow triangle marker
- **Annotations**: MAX_ITERATIONS on orchestrator, retry on LLM-calling agents

Key rules:
- Class boxes use UML style: header band, fields section, methods section
- Inheritance shown with hollow triangle pointing to parent
- Every agent class shows its specific operational details (retry, tools, etc.)

---

## SVG Visual Language

Read [references/svg-template-patterns.md](references/svg-template-patterns.md)
for parameterized SVG building blocks including gradients, shadows, model boxes,
arrows, class boxes, and the color scheme.

### Color Assignments

| Role | Fill gradient | Stroke | Text |
|---|---|---|---|
| Orchestrator | blue #e8f0fe → #cfe0ff | #1a73e8 | #174ea6 |
| Planner | purple #f3e8ff → #e5d5ff | #7c3aed | #5b21b6 |
| Researcher | green #e6f4ea → #d7f0dd | #16a34a | #14532d |
| Writer/Drafter | amber #fff8f1 → #ffedd5 | #d97706 | #9a3412 |
| Router | teal #ccfbf1 → #99f6e4 | #0d9488 | #0f766e |
| Safety/Error | red #fef2f2 | #ef4444 | #991b1b |
| Prompt contracts | teal #ccfbf1 | #0d9488 | #0f766e |
| User | light blue #eef7ff → #d8ecff | #2b6cb0 | #1e3a5f |

For agents beyond these roles, cycle through: indigo, pink, cyan, lime.

### Typography

- Titles: `system-ui, -apple-system, sans-serif`, 22px, weight 700
- Subtitles: same family, 15px, weight 400
- Model fields: `monospace`, 13px
- Annotations: `system-ui`, 11-12px, weight 600, fill #dc2626 for warnings

### Layout — EXACT FORMULAS (not suggestions)

**Canvas sizing formula** (calculate, do not guess):

```
CANVAS_WIDTH  = 1400  (constant — never change this)
CENTER_X      = 700   (constant — all centered elements use this)

SECTION_1_HEIGHT = 120 + (AGENT_COUNT × 160)   (flow section)
SECTION_2_HEIGHT = 60 + 2 × (MAX_BOX_HEIGHT + 30)  (2×2 grid)
SECTION_3_HEIGHT = 60 + STATE_BOX_HEIGHT + 40 + PARA_NOTE_HEIGHT + 60 + BASE_CLASS_HEIGHT + 80 + CHILD_CLASS_HEIGHT

CANVAS_HEIGHT = SECTION_1_HEIGHT + 80 + SECTION_2_HEIGHT + 80 + SECTION_3_HEIGHT + 60
```

**Flow node vertical positioning** (Section 1):

```
USER_Y        = 120
ORCH_Y        = USER_Y + USER_H + 80     (80px gap minimum)
ROUTER_Y      = ORCH_Y + ORCH_H + 70
SIDE_AGENTS_Y = ROUTER_CY - SIDE_H/2     (vertically centered on router)
BOTTOM_AGENT_Y = ROUTER_Y + ROUTER_H + 80
```

**Arrow label Y formula** (prevents overlap with boxes):

```
LABEL_Y = (SOURCE_BOTTOM + TARGET_TOP) / 2
```

Never place a label at the same Y coordinate as text inside a box.
Never place a label within 15px of a box edge.

**Section 2 grid** (2 rows × 2 columns, ALWAYS):

```
ROW1_LEFT_X   = 60       ROW1_RIGHT_X  = CENTER_X + 40
ROW1_Y        = section2_title_y + 40
BOX_WIDTH     = (CANVAS_WIDTH - 60 - 60 - 40) / 2   (≈ 620px each)

ROW2_Y        = ROW1_Y + ROW1_HEIGHT + 30
```

Never put 3 or 4 boxes in one row. Always 2×2.

**Section 3 child classes** — evenly distributed:

```
TOTAL_CHILDREN_WIDTH = sum(child_widths) + (N-1) × 60
START_X = CENTER_X - TOTAL_CHILDREN_WIDTH / 2
```

- Agent nodes: 280-320px wide, 80-130px tall
- Model boxes: width from formula above, height = 36px header + 26px × field_count + 40px footer
- Multi-line text: **26px line-height** for 14px font, **22px** for 13px font
- Full spacing reference: [references/svg-template-patterns.md](references/svg-template-patterns.md)

---

## Phase C: Phased Construction (Phase 0 → Phase 4)

**The single most important rule of this skill**: do NOT write the SVG
end-to-end and render once at the end. That approach fails every time because
layout, content, and connection bugs stack invisibly until the final render.

Instead, build the SVG in five strict phases. Each phase has an entry gate,
an exit gate, and a mandatory render checkpoint between it and the next.
Never skip a render gate to save time — the time saved is paid back 10×
in debugging.

Detailed per-phase mechanics (commands, good/bad examples, common failures)
live in [references/phased-construction.md](references/phased-construction.md).
The main skill defines **what** each phase does; the reference doc defines
**how** to execute it.

### The render gate (automated)

A user-level hook at `~/.cursor/hooks.json` watches every `.svg` write. After
each edit it automatically:

1. Parses XML with `xml.etree.ElementTree`.
2. Scans for corrupted bytes (`0x00–0x1F` control chars, `0x80–0x9F`
   Windows-1252 garbage).
3. Renders the SVG to a sibling PNG via `rsvg-convert`.
4. Writes a JSON report to `<svg>.render-report.json` and returns a summary
   to the agent as `additional_context`.

You must **read the report after every write** and only advance to the next
phase when the report says `status: "OK"` and the rendered PNG visually
matches the phase's exit criteria.

The hook is non-blocking: it reports failures, it doesn't refuse the write.
The skill is responsible for honoring the report.

### Phase 0 — Plan (no XML yet)

**Goal**: produce a complete component inventory and coordinate plan
**before** any XML is written.

**Entry gate**: Phase A (interrogation) and Phase B (refinement) complete.

**Do**:
1. List every component by name and band: primary-pipeline, tool/helper,
   reference panel, legend.
2. Decide the primary axis (vertical or horizontal) and the `SPINE_X`
   (or `SPINE_Y`) coordinate.
3. Draft a coordinate table: each component gets `(x, y, w, h)` and its band.
4. Estimate `viewBox` width and height from the table.

**Exit gate**: you can answer, for every component: "where does it go and
how big is it?" without running any code.

No render yet — Phase 0 produces a text plan, not SVG.

### Phase 1 — Scaffold (empty boxes with titles)

**Goal**: prove the layout plan is visually plausible before investing in
content.

**Entry gate**: Phase 0 coordinate table ready.

**Do**:
1. Write the SVG header, `viewBox`, and `<defs>` (gradients, shadow, arrow
   markers).
2. For each component in the plan, draw a **plain rounded rect with a single
   centered title text**. No fields, no chips, no gradients, no borders
   beyond a single stroke, no arrows.
3. Save the file.

**Render gate** (mandatory):
- Read the hook's render report.
- Open the PNG and verify: no overlaps, gutters clear, spine aligned,
  `viewBox` fits content, no component clipped at an edge.

**Exit gate**: layout looks right at skeleton level. If anything is wrong,
**fix the plan and the skeleton** before moving on — never proceed with a
broken layout.

### Phase 2 — Fill components (one at a time)

**Goal**: add full content to each component without letting errors compound.

**Entry gate**: Phase 1 skeleton renders cleanly.

**Do**, per component (never in parallel):
1. Pick one component from the plan.
2. Add its full content: fields, chips, typography, colours, gradients,
   borders, inline annotations.
3. Save the file.
4. **Render gate**: read the report, open the PNG, verify that component
   alone for: text overflow, chip alignment, border/colour correctness,
   no encroachment into neighbouring components.
5. Only when the component is clean, move to the next.

**Exit gate**: every component has its full content and passes its
individual render gate.

**Common trap**: filling two components in one edit. Don't. If the render
regresses, you lose the ability to attribute which component caused it.

### Phase 3 — Connect flows

**Goal**: draw arrows between finalized box positions. Because Phase 2 has
frozen every box's `(x, y, w, h)`, every arrow can guarantee its endpoints
are inside the source and target bounds.

**Entry gate**: every component filled and individually rendered clean.

**Do**:
1. Draw primary (cross-group) arrows first — straight lines along the spine.
2. Draw secondary (intra-group) arrows — perpendicular to the spine, kept
   inside their band.
3. Add pill-style labels on each arrow.
4. Add failure/sentinel annotations where the interrogation specified them.
5. Save the file.

**Render gate**: verify arrow integrity — every `x1/y1` inside the source
box, every `x2/y2` inside the target box, no primary arrow crossed by
another line, no label overlapping a box border.

**Exit gate**: all arrows in place, render clean.

### Phase 4 — Polish

**Goal**: final visual pass for structure labels, legend, stage numbers,
typography micro-adjustments.

**Entry gate**: Phase 3 arrows in place and clean.

**Do**:
1. Add section-band badges (rounded rects, not horizontal lines).
2. Add circled stage numbers on the spine if there are more than two stages.
3. Add the legend panel if the diagram uses multiple arrow line types.
4. Adjust pill positions, letter-spacing, any final typography tweaks.
5. Save the file.

**Render gate**: final full-diagram render. Visually confirm nothing
introduced in Phase 4 broke anything from Phase 3 (badges crossing arrows,
legend overlapping a component, etc.).

**Exit gate**: Quality Checklist below passes in full.

---

## Quality Checklist

Before declaring the diagram complete, verify ALL items:

**Content completeness:**
- [ ] Every data type referenced in an arrow label has its own model box
- [ ] Every agent that calls LLM has retry + empty response annotation
- [ ] Every parallel execution path has failure isolation shown
- [ ] Prompt contracts exist for every LLM-calling agent
- [ ] MAX_ITERATIONS / loop cap shown on orchestrator class box
- [ ] Timing proof: log format annotated (e.g. `f"[{id}] duration={ms}ms"`)
- [ ] .gitignore artifacts listed in Operational Safety box
- [ ] Resilience annotation: which agent "always runs" even if upstream fails
- [ ] All Optional fields annotated with "None until X populates it"
- [ ] No model appears in another model's fields without its own definition box
- [ ] Section dividers present between all three sections
- [ ] All arrows have labels; no unlabeled connections
- [ ] Every factual claim (retries, timeouts, models, queue sizes) is backed
      by a concrete constant or type from source, not a generic verb

**Layout correctness (CRITICAL — most common failure point):**
- [ ] viewBox width = 1400 (not wider, not narrower) — unless the diagram
      uses a bespoke vertical/pipeline layout, in which case `viewBox`
      matches actual content extent
- [ ] viewBox height matches calculated total (not guessed)
- [ ] Every flow node gap ≥ 80px (measure: next_Y - prev_Y - prev_H ≥ 80)
- [ ] Every arrow label Y = (source_bottom + target_top) / 2 (±5px)
- [ ] No arrow label shares a Y coordinate with text inside any box
- [ ] Section 2 has exactly 2 rows of 2 boxes (not 3 or 4 in a row)
- [ ] Row gap in Section 2 ≥ 30px
- [ ] Horizontal gap between side-by-side boxes ≥ 40px
- [ ] No text smaller than 11px
- [ ] Model fields use 14px font with 26px line-height
- [ ] SVG is well-formed XML with proper viewBox

**Flow convention (pipeline / multi-stage diagrams):**
- [ ] Every cross-group transition is a straight line along the primary axis
      (vertical for vertical diagrams, horizontal for landscape diagrams)
- [ ] Every intra-group transition is on the perpendicular axis and stays
      inside its owning band
- [ ] All primary-pipeline boxes share a single spine coordinate
- [ ] Every arrow starts inside the source box bounds and ends inside the
      target box bounds
- [ ] Primary arrows are measurably thicker than secondary arrows
- [ ] Dashed lines are used only for references/relationships, never for
      primary flow
- [ ] Section band labels use rect badges, not horizontal lines that cross
      arrows
- [ ] Each colour maps to exactly one role (no red for both failure and
      classification)

**Render validation:**
- [ ] SVG rendered to PNG and visually inspected at least once
- [ ] No corrupted bytes / control characters in source (`xxd` clean)
- [ ] No arrow visibly broken, no label overlapping a box border in the PNG

**Scope compliance:**
- [ ] Only `.svg` files were written (no `.py`, `.js`, `.ts` files touched)
- [ ] No source code was modified to "match" the diagram

---

## The 15-Minute Design Rule

This maps to interview Phase 1 timing:

```
1. Draw happy path flow                              (5 min)
2. Define every data model that crosses an arrow      (3 min)
3. Annotate failure paths on every arrow              (3 min)
4. Add Prompt Contracts + Operational Safety boxes    (2 min)
5. Check: every arrow label has a definition box?     (2 min)
```

---

## Additional Resources

- Per-phase construction mechanics (commands, good/bad examples, common
  failures, render-gate cookbook):
  [references/phased-construction.md](references/phased-construction.md)
- SVG building blocks: [references/svg-template-patterns.md](references/svg-template-patterns.md)
- Generalized readability guidelines (flow conventions, arrow integrity,
  density, typography, anti-patterns, pre-ship checklist):
  [references/diagram-readability-guide.md](references/diagram-readability-guide.md)
- Full question bank with SVG mappings: [references/interrogation-checklist.md](references/interrogation-checklist.md)
- Annotated example walkthrough: [references/examples.md](references/examples.md)

---

## Automated render gate (companion hook)

The skill is accompanied by a user-level hook at `~/.cursor/hooks.json`
that runs after every `.svg` write:

- Hook definition: `~/.cursor/hooks.json` (event: `afterFileEdit`, matcher:
  `Write`)
- Script: `~/.cursor/hooks/svg-render-gate/validate.py`
- Output: JSON report at `<svg-path>.render-report.json` plus a sibling
  `<svg-path>.png` rendered preview
- Behavior: **non-blocking**. The hook reports problems; the skill must
  read the report and honor it.

The hook replaces every manual render step in the phases above. If the hook
is missing (e.g. on a machine without this user setup), the skill falls back
to running the same commands manually — see
[references/phased-construction.md](references/phased-construction.md)
§ Manual fallback.

### Gitignore recommendation

The hook produces two sibling files next to every `.svg` it validates:

```
<name>.svg
<name>.svg.png                  # rendered preview
<name>.svg.render-report.json   # validation report
```

Both are regenerated on every SVG save. Add to the project's `.gitignore`:

```
*.svg.png
*.svg.render-report.json
```
