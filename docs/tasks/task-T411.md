# Task T411 — Author 20 golden cases (≥5 known-failing)

**ID:** T411
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T410 (done — see `docs/artifacts/golden-suite-format-v1.md`,
`tests/golden/README.md`, `tests/golden/_example-scaffold/`)
**Created:** 2026-08-13
**Completed:** 2026-08-13
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 1, §2.4, Layer 1 table, row T411)

This brief is self-contained, but you must read `docs/artifacts/golden-suite-format-v1.md` in full
before writing any case — it is the contract you are authoring against, not optional background.

## Where to work
T410 landed on `feature/T410-phase1-golden-suite-v6.12.0`, in the existing worktree at
`/home/emage/Code/emage/worktrees/phase1-golden-suite` (commit `ed8c525`). **Work in that same
worktree, on that same branch** — do not create a new worktree/branch. This branch stacks T410
through T416 (mirrors the Phase 0 `feature/T400-...` pattern); no MR yet.

## Objective
Author 20 golden cases under `tests/golden/<case-id>/` (flat — `open/`/`held-out/` split is T412's
job, not yours), spanning the five command surfaces: `/new-feature`, `/code-review`, `/plan`,
`/security-audit`, `/prepare-release` (4 cases each is a reasonable default split; deviate if you
find good reason, but cover all five). **At least 5 of the 20 must be `status: known_failing`** at
authoring time (`case.yaml`'s `known_failing_category: tracked_defect` or `capability_gap`, per the
format spec §4.3-4.4). A 20/20-passing baseline is treated as a suite defect per plan-035's own
risk table — do not let the suite come out too easy.

## The contract you are building against (read `golden-suite-format-v1.md` for the full version)
Every case: `brief.md` (intent), `fixture/` (state `expect.py` checks against), `case.yaml`
(metadata), `expect.py` (a `check(case_dir: Path) -> bool` function — pure, deterministic, no
network calls, no live/sampling model calls, no time/env/random dependence, must not mutate the
checked-in `fixture/`). `scripts/scorecard.py` (T413, not yet built) will import and call
`check()` directly for every case — it does not shell out or invoke a live agent.

## What a case should actually check (grounding, not fabrication)
The design intent (per the format spec §2.3-2.4) is that each case validates a **real, falsifiable
property of a command's declared output contract** — not an arbitrary synthetic scenario. Read the
five command definitions first:
`implementation/knowledge/commands/new-feature.md`, `code-review.md`, `plan.md`,
`security-audit.md`, `prepare-release.md`. Each specifies a structured, parseable output shape
(e.g. `/code-review`'s `## VERDICT` block with `Status:`/`Must Fix count`/etc fields; `/plan`'s
required section headers and its Task Creation Precondition; `/security-audit`'s 10-row OWASP
matrix; `/prepare-release`'s `## RELEASE VERDICT` block; `/new-feature`'s plan doc + `[CHECKPOINT]`
line format). The format spec's own audit table (§2.4) is a starting point, not exhaustive — verify
against the actual command files yourself.

