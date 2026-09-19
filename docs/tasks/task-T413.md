# Task T413 — `scripts/scorecard.py` (golden suite JSON + MD scorecard)

**ID:** T413
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** T410 (done — `docs/artifacts/golden-suite-format-v1.md`), T412 (done —
`tests/golden/open/`/`tests/golden/held-out/` split + isolation guard)
**Created:** 2026-08-13
**Completed:** 2026-08-13
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 1, §2.4, Layer 1 table, row T413:
*"`scripts/scorecard.py` → `docs/benchmarks/scorecard-<version>.json` + `.md`. Machine-readable
first, human-readable rendered from it."*) and the Phase 1 acceptance-criteria block (several
criteria are this task's responsibility — see below).

This brief is self-contained, but you must read `docs/artifacts/golden-suite-format-v1.md` in full
(the `expect.py` contract, §4.1, is the load-bearing interface you build against) and
`tests/functional/test_golden_held_out_isolation.py`'s module docstring (you are the one file
pre-allowlisted to reference `tests/golden/held-out/` — understand exactly what that allowlist
does and does not permit before writing code).

## Where to work
This branch stacks T410 through T416 (mirrors the Phase 0 `feature/T400-...` pattern). Existing
worktree, DO NOT create a new one: `/home/emage/Code/emage/worktrees/phase1-golden-suite`, branch
`feature/T410-phase1-golden-suite-v6.12.0` (currently at commit `e3381b8`, T410+T411+T412 all
landed on it). Work on top of that.

## Objective
Build `scripts/scorecard.py`: a single command that discovers every golden case under
`tests/golden/` (both `open/` and `held-out/`), runs each one's `expect.py` contract, and emits a
machine-readable JSON scorecard plus a human-readable Markdown rendering derived from it — not two
independently-authored outputs.

## The contract you run against (format spec §3.1, §4.1 — read in full, this is not optional)
- **Discovery**: recursively glob for `expect.py` files under `tests/golden/`, treat each
  `expect.py`'s parent directory as `case_dir`. MUST exclude any path component starting with `_`
  (excludes `tests/golden/_example-scaffold/`). MUST NOT assume a fixed nesting depth — this is
  what makes T412's `open/`/`held-out/` split transparent to you; you should not need to hardcode
  either directory name anywhere except where the isolation guard's allowlist logic in
  `tests/functional/test_golden_held_out_isolation.py` expects to find you (`scripts/scorecard.py`,
  exact path — do not rename this file or move it, the guard's allowlist is keyed on this literal
  path).
- **Execution**: load every discovered `expect.py` via `importlib.util.spec_from_file_location`
  (mirrors `tests/functional/test_check_version_consistency.py`'s `_load_module()` pattern, already
  used by T412's own guard test) and call `module.check(case_dir)` directly. **No subprocess, no
  shelling out** — the format spec is explicit that the import-and-call path is the one and only
  contract this script builds against, not the CLI wrapper some `expect.py` files also expose.
- **Read-only**: `scripts/scorecard.py` must not write anything under `tests/golden/` (not even a
  cache file) — it is a pure reader of that tree. All of this task's own outputs go under
  `docs/benchmarks/`.

## What the scorecard must report (several are literal Phase 1 acceptance criteria — not optional)
- **Per-case results**: case ID, command surface, `open`/`held-out` location, declared `status`
  (`expected_pass`/`known_failing`), declared `known_failing_category` where applicable, and the
  actual `check()` result.
- **A clear pass/fail/regression distinction**, per the format spec §4.4: an `expected_pass` case
  that returns `False` is a **regression**, reported distinctly from the known-failing set — do not
  collapse "expected but failing" into the same bucket as "known and failing."
- **`tracked_defect` and `capability_gap` counts reported separately** (format spec §4.4's explicit
  requirement) — not collapsed into one "known failures" number.
- **`open`/`held-out` breakdown reported separately** as well as combined totals — this is what lets
  T414's baseline and any future improvement work distinguish suite-wide health from held-out-only
  health without either side needing to read the other's case content directly (scorecard.py is the
  one place both are legitimately visible at once, per its allowlist).
- **Aggregate summary**: total cases run, total pass, total fail, with the counts above broken out.

## The determinism requirement (a real design decision, not a formality)
Phase 1's acceptance criteria: *"Re-running on an unchanged tree produces an identical golden
scorecard (deterministic)."* Taken completely literally, a naive JSON emission (e.g. including a
`generated_at` wall-clock timestamp as a top-level field) would make **every** run byte-different,
trivially failing this criterion despite the actual pass/fail content being identical. You need to
resolve this the same way T410 resolved its own determinism-vs-real-signal tension (§2.3 of the
format spec is a worked example of exactly this kind of reasoning) — pick a real design and justify
it, don't just hand-wave past it. Two reasonable approaches (not exhaustive — use your judgment,
but whatever you choose must make the criterion checkable, e.g. "re-run twice, diff, only the
`generated_at` field differs" is an acceptable and checkable outcome; "everything differs" is not):
1. Include a timestamp field, but document explicitly that "identical" is scoped to every field
   except it — and prove this by actually running the script twice against an unchanged tree and
   diffing the output, confirming only the timestamp differs.
