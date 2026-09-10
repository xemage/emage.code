# Commands and Skills Overview

This page documents the user-invocable commands and the reusable skills that
back them, filling a documentation gap noted directly in
`docs/artifacts/maturity-promotion-criteria-v1.md`: neither commands nor
skills previously had a dedicated overview page under `docs/wiki/**`, unlike
agents (see [Agents Overview](agents-overview)). Entries below are added as
components are promoted through the maturity ladder (`experimental` →
`beta` → `stable`). As of T434 (Wave 2), all 19 commands have a documentation
row here; this is not yet a complete catalogue of all 26 skills.

## Commands

| Command | Owning agent | Role |
|---------|-------------|------|
| `/plan` | `orchestrator` | Plan-only mode — produces a task decomposition, dependency graph, and plan document without executing any work, so the user can review and refine scope before approving execution. |
| `/code-review` | `tech-lead` | Requests a thorough, checklist-driven code review of specified files or the current changes, concluding in a structured VERDICT block (`PASS`/`CONDITIONAL_PASS`/`FAIL`) that downstream release tooling consumes directly. |
| `/batch` | `orchestrator` | Decomposes a sweeping change into independent, self-contained units for parallel execution across isolated worktrees, tracking the full batch manifest in the task ledger. |
| `/bug-report` | `orchestrator` | Produces a structured bug report (severity, repro steps, root-cause analysis, suggested fix) and creates a tracked task entry with a severity-mapped priority. |
| `/consolidate-memory` | `orchestrator` | Reviews MCP Memory entries, categorizes each as Keep, Promote, or Prune, and applies only user-approved changes to keep the persistent knowledge base accurate and lean. |
| `/discover-skills` | `orchestrator` | Matches the user's stated task intent against the skill registry and returns a ranked, mandatory-vs-suggested recommendation table with the next command to run. |
| `/evaluate-poc` | `poc-orchestrator` | Evaluates whether a PoC actually validated its hypothesis, producing a structured VERDICT, a Technical Debt Scorecard, and a production-handoff checklist. |
| `/handoff` | `orchestrator` | Produces a resumable session handoff artifact (JSON payload plus human-readable summary) conforming to the handoff schema, so the next session can resume without losing context. |
| `/new-feature` | `orchestrator` | Plans and delivers a new feature end-to-end — user story, technical-impact assessment, task breakdown, and versioned deliverable artifacts — gated on explicit plan approval. |
| `/new-poc` | `poc-orchestrator` | Starts a proof-of-concept project with a hypothesis-first lightweight plan, coordinating PoC specialists through feasibility, build, and evaluation phases. |
| `/new-project` | `orchestrator` | Triggers the full production orchestration workflow from an idea — planning, requirements, architecture, sprint planning, setup, and execution — gated on explicit plan approval. |
| `/poc-demo` | `poc-orchestrator` | Packages the current PoC build into a stakeholder-ready demo package with a walkthrough script, artifact references, and an explicit hypothesis validation status block. |
| `/prepare-release` | `orchestrator` | Prepares a new release: version bump, changelog generated from completed tasks, release checklist, and a structured RELEASE VERDICT gated on all quality gates passing. |
| `/security-audit` | `security-engineer` | Performs an OWASP Top 10 security audit of the requested scope, producing a coverage matrix, severity-classified findings, and a VERDICT that must be FAIL if any CRITICAL finding exists. |
| `/skillify` | `orchestrator` | Captures a recurring workflow as a reusable skill file through a structured four-round interview (trigger, inputs, steps, success criteria), applied only after user approval. |
| `/sprint-status` | `orchestrator` | Reports current sprint metrics, a task dependency graph, checkpoint activity, and token spend telemetry, reading from the active and completed task ledgers. |
| `/team-status` | `orchestrator` | Reports team-wide status across active streams — blockers, role workload, velocity, and a task dependency graph — gated behind the `TEAM_STATUS_V1_ENABLED` feature flag. |
| `/validate-tasks` | `orchestrator` | Runs the task ledger's own integrity validator and reports every `FAIL C<n>` violation verbatim, required before every checkpoint, release, and `install.sh --update`. |
| `/validate-workflow` | `orchestrator` | Runs scenario-based validation of the multi-agent workflow — role behavior, handoff integration, and command regression checks — against every documented validation gate. |

The `plan` command implements the Plan phase of the Plan-Approve-Execute
protocol described in `AGENTS.md`; it is deliberately forbidden from
creating task rows in `docs/tasks/active-tasks.md` until its own plan
document has been written and presented for review, closing the loop this
project's task-creation precondition depends on.

The `code-review` command is the invocable surface for the `code-review`
skill described below: running `/code-review` executes the same checklist
and produces the same verdict format that skill documents in full, so a
human reviewer or another agent gets identical behaviour whether they
invoke the command directly or delegate to `tech-lead` with the skill
referenced by id.

## Skills

| Skill | Referenced by | Role |
|-------|---------------|------|
| `validation-gates` | `AGENTS.md`'s mandatory Skill Workflow table (phase/validation transitions) | Defines the five gate types (architecture, implementation, integration, security, release), their executors, and the shared `PASS`/`CONDITIONAL_PASS`/`FAIL` verdict format every gate-producing agent in this repo must emit. |
| `code-review` | `tech-lead.md`'s Code Review section | Defines the structured review checklist (correctness, security, performance, maintainability, testing, documentation) and severity guide (Must Fix / Should Fix / Nice to Have) that both the `/code-review` command and the `tech-lead` agent's own review workflow implement. |

`validation-gates` is the shared contract behind every quality checkpoint in
this repo's Plan-Approve-Execute lifecycle: it is what lets an
`implementation gate` verdict from `tech-lead` and a `security gate` verdict
from `security-engineer` be consumed identically by the orchestrator's
blocker-handling and phase-transition logic, rather than each agent
inventing its own ad hoc pass/fail vocabulary.

`code-review` is the most heavily reused skill in the repository's own
review workflow: its structured feedback format and severity levels are the
basis for `tech-lead.md`'s Review Feedback Format section, and its VERDICT
block is the same block every merge request review in this project is
expected to produce before a merge is authorized.
