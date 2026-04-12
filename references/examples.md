# Example: Async Multi-Agent Task Decomposer

Annotated walkthrough of building the `multi-agent-diagram.svg` from scratch,
showing how iterative refinement raised the diagram from 7/10 to 9.5/10.

## The System

An async multi-agent research pipeline:
- **Planner** decomposes a topic into subtasks
- **Researchers** (parallel) search the web per task
- **Drafter** compiles findings into a report
- **Orchestrator** coordinates via a state-machine router

## Version 1: Happy Path Only (7/10)

### What was drawn

- User → Orchestrator → Router → Planner/Researcher/Drafter flow
- Stacked researcher boxes showing parallelism
- AgentState box with fields
- BaseAgent class with inheritance

### What was missing

| Gap | Impact on generated code |
|---|---|
| No `ResearchResult` model box | Cursor invents `result: str` instead of typed model |
| No failure path on Router → Drafter arrow | Drafter doesn't know what failed |
| No `Report` output model | Writer produces unstructured string |
| No prompt contracts | LLM hallucinations not prevented |
| No retry/MAX_ITERATIONS shown | No safety mechanisms generated |
| No timing proof | Cannot demo concurrency |

### Score breakdown

| Criterion | Score | Issue |
|---|---|---|
| Happy path completeness | 9/10 | All agents shown |
| Data model coverage | 4/10 | Only AgentState defined |
| Failure paths | 2/10 | None drawn |
| Prompt contracts | 0/10 | Not present |
| Operational safety | 2/10 | No retry, no loop cap |
| **Overall** | **7/10** | Generates code with integration bugs |

---

## Version 2: Data Models + Failure Paths (8.5/10)

### What was added

1. **ResearchResult model box** with `status: Literal["success","failed"]`,
   `findings: str`, `error: Optional[str]`, `duration_ms: float`
2. **Report model box** with `summary`, `findings: list[ReportSection]`,
   `gaps: list[str]` (annotated as failed task IDs)
3. **Failure path on Router → Drafter arrow**: "results + list of failed task IDs"
4. **Parallelization note**: `isinstance(r, Exception) → failed`
5. **"Drafter always runs"** annotation
6. **`duration_ms` with "forces timing"** annotation

### What was still missing

| Gap | Why it matters |
|---|---|
| `Task` model not defined | AgentState says `list[Task]` but Task fields are unknown |
| `ReportSection` not defined | Report says `list[ReportSection]` but no definition |
| No prompt contracts | LLM instructions not specified |
| No retry/MAX_ITERATIONS | Safety mechanisms not in diagram |
| No .gitignore artifacts | Minor but part of operational completeness |

### The Rule That Was Violated

> "Every box that appears in an arrow label must have its own definition box."

`ReportSection` appeared in `Report.findings` without a definition.
`Task` appeared in `AgentState.tasks` without a definition.

---

## Version 3: Full Spec (9.5/10)

### What was added

1. **Task model box** (purple): `id: str`, `description: str`,
   `result: Optional[ResearchResult]` with annotation "result is None until
   researcher populates it"

2. **ReportSection model box** (amber): `task_id: str`, `title: str`,
   `content: str`

3. **Prompt Contracts box** (teal):
   - Planner → JSON list[Task], 3-5 subtasks
   - Researcher → ONLY use search results
   - Drafter → Report with Gaps section
   - → must NOT invent data
   - → cite [task_id] per finding

4. **Operational Safety box** (red):
   - MAX_ITERATIONS = 10 (loop cap)
   - LLM retry: 3x exponential backoff
   - Empty LLM response → error + retry
   - .gitignore: `__pycache__/`, `*.pyc`, `.env`, `*.db`, `chroma_db/`, `.venv/`

5. **Class annotations**:
   - OrchestratorAgent: `MAX_ITERATIONS = 10`
   - ResearcherAgent: `retry 3x exp. backoff`, `empty response → error`

6. **Model relationship connectors**:
   - Task.result → ResearchResult (dashed "contains" arrow)
   - ReportSection → Report.findings (dashed "used in" arrow)

### Final Three-Section Layout

```
Section 1: Message-Based Router Flow (y=0 to ~750)
  - User → Orchestrator → Router → Planner/Researchers/Drafter
  - ResearchResult + Report model boxes alongside their producing agents
  - All arrows labeled with data types
  - Failure paths annotated

--- dashed divider ---

Section 2: Data Contracts & Operational Specifications (y=755 to ~940)
  - Task model | ReportSection model | Prompt Contracts | Operational Safety
  - Relationship arrows connecting to Section 1 models

--- dashed divider ---

Section 3: Vanilla Python Unified State & Class Architecture (y=1010 to ~1440)
  - AgentState box with field descriptions
  - Router Parallelization note box
  - BaseAgent → OrchestratorAgent, Planner/Drafter, ResearcherAgent
  - UML inheritance lines
```

### Remaining gap (the 0.5)

No timing proof mechanism was drawn — the `duration_ms` field existed but no
log output format was specified. Fix:

```
Timing proof:
  log: f"[{task_id}] start={start:.2f} end={end:.2f} duration={duration_ms}ms"
  orchestrator logs total_pipeline_ms after gather completes
```

---

## Scoring Rubric

Use this rubric to evaluate any agent architecture diagram:

