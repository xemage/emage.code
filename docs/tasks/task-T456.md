# Task T456 — Downstream measurement (ship gate) — BLOCKED on missing infrastructure

**ID:** T456
**Owner:** evaluation-agent (per `plan-038`'s nominal assignment — never actually dispatched to an
agent; this blocker was found by the orchestrator during pre-dispatch brief authoring, before any
worktree/branch existed, mirroring T454's own "orchestrator-caught, pre-dispatch" gap category)
**Status:** blocked
**Priority:** P0 (unchanged from `plan-038` — this is Phase 5's literal ship gate; the block is on
*infrastructure*, not on this task's own priority)
**Depends on:** T454 (done), T455 (done) — **and now also T458** (new: build a real live-execution
harness for the golden suite; does not exist yet, this task cannot proceed without it)
**Created:** 2026-09-09
**Completed:** — (genuinely blocked, not completed; see "Disposition" below — do not read the
absence of a completion date as abandonment)
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T456's own literal row:
"Downstream measurement: re-run the Phase 1 baseline with retrieval enabled. **If the golden suite
does not improve, the feature does not ship.**"; Phase 5's acceptance-criteria checklist: "Golden
suite improves measurably with retrieval enabled, against the same baseline"); `docs/plans/plan-038-
phase5-detailed-planning.md`'s T456 per-task summary (objective, inputs — T454's agent, T455's eval
sub-suite, `docs/benchmarks/baseline-v6.12.0.md` — outputs, acceptance criteria, and its own note
that "this task's brief should pre-register what 'improve' means numerically before the run"); the
finding itself is grounded directly in `docs/artifacts/golden-suite-format-v1.md` §2.2/§4.2 and
`scripts/scorecard.py` (both read-only references — **never edited**, per this task's own
Constraints, since both are protected paths under `docs/artifacts/protected-paths-v1.md`).

## Objective (as originally scoped, per `plan-038`)

Re-run the Phase 1 golden-suite baseline (`docs/benchmarks/baseline-v6.12.0.md`, T414: 20 cases,
11 pass, 9 known-failing) with `@context-retriever` retrieval enabled, and compare against that same
baseline. If the golden suite does not measurably improve, Phase 5's RAG feature does not ship, per
`plan-035`'s own literal, non-negotiable ship-gate wording.

## What actually happened: a pre-dispatch blocker, not a completed measurement

Before authoring a dispatch brief that could be handed to an implementing agent, the orchestrator
re-confirmed T456's actual mechanism by reading the golden suite's real execution model directly —
not assuming a "re-run the scorecard tool twice" comparison would be meaningful without first
confirming what the scorecard tool actually does. It found a genuine, load-bearing gap:

**The golden suite was deliberately designed, as a Phase 1 architectural decision, to never invoke
a live agent/model completion in its automated run path.** Direct citations, not paraphrase:

- `docs/artifacts/golden-suite-format-v1.md` §2.2 ("Decision"): *"Each case's `expect.py` performs
  deterministic, scripted validation of a given end state. It **never itself invokes a live,
  sampling model completion.**"*
- `docs/artifacts/golden-suite-format-v1.md` §4.2 ("Purity rules"): `check()` MUST *"make no network
  calls and invoke no live/sampling model completion."*
- `docs/artifacts/golden-suite-format-v1.md` §4.1: `scripts/scorecard.py` loads every discovered
  `expect.py` via `importlib.util.spec_from_file_location` and calls `module.check(case_dir)`
  directly — *"no subprocess, no shelling out, uniform across every case."*
- `scripts/scorecard.py`'s own docstring for `load_expect_module()`: *"No subprocess, no shelling
  out."* (read directly from the live file at the commit this brief was authored against, not
  quoted from memory).

**The consequence, worked through explicitly:** every one of the 20 existing golden cases' pass/fail
outcome is a pure function of the bytes checked into that case's `fixture/` directory, evaluated by
a script that never calls any agent, model, or `@context-retriever` at all. There is no "retrieval
enabled" vs. "retrieval disabled" configuration that could change `scripts/scorecard.py`'s output on
the existing case set — running it twice, in any two configurations, produces byte-identical
scorecards, because nothing in that pipeline is sensitive to whether retrieval exists, is enabled, or
is even installed. A repo-wide search confirmed no separate live-agent-execution mechanism for golden
cases exists anywhere else in this repository either (unlike Terminal-Bench/Layer 2, which does run
live trials via Harbor/Docker — the golden suite has no equivalent).

**Genuinely measuring "does retrieval improve the golden suite" therefore requires new
infrastructure that does not exist today**: something that actually invokes a live agent session
against each case's `brief.md` (with `@context-retriever` available for a treatment arm, absent for
a control arm), producing a new candidate output, then checks that candidate against the case's
*existing* `expect.py` (reused, not modified — `expect.py`'s own purity/determinism contract is
exactly what makes it a valid, reusable check against a *new* candidate output, not just the
checked-in fixture). This is real, substantial new infrastructure, comparable in shape to what
Terminal-Bench's own Layer 2 harness (T417-T419) needed — not a "medium, 30k-token" task's worth of
work, and not something `scripts/scorecard.py` itself should be modified to do (it is a protected
path under `docs/artifacts/protected-paths-v1.md`, and its own explicit, hard-won Phase 1 design
decision — the determinism/no-live-model tension `golden-suite-format-v1.md` §2.1 documents at
length — is not something this task has standing to silently reverse).

## Disposition (user-approved, 2026-09-09)

Presented four options to the user (build the harness now under T456's own mismatched scope; a
bounded pilot on a few cases; declare the literal gate honestly unmeasurable with current
infrastructure and open a properly-scoped follow-up; or redefine "improve" to avoid live
re-execution entirely). **User approved option (C): declare T456's literal ship gate honestly
unmeasurable with current infrastructure, close this task with an honest `blocked` status — not a
fabricated pass, and not silently dropped — and open a properly-scoped follow-up task for the real
live-execution harness rather than building it under this task's own scope.**

This task's status is **`blocked`**, per this repo's own task-lifecycle convention
(`pending → in_progress → blocked → in_progress → in_review → done`, `blocked` triggered by "Dependency
or blocker encountered" — `implementation/knowledge/skills/task-management/SKILL.md`). This is
deliberately **not** `done` (no measurement was actually performed, so no pass can honestly be
claimed) and **not** `cancelled` (the objective is still valid and still required before Phase 5 can
formally ship — nothing about *wanting* this measurement has changed, only the discovery that the
infrastructure to perform it does not yet exist). It remains in `docs/tasks/active-tasks.md` (blocked
tasks are not terminal and are not archived) until **T458** (the new follow-up task, below) is done,
at which point T456 can be genuinely re-attempted using T458's harness.

## What this does and does not mean for Phase 5

- **T450-T455 (6 of Phase 5's 7 tasks) are genuinely done and independently verified** — the
  git-versioned knowledge store, the three enforced scopes, the indexing pipeline, hybrid retrieval,
  the read-only `@context-retriever` agent, and its own independently-verified retrieval-quality eval
  (recall@5=1.000, real measured latency well under budget) all exist, work, and are usable by any
  agent today.
- **Phase 5's formal ship gate (T456) has not been cleared.** Per `plan-035`'s own literal,
  non-negotiable rule, the RAG feature does not formally ship — meaning it should not be presented
  as "shipped," "measured to improve outcomes," or promoted out of an experimental/available-but-
  unvalidated status — until T456 actually runs using T458's harness and either passes or fails the
  pre-registered improvement threshold.
- **Gate G3** (`plan-035` §2.4, "closes here" at the end of Phase 5's task table) **remains open**
  for the same reason — this is not a new finding, it is the direct, honest consequence of T456
  being blocked rather than passed.
- This is a genuine, disclosed infrastructure gap discovered at the last mile of Phase 5, not a
  quality problem with T450-T455's own work — none of their acceptance criteria required this
  harness to exist, and none of their independent verification is affected by this finding.

## Blocker Protocol record

- **Type:** `technical`
- **Severity:** `critical` (blocks this task's own execution entirely; does not block Phase 5's
  already-delivered functionality)
- **Description:** as above — the golden suite has no live-agent execution path by deliberate Phase
  1 design, so no existing mechanism can measure a "retrieval enabled vs. disabled" delta on the
  current 20-case suite.
- **Suggested resolution:** build a dedicated live-execution harness (T458, opened below) rather than
  attempt to route around the golden suite's own frozen, protected determinism contract.
- Escalated to and resolved by the user directly (not a 2-retry agent-level blocker — this was found
  by the orchestrator during pre-dispatch scoping, before any agent was ever dispatched).

## Constraints (honored throughout this finding's own authoring)

- Did not touch `.mcp.json`, the main checkout, `tests/golden/**`, `scripts/scorecard.py`,
  `docs/benchmarks/tb-subset.json`/`.md`, `feature/T475-codex-platform-integration`, or start any
  Phase 3 work. `golden-suite-format-v1.md` and `scripts/scorecard.py` were read directly to ground
  this finding in primary evidence, never edited.
