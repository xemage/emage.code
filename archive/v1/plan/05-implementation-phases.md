# emage.code — Implementation Phases

## Phase Overview

```
Phase 0: Foundation         ← Protocols, AGENTS.md, docs/ structure
Phase 1: Orchestrator Core  ← Plan-Approve-Execute, task DAG, delegation
Phase 2: Agent Enhancement  ← Protocol-aware agents (all 27)
Phase 3: Skills Library     ← New skills for protocols + enhanced existing
Phase 4: Commands           ← New slash commands + enhanced existing
Phase 5: Quality & Safety   ← Validation gates, blocker protocol, security
Phase 6: Advanced Features  ← Batch, skillify, memory, worktree isolation
Phase 7: Testing & Polish   ← End-to-end validation, docs, migration guide
```

---

## Phase 0: Foundation

**Goal:** Establish the infrastructure that all subsequent work builds on.

### Deliverables
1. **`AGENTS.md`** — Rewrite workspace-level instructions to reference new protocols
   - Lifecycle states (`pending → in_progress → blocked → in_review → done`)
   - Task file protocol (where tasks live, format, rules)
   - Checkpoint protocol (format, cadence, compression)
   - Delegation brief format
   - Artifact versioning rules
   - Blocker escalation path
   - Memory hierarchy description

2. **`docs/` directory templates** — Create starter files
   - `docs/tasks/active-tasks.md` — Empty task table with correct headers
   - `docs/tasks/completed-tasks.md` — Empty archive
   - `docs/plans/.gitkeep`
   - `docs/decisions/.gitkeep`
   - `docs/checkpoints/.gitkeep`
   - `docs/artifacts/.gitkeep`

3. **`.vscode/mcp.json`** — MCP server configuration (carried from DEV-Team-Recruiter, verified)

4. **`.github/hooks/post-edit-reminder.json`** — Carried forward

### Exit Criteria
- `AGENTS.md` contains all protocol references
- `docs/` structure exists with correct templates
- MCP servers are configured and launchable

---

## Phase 1: Orchestrator Core

**Goal:** Rebuild the orchestrator as the coordination engine implementing all protocols.

### Deliverables
1. **`orchestrator.agent.md`** — Complete rewrite with:
   - **Plan Phase:** Analyze request → decompose tasks → build dependency graph → write plan → ask approval
   - **Execute Phase:** Read task graph → find unblocked tasks → delegate with structured briefs → track via checkpoints
   - **Review Phase:** Invoke validation gates → process verdicts → handle conditional passes → manage fixes
   - **Blocker handling:** Read blocker reports → route to appropriate resolver → escalate if unresolved
   - **Checkpoint cadence:** Write checkpoints at every phase boundary
   - **Token governance:** Track spend per phase, warn at budget thresholds
   - **Delegation brief protocol:** Include objective + context + inputs + constraints + expected outputs + acceptance criteria

2. **`poc-orchestrator.agent.md`** — Same patterns adapted for PoC track:
   - Lighter plan (hypothesis + success criteria + 3-step validation path)
   - Faster checkpoint cadence (after each PoC phase)
   - Explicit debt tracking delegation
   - Production handoff artifact generation

### Dependencies
- Phase 0 (AGENTS.md, docs/ templates)

### Exit Criteria
- Orchestrator can produce a plan document from a project idea
- Orchestrator asks for user approval before executing
- Orchestrator creates tasks with correct dependency structure
- Orchestrator writes checkpoints at phase boundaries
- Orchestrator delegates with structured briefs (not bare requests)

---

## Phase 2: Agent Enhancement

**Goal:** Update all 27 agents to be protocol-aware — they understand task format, checkpoint references, blocker reporting, and artifact versioning.

### Deliverables

**Production Agents (15 agent files updated):**

| Agent | Key Enhancements |
|-------|-----------------|
| `product-owner` | Produces `requirements-vN.md` as immutable artifact. Reports task completion with artifact list. |
| `solution-architect` | Produces `architecture-vN.md` + ADRs. References requirement version. Reports task completion. |
| `tech-lead` | Structured VERDICT output (PASS/CONDITIONAL/FAIL). Read-only during review. Merge gate authority. |
| `scrum-master` | Reads/updates `active-tasks.md`. Creates GitLab issues from task entries. Tracks velocity. |
| `backend-developer` | References architecture version. Reports blockers with type/severity. Respects file ownership boundaries. |
| `frontend-developer` | Same as backend. Respects UI file ownership. References API contracts from backend. |
| `database-engineer` | Produces versioned migration artifacts. References architecture. |
| `qa-engineer` | Structured test report with coverage metrics. VERDICT for quality gate. |
| `security-engineer` | OWASP audit with structured VERDICT. Read-only constraint. CRITICAL/HIGH/MEDIUM/LOW findings. |
| `devops-engineer` | CI/CD artifacts versioned. References architecture for deployment targets. |
| `release-manager` | Release gate VERDICT. Changelog from task completions. Version management. |
| `technical-writer` | Reads checkpoints for project state. Produces docs from artifact lineage. |
| `ux-designer` | Produces wireframe artifacts (versioned). References requirements. |

