# emage.code — Claude Code Patterns Adapted for VS Code Copilot

This document maps the key patterns discovered in the Claude Code prompt architecture to their VS Code + GitHub Copilot equivalents, identifying what's directly usable, what needs adaptation, and what requires creative workarounds.

## Pattern Mapping

### 1. Agent Spawning (Fork vs. Delegate)

**Claude Code:** `AgentTool` with `fork` (full context) and `delegate` (self-contained brief) modes.

**Copilot Adaptation:**
- **Delegate mode** → Native `agent` tool invocation. The orchestrator's `.agent.md` lists `agent` in its tools and delegates to named subagents.
- **Fork mode** → Not directly available. Approximated by including rich context in the delegation brief (orchestrator constructs a detailed context package from checkpoint state + relevant artifacts).
- **Implementation:** Orchestrator instructions mandate "brief like a smart colleague who just walked into the room" — include objective, constraints, prior decisions, artifacts to reference, and expected output format.

### 2. Worktree Isolation

**Claude Code:** `isolation: "worktree"` parameter in AgentTool creates a clean git worktree per agent.

**Copilot Adaptation:**
- Not a native Copilot feature. Achieved through **convention in orchestrator instructions**:
  1. Orchestrator executes `git worktree add .worktrees/<agent-name>-<task-id> -b <branch>`
  2. Agent instructions specify working directory prefix
  3. After completion, orchestrator merges worktree branches
- **Fallback for simple projects:** File-ownership boundaries (Backend owns `src/api/`, Frontend owns `src/ui/`) without worktrees.

### 3. Team = TaskList Coordination

**Claude Code:** `TeamCreateTool` creates named teams with file-backed config and task stores. Agents claim tasks FIFO.

**Copilot Adaptation:**
- Replicated via **file-based task protocol** in `docs/tasks/`:
  ```
  docs/tasks/
    active-tasks.md        ← structured task list (ID, status, owner, dependencies, blockers)
    completed-tasks.md     ← archive of completed tasks
    task-<id>.md           ← detailed task brief per task
  ```
