# Task T410 — Define the golden task suite format under `tests/golden/`

**ID:** T410
**Owner:** solution-architect, orchestrator
**Status:** done
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-13
**Completed:** 2026-08-13
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 1, §2.4, Layer 1 table, row T410)

This brief is self-contained. Read `docs/checkpoints/checkpoint-016-phase0-ground-truth-complete.md`
and `checkpoint-017-t417-harbor-oracle-smoke-complete.md` for prior-phase context and this repo's
established execution patterns (worktree -> MR -> CI -> validation gate -> merge); you do not need
the full conversation history.

## Objective
Design and land the *format* of emage.code's internal golden task suite: a directory-per-case
layout under `tests/golden/` where every case has `brief.md`, `fixture/`, and `expect.py`, and
`expect.py` yields a binary pass/fail — no LLM-judged scoring anywhere in the suite. This is the
scaffolding five more tasks (T411-T416) build on, so precision here compounds; get the contract
right, not fast.

## Why this task exists (Gate G1)
`tests/performance/` already measures whether the harness *runs*. It does not measure whether a
command's output is *correct*. Gate G1 ("No component may be promoted out of beta until an outcome
eval exists that can fail it") requires a suite that can actually fail a real component. That is
this suite.

## The central design decision you must make and document
The plan states two hard constraints that interact:
1. `expect.py` returns **binary pass/fail**, **no LLM-judged scoring**.
2. Acceptance criteria (T413, later) require: "Re-running on an unchanged tree produces an
   identical golden scorecard (**deterministic**)."

A golden case that works by invoking a real agent/model completion live inside the test run (e.g.
actually running `/new-feature` end-to-end via a live Claude Code session) is not deterministic
run-to-run (model sampling, latency, occasional infra flakiness) and is expensive/slow at suite
scale (20 cases, run repeatedly). A golden case that only validates static repo state that never
changes is not testing anything real.

You must choose and document an execution model that satisfies both constraints. The intended
resolution (not mandated — a design choice for you to make and justify, or replace with something
better if you find a stronger option) is: **each case's `expect.py` performs deterministic,
scripted validation** — it does not itself invoke a live nondeterministic model completion. Instead
a case encodes:
- `brief.md` — the task/prompt a user or agent would be given (documentation of *intent*, and also
  usable later as the literal input if T411 chooses to exercise a case against a live agent
  separately as an offline authoring step — but the suite's automated, repeated, CI-safe execution
  path must not require that).
- `fixture/` — the starting repo/workspace state the case operates against.
- `expect.py` — a script that deterministically checks whether a *given end state* (either a
  pre-authored "what correct output looks like" fixture checked into the case, or the actual state
  of `fixture/` after some deterministic, scripted transformation) satisfies the case's pass
  condition. This makes the suite closer to golden-file/property-based testing of each command's
  **rails** (declared preconditions, required output structure, protected-path respect, whether a
  command's own deterministic tooling behaves correctly) than to live capability benchmarking of
  raw model output — Terminal-Bench (Layer 2, T417-T41C) already covers raw agentic capability
  measurement; this suite's job is to cover the 76-component harness's own rails and command
  surface, which Terminal-Bench cannot see.

If, after auditing the actual command surface (`/new-feature`, `/code-review`, `/plan`,
`/security-audit`, `/prepare-release` — read their definitions under
`implementation/knowledge/commands/`), you conclude a different execution model serves Gate G1
better while still satisfying the two hard constraints above, you may propose it — but you must
write down the reasoning and the tradeoff in the format spec (see Expected outputs), since T411's
qa-engineer and T413's devops-engineer both build directly on your choice and cannot re-derive it
from silence.

## Inputs
- `implementation/knowledge/commands/new-feature.md`, `code-review.md`, `plan.md`,
  `security-audit.md`, `prepare-release.md` — the five command surfaces T411's 20 cases will span;
  read enough of each to know what a case for it would plausibly check.
- `tests/performance/` — existing suite, for contrast (what it already covers, so you don't
  duplicate it) and for this repo's existing Python test conventions (`tests/run.py`, `unittest`
  style visible in `tests/performance/test_team_health.py`).
- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1 (T410-T416 table, acceptance criteria
  list, risk table row "Golden suite is authored too easy... T411 mandates >=5 known-failing
  cases").

## Expected outputs
1. `docs/artifacts/golden-suite-format-v1.md` — the format spec: directory layout, the exact
   contract `expect.py` must satisfy (e.g. a `check(case_dir: Path) -> bool` function, or a
   process-exit-code contract — pick one, document it precisely enough that T413's scorecard.py
   can invoke every case uniformly without per-case special-casing), the execution-model decision
   above with rationale, and how `open/` vs `held-out/` (T412, not yours to build) will slot into
   this layout without requiring a format change.
2. `tests/golden/README.md` — practitioner-facing version of the same contract (how to add a case,
   how a case is scored, what "known-failing" means and how it's marked).
3. `tests/golden/_example-scaffold/` — one worked, minimal example case (not one of T411's 20 real
   cases, not counted toward the suite) that mechanically proves the contract: `brief.md`,
   `fixture/`, `expect.py`. Include a small automated test (e.g.
   `tests/functional/test_golden_suite_format.py`) that imports/invokes `expect.py`'s contract
   function against the scaffold and asserts it returns a bool, and that a deliberately-broken
   fixture flips the result — proving the mechanism actually discriminates pass from fail, not
   just always returning `True`.
4. A short note (in the format spec) on how a case should be marked `known-failing` at authoring
   time (T411 needs this) — e.g. a field/marker file distinguishing "expected to fail today,
   tracked" from "should pass, currently broken" (an accidental regression) versus "genuinely
   documents a capability gap."

## Acceptance criteria
1. `docs/artifacts/golden-suite-format-v1.md` exists and unambiguously specifies the case
   directory layout and the `expect.py` contract.
2. `tests/golden/_example-scaffold/` exists and its `expect.py` is invoked successfully by a new
   automated test, which passes on the correct fixture and fails on a deliberately broken one.
3. The design resolves (or explicitly and reasonedly replaces) the determinism-vs-liveness tension
   above — you may not leave it unresolved or push the decision to T411/T413.
4. `python3 tests/run.py` still exits 0 (no regression).
5. The spec explicitly reserves the `open/` / `held-out/` split point for T412 without requiring
   T412 to redesign the per-case contract.

## Blocker protocol
- If the five command surfaces are too heterogeneous for one uniform `expect.py` contract to cover
  all of them meaningfully -> `type: unclear_requirements`, `severity: major`. Do not silently
  narrow scope to fewer command types; report and propose an option (e.g. a thin per-family
  adapter layer under one outer contract) instead.
- If you find the existing `tests/performance/` suite already covers something the plan assumes is
  missing -> `type: dependency`, `severity: minor` (mirrors the Part 1 lesson from the source
  roadmap audit: verify before building).

## Git workflow
1. Create worktree + branch: `git worktree add ../worktrees/phase1-golden-suite -b
   feature/T410-phase1-golden-suite-v6.12.0 develop`. This branch will accumulate T410-T416's
   commits (mirrors the Phase 0 `feature/T400-phase0-ground-truth-v6.11.0` stacking pattern) — do
   not open an MR yet.
2. Commit with a Conventional Commit message (`feat(golden): define golden task suite format...
   Refs T410`).
3. Do not push. Report the worktree path, branch name, and commit SHA back to the orchestrator,
   who owns the branch's push/MR lifecycle per `.claude/rules/git-workflow.md`.

## Constraints
- Token budget: ~25k tokens.
- File ownership: `docs/artifacts/golden-suite-format-v1.md`, `tests/golden/README.md`,
  `tests/golden/_example-scaffold/**`, one new functional test file. Do not touch
  `tests/performance/**`, `scripts/**`, or any command/agent definitions.
- Read-only for implementation code outside the above (per your Conditional Permissions
  classification in `.claude/rules/security-guidelines.md`: "Architect — read-only for
  implementation code; write access limited to architecture docs and decision records" — the
  `tests/golden/` scaffold/format files above are the schema-definition exception this plan
  explicitly assigns you, consistent with your other "Define X" tasks elsewhere in plan-035, e.g.
  T430/T440/T450).

## Addendum (orchestrator, 2026-08-13, tool-grant gap + fallback application)
The dispatched `solution-architect` session completed all real design work — the execution-model
decision, the full command-surface audit, the format spec, the README, the scaffold case, and the
discriminating test — but reported a `type: technical`, `severity: major` blocker at the apply
step: the registered `solution-architect` (`.claude/agents/solution-architect.md`) grants only
`Read, Edit, Write, WebFetch, WebSearch, TodoWrite, mcp__sequential-thinking, mcp__fetch` — no Bash
— so it could not create the worktree/branch, run `python3 tests/run.py` (acceptance criterion 4),
or commit. It correctly did not write into the primary `develop` checkout or fabricate a commit
SHA; instead it staged every output file plus a `RUNBOOK.md` (exact apply sequence + intended
commit message) to the orchestrator's scratchpad and reported cleanly.

This is a different failure mode from T418's (which had no usable design output at all): here the
design work was complete, only the mechanical apply step was blocked. Per this repo's established
fallback precedent (T379/T380/T387/T392 — a Bash-less delegate produces content via Read/Edit, the
Bash-capable orchestrator independently reviews it, then performs the worktree/verification/commit
steps itself), the orchestrator:
1. Independently read and verified every staged file (`golden-suite-format-v1.md`,
   `tests/golden/README.md`, the `_example-scaffold/` case, `test_golden_suite_format.py`) rather
   than trusting the agent's self-report — confirmed the design genuinely resolves the
   determinism-vs-liveness tension (§2 of the format spec), confirmed the cited
   `tests/_helpers/repo.py::repo_root()` and `importlib.util`/`_load_module()` precedent
   (`tests/functional/test_check_version_consistency.py`) both exist exactly as described, and
   confirmed the discriminating test is real (passes on the correct fixture, fails on a
   deliberately-broken copy and on a missing file — not a rubber-stamp `True`).
2. Created the worktree/branch per the RUNBOOK, copied the staged files in, ran the manual
   `expect.py` CLI sanity check (exit 0) and the full `python3 tests/run.py` (359 tests, exit 0, no
   regressions — the new test joined `tests/functional` via automatic discovery).
3. Committed exactly the 7 expected files with the RUNBOOK's prepared Conventional Commit message.

Commit: `ed8c525` on `feature/T410-phase1-golden-suite-v6.12.0`
(`/home/emage/Code/emage/worktrees/phase1-golden-suite`). Not yet pushed/merged — this branch
continues to accumulate T411-T416 per the original git-workflow plan; push/MR/merge happens once
the full Layer 1 chain lands, gated by T416's tech-lead review.

`solution-architect`'s tool grant is unchanged — this was resolved per-task, not by widening the
role's registry permissions, consistent with how T418's mismatch was handled.
