# Migration Guide: DEV-Team-Recruiter → emage.code

This guide covers the migration path from DEV-Team-Recruiter to emage.code — what changed, what's new, and how to upgrade.

---

## What Changed

emage.code is an evolution of DEV-Team-Recruiter, not a rewrite from scratch. The core agent team remains, but the orchestration model has been fundamentally improved:

| Area | Before (DEV-Team-Recruiter) | After (emage.code) |
|------|----------------------------|---------------------|
| **Workflow control** | Implicit delegation | Plan-Approve-Execute with user approval gates |
| **Task tracking** | Ad-hoc | DAG-based task management in `docs/tasks/` |
| **Context management** | Full history in context | Checkpoint compression at phase boundaries |
| **Quality assurance** | Agent-dependent | Structured validation gates (PASS/CONDITIONAL_PASS/FAIL) |
| **Blocker handling** | Unstructured | Typed blocker reports with deterministic routing |
| **Artifact management** | Overwrite-in-place | Immutable versioned artifacts (`<type>-v<N>.md`) |
| **Agent delegation** | Free-form instructions | Structured delegation briefs with criteria |
| **Token awareness** | None | Per-phase token budgets with compression triggers |

---

## File Mapping

### Agents (old → new)

| DEV-Team-Recruiter | emage.code | Change |
|--------------------|------------|--------|
| `project-orchestrator.agent.md` | `orchestrator.agent.md` | **Renamed** + complete rewrite with Plan-Approve-Execute |
| `product-owner.agent.md` | `product-owner.agent.md` | Enhanced with protocol awareness |
| `solution-architect.agent.md` | `solution-architect.agent.md` | Enhanced with protocol awareness |
| `tech-lead.agent.md` | `tech-lead.agent.md` | Enhanced with protocol awareness |
| `scrum-master.agent.md` | `scrum-master.agent.md` | Enhanced with protocol awareness |
| `frontend-developer.agent.md` | `frontend-developer.agent.md` | Enhanced with protocol awareness |
| `backend-developer.agent.md` | `backend-developer.agent.md` | Enhanced with protocol awareness |
| `database-engineer.agent.md` | `database-engineer.agent.md` | Enhanced with protocol awareness |
| `qa-engineer.agent.md` | `qa-engineer.agent.md` | Enhanced with protocol awareness |
| `security-engineer.agent.md` | `security-engineer.agent.md` | Enhanced with protocol awareness |
| `devops-engineer.agent.md` | `devops-engineer.agent.md` | Enhanced with protocol awareness |
| `technical-writer.agent.md` | `technical-writer.agent.md` | Enhanced with protocol awareness |
| `release-manager.agent.md` | `release-manager.agent.md` | Enhanced with protocol awareness |
| `ux-designer.agent.md` | `ux-designer.agent.md` | Enhanced with protocol awareness |
| `poc-orchestrator.agent.md` | `poc-orchestrator.agent.md` | Enhanced with protocol awareness |
| `technology-scout.agent.md` | `technology-scout.agent.md` | Enhanced with protocol awareness |
| `feasibility-agent.agent.md` | `feasibility-agent.agent.md` | Enhanced with protocol awareness |
| `scaffolding-agent.agent.md` | `scaffolding-agent.agent.md` | Enhanced with protocol awareness |
| `demo-agent.agent.md` | `demo-agent.agent.md` | Enhanced with protocol awareness |
| `evaluation-agent.agent.md` | `evaluation-agent.agent.md` | Enhanced with protocol awareness |
| `data-mockup-agent.agent.md` | `data-mockup-agent.agent.md` | Enhanced with protocol awareness |
| `integration-agent.agent.md` | `integration-agent.agent.md` | Enhanced with protocol awareness |
| `technical-debt-narrator.agent.md` | `technical-debt-narrator.agent.md` | Enhanced with protocol awareness |
| `poc-devops-engineer.agent.md` | `poc-devops-engineer.agent.md` | Enhanced with protocol awareness |
| `poc-qa-engineer.agent.md` | `poc-qa-engineer.agent.md` | Enhanced with protocol awareness |
| `poc-security-engineer.agent.md` | `poc-security-engineer.agent.md` | Enhanced with protocol awareness |
| `poc-technical-writer.agent.md` | `poc-technical-writer.agent.md` | Enhanced with protocol awareness |

