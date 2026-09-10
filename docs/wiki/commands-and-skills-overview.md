# Commands and Skills Overview

This page documents the user-invocable commands and the reusable skills that
back them, filling a documentation gap noted directly in
`docs/artifacts/maturity-promotion-criteria-v1.md`: neither commands nor
skills previously had a dedicated overview page under `docs/wiki/**`, unlike
agents (see [Agents Overview](agents-overview)). Entries below are added as
components are promoted through the maturity ladder (`experimental` →
`beta` → `stable`); this is not yet a complete catalogue of all 19 commands
or all 26 skills.

## Commands

| Command | Owning agent | Role |
|---------|-------------|------|
| `/plan` | `orchestrator` | Plan-only mode — produces a task decomposition, dependency graph, and plan document without executing any work, so the user can review and refine scope before approving execution. |
| `/code-review` | `tech-lead` | Requests a thorough, checklist-driven code review of specified files or the current changes, concluding in a structured VERDICT block (`PASS`/`CONDITIONAL_PASS`/`FAIL`) that downstream release tooling consumes directly. |

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
