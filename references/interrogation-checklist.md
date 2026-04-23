# Interrogation Checklist

Complete question bank for the hybrid interrogation protocol. Each question
maps to a specific SVG element so nothing is left unspecified.

## Block 1 — System Overview

Use AskQuestion tool for these.

| # | Question | Answer format | SVG element produced |
|---|---|---|---|
| 1.1 | What type of agent system? | Single choice: single tool-loop / multi-agent orchestrated / hierarchical | Determines overall layout: single column vs fan-out vs nested |
| 1.2 | List every agent: name + one-line role | Free text list | One Agent Node per entry in Section 1 |
| 1.3 | Is there a central orchestrator? | Yes/No + name | Orchestrator Node at top of flow |
| 1.4 | Is there a router or state machine? | Yes/No + routing logic summary | Router Diamond in flow |
| 1.5 | What is the entry point? (user input / API / cron) | Single choice | User/Entry Node at very top |

### Example Answers (Multi-Agent Decomposer)

- 1.1: Multi-agent orchestrated
- 1.2: Planner (decomposes topic into tasks), Researcher (searches per task), Drafter (compiles report)
- 1.3: Yes — OrchestratorAgent
- 1.4: Yes — routes by `state.sender` field
- 1.5: User provides research topic

---

## Block 2 — State Architecture

Use AskQuestion tool for these.

| # | Question | Answer format | SVG element produced |
|---|---|---|---|
| 2.1 | Global unified state or per-agent isolated state? | Single choice | State Model Box shape in Section 3 |
| 2.2 | List every field on the shared state | `name: type` list | Fields inside State Model Box |
| 2.3 | Which agent writes which state fields? | Agent → field mapping | Annotation comments in State Model Box |
| 2.4 | Does state carry conversation history? | Yes/No + field name | `messages: list[dict]` field or equivalent |

### Example Answers

- 2.1: Global unified (AgentState)
- 2.2: `tasks: list[Task]`, `sender: str`, `next: str`, `messages: list[dict]`
- 2.3: Planner writes `tasks`, Orchestrator writes `sender`/`next`, Researcher writes `task.result`
- 2.4: Yes — `messages: list[dict]`

---

## Block 3 — Per-Agent Deep Dive

Ask conversationally for EACH agent. Repeat this block N times.

| # | Question | Answer format | SVG element produced |
|---|---|---|---|
| 3.1 | Does `{AGENT}` call an LLM? Which model? | Yes/No + model name | LLM annotation on agent class box |
| 3.2 | Does `{AGENT}` have tools? List each. | `name → description` list | Tool Badge on agent node; tools field in class box |
| 3.3 | Shared tool pool or dedicated tools? | Single choice | Tool registry note in Section 3 |
| 3.4 | What data does `{AGENT}` receive as input? | Model name + key fields | Arrow label entering agent; Model Box if new |
| 3.5 | What data does `{AGENT}` produce as output? | Model name + key fields | Arrow label leaving agent; Model Box if new |
| 3.6 | How does `{AGENT}` handle failure? | Retry/error field/propagate/skip | Red annotation on agent's outgoing arrow |
| 3.7 | Does `{AGENT}` always run even if upstream fails? | Yes/No | "Always runs" resilience annotation |

### Example Answers (Researcher)

- 3.1: Yes — litellm with `gpt-4o-mini`
- 3.2: `web_search → DuckDuckGo search via ddgs`
- 3.3: Dedicated (only researcher has web_search)
- 3.4: Receives `AgentState` with a single `Task` assigned
- 3.5: Produces `ResearchResult` with status/findings/error/duration_ms
- 3.6: Sets `status: "failed"` + `error: str` on ResearchResult; never propagates
- 3.7: No — only runs when Planner succeeds

---

## Block 4 — Data Models

Ask conversationally. One pass per model discovered in Block 3.