**PoC Agents (12 agent files updated):**
- All PoC agents updated with: lightweight task completion reporting, blocker protocol, artifact versioning (simplified for PoC speed).

### Common Agent Enhancement Pattern
Every agent gets these additions to their instructions:
```
## Protocol Awareness

### Task Completion
When you complete your work:
1. List all artifacts produced (with filenames and versions)
2. Confirm each acceptance criterion is met
3. Note any concerns or follow-up items

### Blocker Reporting
If you cannot proceed:
1. Describe the blocker clearly
2. Classify it: technical | dependency | unclear_requirements | external
3. Suggest a resolution if you have one
4. The orchestrator will handle escalation

### Artifact References
- Always reference the specific version of input artifacts you consumed
- Name your output artifacts following the versioning convention: <type>-vN.md
```

### Dependencies
- Phase 0 (AGENTS.md protocols)
- Phase 1 (orchestrator delegation brief format — agents must understand what they receive)

### Exit Criteria
- All 27 agents include protocol-awareness instructions
- Agents produce structured completion reports
- Agents report blockers in the defined format
- Agents reference artifact versions explicitly

---

## Phase 3: Skills Library

**Goal:** Create the new skills and enhance existing ones to support the protocols.

### New Skills (10)

| # | Skill | Purpose | Used By |
|---|-------|---------|---------|
| 1 | `task-management` | Task protocol: create, read, update, transition, archive tasks | Orchestrator, Scrum Master |
| 2 | `dependency-graphing` | Build Mermaid dependency DAGs from task lists, identify critical path | Orchestrator |
| 3 | `checkpoint-protocol` | Checkpoint format, when to write, compression rules, resume briefs | Orchestrator |
| 4 | `plan-approve-execute` | Plan document format, approval workflow, execution kickoff | Orchestrator |
| 5 | `blocker-escalation` | Blocker report format, escalation path, retry rules | All agents, Orchestrator |
| 6 | `validation-gates` | Gate definitions, VERDICT format, pass/fail criteria | Tech Lead, QA, Security |
| 7 | `worktree-isolation` | Git worktree creation, agent assignment, branch management, merge | Orchestrator |
| 8 | `skillify` | Capture workflow as reusable SKILL.md via structured interview | Orchestrator |
| 9 | `memory-management` | Memory hierarchy, when to persist, consolidation rules | Orchestrator |
| 10 | `release-workflow` | Versioning, changelog generation, release gates, hotfix workflow | Release Manager |

### Enhanced Existing Skills (12 carried forward with updates)
- All 12 existing skills updated with references to new protocols where relevant
- `testing-strategy` enhanced with validation gate awareness
- `code-review` enhanced with VERDICT format
- `context-window-management` enhanced with checkpoint compression rules
- `cost-token-governance` enhanced with phase-specific budgets

### Dependencies
- Phase 0 (protocol definitions)
- Phase 1 (orchestrator needs skills to function)

### Exit Criteria
- All 22 skills written and placed in `.github/skills/`
- Skills are referenced in appropriate agent definitions
- Skill format is consistent (purpose, when to use, procedure, examples)

---

## Phase 4: Commands

**Goal:** Create new slash commands and enhance existing ones.

### New Commands (4)

| Command | Agent | Purpose |
|---------|-------|---------|
| `/plan` | `@orchestrator` | Plan-only mode — produce task decomposition and plan document without executing |
| `/batch` | `@orchestrator` | Decompose a sweeping change into independent units for parallel execution |
| `/skillify` | `@orchestrator` | Capture the current workflow as a reusable skill via structured interview |
| `/consolidate-memory` | `@orchestrator` | Review MCP Memory entries, prune stale items, promote valuable items to AGENTS.md |

### Enhanced Commands (12 carried forward)
- All existing commands updated with plan-approve-execute flow where appropriate
- `/new-project` — Major enhancement: plan phase added before execution
- `/new-feature` — Plan phase added
- `/new-poc` — Lightweight plan phase (hypothesis + validation path)
- `/team-status` — Enhanced with task DAG visualization and checkpoint metrics

### Dependencies
- Phase 1 (orchestrator must support plan-approve-execute)
- Phase 3 (commands invoke skills)

### Exit Criteria
- All 16 commands placed in `.github/prompts/`
- Commands follow consistent format
- New commands tested with sample invocations

---

## Phase 5: Quality & Safety

**Goal:** Implement validation gates, blocker protocol, and security model in full.

### Deliverables
1. **Validation gate implementation** in agent instructions:
   - Tech Lead: structured code review with VERDICT
   - QA Engineer: test completeness VERDICT
   - Security Engineer: OWASP audit VERDICT
   - Release Manager: release readiness VERDICT

2. **Blocker escalation implementation** in orchestrator:
   - Orchestrator reads blocker reports from task files
   - Routes to appropriate resolver based on blocker type
   - Tracks retry count
   - Escalates to user after 2 failed attempts

