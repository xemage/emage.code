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
| `task-management` | `AGENTS.md`'s Task Protocol section; `orchestrator.md`'s Task Management section | Defines the full task-ledger lifecycle: creation preconditions, the 7-column `active-tasks.md`/5-column `completed-tasks.md` schemas, the never-hold-a-terminal-row invariant, and the atomic 4-step "Complete a Task" procedure only the orchestrator may perform. |
| `checkpoint-protocol` | `AGENTS.md`'s Checkpoint Protocol section | Defines when a checkpoint must be written (phase boundaries, every 3-5 task completions, before anticipated context exhaustion), the `checkpoint-<SEQ>-<phase>.md` filename convention, and the compression/resume-brief procedures that let work continue across a context reset. |
| `receiving-code-review` | `AGENTS.md`'s mandatory Skill Workflow table ("code review feedback to implement") | Defines the READ/UNDERSTAND/VERIFY/EVALUATE/RESPOND/IMPLEMENT response pattern an agent must follow before acting on review feedback, and the Forbidden Patterns (implementing before understanding, marking resolved without re-running tests) that count as a violation. |
| `systematic-debugging` | `AGENTS.md`'s mandatory Skill Workflow table ("any bug, test failure, unexpected behavior") | Defines the four-phase (Investigate / Hypothesize / Experiment / Fix-and-Verify) root-cause process and the Iron Rule forbidding any fix before root cause is confirmed, plus the escalation path (`technical`/`major` blocker) when two structured cycles don't resolve it. |
| `verification-before-completion` | `AGENTS.md`'s mandatory Skill Workflow table ("marking work done, commit, MR, release") | Defines the Iron Rule that no completion claim may be made without fresh command-output evidence, the Claim → Evidence map, and the standard emage.code verification commands (`check.py`, `verify.mjs`, `tests/run.py`, `verify-release-docs.py`) every claim is checked against. |
| `testing-strategy` | `orchestrator.md`'s Validation Gates section (Integration Gate) | Defines the testing pyramid, framework selection per language, the test plan template, and the coverage-threshold table (unit coverage, integration pass rate, E2E critical-path pass rate, security scan, performance) that determines whether the Integration Gate's `PASS`/`CONDITIONAL_PASS`/`FAIL` verdict is earned. |

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
