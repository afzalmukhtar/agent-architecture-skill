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

### Layout

- Canvas width: 1300px (fixed)
- Canvas height: calculated based on content (start at 800, add ~300 per section)
- Section dividers: dashed line at full width with centered section title above
- Model boxes: 250-350px wide, height = 32px header + 22px per field + 40px footer
- Agent nodes: 280-300px wide, 80-120px tall

---

## Quality Checklist

Before declaring the diagram complete, verify ALL items:

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
- [ ] SVG is well-formed XML with proper viewBox

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

- SVG building blocks: [references/svg-template-patterns.md](references/svg-template-patterns.md)
- Full question bank with SVG mappings: [references/interrogation-checklist.md](references/interrogation-checklist.md)
- Annotated example walkthrough: [references/examples.md](references/examples.md)