| Criterion | Weight | 10/10 means | 0/10 means |
|---|---|---|---|
| Happy path flow | 15% | All agents shown with directional arrows and labels | Missing agents or unlabeled arrows |
| Data model coverage | 25% | Every type on every arrow has a definition box | Types referenced but never defined |
| Failure paths | 20% | Every arrow that can fail has a failure annotation | No failure handling shown |
| Prompt contracts | 15% | Every LLM-calling agent has output format + grounding rules | No prompt spec |
| Operational safety | 15% | MAX_ITERATIONS, retry, empty handling, .gitignore all shown | None of these present |
| Timing proof | 5% | Log format + where it fires documented | No timing mechanism |
| Visual clarity | 5% | Clean sections, consistent colors, readable at 100% zoom | Overlapping, cramped, inconsistent |

### Score Bands

| Score | Diagram quality | Code generation impact |
|---|---|---|
| 9-10 | Production spec | Zero integration bugs, zero ambiguous decisions |
| 7-8 | Good draft | Some model fields guessed, failure paths incomplete |
| 5-6 | Skeleton | Major data shapes missing, code will have type errors |
| 3-4 | Napkin sketch | Happy path only, significant rework needed |
| 1-2 | No diagram | Cursor guesses everything |

---

## Key Lessons

1. **Start with data models, not flow** — if you define every model first, the
   arrows practically draw themselves.

2. **The cardinal rule catches 80% of gaps** — "every arrow label needs a
   definition box" is the single most effective verification.

3. **Prompt contracts prevent hallucination** — without them in the diagram,
   they won't appear in the code.

4. **Operational safety is the difference between demo and production** —
   retry, loop caps, and timing are what interviewers look for.

5. **Three sections keep complexity manageable** — flow, data, class
   architecture each have their own visual language and don't interfere.

---

## Common AI Mistakes (documented from real failures)

These failures were observed when AI models attempted to use this skill.
Each mistake has a concrete fix built into the skill constraints.

### Mistake 1: Modifying Source Code Instead of Only the SVG

**What happened**: The AI read the skill, saw that the diagram should show
`MAX_ITERATIONS = 10` and `retry 3× exponential backoff`, then rewrote
`llm.py` and `driver.py` to add those features — even though the user only
asked to improve the SVG diagram.

**Why it's wrong**: This skill produces ONLY `.svg` files. The diagram is a
design spec that DRIVES future code generation. Modifying code to match the
diagram reverses the intended workflow.

**Prevention**: SKILL.md now has Hard Constraint 1: "Before calling
Write/StrReplace, verify the file path ends in `.svg`. If it does not, STOP."

### Mistake 2: Removing Diagram Elements That Don't Exist in Code Yet

**What happened**: The AI read `state.py`, saw no `ResearchResult` or
`ReportSection` class, and removed those model boxes from the SVG. It replaced
typed models with plain `str` because "that's what the code has."

**Why it's wrong**: The diagram represents the INTENDED architecture, not the
current code state. If the user's design includes `ResearchResult` as a typed
model, it stays in the diagram even if `state.py` only has `result: str`.

**Prevention**: SKILL.md now has Hard Constraint 2: "The diagram drives the
code, not the other way around."

### Mistake 3: Canvas Size Oscillation

**What happened**: Across 4 iterations, the canvas went 1300→1650→2000→1400px
wide. Each attempt either cramped content or made it too sparse because the AI
was guessing instead of calculating.

**Why it's wrong**: Canvas size should be deterministic — calculated from
component count and spacing rules, not eyeballed.

**Prevention**: `svg-template-patterns.md` now has exact formulas:
`CANVAS_WIDTH = 1400` (constant) and `CANVAS_HEIGHT` is calculated by summing
all section heights plus gaps.

### Mistake 4: Arrow Labels Overlapping Box Interiors

**What happened**: Labels like "AgentState (tasks added)" were placed at the
same Y coordinate as text inside agent boxes, making both unreadable.

**Why it's wrong**: Arrow labels must sit in the empty space BETWEEN nodes,
never at the same Y as any box's internal text.

**Prevention**: `svg-template-patterns.md` now requires:
`LABEL_Y = floor((SOURCE_BOTTOM + TARGET_TOP) / 2)` with a minimum 15px
clearance from either box edge.

### Mistake 5: Putting 4 Model Boxes in One Row

**What happened**: Section 2 crammed AgentState, Task, Prompt Contracts, and
Operational Safety into a single row. At 1400px width, each box got ~310px —
not enough for monospace code strings.

**Why it's wrong**: Monospace text for field definitions like
`Planner → JSON list[{"id", "description"}]` needs ~520px minimum width.

**Prevention**: Layout rules now mandate a 2×2 grid for Section 2, with each
box getting approximately 620px width.

### Mistake 6: Excessive Reasoning Loops (15+ Thinking Paragraphs)

**What happened**: The AI output 15-20 "I'm now focusing on...",
"I'm now determining...", "I'm now carefully..." paragraphs before each SVG
write action, burning tokens without making progress.

**Why it's wrong**: The skill provides explicit formulas and step-by-step
construction. There's nothing to "determine" — just compute coordinates and
write XML.

**Prevention**: SKILL.md now has Hard Constraint 3: "No thinking loops. One
planning paragraph maximum, then act." The Phase C construction process gives
explicit steps to follow.

### Mistake 7: Researcher Stack Rects Overlapping

**What happened**: The 3 stacked rectangles used 15px X/Y offsets, but the
text was 22px — so the stack visual was barely visible and text overflowed.

**Why it's wrong**: Stack offsets need to be visually distinct. 15px offset
with 22px font means the "back" rect is almost hidden behind the "front" one.

**Prevention**: Template now uses 20px Y offsets and 20px X offsets (40px
total spread), making the parallel-instance visual clear.