- Orchestrator maintains the task list. Agents receive task IDs in their delegation brief.
- No automatic FIFO claiming (Copilot agents don't self-activate). The orchestrator drives the claiming loop.
- **Implementation:** A `task-management` skill defines the protocol. Orchestrator instructions enforce it.

### 4. DAG-Based Task Dependencies

**Claude Code:** `TaskUpdate` with `blocks`/`blockedBy` fields enable dependency-ordered execution.

**Copilot Adaptation:**
- Dependency graph expressed as a Mermaid diagram + structured frontmatter in `active-tasks.md`:
  ```markdown
  ## Task Graph
  ```mermaid
  graph TD
    T1[Architecture] --> T2[Backend API]
    T1 --> T3[Frontend Shell]
    T2 --> T4[Integration Tests]
    T3 --> T4
    T4 --> T5[QA + Security]
  ```
  
  ## Tasks
  | ID | Title | Status | Owner | Blocked By | Blocks |
  |----|-------|--------|-------|------------|--------|
  | T1 | Architecture | done | @architect | — | T2, T3 |
  | T2 | Backend API | in_progress | @backend | T1 | T4 |
  ```
- Orchestrator consults the graph before delegating. Won't delegate a task whose blockers aren't `done`.

### 5. Plan-Approve-Execute

**Claude Code:** `EnterPlanMode` → explore/design → present to user → `ExitPlanMode` → implement.

**Copilot Adaptation:**
- Modeled as a **two-phase prompt flow** in orchestrator instructions:
  1. **Phase 1 (Plan):** Orchestrator produces a plan document (`docs/plans/plan-<id>.md`) with: goals, task decomposition, agent assignments, dependency graph, estimated scope, risks.
  2. **Phase 2 (Approval):** Orchestrator presents the plan to the user as a formatted summary and asks for explicit approval.
  3. **Phase 3 (Execute):** Only after approval, orchestrator begins delegation.
- A `/plan` slash command forces plan-only mode (no execution).

### 6. Checkpoint Compression

**Claude Code:** Automatic state summaries at phase boundaries, progressive context loading.

**Copilot Adaptation:**
- **Checkpoint files** in `docs/checkpoints/`:
  ```
  docs/checkpoints/
    checkpoint-001-planning.md
    checkpoint-002-architecture.md
    checkpoint-003-implementation.md
  ```
- Each checkpoint contains: completed tasks, key decisions, open blockers, token metrics, next steps.
- Orchestrator instructions mandate: "At each phase boundary, write a checkpoint. When delegating to agents, provide only the latest checkpoint + task-specific context, not the full history."
- A `checkpoint-protocol` skill defines the checkpoint format and compression rules.

### 7. Structured Shutdown Protocol

**Claude Code:** `SendMessage` with `shutdown_request` for graceful team termination.

**Copilot Adaptation:**
- Not applicable in the same way (Copilot agents don't run persistently).
- Equivalent: Orchestrator marks all remaining tasks as `cancelled` in the task list and writes a final checkpoint with project status.
- For long workflows, the orchestrator can write a "resume brief" to enable continuation in a new session.

### 8. Batch Processing Pipeline

**Claude Code:** `/batch` decomposes into 5-30 independent units, each in a worktree with a background agent.

**Copilot Adaptation:**
- A `/batch` command that instructs the orchestrator to:
  1. Decompose the change into independent units
  2. For each unit: create a worktree + branch, delegate to an agent
  3. Track progress in the task list
  4. Create MRs/PRs from each branch
- More sequential than Claude Code's fully parallel version (Copilot agents are sequential within a conversation).
- **Workaround for parallelism:** User can open multiple Copilot chat sessions and assign different units.

### 9. Memory Hierarchy

**Claude Code:** Auto-memory → CLAUDE.md (project) → CLAUDE.local.md (personal) → Team memory (org-wide). Background extraction, semantic retrieval, dream consolidation.

**Copilot Adaptation:**
- **Session memory** → In-conversation context (managed by Copilot natively)
- **Project memory** → `AGENTS.md` (workspace instructions) + `docs/decisions/` (ADRs) + `docs/checkpoints/` (state)
- **Team memory** → MCP Memory server (persistent knowledge graph, cross-session)
- **Background extraction** → Not available natively. Approximated by orchestrator writing key decisions to `AGENTS.md` and MCP Memory at phase boundaries.
- **Dream consolidation** → A `/consolidate-memory` command that reviews MCP Memory entries and prunes/promotes.

### 10. Validation / Verification Agent

**Claude Code:** Adversarial verification agent with PASS/FAIL/PARTIAL verdicts, do-not-modify constraints.

**Copilot Adaptation:**
- **`@tech-lead` agent** already serves this role for code review.
- Enhanced with:
  - Explicit `VERDICT: PASS | CONDITIONAL_PASS | FAIL` output requirement
  - "You MUST NOT modify any code. Read and report only." constraint
  - Structured review template: correctness → conventions → security → performance → test coverage
- **Security Engineer** does the same for security audits.
- **QA Engineer** does the same for test completeness.

### 11. Skillify (Self-Tooling)

**Claude Code:** `/skillify` converts a completed workflow into a reusable `SKILL.md` via structured interview.

**Copilot Adaptation:**
- A `/skillify` slash command that directs the orchestrator to:
  1. Analyze the current session's workflow
  2. Ask the user: "What triggers this workflow? What inputs does it need? What's the success criteria?"
  3. Generate a new `.github/skills/<name>.md` file with the captured pattern
  4. Present for user approval before writing
- This is a **meta-capability** that allows the system to evolve over time.

### 12. Permission Classification

**Claude Code:** LLM-as-classifier evaluates commands for risk level (LOW/MEDIUM/HIGH) with structured output.

**Copilot Adaptation:**
- Modeled in orchestrator instructions: "Before executing any destructive action (file deletion, force push, production deployment), classify the risk as LOW/MEDIUM/HIGH and request user confirmation for MEDIUM or higher."
- The `security-guidelines` instruction file covers security-sensitive operations.
- Post-edit hooks serve as a lightweight classification gate.

## Patterns NOT Directly Portable

| Pattern | Why Not | Workaround |
|---------|---------|------------|
| **Background agents** (persistent, polling) | Copilot agents exist only during conversation | Sequential delegation; resume briefs for multi-session |
| **Inter-agent messaging** (SendMessage) | No native message bus | File-based handoff via task files and checkpoints |
| **Automatic task claiming** (FIFO swarm) | Agents don't self-activate | Orchestrator drives all delegation |
| **Cron scheduling** (`/loop`) | No scheduled execution in Copilot | Manual re-invocation or external scheduler |
| **Proactive mode** (Kairos tick loop) | Copilot is request-response only | Not applicable; user initiates all work |
| **Cross-session communication** (UDS/bridge) | Copilot sessions are isolated | MCP Memory for state transfer; resume briefs |

## Patterns to Prioritize

Based on impact and feasibility:

1. **Plan-Approve-Execute** — High impact, directly implementable in instructions
2. **File-based task protocol** — High impact, enables structured coordination
3. **Checkpoint compression** — High impact, prevents context window exhaustion
4. **Validation gates** — High impact, ensures quality before progression
5. **Blocker/escalation protocol** — High impact, prevents project stalls
6. **Worktree isolation** — Medium impact, enables safer parallel work
7. **Skillify** — Medium impact, enables system self-improvement
8. **Memory hierarchy** — Medium impact, enables cross-session continuity
9. **Batch pipeline** — Lower priority, depends on worktree isolation
10. **Permission classification** — Lower priority, Copilot has built-in safety