**Prefer grounding fixtures in real artifacts already in this repo** where practical — this repo
has a large real history of command output (`docs/plans/*.md`, `docs/checkpoints/*.md`,
`docs/tasks/task-*.md`, real `## VERDICT`/`## RELEASE VERDICT` blocks in prior checkpoints and task
briefs, e.g. `docs/checkpoints/checkpoint-016-*.md`, `docs/tasks/task-T406.md`). Copying (not
referencing/symlinking — `fixture/` must be self-contained and checked in) a real historical
artifact into a case's `fixture/` and writing `expect.py` to check it against the command's
declared contract is both more grounded and doubles as a regression check against this repo's own
history, versus a fully hand-fabricated fixture. Use your judgment case-by-case — a hand-fabricated
fixture is fine and sometimes necessary (especially for `known_failing`/`capability_gap` cases,
which by definition describe something that doesn't cleanly exist in history yet), but don't default
to fabrication when a real example is available and clean.

## Known-failing cases — two distinct kinds, both count toward the ≥5
1. **`tracked_defect`** — you find (or construct) a case where the command's *declared* contract is
   violated by something that should reasonably be fixed. If you find a real example of this in the
   repo's existing artifacts during your research, that's a strong case — cite it plainly in
   `known_failing_reason`.
2. **`capability_gap`** — a deliberate demonstration that the current command surface doesn't yet
   handle some scenario (e.g. a case whose `brief.md` describes an edge case the command's own
   definition doesn't address). This is not a "bug" — it's an honest gap.

Do not mark a case `known_failing` just to hit the quota if it actually passes — that defeats the
point (T413/T415 will need this signal to be real). Conversely, do not manufacture artificially
easy passes to pad the other 15 — a 20/20 result before this task even finishes would itself be a
red flag per the plan's own risk table.

## Inputs
- `docs/artifacts/golden-suite-format-v1.md` — the format spec (read in full)
- `tests/golden/README.md` — quick-reference practitioner guide
- `tests/golden/_example-scaffold/` — worked minimal example (not a real case, don't touch it)
- `implementation/knowledge/commands/{new-feature,code-review,plan,security-audit,prepare-release}.md`
- Real historical artifacts for fixture grounding: `docs/plans/`, `docs/checkpoints/`,
  `docs/tasks/task-*.md`, `docs/artifacts/`

## Expected outputs
- 20 new directories under `tests/golden/`, each with `brief.md`, `fixture/`, `case.yaml`,
  `expect.py`, satisfying the format spec's contract exactly.
- At least 5 with `status: known_failing` (mix of `tracked_defect`/`capability_gap`, your call on
  the exact split, but both categories should be represented — don't make all 5+ the same category).
- Each case's `expect.py` must be runnable standalone: `python3 tests/golden/<case-id>/expect.py
  tests/golden/<case-id>` exits 0 for a case whose fixture currently satisfies its own pass
  condition, 1 otherwise (this must match `case.yaml`'s declared `status` — an `expected_pass` case
  whose `expect.py` currently returns `False` is a bug in your case, not evidence of anything; a
  `known_failing` case's `expect.py` returning `False` today is the expected, correct state).

## Acceptance criteria
1. Exactly 20 case directories exist under `tests/golden/` (excluding `_example-scaffold/`), each
   with all four required members.
2. At least 5 have `status: known_failing` in `case.yaml`; running their `expect.py` against their
   own `fixture/` actually returns `False` (i.e. they are genuinely failing today, not mislabeled).
3. Every `status: expected_pass` case's `expect.py` actually returns `True` against its own
   `fixture/` (no accidental placeholder failures among the "should pass" set).
4. All five command surfaces (`/new-feature`, `/code-review`, `/plan`, `/security-audit`,
   `/prepare-release`) have at least 2 cases each.
5. Every `expect.py` satisfies the purity rules (format spec §4.2) — spot-check by running the full
   set twice in a row and confirming identical results, and confirm `git status` is clean after
   running every case's `expect.py` (no fixture mutation).
6. `python3 tests/run.py` still exits 0 (no regression in the existing suite — your new
   `tests/golden/` content is not itself part of `tests/functional`/`tests/performance` discovery,
   so this should be unaffected, but confirm).
7. Write a short manifest, `tests/golden/_manifest-t411.md` (or similar — your call on exact name),
   listing all 20 case IDs, which command each targets, and pass/known-failing status — this is a
   convenience index for T413/T414/T415's authors, not part of the format contract itself.

## Blocker protocol
- If you find a command definition's declared contract is itself ambiguous or contradictory (can't
  tell what "correct" output looks like well enough to write a deterministic check) ->
  `type: unclear_requirements`, `severity: minor` — pick your best reading, document the ambiguity
  in that case's `brief.md`, and keep moving; don't block the whole task on one case.
- If you genuinely cannot find or construct 5 known-failing cases across two categories (i.e.
  everything you try turns out to already pass) -> `type: unclear_requirements`, `severity: major`
  — report before padding the count with borderline cases.

## Git workflow
1. `cd /home/emage/Code/emage/worktrees/phase1-golden-suite` (existing worktree, branch
   `feature/T410-phase1-golden-suite-v6.12.0` — do not create a new one).
2. Author all 20 cases; run the full verification bar above.
3. Commit with a Conventional Commit message (`feat(golden): author 20 golden cases across 5
   command surfaces... Refs T411`). One commit is fine; multiple is also fine if it helps you work
   incrementally — your call.
4. Do not push, do not open an MR. Report worktree path (unchanged), branch name (unchanged),
   commit SHA(s), and the manifest's contents back to the orchestrator.

## Constraints
- Token budget: ~60k tokens (largest single task in this plan's Layer 1 — budget accordingly, this
  is real work, not padding).
- File ownership: `tests/golden/<new case dirs>/**`, `tests/golden/_manifest-t411.md`. Do not touch
  `tests/golden/README.md`, `tests/golden/_example-scaffold/`, `docs/artifacts/golden-suite-format-v1.md`,
  or anything under `scripts/`, `tests/functional/`, `tests/performance/`.

## Completion addendum (2026-08-13)

First dispatch was interrupted mid-task by an account-wide Claude usage-limit stop (not a code
error, not a reported blocker). State on resumption: 11 of 20 case directories complete (all
independently re-verified correct at that point — each `expect.py` matched its declared status),
plus one half-authored stub (`security-audit-verdict-fields-compliant/`, `fixture/` only, missing
`brief.md`/`case.yaml`/`expect.py`), and zero cases for `/new-feature`/`/prepare-release` — failing
acceptance criterion 4. Everything was uncommitted in the existing worktree/branch.

A second `qa-engineer` dispatch, working in the same worktree/branch, resolved the stub and
authored the remaining 9 cases (1 `/security-audit`, 4 `/new-feature`, 4 `/prepare-release`),
bringing the suite to the required 20/20 with exactly 4 cases per surface and 9 `known_failing`
(6 `tracked_defect`, 3 `capability_gap`) against 11 `expected_pass`. Several new cases ground their
fixtures in real repo artifacts rather than hand-authored ones
(`docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md`, copied verbatim;
`docs/artifacts/adapter-evaluation-v1.md`, `docs/artifacts/benchmark-report-v1.md`, and
`docs/checkpoints/checkpoint-release-v6.4.1.md`, copied with small, inline-documented cosmetic
redactions — markdown links converted to inline code spans, leading `v` dropped from version
tokens — solely because `tests/golden/` is not in the path-exclusion list of this repo's own
`tests/functional/test_link_integrity.py`/`test_check_version_consistency.py` gates, and an
unredacted copy would have false-triggered them). Self-resolved per the Blocker Protocol's "pick
best reading, document, keep moving" allowance (`type: unclear_requirements`, `severity: minor`,
not escalated) rather than choosing between exact-byte-copy and redaction by asking first.

**Orchestrator independent verification** (not a re-statement of the agent's self-report):
1. Confirmed 20/20 case dirs (excluding `_example-scaffold/`) via direct `ls`, each with all four
   required members present, exactly 4 per surface across all 5 surfaces.
2. Confirmed status distribution matches the claim exactly: 9 `known_failing` (6 `tracked_defect`,
   3 `capability_gap`), 11 `expected_pass`.
3. Ran every case's `expect.py` against its own fixture twice in direct succession: identical exit
   codes both runs (determinism demonstrated, not asserted), every result matches its declared
   `case.yaml` status, `git status --short` clean after each run (no fixture mutation).
4. Ran `python3 tests/run.py` fresh: 359 tests, exit 0, no regression (includes the two
   markdown-link/version-consistency gates the redacted fixtures interact with).
5. Specifically targeted the one place a shortcut could quietly invalidate a case: diffed all
   three real-artifact fixtures against their live repo originals, then read each affected case's
   `expect.py` line-by-line to confirm the redacted content is outside what that check actually
   inspects — `new-feature-real-artifact-versioning-drift` checks only a filename glob pattern
   (never reads file content); `prepare-release-real-verdict-missing` checks only for a
   `## RELEASE VERDICT` heading's presence/absence (absent in both original and redacted copy,
   the version-string edits are irrelevant to the check); the checkpoint-017 copy needed no
   redaction at all (diff against the original is empty). Confirmed genuinely cosmetic in all
   three cases, as claimed.

Status set to `done`. See `docs/tasks/completed-tasks.md` and `docs/tasks/active-tasks.md`'s
"Owner corrections and closure history" for the ledger-level closure note.