### Skills (old → new)

| DEV-Team-Recruiter | emage.code | Status |
|--------------------|------------|--------|
| `api-design/` | `api-design/` | Carried forward |
| `ci-cd-pipeline/` | `ci-cd-pipeline/` | Carried forward |
| `code-review/` | `code-review/` | Carried forward |
| `context-window-management/` | `context-window-management/` | Carried forward |
| `dependency-graphing/` | `dependency-graphing/` | Carried forward |
| `gitlab-management/` | `gitlab-management/` | Carried forward |
| `poc-evaluation/` | `poc-evaluation/` | Carried forward |
| `project-planning/` | `project-planning/` | Carried forward |
| `rapid-prototyping/` | `rapid-prototyping/` | Carried forward |
| `release-workflow/` | `release-workflow/` | Carried forward |
| `technical-debt-tracking/` | `technical-debt-tracking/` | Carried forward |
| `technology-scouting/` | `technology-scouting/` | Carried forward |
| — | `plan-approve-execute/` | **New** |
| — | `task-management/` | **New** |
| — | `checkpoint-protocol/` | **New** |
| — | `blocker-escalation/` | **New** |
| — | `validation-gates/` | **New** |
| — | `cost-token-governance/` | **New** |
| — | `testing-strategy/` | **New** |
| — | `skillify/` | **New** |
| — | `memory-management/` | **New** |
| — | `worktree-isolation/` | **New** |

### Prompts (old → new)

| DEV-Team-Recruiter | emage.code | Status |
|--------------------|------------|--------|
| `new-project.prompt.md` | `new-project.prompt.md` | Carried forward |
| `new-feature.prompt.md` | `new-feature.prompt.md` | Carried forward |
| `bug-report.prompt.md` | `bug-report.prompt.md` | Carried forward |
| `code-review.prompt.md` | `code-review.prompt.md` | Carried forward |
| `security-audit.prompt.md` | `security-audit.prompt.md` | Carried forward |
| `prepare-release.prompt.md` | `prepare-release.prompt.md` | Carried forward |
| `sprint-status.prompt.md` | `sprint-status.prompt.md` | Carried forward |
| `team-status.prompt.md` | `team-status.prompt.md` | Carried forward |
| `new-poc.prompt.md` | `new-poc.prompt.md` | Carried forward |
| `evaluate-poc.prompt.md` | `evaluate-poc.prompt.md` | Carried forward |
| `poc-demo.prompt.md` | `poc-demo.prompt.md` | Carried forward |
| `validate-workflow.prompt.md` | `validate-workflow.prompt.md` | Carried forward |
| — | `plan.prompt.md` | **New** |
| — | `batch.prompt.md` | **New** |
| — | `skillify.prompt.md` | **New** |
| — | `consolidate-memory.prompt.md` | **New** |

### Instructions & Other Files

| DEV-Team-Recruiter | emage.code | Status |
|--------------------|------------|--------|
| `coding-standards.instructions.md` | `coding-standards.instructions.md` | Enhanced with protocol rules |
| `git-workflow.instructions.md` | `git-workflow.instructions.md` | Enhanced with protocol rules |
| `poc-guidelines.instructions.md` | `poc-guidelines.instructions.md` | Enhanced with protocol rules |
| `security-guidelines.instructions.md` | `security-guidelines.instructions.md` | Enhanced with protocol rules |
| `hooks/post-edit-reminder.json` | `hooks/post-edit-reminder.json` | Carried forward |
| `.vscode/mcp.json` | `.vscode/mcp.json` | Compatible |
| `AGENTS.md` | `AGENTS.md` | **Rewritten** |
| — | `docs/` directory | **New** — runtime state location |

---

## Breaking Changes

### 1. Agent Rename: `project-orchestrator` → `orchestrator`

The main orchestrator agent has been renamed. If you have scripts or workflows referencing `project-orchestrator`, update them to `orchestrator`.

### 2. Protocol Requirements

All agents now follow structured protocols:
- **Task completion reports** — Agents must report completion status with structured output
- **Blocker reports** — Agents must use typed blocker categories (`TECHNICAL`, `DEPENDENCY`, `CLARIFICATION`, `ACCESS`, `DESIGN`)
- **Artifact versioning** — Outputs follow `<type>-v<N>.md` immutable naming

### 3. `docs/` Directory Required

