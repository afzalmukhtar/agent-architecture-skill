# Agent Architecture SVG — Cursor Skill

Generate production-quality SVG architecture diagrams for AI agent systems,
packaged as a [Cursor Agent Skill](https://docs.cursor.com/context/skills)
with a companion render-gate hook.

Interrogates you about every detail of your agent system — state, tools, data
models, prompt contracts, operational safety — then produces a three-section SVG
that serves as zero-ambiguity context for code generation.

## What It Produces

A fully-specced SVG with three sections:

| Section | Contents |
|---|---|
| **Message Flow** | Agent nodes, router diamond, directional arrows with data labels, parallel agent stacks, failure path annotations |
| **Data Contracts & Safety** | Model definition boxes (typed fields), Prompt Contracts box, Operational Safety box, model relationship arrows |
| **Class Architecture** | UML-style class hierarchy, state model, inheritance lines, method signatures |

## The Cardinal Rule

> **Every box that appears in an arrow label must have its own definition box.**

When this rule holds, Cursor has zero ambiguous decisions when generating code.

## Supported Architecture Types

- **Single agent** — tool-loop agent with tool registry
- **Multi-agent** — orchestrator + N specialized agents with central router
- **Hierarchical** — supervisor agents spawning sub-agent teams

## Phased Construction Workflow

The skill enforces a 5-phase workflow with a **render gate** between every
phase. Each phase has a single deliverable and a visual checkpoint:

| Phase | Deliverable | Render gate check |
|---|---|---|
| **Phase 0 — Plan** | Component list + flow storyboard (markdown, no SVG yet) | Peer/self review of the plan before drawing anything |
| **Phase 1 — Scaffold** | Canvas, spine, empty component rects with IDs | PNG shows aligned empty boxes at the right positions |
| **Phase 2 — Fill** | Component internals (titles, chips, property lists) | Every box is legible at 100%, no text overflow |
| **Phase 3 — Connect** | Arrows + labels between components | Every arrow starts and ends inside a box, no orphans |
| **Phase 4 — Polish** | Legends, section bands, hierarchy, colour semantics | Final pixel review; backtrack if issues appear |

Full cookbook with commands and examples:
[`references/phased-construction.md`](./references/phased-construction.md).

General diagram readability principles:
[`references/diagram-readability-guide.md`](./references/diagram-readability-guide.md).

## Companion Hook: `svg-render-gate`

A non-blocking Cursor hook that runs on every SVG write and reports:

- UTF-8 corruption (stray Windows-1252 bytes, control chars)
- XML well-formedness
- PNG render via `rsvg-convert`

The hook writes `<file>.svg.render-report.json` next to the SVG and feeds a
one-screen summary back to the agent, so the phase gates are enforced
automatically instead of by convention.

Install instructions and report schema:
[`hooks/svg-render-gate/README.md`](./hooks/svg-render-gate/README.md).

## Installation

### Skill — personal (all projects)

```bash
git clone git@github.com:afzalmukhtar/agent-architecture-skill.git \
  ~/.cursor/skills/build-agent-architecture-svg
```

### Skill — project-local (single repo)

```bash
git clone git@github.com:afzalmukhtar/agent-architecture-skill.git \
  .cursor/skills/build-agent-architecture-svg
```

### Hook — one-time user setup

```bash
# From your clone of this repo:
mkdir -p ~/.cursor/hooks/svg-render-gate
cp hooks/svg-render-gate/validate.py ~/.cursor/hooks/svg-render-gate/
chmod +x ~/.cursor/hooks/svg-render-gate/validate.py

# Merge or copy the hook registration
cp hooks/svg-render-gate/hooks.json.example ~/.cursor/hooks.json

# Install rsvg-convert for PNG rendering
brew install librsvg   # macOS
# sudo apt install librsvg2-bin   # Debian/Ubuntu
```

Add the hook's sidecar artifacts to any project that authors SVGs:

```gitignore
# SVG render gate hook artifacts
*.svg.png
*.svg.render-report.json
```

## Usage

The skill triggers when you say things like:
- "Draw the architecture diagram"
- "Build me an agent SVG"
- "Design the system before coding"
- Or before any multi-file agent implementation

### Interrogation Protocol

The skill uses a hybrid approach:

1. **Structured questions** (via checkboxes) for system overview and state
2. **Conversational deep-dive** for per-agent details, data models, and safety
3. **Verification checklist** before generating the SVG

### The 15-Minute Rule

Maps to interview Phase 1 timing:

```
1. Draw happy path flow                              (5 min)
2. Define every data model that crosses an arrow      (3 min)
3. Annotate failure paths on every arrow              (3 min)
4. Add Prompt Contracts + Operational Safety boxes    (2 min)
5. Check: every arrow label has a definition box?     (2 min)
```

## File Structure

```
SKILL.md                              # Main instructions (Phase 0 → Phase 4)
README.md                             # This file
references/
  diagram-readability-guide.md        # Generalised readability principles
  phased-construction.md              # Per-phase mechanics cookbook
  svg-template-patterns.md            # Parameterized SVG building blocks
  interrogation-checklist.md          # Full question bank with SVG mappings
  examples.md                         # Annotated walkthrough + scoring rubric
hooks/
  svg-render-gate/
    README.md                         # Hook install + report schema
    validate.py                       # The hook script
    hooks.json.example                # Snippet for ~/.cursor/hooks.json
```

## Companion Skill

This skill pairs with
[ai-engineering-standards-skill](https://github.com/afzalmukhtar/ai-engineering-standards-skill)
which covers the code-level patterns (Pydantic, prompts, agent classes, async, project structure).

Workflow: **diagram first** (this skill) → **code second** (ai-engineering-standards).

## License

MIT
