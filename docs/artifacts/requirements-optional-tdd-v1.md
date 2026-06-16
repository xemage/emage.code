# Requirements: Optional TDD Enforcement & Skill Gap Closure v1

Based on: [research-agents-skills-ecosystem-v1.md](research-agents-skills-ecosystem-v1.md), [plan-007-v4-ecosystem-workflows.md](../plans/plan-007-v4-ecosystem-workflows.md), [HackerNoon — 12 OpenCode Skills](https://hackernoon.com/twelve-opencode-skills-every-dev-team-should-steal), [obra/superpowers TDD skill](https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/SKILL.md)

Status: **draft** — awaiting Plan-Approve-Execute approval

## Problem statement

emage.code v4 closed the highest-priority Superpowers gaps (systematic-debugging, receiving-code-review, verification-before-completion, handoff, discover-skills). **Test-first implementation** remains the largest behavioral gap: `testing-strategy` plans coverage but does not enforce RED-GREEN-REFACTOR during implementation.

Teams differ on TDD strictness. Superpowers treats TDD as always mandatory; emage.code should support **optional enforcement with user consent** (`ask` default), aligned with [OpenCode skill permissions](https://opencode.ai/docs/skills/) (`allow` / `deny` / `ask`).

## Goals

1. Add a canonical `test-driven-development` skill adapted from Superpowers.
2. Introduce per-project workflow preferences so TDD can be `ask` (default), `always`, or `never`.
3. Wire preferences into orchestrator delegation, `/discover-skills`, and `AGENTS.md` conditional mandatory rules.
4. Document remaining ecosystem gaps for v6.x follow-up (no scope creep in this release).

## Non-goals

- Hard-mandatory TDD for all consumers (Superpowers parity) — opt-in only.
- Pi extension bridge, plan annotation UI, OPA/Rego policy layer (deferred from plan-007).
- Replacing `testing-strategy` (complementary: strategy vs. implementation discipline).

## Functional requirements

### FR-1 — TDD skill

| ID | Requirement |
|----|-------------|
| FR-1.1 | Canonical skill at `implementation/knowledge/skills/test-driven-development/SKILL.md`. |
| FR-1.2 | Content based on [obra TDD skill](https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/SKILL.md): RED-GREEN-REFACTOR, Iron Law, verification checklist, rationalization table. |
| FR-1.3 | Add **emage.code optional mode** section: when `tdd_enforcement` is `ask`, agent MUST prompt user before implementation; when `never`, skill is informational only; when `always`, treat as mandatory per FR-3. |
| FR-1.4 | Skill projected to all five platforms via `sync.mjs`; registry regenerated. |

### FR-2 — Workflow preferences file

| ID | Requirement |
|----|-------------|
| FR-2.1 | Template at `implementation/docs/emage-workflow.yaml` (installed to consumer `docs/emage-workflow.yaml`). |
| FR-2.2 | Schema field `workflow.tdd_enforcement`: `ask` \| `always` \| `never` (default `ask`). |
| FR-2.3 | `install.sh` seeds file on fresh install; `--update` merges new keys without overwriting user values (same pattern as task ledger merge). |
| FR-2.4 | Optional JSON Schema at `implementation/runtime/workflow/schema-v1.json` + validator in `check.py` (lightweight). |

### FR-3 — Conditional mandatory workflow

| ID | Requirement |
|----|-------------|
| FR-3.1 | Extend root `AGENTS.md` Skill Workflow table with conditional row: implementation tasks when `tdd_enforcement: always` → `test-driven-development`. |
| FR-3.2 | When `ask`, orchestrator and implementer agents prompt: *"Enable strict TDD (RED-GREEN-REFACTOR) for this task?"* — record answer in task brief or checkpoint. |
| FR-3.3 | `/discover-skills` reads `docs/emage-workflow.yaml` and marks TDD mandatory/suggested/optional accordingly. |
| FR-3.4 | Orchestrator delegation brief includes `workflow.tdd_enforcement` and per-task TDD decision when applicable. |

### FR-4 — Bootstrap prompts

| ID | Requirement |
|----|-------------|
| FR-4.1 | `/new-project` Phase 1 includes workflow preference question (TDD default `ask`). |
| FR-4.2 | Post-install message in `install.sh` mentions `docs/emage-workflow.yaml` and TDD toggle. |

### FR-5 — Validation & docs

| ID | Requirement |
|----|-------------|
| FR-5.1 | Extend `validate-workflow` command with TDD preference scenario. |
| FR-5.2 | Release brief `docs/releases/v6.1.0.md` (or next minor) with Install + Highlights. |
| FR-5.3 | Update `docs/artifacts/research-agents-skills-ecosystem-v1.md` status for TDD gap. |

## Acceptance criteria

- [ ] `test-driven-development` skill exists in canonical knowledge and all platform projections
- [ ] `docs/emage-workflow.yaml` template installs and survives `--update`
- [ ] `AGENTS.md` documents conditional TDD mandatory rule
- [ ] `/discover-skills` and orchestrator agent reference workflow preferences
- [ ] `node scripts/sync.mjs` + `node scripts/verify.mjs` pass; registry updated
- [ ] Functional test covers workflow file merge on `--update`
- [ ] All existing tests pass

## Gap analysis summary (remaining vs. ecosystem)

See [plan-008](../plans/plan-008-optional-tdd-and-skill-gaps.md) for full matrix. Priority follow-ups after this release:

| Priority | Gap | Source |
|----------|-----|--------|
| P1 | `test-driven-development` + optional enforcement | Superpowers, HackerNoon #4 |
| P2 | `brainstorming` / `using-superpowers` bootstrap skill | Superpowers |
| P2 | `subagent-driven-development` skill | Superpowers |
| P2 | `finishing-a-development-branch` skill | Superpowers |
| P2 | Dynamic context pruning in token governance | Awesome OpenCode |
| P3 | Pi extension bridge | plan-007 out-of-scope |
| P3 | OPA/Rego policy layer | Awesome OpenCode / Cupcake |
