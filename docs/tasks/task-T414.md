# Task T414 — Publish `docs/benchmarks/baseline-v6.12.0.md`

**ID:** T414
**Owner:** release-manager
**Status:** in_progress
**Priority:** P0
**Depends on:** T410 (done), T411 (done), T412 (done), T413 (done — `scripts/scorecard.py`,
`docs/benchmarks/scorecard-v6.12.0.json`/`.md`)
**Created:** 2026-08-13
**Completed:** —
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 1, §2.4, Layer 1 table, row T414:
*"Publish `docs/benchmarks/baseline-v6.12.0.md`. **Do not optimise anything before this file
exists.**"*) and the plan's risk table: *"Golden suite is authored too easy, baseline reads 20/20 |
Medium | High | T411 mandates ≥5 known-failing cases; **T414 rejects a perfect baseline**."*

This is the smallest-scope task in Layer 1, but it is a real gate, not a formality — read the risk
table line above carefully. T414's job is not just to copy T413's numbers into a new file; it is to
be the control point that would have caught it if T411 had produced a too-easy suite, and to
formally establish this scorecard as the frozen reference point all future improvement work is
measured against.

## Where to work
Existing worktree, DO NOT create a new one: `/home/emage/Code/emage/worktrees/phase1-golden-suite`,
branch `feature/T410-phase1-golden-suite-v6.12.0` (currently at commit `7c1c698`, with
T410+T411+T412+T413 all landed). Work on top of that.

## Objective
Publish `docs/benchmarks/baseline-v6.12.0.md` — the formal, human-facing baseline document that
establishes the current golden suite scorecard (`docs/benchmarks/scorecard-v6.12.0.json`/`.md`,
T413, already committed on this branch) as the reference point for Phase 1. Once this file exists,
plan-035's own instruction is explicit: **no improvement/optimization work against the golden suite
may begin until it does.**

## What "rejects a perfect baseline" means in practice
Before publishing, verify — don't assume — that the current scorecard is not a 20/20 (or otherwise
too-easy) result:
1. Read `docs/benchmarks/scorecard-v6.12.0.json`'s `content.summary` directly. Confirm
   `known_failing` (the sum of `tracked_defect` + `capability_gap`) is at least 5, per T411's own
   mandate. At the time of this task's authoring, the real committed scorecard shows 9
   known_failing (6 `tracked_defect`, 3 `capability_gap`) against 11 pass — comfortably clears the
   floor. Confirm this yourself by reading the actual file, not by trusting this brief's numbers,
   which could be stale if anything changed between this brief being written and you picking it up.
2. If — contrary to the above — you find the real scorecard at or near 20/20 (or otherwise judge
   the known-failing set too thin to be a meaningful signal), **do not publish a baseline that
   claims a too-easy result as if it were a healthy one.** This is the literal "T414 rejects a
   perfect baseline" control. In that case: stop, do not create `baseline-v6.12.0.md`, and report a
   blocker (`type: unclear_requirements`, `severity: major` — "golden suite baseline reads as too
   easy, needs hardening before Phase 1 can proceed per the plan's own risk table") rather than
   publishing anyway. This should not trigger given the real current numbers, but the check itself
   — actually reading the numbers and reasoning about whether they clear the bar, not rubber-stamping
   — is the deliverable, not just the file.

## What the published baseline document should contain
- The scorecard's headline numbers (total cases, pass, regressions, known_failing broken into
  `tracked_defect`/`capability_gap`, the `open`/`held-out` breakdown) — sourced from
  `docs/benchmarks/scorecard-v6.12.0.json`, not restated by hand from memory (link to or quote the
  actual JSON/MD, don't risk a transcription drift between the source of truth and this new
  document).
- An explicit statement that this is the **frozen Phase 1 baseline** — the reference point future
  improvement work's golden-suite results are compared against — and the plan's own instruction
  that no optimization work may begin before this file exists (quote it; this is a real process
  gate other agents/tasks need to be able to find and cite).