3. **Security model hardening:**
   - Update `security-guidelines.instructions.md` with immutable security constraints
   - Ensure agents that should not modify code (Tech Lead during review, Security Engineer during audit) have explicit read-only constraints
   - Post-edit hook updated with security-specific checks

4. **Instructions enhancement:**
   - `coding-standards.instructions.md` — Add artifact versioning naming rules
   - `git-workflow.instructions.md` — Add worktree branch naming convention
   - `security-guidelines.instructions.md` — Add permission classification rules
   - `poc-guidelines.instructions.md` — Add debt tracking requirements

### Dependencies
- Phase 2 (agents must understand VERDICT format)
- Phase 3 (validation-gates skill)

### Exit Criteria
- All validation gates produce structured VERDICTs
- Blocker escalation follows the documented path
- Read-only constraints enforced for reviewer agents
- Security guidelines are comprehensive and immutable

---

## Phase 6: Advanced Features

**Goal:** Implement batch processing, skillify, memory management, and worktree isolation.

### Deliverables
1. **Batch pipeline** (`/batch` command + orchestrator support):
   - Decompose change into independent units
   - Create worktree + branch per unit (using `worktree-isolation` skill)
   - Delegate each unit to appropriate agent
   - Track progress in task list
   - Guide user through PR creation from branches

2. **Skillify workflow** (`/skillify` command):
   - Analyze conversation history for workflow pattern
   - Conduct 4-round interview: trigger, inputs, steps, success criteria
   - Generate `.github/skills/<name>.md`
   - Present for user approval

3. **Memory management** (`/consolidate-memory` command):
   - Read MCP Memory entries
   - Categorize: keep, promote to AGENTS.md, prune
   - Present recommendations to user
   - Execute approved changes

4. **Worktree isolation** (orchestrator capability):
   - Create worktrees via shell commands in orchestrator
   - Assign file ownership per worktree
   - Merge worktree branches after task completion
   - Clean up worktrees after merge

### Dependencies
- Phase 1-5 (full orchestrator + agent + skill stack)

### Exit Criteria
- `/batch` can decompose and track multi-unit changes
- `/skillify` can capture a workflow as a skill file
- `/consolidate-memory` can review and manage memory entries
- Worktree isolation works for parallel agent tasks

---

## Phase 7: Testing & Polish

**Goal:** Validate the full system, write documentation, and create onboarding materials.

### Deliverables
1. **Scenario tests** (documented, manually executable):
   - Small: "Build a TODO API" — 4 agents, 1 sprint
   - Medium: "Build a blog platform with auth" — 8 agents, 3 sprints
   - Complex: "Build a microservice e-commerce platform" — full team, parallel work

2. **Validation checklist** for each scenario:
   - Plan document produced and correct
   - Task DAG has valid dependencies
   - Checkpoints written at phase boundaries
   - Artifacts versioned correctly
   - Blockers reported and escalated properly
   - VERDICTs produced for gates
   - Final deliverables complete

3. **Documentation:**
   - `emage.code/README.md` — Quick start, architecture overview, command reference
   - `emage.code/MIGRATION.md` — Upgrade guide from DEV-Team-Recruiter
   - `emage.code/PREREQUISITES.md` — Required tooling

4. **Migration guide:**
   - File-by-file mapping from DEV-Team-Recruiter to emage.code
   - Breaking changes (if any)
   - Feature comparison table

### Dependencies
- All previous phases

### Exit Criteria
- All three scenario tests documented with expected outcomes
- README covers quick start through advanced usage
- Migration guide enables existing users to upgrade

---

## Critical Path

```
Phase 0 ──→ Phase 1 ──→ Phase 2 ──→ Phase 5
                │            │
                ↓            ↓
            Phase 3      Phase 4
                │            │
                └──→ Phase 6 ←┘
                       │
                       ↓
                   Phase 7
```

- **Sequential critical path:** Phase 0 → Phase 1 → Phase 2 → Phase 5
- **Parallel after Phase 1:** Phase 3 (skills) and Phase 4 (commands) can run in parallel with Phase 2
- **Phase 6** requires Phase 3 + 4 + 5
- **Phase 7** is the final integration/polish phase

## Estimated Effort per Phase

| Phase | Scope | Files Created/Modified |
|-------|-------|----------------------|
| Phase 0 | Foundation | ~10 files (AGENTS.md, templates, configs) |
| Phase 1 | Orchestrator Core | 2 agent files (major rewrites) |
| Phase 2 | Agent Enhancement | 25 agent files (moderate updates) |
| Phase 3 | Skills Library | 22 skill files (10 new + 12 updated) |
| Phase 4 | Commands | 16 prompt files (4 new + 12 updated) |
| Phase 5 | Quality & Safety | ~10 files (agents + instructions) |
| Phase 6 | Advanced Features | ~8 files (commands + skills + orchestrator) |
| Phase 7 | Testing & Polish | ~5 files (docs, migration guide, test scenarios) |
