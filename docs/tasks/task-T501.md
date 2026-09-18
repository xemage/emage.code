# Task T501 — Wire weakness mining to the Phase 1 failure taxonomy (`plan-035` nominal T461)

**Owner:** backend-developer
**Status:** in_progress
**Priority:** P0
**Depends on:** none (T415/T409 taxonomy artifacts are already `done` and merged)
**Created:** 2026-09-18
**Based on:** `docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's
`T461-equiv` row and §1 (this repo's real next-free task ID, `T501`, assigned at dispatch time
per that plan's own explicit instruction not to invent numbers itself); `docs/artifacts/
phase6-sia-readiness-audit-v1.md` §5 item 1 (the open design question this brief resolves below)
and §4 (the corrected Phase 6 dependency graph — this task depends on the golden-harness/
failure-taxonomy infrastructure, **not** on `implementation/sia/` or any reward/trajectory/
fine-tuning subsystem); `docs/artifacts/failure-taxonomy-v1.md` (T415, the real, tested
`cause x behavior x mechanism` scheme this task wires into); `docs/benchmarks/failures/README.md`
and its two index tables (T415 golden-suite cases, T409 Terminal-Bench patterns).

**Do not treat `plan-035` §2.4 Phase 6's own introductory prose ("`implementation/sia/`,
`sia-executor.py`, reward shaping, harness capture, and reward attachment already exist")
as a scoping instruction for this task.** Per the audit's primary finding, that prose describes
a different, invalidated subsystem this task has no dependency on. This task's real dependency
graph is: `docs/artifacts/failure-taxonomy-v1.md` + `docs/benchmarks/failures/**` (T415/T409,
real, merged, tested) feed this task directly.

## Why this task exists

T415 defined a real, reusable three-axis failure classification scheme and classified 15 real
failure records against it (9 golden-suite `known_failing` cases + 6 Terminal-Bench failure
patterns, per `docs/benchmarks/failures/README.md`'s two index tables). Today that classification
exists only as human-readable Markdown (per-case `.md` files plus a `README.md` index table) —
nothing in this repo can query it programmatically. Phase 6's later tasks (a future diff-proposal
generator, not built by this task) will need to consume "which failures share this `cause`/
`behavior`/`mechanism` combination" as structured input, not by re-parsing prose. This task's job
is to make that existing, static taxonomy genuinely machine-consumable — nothing more.

## A disclosed scoping decision, not an oversight

The audit (§5 item 1) flags an open design question this brief must resolve, not leave to the
implementer to guess: how do failures beyond the 15 currently-classified records flow into the
same taxonomy on an ongoing basis (future golden-suite runs, or the Terminal-Bench delta harness
tasks T417-T419)?

**Resolution: this task's scope is deliberately narrowed to the first real increment only.**
This task makes the 15 *currently existing* classified failure records (the ones T415/T409 already
produced and committed) real, structured, queryable input for a future weakness-mining consumer.
**It explicitly does NOT build any mechanism for new failures to be added to, or re-classified
into, the taxonomy over time.** That is a separate, real, not-yet-scoped future increment — it
needs its own design pass (at minimum: who/what triggers re-classification after a golden-suite
or Terminal-Bench delta run, how a not-yet-seen failure shape gets a new axis value versus reusing
an existing one, and whether it's automated or human-reviewed) that this task does not attempt.
State this explicitly in whatever documentation this task produces, exactly as stated here: this
is a deliberate scope boundary, not a gap the implementer forgot about.

This resolution was chosen (over attempting both problems at once) because: (a) the "ongoing feed"
problem has no existing design to build against — inventing one inside this task would silently
expand a `medium`-scoped task into an undefined-size research task; (b) proving the *existing*
taxonomy is genuinely consumable is a real, independently valuable, and completely buildable
increment on its own, and a future consumer (the not-yet-built diff-proposal generator) needs
exactly this much to start being designed against; (c) it mirrors this repo's own repeated
practice of narrowing a task to what is concretely buildable now and disclosing the rest as a
named follow-up rather than silently expanding scope (see T461's own audit precedent, and T415's
own "regressions and unexpected_pass cases are out of scope... note explicitly" instruction).

## Objective

1. Build a real, tested Python module that parses the existing failure-classification data under
   `docs/benchmarks/failures/**` (all 15 currently-committed records: 9 golden-suite files in the
   top-level directory, 6 Terminal-Bench pattern files under `terminal-bench/`) into structured
   records, and exposes a query API over them (e.g. "all records with `cause: X`", "all records
   with `behavior: Y` regardless of source", "the full record for a given file/case id"). Your
   call on the exact internal data shape (dataclass, dict, whatever fits this repo's existing
   style) and on whether you parse the individual per-case `.md` files directly or the `README.md`
   index tables (or both, cross-checked against each other) — document which you chose and why,
   the same way T415's own brief left "one file per case or a single index" as an implementer
   decision to be documented, not prescribed here.
2. Module location: your call, but the natural precedent in this repo is `implementation/runtime/
   golden_harness/` (T458's real, tested `scoring.py`/`policy.py`/`schema.py`) for harness-adjacent
   code — either add a new file there or start a clearly-named sibling module under
   `implementation/runtime/`. Document your choice.
3. A committed test (following the `tests/functional/test_golden_harness_*.py` naming precedent
   for modules in this area) that exercises real queries against the real on-disk data under
   `docs/benchmarks/failures/**` — not mocked/fixture data — and asserts specific, correct results
   (e.g. the known record count per source, a specific known case's full axis assignment, a query
   by axis value returning exactly the expected set of case/file ids). This test is the actual
   proof this task's own claim ("the taxonomy is now genuinely consumable") is true, not merely
   asserted.
4. A short design note (inline in the module's own docstring is sufficient — a new
   `docs/artifacts/*.md` file is not required for a wiring task this size, your call if you think
   one adds real value) stating: what this task built, the explicit "future increment" scope
   boundary from the section above, and which future task (a not-yet-built diff-proposal
   generator) is expected to consume this module.

## Held-out isolation — same discipline this repo has applied to every task touching this data

`docs/benchmarks/failures/**` already redacts the 3 held-out golden-suite cases as
`held-out-case-<n>` labels (T415's own discipline, carried from earlier tasks). Your new module
and test **only read already-redacted, already-committed files** — you are not touching
`tests/golden/held-out/` or any real held-out case identity directly, so no new leakage risk
should be introduced by this task's own scope. Verify this yourself anyway before finishing: grep
any new file you add for the real held-out case identities (you do not need to know what they are
to do this — `tests/functional/test_golden_held_out_isolation.py`'s own guard already knows the
real six and will fail if any appear anywhere outside `tests/golden/`), and re-run that guard test
after adding your files to confirm it still passes.

## Inputs

- `docs/artifacts/failure-taxonomy-v1.md` (T415, full document — the scheme definition, all three
  axes' enumerated values, and the full case-by-case table in its §4).
- `docs/benchmarks/failures/README.md` (the index — both the golden-suite table and the
  Terminal-Bench table) and every `.md` file it indexes (15 files total).
- `implementation/runtime/golden_harness/{scoring,policy,schema}.py` (T458, for this repo's
  existing style/conventions in this exact area of the codebase — not a functional dependency of
  this task, just a style precedent to match).
- `tests/functional/test_golden_harness_policy.py` / `test_golden_harness_scoring.py` (style
  precedent for how modules in this area are tested).

## Constraints

- Token budget: keep this task well under 60k tokens — it is a `medium`-scoped wiring task over
  already-existing, already-read-and-summarized data, not new research.
- File ownership: this task may only create/modify files under `implementation/runtime/**` and
  `tests/functional/**` (its own new module + its own new test file), plus its own
  `docs/tasks/task-T501.md` status field. Do not modify `docs/benchmarks/failures/**` or
  `docs/artifacts/failure-taxonomy-v1.md` themselves — this task reads that data, it does not
  re-author it.
- Protected paths — do not touch, no exceptions: `tests/golden/**`, `scripts/scorecard.py`,
  `.mcp.json`, `docs/benchmarks/tb-subset.*`. Do not touch or branch from the
  `feature/T475-codex-platform-integration` branch — it is unrelated, in-flight work.
- Do not build any part of a diff-proposal generator, a weakness-clustering algorithm, or
  anything resembling `@meta-improver` — that is a separate, larger, not-yet-dispatched future
  task (`plan-055`'s `T462-equiv`). This task ends at "the taxonomy is a queryable library import."
- Do not build any mechanism for new failures to flow into the taxonomy over time — see the
  disclosed scoping decision above. If you find, after reading the real taxonomy artifact and its
  data yourself, that this scoping decision is wrong (e.g. the "first increment" is trivially
  small and a bit more is clearly still within a `medium` budget), you may say so in your
  completion report as a disclosed recommendation — but do not silently expand scope without
  flagging it first.
- No self-merge: work only in this task's own dedicated worktree/branch
  (`agent/backend-developer/T501`, already created off `develop`). Commit, push, open a merge
  request, and stop. Do not merge it.

## Expected outputs

1. A new Python module under `implementation/runtime/**` exposing a real query API over the 15
   currently-classified failure records.
2. A new test file under `tests/functional/**` proving the module works against the real on-disk
   data.
3. A short completion report (in your final message back to the orchestrator, not necessarily a
   new file) stating: the exact module/test paths chosen, the parsing approach chosen and why, and
   explicit confirmation the held-out isolation guard still passes.

## Acceptance criteria

- [ ] The new module can answer, programmatically, at least: "give me all classified failure
      records" (all 15), "give me all records with a given `cause`/`behavior`/`mechanism` value",
      and "give me the full record for a given case/file id" — each backed by a real committed
      test against the real on-disk data.
- [ ] The test's assertions are checked against real, specific values from
      `docs/benchmarks/failures/README.md`'s own index tables (e.g. asserting the known 9+6=15
      count, or a specific known case's exact axis values) — not a tautological "returns something
      non-empty" check.
- [ ] `tests/functional/test_golden_held_out_isolation.py` passes after this task's files are
      added (re-run fresh, not assumed).
- [ ] The module's docstring (or an equivalent short note) states the "future increment" scope
      boundary from this brief's own text explicitly, as a deliberate decision.
- [ ] No file outside `implementation/runtime/**`, `tests/functional/**`, and this task's own
      `docs/tasks/task-T501.md` status field is modified. Zero hits on any protected path.
- [ ] `python3 tests/run.py` passes with no new failures relative to the pre-task baseline on
      `develop`.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). If anything about the taxonomy data itself looks
inconsistent with `failure-taxonomy-v1.md`'s own description once you read it directly (e.g. a
case file whose axis values don't match the README index table), report it as a `dependency`
blocker rather than silently reconciling it one way or the other.
