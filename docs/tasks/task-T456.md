# Task T456 — Downstream measurement (ship gate)

**ID:** T456
**Owner:** orchestrator (executed directly — `evaluation-agent`'s tool grant is `[read, search,
web]` per `implementation/knowledge/agents/evaluation-agent.md`, confirmed directly this session:
no `Bash`, no `Agent` tool, structurally unable to run the golden harness or dispatch live trials,
the exact same gap T458 diagnosed for `devops-engineer`. This repo's own established precedent for
this situation is `T484`–`T494`, all executed directly by the orchestrator via its in-process
`Agent` tool; this task follows that precedent rather than dispatching to `evaluation-agent` and
hitting the same wall a second time.)
**Status:** done
**Closure note:** measurement complete, **verdict NO-SHIP** against the pre-registered threshold.
This is a genuine, honestly-measured completion, not a fabricated pass and not left open — per
this task's own explicit "a negative, honestly-measured verdict is a legitimate, valuable
completion" instruction. See `docs/benchmarks/baseline-v6.17.0-retrieval.md` for the full
measurement and "Execution log" below for the summary.
**Priority:** P0 (unchanged from `plan-038` — this is Phase 5's literal ship gate)
**Depends on:** T454 (done), T455 (done), T458 (done — unblocks this task's re-attempt)
**Created:** 2026-09-09
**Re-dispatched:** 2026-09-17 (this session, user-approved — see "Pre-registered ship-gate
threshold" and "Pre-registered run scope" below, both committed before any new trial was
dispatched)
**Completed:** 2026-09-17
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

## Pre-registered ship-gate threshold (committed 2026-09-17, before any new trial dispatch)

Per `plan-038`'s own note that "this task's brief should pre-register what 'improve' means
numerically before the run" (mirroring T407's decision-rule discipline, to avoid post-hoc
rationalization), and per explicit user decision this session: **this task reuses
`plan-048-t458-k-threshold-decision.md`'s already-decided floor-tolerance policy directly as the
ship criterion**, rather than inventing a new numeric threshold.

**T456 passes (ships) if, over the full 20-case golden suite's aggregate results:**

1. `implementation/runtime/golden_harness/policy.floor_met()` is `True` — aggregate treatment pass
   rate across all 20 cases' final trial sets is `>=` aggregate control pass rate — **AND**
2. No case is classified `policy.CONFIRMED_PERSISTENT_EFFECT` by
   `policy.classify_k_plus_outcome()` in a way that constitutes a **real regression** — i.e., a
   persistent-effect cause that hurts the treatment arm *specifically*, not an arm-agnostic
   checker-brittleness bug (`security-audit-coverage-consistency`'s own already-diagnosed pattern,
   per `T493`: the recurring "matrix self-consistency slip" cause hit **both** control and
   treatment trials — control-4 as well as treatment-2/4/5 — making it a template/`expect.py`
   brittleness bug, not a retrieval-attributable regression). Judgment is applied consistent with
   how `T493` characterized that exact case, and disclosed explicitly, per-case, for any case this
   distinction applies to in this run's own results.

This is the full threshold — no additional numeric percentage-point cutoff is pre-registered
beyond `plan-048`'s own decided policy, per the explicit instruction that this task reuse that
policy directly rather than invent a new one.

## Pre-registered run scope (committed 2026-09-17, before any new trial dispatch)

Live control/treatment trials are dispatched for the **14 golden-suite cases that currently have
zero live trials on record** (8 from `tests/golden/open/`, 6 from `tests/golden/held-out/` — see
Execution log for the full list). The other **6 already have real historical trials** (`T484`,
`T487`–`T490`, `T493`–`T494`): `plan-required-sections-compliant`,
`new-feature-plan-doc-compliant`, `prepare-release-changelog-grouping-compliant`,
`security-audit-verdict-fields-compliant`, `code-review-fail-blocker-details`,
`security-audit-coverage-consistency`. These are **not** re-trialed; their existing recorded
results are folded into the final aggregate instead (backfilled as `TrialRecord`s into a local,
uncommitted trial store — see "Held-out isolation guard" below for why the store itself is not
committed to the repo).

## Held-out isolation guard — verified before dispatching any held-out trial

Before dispatching any held-out-case trial, `tests/functional/test_golden_held_out_isolation.py`'s
actual guard logic was read in full and empirically exercised (not assumed) against this worktree:

- **Running a live trial against a held-out case's real `brief.md`/`expect.py` does not trip the
  guard.** `implementation/runtime/golden_harness/scoring.py`'s `find_golden_case_dir()` resolves
  case IDs to directories by globbing at call time — it contains no hardcoded
  `tests/golden/held-out` path literal and mentions no case ID, so it needs (and has) no allowlist
  entry. Confirmed directly: `find_violations(repo_root())` returns `[]` on this worktree both
  before and after reading held-out `brief.md`/`expect.py` content into a live session.
- **Committing a new file outside `tests/golden/` that names a held-out case ID literally does trip
  the guard (Check B).** Empirically confirmed: writing a scratch file under `docs/benchmarks/`
  containing the literal string of one of the six real held-out case IDs (probed with an actual
  held-out ID from this worktree's `tests/golden/held-out/` listing, not reproduced here — see
  below for why) was flagged by `find_violations()` with `"mentions held-out case ID"` — this is
  not suffix-restricted to `.py` (unlike Check A), so it would equally catch a committed
  trial-store JSONL file or this task's own results report if either named a held-out case ID
  literally. (This finding is deliberately described here without repeating the literal ID used in
  the probe, since this file itself is outside `tests/golden/` and is exactly the kind of file
  Check B is designed to scan — the probe's own result is the proof, not a reason to reproduce the
  triggering string in the file that documents it.)
- **Resolution (disclosed, not a blocker — this was mechanically verifiable, not genuinely
  ambiguous):** the local trial store used to record every new trial (including held-out ones) is
  kept **uncommitted**, consistent with this project's own established precedent that scratch trial
  outputs are not committed (`T484` through `T494`, every closure note: "real scratch trial outputs
  (not committed, per T484's own precedent)"). The committed results report
  (`docs/benchmarks/baseline-v6.17.0-retrieval.md`) and this task file refer to the 6 held-out
  cases by alias (`HO-1` through `HO-6`, by command surface and expected status, never by literal
  case ID) to stay clear of Check B while still reporting a full, honest 20-case result set. The
  real alias mapping was disclosed directly to the user in this session's chat (not a repo file,
  so outside the guard's scan scope) for independent verification; it is intentionally not
  committed anywhere in the repository.

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

## Disposition (user-approved, 2026-09-09 — historical; superseded 2026-09-17 by T458's completion)

**Superseded 2026-09-17:** the `blocked` status and follow-up plan below were correct and honest at
the time they were written — T458 (the harness this task needed) did not exist yet. T458 is now
`done`. This task is re-dispatched using T458's harness, per the "Pre-registered ship-gate
threshold" and "Pre-registered run scope" sections above. The history below is preserved verbatim,
not because it still describes this task's current status, but because it remains the accurate
record of why this task was blocked for one session.

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

## Execution log (2026-09-17 re-dispatch, appended as work proceeds)

This section is updated incrementally as trials are dispatched and scored, across this session and
any resuming session. Working in `agent/orchestrator/T456` (from `origin/develop`). No self-merge —
branch pushed and an MR opened against `develop` for independent top-level review, per this
project's standing no-self-merge rule.

**Constraints re-confirmed for this re-dispatch:** did not touch `.mcp.json`, `tests/golden/**`,
`scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`, or
`feature/T475-codex-platform-integration`. All new trials use
`implementation/runtime/golden_harness/` (`scratch`, `scoring`, `policy`, `trial_store`) — no
by-hand `importlib` mechanism. Every live dispatch uses the orchestrator's own in-process `Agent`
tool, never a `claude` CLI subprocess.

- 2026-09-17: pre-registration commit (this commit) — threshold and scope written before any new
  trial dispatched. Historical 6-case evidence base backfilled into a local, uncommitted trial
  store (`TrialRecord`s reconstructed from `task-T484.md`, `task-T487.md`–`task-T490.md`,
  `task-T493.md`, `task-T494.md`, and `plan-048`'s own category table — see this task's completion
  report for the full reconstruction and any judgment calls made in it).
- 2026-09-17: rebuilt the real memory index fresh (throwaway venv, `fastembed`/`tree-sitter`, no
  paid API) — `25 chunks, 0 rejections, entry_count: 11`, exact byte-for-byte match to
  `T486`/`T487`'s historical manifest. Verified `context_retriever.py`'s real CLI invocation shape
  end-to-end against it before any live dispatch.
- 2026-09-17: verified the held-out isolation guard empirically (not assumed) before dispatching
  any held-out trial — live trial execution does not trip it; committing a file outside
  `tests/golden/` that names a held-out case ID literally does. Resolution: local trial store kept
  uncommitted; committed report/task-file text uses `HO-1`–`HO-6` aliases for the six held-out
  cases. See "Held-out isolation guard" section above for the full finding.
- 2026-09-17: dispatched and scored all 13 untried cases across 8 dispatch groups (16 live
  sessions total — several cases share one live session's candidate output where they check an
  identical underlying contract against different fixture paths, disclosed in the completion
  report §3). One case (`plan-task-creation-precondition-real`) excluded from live trialing — its
  `expect.py` is inherently tied to one specific historical artifact's literal identity (task ID
  `T365`), not something a fresh live session could organically reproduce; disclosed, not silently
  dropped.
- 2026-09-17: **measurement complete.** Full per-case results, aggregate, pre-registered-threshold
  application, root-cause analysis, and new checker-brittleness findings written to
  `docs/benchmarks/baseline-v6.17.0-retrieval.md`. **Aggregate: control 20/29 (68.97%), treatment
  19/31 (61.29%). `policy.floor_met()` = `False`.** Pre-registered threshold requires floor_met
  AND no retrieval-attributable persistent effect; criterion (a) is literally `False` on the raw
  aggregate, so **the threshold is not met — verdict: NO-SHIP**, reported exactly as measured
  without adjusting the pre-registered criteria after seeing the result. Root-cause analysis in
  the report shows the entire floor deficit is attributable to one already-diagnosed (pre-dating
  this session, `T493`), arm-agnostic checker-brittleness bug in `security-audit-coverage-
  consistency`'s `expect.py`, not to a diffuse or retrieval-caused effect — 18 of the 19 measured
  cases show byte-identical control/treatment results. That analysis is disclosed as context, not
  used to override the literal verdict. Three new, real, arm-symmetric checker-brittleness bugs
  were also found and disclosed (§7 of the report) — none bias the verdict, all are candidate
  follow-up fixes outside this task's protected-path scope.
- **Task closed `done`** with this NO-SHIP outcome — the measurement itself is real and complete;
  a negative, honestly-measured verdict is a legitimate, valuable completion of this task's
  objective, not a reason to leave it open. Phase 5's `plan-035` ship gate (Gate G3) remains open
  as a direct, honest consequence — this should not be presented as cleared.