emage.code expects a `docs/` directory in your project root with subdirectories:
- `docs/tasks/` — Active and completed task tracking
- `docs/plans/` — Approved plan documents
- `docs/decisions/` — Architecture decision records
- `docs/checkpoints/` — Phase-boundary summaries
- `docs/artifacts/` — Versioned deliverables

### 4. AGENTS.md Rewritten

The workspace-level `AGENTS.md` has been completely rewritten with protocol conventions. Replace your existing file.

---

## New Features

### Plan-Approve-Execute
All non-trivial workflows now go through a structured plan phase. The orchestrator proposes a plan, you approve (or modify), then execution proceeds. Trivial tasks (< 3 steps, single agent) skip the plan phase automatically.

### DAG-Based Task Management
Tasks are tracked in `docs/tasks/active-tasks.md` with explicit dependencies (`blocks`/`blockedBy`), ownership, and status. The orchestrator manages the DAG and delegates in topological order.

### Checkpoint Compression
At phase boundaries, the orchestrator writes a checkpoint summary to `docs/checkpoints/`. Subsequent phases load only the checkpoint, not the full history — keeping context windows manageable.

### Blocker Escalation Protocol
When an agent is blocked, it files a typed blocker report. The orchestrator routes it deterministically (e.g., `TECHNICAL` → tech-lead, `DESIGN` → solution-architect). After 2 failed retries, the blocker escalates to the user.

### Validation Gates
Quality checkpoints produce structured verdicts: `PASS`, `CONDITIONAL_PASS` (with required follow-ups), or `FAIL` (with remediation items). No ambiguous "looks good" — explicit pass/fail decisions.

### Artifact Versioning
Deliverables use immutable naming: `architecture-v1.md`, `architecture-v2.md`. Each version references its dependencies explicitly. No overwriting — full audit trail.

### Batch Processing (`/batch`)
Decompose large-scale changes (rename across 50 files, add logging everywhere) into isolated units for parallel execution. Each unit is self-contained with its own validation.

### Skillify (`/skillify`)
After completing a successful workflow, capture it as a reusable skill via structured interview. The skill file includes triggers, steps, validation criteria, and examples.

### Memory Management (`/consolidate-memory`)
Review and organize MCP Memory entries with a promote/prune workflow. Promote useful learnings from session to persistent memory; prune stale or incorrect entries.

### Worktree Isolation
Parallel workstreams use Git worktrees for full file-system isolation. No branch-switching conflicts, no half-committed state.

---

## Feature Comparison

| Feature | DEV-Team-Recruiter | emage.code |
|---------|-------------------|------------|
| Agent count | 27 | 27 |
| Production agents | 14 | 14 (protocol-enhanced) |
| PoC agents | 13 | 13 (protocol-enhanced) |
| Slash commands | 12 | 16 |
| Skills | 12 | 22 |
| Instructions | 4 | 4 (enhanced) |
| MCP servers | 7 | 7 |
| Plan-Approve-Execute | ✗ | ✓ |
| DAG task management | ✗ | ✓ |
| Checkpoint compression | ✗ | ✓ |
| Validation gates | ✗ | ✓ |
| Blocker escalation | ✗ | ✓ |
| Artifact versioning | ✗ | ✓ |
| Token governance | ✗ | ✓ |
| Batch processing | ✗ | ✓ |
| Skillify | ✗ | ✓ |
| Memory consolidation | ✗ | ✓ |
| Worktree isolation | ✗ | ✓ |
| Structured delegation briefs | ✗ | ✓ |
| `docs/` runtime state | ✗ | ✓ |

---

## Migration Steps

1. **Back up your current `.github/` directory** (optional, for reference)
2. **Copy the new `.github/` directory** from emage.code — replaces all agents, skills, prompts, instructions, hooks
3. **Copy the new `AGENTS.md`** — replaces workspace conventions
4. **Copy `.vscode/mcp.json`** — compatible, may have minor updates
5. **Create `docs/` directory** with subdirectories: `tasks/`, `plans/`, `decisions/`, `checkpoints/`, `artifacts/`
6. **Seed task files** — Copy `docs/tasks/active-tasks.md` and `docs/tasks/completed-tasks.md` templates
7. **Update any scripts** referencing `project-orchestrator` → `orchestrator`
8. **Test** — Run `/team-status` to verify all agents are recognized