| # | Question | Answer format | SVG element produced |
|---|---|---|---|
| 4.1 | For `{MODEL}`: list all fields with types and defaults | `name: type = default` list | Model Definition Box fields |
| 4.2 | Which fields are Optional? What are they None until? | Field → "None until {AGENT} populates" | Red annotation on Optional fields |
| 4.3 | Does `{MODEL}` contain other models? Which? | Nesting list | Dashed "contains" arrow between boxes |
| 4.4 | Any Literal or enum fields? Allowed values? | Field → `Literal["a","b"]` | Literal type shown in field list |
| 4.5 | Is `{MODEL}` used inside another model's field list? | Yes → which parent model and field | Dashed "used in X.field" arrow |

### Example Answers (ResearchResult)

- 4.1: `status: Literal["success","failed"]`, `findings: str`, `error: Optional[str] = None`, `duration_ms: float`
- 4.2: `error` is None when status is "success"; `result` on Task is None until Researcher populates
- 4.3: No nested models
- 4.4: `status: Literal["success","failed"]`
- 4.5: Yes — used in `Task.result: Optional[ResearchResult]`

---

## Block 5 — Prompt Contracts

Ask conversationally. One pass per LLM-calling agent.

| # | Question | Answer format | SVG element produced |
|---|---|---|---|
| 5.1 | What output format does `{AGENT}`'s prompt demand? | JSON / markdown / free text / structured | Line in Prompt Contracts box |
| 5.2 | Output constraints? | Max items, required sections, field names | Constraint annotation in box |
| 5.3 | Grounding rules? | Cite sources / use task_id / only provided data | Grounding line in box |
| 5.4 | Hallucination prevention? | Must-not-invent rule | Red "must NOT invent data" line |

### Example Answers (Drafter)

- 5.1: Produces Report model (structured JSON → Pydantic)
- 5.2: Must include `gaps` section listing failed task IDs
- 5.3: Cite `[task_id]` per finding
- 5.4: Must NOT invent data beyond provided findings

---

## Block 6 — Operational Safety

Ask conversationally.

| # | Question | Answer format | SVG element produced |
|---|---|---|---|
| 6.1 | MAX_ITERATIONS or loop cap? | Number | Operational Safety box line + class annotation |
| 6.2 | LLM retry: count, backoff type, empty handling? | `3× exponential backoff` etc. | Safety box line + agent class annotation |
| 6.3 | Concurrency mechanism? | asyncio.gather / thread pool / sequential | Parallelization Note Box code line |
| 6.4 | Failure isolation in concurrency? | return_exceptions=True / try-except per task | Parallelization Note Box code line |
| 6.5 | Timing: duration fields + log format? | Field names + format string | Timing Proof Annotation |
| 6.6 | Runtime artifacts for .gitignore? | File/folder list | Safety box footer |

### Example Answers

- 6.1: MAX_ITERATIONS = 10
- 6.2: 3× exponential backoff; empty response → error + retry
- 6.3: asyncio.gather with return_exceptions=True
- 6.4: `isinstance(r, Exception) → failed`; Drafter always runs with gaps
- 6.5: `duration_ms: float` on ResearchResult; log `f"[{id}] duration={ms}ms"`
- 6.6: `__pycache__/`, `*.pyc`, `.env`, `*.db`, `chroma_db/`, `usage.json`, `.venv/`

---

## Post-Interrogation Verification

After all 6 blocks, run these checks BEFORE generating SVG:

| # | Verification question | If NO → action |
|---|---|---|
| V.1 | Does every arrow label reference a defined model? | Ask user to define the missing model |
| V.2 | Does every model with Optional fields say when they get populated? | Ask user: "When does {field} get set?" |
| V.3 | Is there a timing proof mechanism? | Ask: "How will you prove concurrency in demo?" |
| V.4 | Does every LLM-calling agent have a prompt contract? | Ask: "What does {agent}'s prompt instruct?" |
| V.5 | Are failure paths shown on every arrow that can fail? | Ask: "What happens when {agent} fails?" |
| V.6 | Is there a resilience annotation? (which agent always runs) | Ask: "Does any agent run even if upstream fails?" |

Only proceed to SVG generation when ALL verifications pass.