2. Separate "content" (the deterministic part: per-case results, counts) from "run metadata"
   (timestamp) into distinct top-level JSON keys, so a caller can trivially hash/compare just the
   content key for a strict determinism check.
Either is fine. Silently omitting a timestamp entirely, or fudging the determinism claim by not
actually testing it twice, is not.

## Naming and versioning
Plan-035 fixes Phase 1's target release label as `v6.12.0` throughout (see the plan's own Mermaid
diagram and every other Phase 1 artifact name: `tb-subset.json`/`.md`,
`baseline-v6.12.0.md` [T414], `tb-delta-v6.12.0.md` [T41A/T407]) — this is a **pre-registered
label for this phase's deliverables**, not derived from `README.md`'s "Latest release" marker
(currently `v6.10.0`, a distinct, not-yet-cut value; do not read it programmatically to derive this
task's version string). Emit `docs/benchmarks/scorecard-v6.12.0.json` and
`docs/benchmarks/scorecard-v6.12.0.md` literally.

## Coordination note: T419's interim schema needs reconciling
`scripts/tb-delta.sh` (T419, already done) shipped its own **interim** scorecard JSON schema
(`docs/benchmarks/scorecards/tb-delta-scorecard-<run-id>.json`) ahead of this task, because Layer 1
and Layer 2 ran in parallel and T419 couldn't block on you. Read
`docs/benchmarks/tb-delta-runner.md`'s "Scorecard JSON schema" and "Follow-up" sections (in the
`phase1-tb-delta` worktree/branch, not this one — read via `git show
feature/T418-phase1-tb-delta-harness-v6.12.0:docs/benchmarks/tb-delta-runner.md` from this
worktree, or ask the orchestrator for the content if that's inconvenient) for the schema T419
already shipped and its own documented expectation of "a small reconciliation pass... a
field-renaming/wrapping pass, not a redesign." You are not required to make T413's schema and
T419's schema byte-identical in this task — that reconciliation is explicitly flagged as a small
follow-up in T419's own completion record, not blocking T413. But **do** look at what T419 already
shipped before designing your own schema from scratch, so the eventual reconciliation is genuinely
small rather than a redesign. If you find the two schemas are trivially reconcilable (e.g. by
reusing the same field names for the same concepts — `k`, `model`, `delta`, etc., where they
overlap conceptually with golden-suite reporting, which may be none — the two evals measure
different things, so don't force an unnatural unification), do so. If not, note the gap explicitly
in your own completion report as `type: dependency`, `severity: minor`, same as T419 already did on
its side — two-sided tracking, not silently absorbed either direction.

## Expected outputs
- `scripts/scorecard.py` — the runner.
- `docs/benchmarks/scorecard-v6.12.0.json` — machine-readable, generated by running the script.
- `docs/benchmarks/scorecard-v6.12.0.md` — human-readable, rendered *from* the JSON (not
  independently authored — prove this, e.g. the renderer is a separate function/step that takes the
  JSON structure as input, not a human writing prose that happens to match).

## Acceptance criteria
1. `python3 scripts/scorecard.py` runs the full golden suite (all cases under both `open/` and
   `held-out/`) from one command, producing both output files.
2. Re-running on an unchanged tree produces an identical scorecard per the determinism design you
   chose above — demonstrated by actually running it twice and diffing, not asserted.
3. `tracked_defect` and `capability_gap` are reported as separate counts (not collapsed).
4. `open`/`held-out` breakdown is reported separately as well as combined.
5. Any `expected_pass` case that currently fails is reported as a distinct "regression" category,
   not folded into "known failures." (At the time of this task, T411/T412's 20 cases should have
   zero regressions — all `expected_pass` cases pass, all `known_failing` cases fail, per T411's own
   independently-verified acceptance bar. If your scorecard run finds otherwise, that's either a
   real regression worth flagging loudly, or a bug in your runner — investigate which before
   reporting either way.)
6. `scripts/scorecard.py` does not write anything under `tests/golden/` — confirm `git status`
   clean under that path after every run.
7. `python3 tests/run.py` still exits 0 (no regression) — including
   `tests/functional/test_golden_held_out_isolation.py`'s guard still passing with
   `scripts/scorecard.py` now actually existing (it was pre-allowlisted by path in T412; confirm the
   allowlist still resolves correctly now that the file is real, not hypothetical).

## Blocker protocol
- If the format spec's `check(case_dir) -> bool` contract turns out to be ambiguous or
  under-specified for some real case you hit while building the runner -> `type:
  unclear_requirements`, `severity: minor` — pick your best reading, document it in the script's own
  docstring, keep moving.
- If T419's already-shipped schema and your own design turn out to be irreconcilable without a
  genuine redesign of one or the other -> `type: dependency`, `severity: minor` — report, do not
  force an unnatural unification.

## Git workflow
1. `cd /home/emage/Code/emage/worktrees/phase1-golden-suite` (existing worktree, branch
   `feature/T410-phase1-golden-suite-v6.12.0` — do not create a new one).
2. Build the runner, generate both outputs, verify the full acceptance bar above.
3. Commit with a Conventional Commit message (`feat(golden): scripts/scorecard.py + v6.12.0
   scorecard ... Refs T413`).
4. Do not push, do not open an MR. Report worktree path (unchanged), branch name (unchanged),
   commit SHA(s), the actual scorecard summary (totals, open/held-out breakdown,
   tracked_defect/capability_gap counts), your determinism-design choice and its diff-twice proof,
   and explicit confirmation of each of the 7 acceptance criteria above (pass/fail per criterion,
   not just "done") back to the orchestrator.

## Constraints
- Token budget: ~40k tokens (medium scope per the plan, but real design decisions involved —
  budget accordingly).
- File ownership: `scripts/scorecard.py`, `docs/benchmarks/scorecard-v6.12.0.json`,
  `docs/benchmarks/scorecard-v6.12.0.md`. Do not touch `tests/golden/**` (read-only, per the
  guard's own allowlist logic — you are exempted from being *flagged by* the guard, not exempted
  from actually respecting its read-only intent), `docs/artifacts/golden-suite-format-v1.md`
  (T410's, immutable), or `tests/functional/test_golden_held_out_isolation.py` (T412's, do not
  modify its allowlist — if you genuinely need a different allowlist entry, that's a blocker to
  report, not a file to silently edit).

## Completion addendum (2026-08-13)

Delivered: `scripts/scorecard.py`, `docs/benchmarks/scorecard-v6.12.0.json`,
`docs/benchmarks/scorecard-v6.12.0.md`. Current run: 20 cases, 11 pass, 9 known_failing (6
`tracked_defect`, 3 `capability_gap`), 0 regressions. `open`/`held-out` breakdown: `open` 14 total
(8 pass, 4 `tracked_defect`, 2 `capability_gap`), `held-out` 6 total (3 pass, 2 `tracked_defect`, 1
`capability_gap`) — matches T412's held-out split exactly.

**A real design interaction with T412 surfaced during implementation, not pre-anticipated in the
brief:** the output artifacts (`docs/benchmarks/scorecard-v6.12.0.*`) live outside `tests/golden/`,
so — unlike `scripts/scorecard.py`'s own source, which is allowlisted by exact path — they are not
exempt from `tests/functional/test_golden_held_out_isolation.py`'s Check B. Emitting real held-out
case IDs into them would have been exactly the leak that guard exists to prevent, and the agent
could not edit the guard's allowlist (out of scope for this task). Resolution, within this task's
own file ownership: `open/` cases report full identity (`id`, `case_dir`); `held-out/` cases report
every real field (`command`, `status`, `bucket`, `known_failing_category`, `actual_result`) except
identity, which is replaced with a deterministic anonymized label (`held-out-case-<n>`, assigned by
sorting the real IDs, stable across runs). This is a second, independent enforcement of the
held-out isolation principle on top of T412's own guard, not a replacement for it.

**Orchestrator independently verified the anonymization actually holds, not merely accepted the
self-report** (same rigor as T412's review, since this is a direct extension of that same
highest-severity risk item): grepped both output files directly for all six real held-out case IDs
— zero matches in either file. Re-ran `tests/functional/test_golden_held_out_isolation.py`'s own
test suite against the real tree with these new files present — 8/8 still pass, including
`test_real_repo_has_no_held_out_violations`. Decoded the redacted held-out entries in the JSON
directly and cross-checked each `held-out-case-<n>` label's `command`/`bucket`/`category` against
the real `case.yaml` files' ground truth (independently established during T412's own review) —
all six match in the correct sorted order. Independently re-ran the determinism proof: ran the
script twice more, diffed both JSON and MD outputs myself — confirmed only `run_metadata.
generated_at` differs each time, `content` byte-identical; restored the worktree to its committed
state afterward (`git status` clean). Independently spot-checked the T419 schema-reconciliation
claim: confirmed `schema_version`/`runner`/`generated_at` field-naming is genuinely shared with
`tb-delta.sh`'s schema (read directly) while no forced `k`/`model`/`delta` unification was
attempted, consistent with the claim that the two evals measure genuinely different things.
`python3 tests/run.py` re-run fresh (after one transient, non-reproducing 355/17-skipped anomaly
immediately followed by two stable 367/18-skipped re-runs — treated as environmental flakiness, not
a real regression, since it did not reproduce and T413's commit touches nothing under `tests/`).

All 7 of this brief's acceptance criteria confirmed PASS. Status set to `done`. See
`docs/tasks/completed-tasks.md` and `docs/tasks/active-tasks.md`'s "Owner corrections and closure
history" for the ledger-level closure note.