- An explicit statement confirming the "not a perfect/too-easy baseline" check above was performed
  and passed, with the actual known-failing count cited (not just "checked, looks fine").
- A pointer to the held-out isolation guard (T412,
  `tests/functional/test_golden_held_out_isolation.py`) and a brief explanation of why held-out
  case identities are not enumerated in this document (mirror T413's own reasoning — this baseline
  document lives outside `tests/golden/` and is exactly the kind of file the isolation guard's
  Check B would flag if it named a real held-out case ID; aggregate held-out health is fine to
  cite, identity is not). Verify this yourself before publishing — run
  `tests/functional/test_golden_held_out_isolation.py` after writing the document and confirm it
  still passes with your new file in place, exactly as T413 had to do for its own outputs.
- A short "how to reproduce" note: `python3 scripts/scorecard.py` regenerates the scorecard this
  baseline is sourced from; this baseline document itself is not regenerated automatically (it is a
  point-in-time snapshot/publication, not rebuilt every run the way `scorecard-v6.12.0.json`/`.md`
  are) — make this distinction explicit so a future reader doesn't assume this file updates itself.

## Acceptance criteria
1. `docs/benchmarks/baseline-v6.12.0.md` exists, sourced from the real, current
   `docs/benchmarks/scorecard-v6.12.0.json` (numbers cross-checked against that file, not
   transcribed from a stale copy or hand-recalculated).
2. Explicitly documents that the "reject a too-easy baseline" check was performed, with the actual
   known-failing count cited, and confirms it clears T411's ≥5 floor.
3. Explicitly states the "no optimization before this file exists" gate, quoting plan-035's own
   language.
4. Does not name any real held-out case ID (verify: `grep` your new file for all six real held-out
   case IDs listed in `tests/golden/_manifest-t411.md`'s "open/held-out split (T412)" section —
   zero matches expected) and re-run `tests/functional/test_golden_held_out_isolation.py` after
   writing it to confirm the guard still passes with your file present.
5. `python3 tests/run.py` still exits 0 (no regression).
6. `git status` clean under `tests/golden/` and `scripts/` after your work (you should not have
   touched either — this task's only new file is under `docs/benchmarks/`).

## Blocker protocol
- If the real current scorecard reads as too easy (near 20/20, or known-failing count judged too
  thin to be meaningful) -> `type: unclear_requirements`, `severity: major` — do not publish, report
  instead, per the "what 'rejects a perfect baseline' means" section above.
- If you find any ambiguity in how to present the `open`/`held-out` breakdown without naming
  held-out identities -> `type: unclear_requirements`, `severity: minor` — mirror T413's own
  resolution (aggregate fields visible, identity redacted/omitted), document your reasoning, keep
  moving.

## Git workflow
1. `cd /home/emage/Code/emage/worktrees/phase1-golden-suite` (existing worktree, branch
   `feature/T410-phase1-golden-suite-v6.12.0` — do not create a new one).
2. Write the baseline document, verify the full acceptance bar above.
3. Commit with a Conventional Commit message (`docs(benchmarks): publish golden suite baseline
   v6.12.0 ... Refs T414`).
4. Do not push, do not open an MR. Report worktree path (unchanged), branch name (unchanged),
   commit SHA(s), the actual baseline numbers you published, confirmation the too-easy check was
   performed and passed, and explicit confirmation of each of the 6 acceptance criteria above back
   to the orchestrator.

## Constraints
- Token budget: ~20k tokens (small scope per the plan — this is a focused publication task, not a
  redesign).
- File ownership: `docs/benchmarks/baseline-v6.12.0.md` only. Do not touch
  `docs/benchmarks/scorecard-v6.12.0.json`/`.md` (T413's, generated artifacts — read them, don't
  edit them), `scripts/scorecard.py` (T413's), `tests/golden/**` (read-only), or
  `tests/functional/test_golden_held_out_isolation.py` (T412's).
