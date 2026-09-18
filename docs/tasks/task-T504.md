# Task T504 — Validation: proposal vs. failing case + open suite + held-out suite + baseline;
promotion rule (`plan-035` nominal `T463`)

**Owner:** backend-developer (build phase — evaluator-hash check + promotion-rule glue code);
**orchestrator** (live end-to-end validation phase — see "Split ownership" below)
**Status:** in_progress
**Priority:** P0
**Depends on:** T458 (done — `implementation/runtime/golden_harness/{scoring,policy,schema,
trial_store}.py`, the real primitives this task's promotion-rule glue code reuses directly); T503
(done — `implementation/runtime/meta_improver.py`, the real `DiffProposal` objects this task
validates)
**Created:** 2026-09-18
**Based on:** `docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's
`T463-equiv` row ("`backend-developer` builds the **new** evaluator-hash tamper-evidence check...
and the promotion-rule glue code around the **already-real** `golden_harness.scoring`/
`golden_harness.policy` primitives; **orchestrator executes** the actual live comparison runs...
Real scope reduction from `plan-035`'s original 'large' estimate... only the evaluator-hash check
and the promotion-rule wiring are net-new") and §5's artifact-flow diagram; `docs/artifacts/
phase6-sia-readiness-audit-v1.md` §5 item 3 (the scope-reduction finding this brief is built
directly on) and §6 (the tool-grant split-ownership reasoning); `docs/artifacts/
protected-paths-v1.md` §2 item 2, quoted verbatim below — this task implements *exactly* that
control, not a reinvented variant, per `plan-055` §6's own risk-table warning against that failure
mode; `implementation/runtime/golden_harness/{scoring,policy,schema,trial_store}.py` (T458, real,
merged, tested) and `implementation/runtime/meta_improver.py` (T503, real, merged, tested) — this
task's real, concrete inputs; `docs/plans/plan-058-t504-dispatch-plan-coverage.md` (this task's
own minimal plan-coverage backing document).

**`protected-paths-v1.md` §2 item 2, quoted verbatim (the control this task must implement
exactly):** *"T463's evaluator-hash check (not yet built, a later task, out of scope here) — will
detect if the evaluator's on-disk content silently drifts from a known-good hash, a
tamper-evidence control independent of whether the drift was intentional or accidental."*

**Do not treat `plan-035` §2.4 Phase 6's own introductory prose (`implementation/sia/`,
`sia-executor.py`, reward shaping/harness capture/reward attachment "already exist") as a scoping
instruction for this task**, for the same reason `task-T503.md` disclosed: that prose describes a
different, invalidated RL/fine-tuning subsystem this task has no dependency on. This task's real
dependency is `golden_harness/*` (T458) and `meta_improver.py` (T503) alone.

## Why this task exists

`plan-035`'s literal promotion rule is: **"improvement > regression AND no critical regression AND
evaluator hash unchanged."** Two of these three conjuncts can already be computed from real, tested,
existing code (`golden_harness.policy`) — this task's job is to (a) build the one genuinely missing
piece, the evaluator-hash tamper-evidence check, and (b) write the glue function that combines all
three conjuncts into one real promote/reject decision, reusing the existing `policy` functions
directly rather than reimplementing their logic.

## Piece 1 — the evaluator-hash check

Build a real, tested primitive under `implementation/runtime/golden_harness/evaluator_hash.py`
that:

1. **Computes a content hash over the two protected paths** declared in `docs/artifacts/
   protected-paths-v1.md` §1 (`tests/golden/**` and `scripts/scorecard.py`) — mirror the exact
   hashing pattern `tests/functional/test_meta_improver.py`'s `test_full_pipeline_leaves_repo_byte_
   identical` already uses (SHA-256, sorted `rglob`, feed each file's repo-relative POSIX path
   bytes then its content bytes into the hasher, deterministic order). Compute **two separate
   digests**, one per protected path, not one combined digest — this gives a future caller a
   precise answer to "which of the two paths drifted," not just "something drifted somewhere,"
   which matters for triage.
2. **Compares against a stored known-good reference** and reports drift/no-drift per path, plus an
   aggregate boolean. Never raises on drift — a drift finding is a real, valid, reportable result,
   not an error condition; only a structurally invalid known-good reference file (malformed JSON,
   missing required keys) should raise.
3. **Never writes the known-good reference itself as a side effect of checking.** The check
   function only reads; producing/updating the known-good reference is a separate, explicit,
   human-invoked action (see "known-good storage and update policy" below) — a check function that
   can silently accept its own drift by rewriting its own reference defeats the entire purpose of a
   tamper-evidence control.

### Known-good storage and update policy — decided here, not left ambiguous

**Storage: `docs/artifacts/evaluator-hash-known-good-v1.json`**, a new, small, versioned artifact
(mirroring how `phase6-kill-switch-v1.md` and `meta-improver-v1.md` each picked and justified their
own storage location). Structure (your call on exact key names, but must include at minimum):
the SHA-256 algorithm name, the two per-path digests, the git commit SHA the digests were computed
from, and a UTC timestamp. This is a machine-readable sidecar to a matching prose design doc (see
"Expected outputs" below), not the design doc itself.

**Update policy: manual only, never automatic, via `protected-paths-v1.md` §5's existing exception
path — do not invent a new mechanism.** That section already defines exactly the process a future,
legitimate change to `tests/golden/**` or `scripts/scorecard.py` must go through ("Never a silent
edit... Always a named, authorized task... Ordinary review still applies"). Updating the known-good
hash after such a change is part of that same exception-path task, not a separate automatic
recomputation this module performs on its own. Per this repo's Artifact Versioning convention
(`AGENTS.md`: "Revisions create new versions, never overwrite"), a future legitimate update
produces `evaluator-hash-known-good-v2.json`, it does not edit v1 in place — state this explicitly
in the design doc.

**Bootstrapping this task's own known-good value**: compute the real, current digests of the real,
current `tests/golden/**` and `scripts/scorecard.py` on-disk content at build time, and commit that
as `v1`'s value. This is the one, single, disclosed exception to "never automatic" — establishing
the first known-good baseline is inherently a one-time bootstrap action, not an ongoing automatic
recomputation; state this explicitly in the design doc so a future reader does not mistake it for
the check silently trusting its own current state going forward.

## Piece 2 — promotion-rule glue code

Build a real, tested function under `implementation/runtime/golden_harness/promotion.py` that
combines:

(a) An aggregate before/after golden-suite comparison result, computed by **calling
`golden_harness.policy`'s already-real functions directly — do not reimplement this logic**:
`pass_rate()`, `floor_met()`, `classify_k_plus_outcome()`.

(b) Piece 1's evaluator-hash check result.

into one promote/reject decision plus a human-readable reason, implementing `plan-035`'s literal
rule: **"improvement > regression AND no critical regression AND evaluator hash unchanged."**

### The promotion-rule mapping — decided here, not left ambiguous

This repo has already made this exact kind of decision twice, for an analogous purpose (a binary
ship/no-ship gate over the same `policy` primitives): `task-T456.md`'s pre-registered ship-gate
threshold, reused verbatim by `task-T499.md`'s "Pre-registered ship-gate threshold" section. Reuse
that same two-part mapping here, applied to the promotion rule's first two conjuncts:

1. **"improvement > regression" maps to `policy.floor_met(control_trials, treatment_trials)` being
   `True`** — the treatment arm's aggregate pass rate is not below the control arm's. This is the
   same criterion `task-T456.md`/`task-T499.md` already established as this repo's own operational
   definition of "not worse, and any parity-or-better result ships" for an aggregate before/after
   comparison; reuse it rather than inventing a stricter or looser variant.
2. **"no critical regression" maps to**: no case among the compared trial set is classified
   `policy.CONFIRMED_PERSISTENT_EFFECT` via `policy.classify_k_plus_outcome()` in a way that
   constitutes a real regression specific to the treatment arm (as opposed to an arm-agnostic
   checker-brittleness bug affecting both arms equally) — the same distinction `task-T499.md`'s
   criterion 2 drew explicitly. Since `classify_k_plus_outcome()` requires `k>=3` trials per arm
   (`policy.MIN_ESCALATED_K`), this conjunct only has a non-trivial answer for cases that were
   actually escalated (`policy.should_escalate()`); for a comparison that never escalates past
   k=1, this conjunct is vacuously satisfied (there is no k>=3 case to classify as a critical
   regression) — state this explicitly in your design doc rather than leaving it implicit.
3. **"evaluator hash unchanged" maps to Piece 1's check reporting no drift on either protected
   path.**

All three conjuncts AND together; the function returns a structured result (promote/reject boolean
plus which conjunct(s) failed, if any) — never a bare boolean with no explanation, since a human
reviewer (T464-equiv's eventual MR gate) needs to know *why* a proposal was rejected.

### Function signature — decoupled from how trial data was produced

The promotion function's control/treatment inputs must be plain `list[TrialRecord]` (T458's real
schema), **not** a live-dispatch call embedded inside the function itself. This deliberately
decouples "how do you decide promote/reject given trial records" from "how do you obtain those
trial records" — the latter may be a live dispatch (today, this task's own live validation cycle),
a future automated loop-runner, or a persisted `trial_store.py` file; the promotion function must
not care which. This is not a hedge — it is the concrete resolution of the open design question
below.

## The genuinely open design question — resolved here, with a documented finding

`plan-035`'s literal acceptance criterion ("every proposal runs against the failing case + open
suite + held-out suite + baseline") implies applying a `DiffProposal` and re-measuring golden-suite
results with it applied vs. without. Whether this task validates against **already-recorded
historical trial data** (no live dispatch needed) or requires **live re-measurement** was left open
by `plan-055` for this task's own brief to resolve after investigation. **Investigated and
resolved**: no historical trial data exists anywhere in this repo in `TrialRecord`/`trial_store.py`
JSONL form — a repo-wide search for `*.jsonl` trial-store output found nothing. The 28 historical
trials behind `task-T484.md` through `task-T494.md`/`T456`/`T499` exist only as prose inside those
task briefs' own "Execution log" sections; `trial_store.py`'s own module docstring explicitly
disclaims backfilling them as required, disclosed scope. **Therefore: there is no tractable
"replay historical data" path today — at least one real validation cycle requires genuine live
re-measurement.** This confirms, rather than merely anticipates, that this task is exactly the
split-ownership case `plan-055` pre-scoped it as.

**Consequence for scope**: this task's **build** phase (backend-developer) does not implement a
full "dispatch live agent sessions across the failing case + entire open suite + entire held-out
suite" pipeline — that is expensive, at-scale live-dispatch orchestration outside a pure-code
task's reach, and belongs to a future, larger, not-yet-scoped loop-runner task (downstream of
T464-equiv/T466-equiv both existing first). What this task's build phase **does** deliver, as a
concrete, tractable, pure-code piece: an **apply-to-scratch helper**,
`apply_proposal_to_scratch(proposal: DiffProposal, scratch_root: Path) -> Path`, that writes
`proposal.proposed_content` to an isolated scratch copy of `proposal.target_path` — a plain temp
directory, never a git worktree, never the real tracked file, mirroring both `golden_harness/
scratch.py`'s existing scratch-isolation convention and `meta_improver.py`'s own "never writes to
a real repo file" discipline exactly. This helper is what makes a live validation cycle possible
without ever touching a real tracked file; it does not itself dispatch anything live.

The **orchestrator** then performs one real, minimal (not full-suite) live validation cycle using
this helper plus the promotion function — see "Split ownership" below.

## Split ownership (applied pre-emptively, per `plan-055` §4 and its own risk table)

This repo has hit the same tool-grant gap at least 9 times before this task. `plan-055` §4 applies
the fix in advance here too:

- **`backend-developer`** (tool grant re-confirmed this dispatch: `[read, search, edit, execute,
  web, mcp__fetch]` — no `agent` tool) builds Pieces 1 and 2 above, both pure code requiring no
  live dispatch.
- **The orchestrator**, not `backend-developer` and not `evaluation-agent`, performs at least one
  real end-to-end validation cycle once the code exists. **Re-confirmed directly this dispatch**
  (not assumed): `evaluation-agent`'s tool grant is `[read, search, web]` — no `execute`, no
  `agent` tool — structurally unable to run the golden harness, score a scratch dir, or dispatch a
  live trial, the same recurring gap this repo has now documented at `T410/T415/T418/T420/T430/
  T440/T451/T456/T458/T499` and now T503. The orchestrator will: take one real `DiffProposal`
  (reusing `T503`'s own live-generated example — the `tech-lead.md`-targeting proposal from the
  `naming-convention-drift` cluster — or generate a fresh one if more convenient at review time),
  apply it via the scratch helper, dispatch one real control/treatment k=1 trial pair against one
  real, relevant golden case (mirroring `task-T499.md`'s own methodology exactly: the
  orchestrator's own in-process `Agent` tool, never a `claude` CLI subprocess), score both arms via
  `scoring.score_scratch_dir()`, build real `TrialRecord`s, and run them through the built
  promotion function — confirming it produces a real, sensible promote/reject decision under
  direct, independent exercise, not merely trusting the committed unit tests.

## Inputs

- `implementation/runtime/golden_harness/{scoring,policy,schema,trial_store}.py` (T458, full —
  read every docstring, not just signatures).
- `implementation/runtime/meta_improver.py` (T503, full) and `docs/artifacts/meta-improver-v1.md`
  — the real `DiffProposal` shape this task validates.
- `implementation/runtime/golden_harness/scratch.py` (T458, full) — the existing scratch-isolation
  convention Piece 2's apply-to-scratch helper must mirror.
- `docs/artifacts/protected-paths-v1.md` (full) — the authoritative source for the two protected
  paths and the exception-path process this task's known-good-update policy reuses.
- `docs/artifacts/phase6-kill-switch-v1.md` (T502) and `docs/artifacts/meta-improver-v1.md` (T503)
  — style precedent for this task's own two new design docs.
- `docs/tasks/task-T456.md` and `docs/tasks/task-T499.md` — the ship-gate criteria this task's
  promotion-rule mapping reuses verbatim (read `task-T499.md`'s "Pre-registered ship-gate
  threshold" section directly, not a summary of it).
- `tests/functional/test_meta_improver.py` — the exact hashing pattern Piece 1 mirrors
  (`test_full_pipeline_leaves_repo_byte_identical`).

## Constraints

- Token budget: recommended `medium` per `plan-055` §4's own re-estimate — this is a recommendation,
  not a hard ceiling; report genuine progress honestly if real scope exceeds it rather than forcing
  a shallow result to fit.
- File ownership: this task may only create/modify files under `implementation/runtime/
  golden_harness/**`, `tests/functional/**` (and/or `tests/unit/**` if that better fits a given
  test's nature — your call), `docs/artifacts/**` (its own new files only), plus its own
  `docs/tasks/task-T504.md` status field.
- Protected paths — **read-only dependency, never edit, no exceptions**: `tests/golden/**`,
  `scripts/scorecard.py` (this task reads and hashes them, it does not edit them — same
  read-only-dependency discipline `T501` applied to `docs/benchmarks/failures/**`). Also do not
  touch: `.mcp.json`, `docs/benchmarks/tb-subset.*`. Do not touch or branch from
  `feature/T475-codex-platform-integration` — unrelated, in-flight work.
- Do not build any part of T464-equiv (the MR gate), T465-equiv (the lineage document), or any
  full-scale live-dispatch loop-runner that runs every proposal against the entire open + held-out
  suite — all remain separate, not-yet-dispatched future tasks, per this brief's own "Consequence
  for scope" section above.
- Do not import, call, or reuse anything from `implementation/sia/`, `implementation/adapters/
  sia-target/`, or `implementation/scripts/sia-executor.py`.
- Do not perform any live dispatch yourself (no `Agent`/nested-session calls) — you have no `agent`
  tool grant, and the live validation cycle is explicitly the orchestrator's job per "Split
  ownership" above. Build the apply-to-scratch helper and the promotion function; stop there.
- Commit your work normally to your own dedicated worktree/branch (`agent/backend-developer/T504`,
  created off `develop`). Push it and open a merge request against `develop`, then stop — do not
  merge it yourself.
- **No self-merge, no exceptions for content type.** Work only in your own dedicated worktree/
  branch. Do not merge anything, including into your own branch from elsewhere, and do not merge
  the MR you open. The orchestrator merges after independent review — and per this dispatch's own
  standing instruction this round, even the orchestrator is leaving all merges for the top-level
  session's own independent review this time; you are not the blocker either way.
- If `docs/tasks/task-T504.md` does not yet exist in your freshly forked worktree (the dispatch
  docs branch may not be merged to `develop` yet at the moment your worktree forks — a real,
  disclosed, already-twice-recurring process gap per `task-T501.md`/`task-T502.md`'s own closure
  notes), do not stall or guess: this dispatch message's own prose is the working brief in full: if
  it isn't merged, `git show origin/docs/dispatch-T504:docs/tasks/task-T504.md` recovers it
  directly, or you can proceed on the inline text you were given, whichever is faster; confirm the
  two match before proceeding.

## Expected outputs

1. `implementation/runtime/golden_harness/evaluator_hash.py` — Piece 1.
2. `implementation/runtime/golden_harness/promotion.py` — Piece 2 (the combining function) plus the
   `apply_proposal_to_scratch` helper (co-locate it here, or in a separate small module under the
   same package — your call, document the choice).
3. `docs/artifacts/evaluator-hash-known-good-v1.json` — the bootstrapped known-good reference,
   computed from the real, current repo state.
4. `docs/artifacts/evaluator-hash-check-v1.md` — design doc for Piece 1 (mirroring
   `phase6-kill-switch-v1.md`'s structure): what it declares, storage location and why, update
   policy and why, what it does not do, verification.
5. `docs/artifacts/promotion-rule-v1.md` — design doc for Piece 2: the three-conjunct mapping onto
   real `policy` functions (reproduced from this brief as your own documented decision, not merely
   cited), the function signature's `TrialRecord`-list decoupling rationale, and the "apply proposal
   to scratch copy, never a real file" mechanism.
6. New test file(s) under `tests/functional/**`/`tests/unit/**` covering both pieces with real,
   specific (non-tautological) assertions — including at least: a real drift-detection test (mutate
   a scratch copy of a protected-path file's content, confirm the check reports drift; confirm no
   drift is reported against the real, current, unmodified repo state), a real promotion-rule test
   using constructed `TrialRecord`s exercising all three conjuncts independently (each one failing
   alone should reject; all three passing should promote), and a real test of the apply-to-scratch
   helper proving it never writes to the real tracked file (mirror `test_meta_improver.py`'s
   before/after snapshot pattern).
7. A short completion report (in your final message back to the orchestrator) stating: exact module/
   test/doc paths chosen, the bootstrapped known-good hash values (or where to find them), and
   explicit confirmation of each test category's real pass result.

## Acceptance criteria

- [ ] A real, tested evaluator-hash check exists, computing two separate SHA-256 digests (one per
      protected path) via the same hashing pattern `test_meta_improver.py` already establishes.
- [ ] The known-good reference is stored at `docs/artifacts/evaluator-hash-known-good-v1.json`,
      bootstrapped from the real current repo state, with an explicit, documented, manual-only
      update policy citing `protected-paths-v1.md` §5.
- [ ] A real, tested promotion function exists, combining `policy.floor_met()`,
      `policy.classify_k_plus_outcome()` (where applicable), and the evaluator-hash check's result
      into one promote/reject decision with an explanatory reason, per the three-conjunct mapping
      documented above.
- [ ] The promotion function's control/treatment inputs are plain `TrialRecord` lists — no live
      dispatch call embedded in the function itself.
- [ ] A real, tested `apply_proposal_to_scratch` helper exists, proven (by a real behavioral test)
      to never write to the real tracked target file.
- [ ] `docs/artifacts/evaluator-hash-check-v1.md` and `docs/artifacts/promotion-rule-v1.md` both
      exist and document every decision listed in this brief.
- [ ] No file outside this task's declared file-ownership boundary is modified. Zero edits to
      either protected path. Zero hits on `implementation/sia/`, `implementation/adapters/
      sia-target/`, `implementation/scripts/sia-executor.py`.
- [ ] `python3 tests/run.py` passes with no new failures relative to the pre-task baseline on
      `develop`.
- [ ] `tests/functional/test_golden_held_out_isolation.py` passes after this task's files are
      added (re-run fresh, not assumed).
- [ ] (Orchestrator-owned, not part of backend-developer's own completion) At least one real live
      validation cycle is independently performed and produces a real, sensible promote/reject
      decision, per "Split ownership" above.

## Blocker protocol

Report blockers with type (`technical` | `dependency` | `unclear_requirements` | `external`) and
severity (`critical` | `major` | `minor`). If the three-conjunct promotion-rule mapping documented
above turns out to have a real edge case this brief didn't anticipate (e.g. a `TrialRecord` set
that is escalated in one arm but not the other), report it as a real blocker rather than picking an
interpretation and hoping it's right — this is a safety-relevant gate, not a cosmetic feature. If
the evaluator-hash known-good storage/update mechanism raises a real security question you are not
confident about, report it rather than resolving it unilaterally.
