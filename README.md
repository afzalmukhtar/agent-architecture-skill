# Agent Architecture SVG — Cursor Skill

Generate production-quality SVG architecture diagrams for AI agent systems,
packaged as a [Cursor Agent Skill](https://docs.cursor.com/context/skills).

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

## Installation

### As a Personal Skill (all projects)

```bash
git clone https://github.com/afzal-mukhtar/agent-architecture-skill.git \
  ~/.cursor/skills/build-agent-architecture-svg
```

### As a Project Skill (single repo)

```bash
git clone https://github.com/afzal-mukhtar/agent-architecture-skill.git \
  .cursor/skills/build-agent-architecture-svg
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
SKILL.md                        # Main instructions
references/
  svg-template-patterns.md      # Parameterized SVG building blocks
  interrogation-checklist.md    # Full question bank with SVG mappings
  examples.md                   # Annotated walkthrough + scoring rubric
```

## Companion Skill

This skill pairs with
[ai-engineering-standards-skill](https://github.com/afzal-mukhtar/ai-engineering-standards-skill)
which covers the code-level patterns (Pydantic, prompts, agent classes, async, project structure).

Workflow: **diagram first** (this skill) → **code second** (ai-engineering-standards).

## License

MIT
