# Promotion-Rule Glue Code — v1

**Based on:** `docs/tasks/task-T504.md` (`plan-035-roadmap-v7-ground-up.md`'s nominal `T463`,
`plan-055` §4's `T463-equiv` row), `docs/tasks/task-T456.md` and `docs/tasks/task-T499.md`'s
"Pre-registered ship-gate threshold" section (the two-part mapping this document's conjuncts 1–2
reuse verbatim), `implementation/runtime/golden_harness/policy.py` (T458, the real, already-tested
primitives this glue code calls directly rather than reimplementing),
`implementation/runtime/golden_harness/scratch.py` (T458, the scratch-isolation convention
`apply_proposal_to_scratch` mirrors), `implementation/runtime/meta_improver.py` (T503, the real
`DiffProposal` shape this task validates), `docs/artifacts/evaluator-hash-check-v1.md` (T504
Piece 1, this document's third conjunct), `docs/artifacts/phase6-kill-switch-v1.md` (T502) and
`docs/artifacts/meta-improver-v1.md` (T503, style precedent for this document).

**Refs:** T504. Builds Piece 2 of Phase 6's validation/promotion-rule task.

## 1. What this document declares

This repository now has a real, tested promotion-rule module:

- `implementation/runtime/golden_harness/promotion.py` — the importable library:
  `check_no_critical_regression`, `evaluate_promotion`, `apply_proposal_to_scratch`, and the
  `RegressionCheckResult` / `PromotionResult` result types.
- `tests/functional/test_golden_harness_promotion.py` — the committed test suite proving every
  property documented below.

`plan-035`'s literal promotion rule is: **"improvement > regression AND no critical regression AND
evaluator hash unchanged."** This module combines three already-real pieces into one promote/reject
decision — it does not reimplement any of their logic:

1. `policy.floor_met()` (T458) — conjunct 1.
2. `policy.classify_k_plus_outcome()` (T458), wrapped by this module's own
   `check_no_critical_regression` — conjunct 2.
3. `evaluator_hash.check_evaluator_hash()` (T504 Piece 1) — conjunct 3.

## 2. The three-conjunct mapping — reproduced as this task's own documented decision

Reused **verbatim** from `task-T456.md`'s pre-registered ship-gate threshold, itself reused
verbatim by `task-T499.md`'s "Pre-registered ship-gate threshold" section — this task does not
invent a new, stricter, or looser variant for an analogous binary gate over the same `policy`
primitives.

### Conjunct 1 — "improvement > regression"

Maps to **`policy.floor_met(control_trials, treatment_trials)` being `True`**: the treatment arm's
aggregate pass rate (across all supplied trials, combined) is not below the control arm's. This is
the same criterion `task-T456.md`/`task-T499.md` already established as this repo's own
operational definition of "not worse, and any parity-or-better result ships," applied here without
modification.

### Conjunct 2 — "no critical regression"

Maps to: **no case among the compared trial set is classified `policy.CONFIRMED_PERSISTENT_EFFECT`
via `policy.classify_k_plus_outcome()` in a way that constitutes a real regression specific to the
treatment arm** (as opposed to an arm-agnostic checker-brittleness bug affecting both arms
equally) — the same distinction `task-T499.md`'s criterion 2 drew explicitly.

`classify_k_plus_outcome()` requires `k >= policy.MIN_ESCALATED_K` (3) trials per arm. This gives
`check_no_critical_regression` three real, distinct cases per `case_id` in the compared set:

1. **Both arms reached `MIN_ESCALATED_K` (a genuinely escalated case).** Call
   `policy.classify_k_plus_outcome()` on that case's combined trials directly. If the result is
   `CONFIRMED_PERSISTENT_EFFECT`, it is a *candidate* critical regression — see the judgment-call
   resolution immediately below for how it is finally decided.
2. **Exactly one arm reached `MIN_ESCALATED_K` (a mismatched escalation).** See §3 below — this is
   a distinct, explicitly handled case, not folded into either of the other two.
3. **Neither arm reached `MIN_ESCALATED_K`.** The task brief states this explicitly: *"for a
   comparison that never escalates past k=1, this conjunct is vacuously satisfied (there is no
   k>=3 case to classify as a critical regression)."* `check_no_critical_regression` implements
   this literally — such a case contributes nothing to either `confirmed_regression_case_ids` or
   `mismatched_escalation_case_ids`.

**The "arm-agnostic checker-brittleness bug" judgment call — resolved here, disclosed explicitly,
not silently picked.** `task-T499.md`'s own criterion 2 text states this distinction was applied by
*"Judgment applied consistent with how T493/T456 characterized this distinction, disclosed
explicitly per-case if it applies to any case in this run"* — i.e., in every prior real use of this
gate, a **human analyst** made this specific call per case, not a mechanical formula.
`classify_k_plus_outcome()` itself provides no field or return value that distinguishes "this
persistent effect is specific to the treatment arm" from "this persistent effect affects both arms
roughly equally" — that distinction is not mechanically derivable from a `TrialRecord` set alone
without a threshold this task has no principled, pre-registered basis to invent unilaterally for a
safety-relevant gate.

**Decision:** `check_no_critical_regression` accepts an explicit, caller-supplied
`known_arm_agnostic_case_ids: frozenset[str]` parameter. A case classified
`CONFIRMED_PERSISTENT_EFFECT` counts as a real, blocking critical regression **unless its
`case_id` appears in this caller-supplied set** — i.e., unless a human reviewer has already made
and disclosed exactly the same per-case judgment call `task-T499.md`'s own methodology required,
supplied to this function as an explicit, auditable input rather than inferred by the function
itself. This:

- **Fails closed by default.** With no override supplied (the default, empty `frozenset()`), every
  `CONFIRMED_PERSISTENT_EFFECT` case blocks promotion — the safe default for a safety-relevant gate,
  never silently promoting past an unreviewed persistent-effect finding.
- **Preserves the existing human-judgment step exactly, rather than replacing or automating it.**
  This module does not attempt to computationally distinguish "treatment-specific" from
  "arm-agnostic" — it makes the already-existing judgment call an explicit, disclosed, auditable
  *input* to the function (visible in the function's own signature and in
  `RegressionCheckResult.classified_case_ids`, which still lists every classified case regardless
  of whether it was excused) rather than a silent internal inference a future reader could not
  audit.
- **Was reported, not silently resolved.** Per the task brief's own Blocker Protocol ("if the
  three-conjunct promotion-rule mapping... has a real edge case this brief didn't anticipate...
  report it as a real blocker rather than picking an interpretation and hoping it's right"), this
  exact ambiguity is disclosed as a `minor`/`unclear_requirements` item in this task's own
  completion report, alongside this fail-safe, documented resolution — not merely decided here and
  left for a future reader to discover unannounced.

### Conjunct 3 — "evaluator hash unchanged"

Maps to **Piece 1's check reporting no drift on either protected path** —
`evaluator_hash_check.any_drift` being `False`. `evaluate_promotion` accepts a caller-supplied
`evaluator_hash.DriftCheckResult` rather than calling `check_evaluator_hash()` internally, so a
caller can reuse one hash-check result across multiple promotion evaluations within the same
validation cycle without re-hashing the protected paths on every call.

All three conjuncts **AND** together. `evaluate_promotion` returns a `PromotionResult` — never a
bare boolean — reporting each conjunct's individual outcome plus a human-readable `reason` string
listing every failing conjunct (not just the first one found), since a human reviewer
(T464-equiv's eventual MR gate) needs to know *why* a proposal was rejected, and a proposal can
fail more than one conjunct at once.

## 3. Mismatched escalation — a real edge case, resolved fail-safe

A case where one arm reaches `MIN_ESCALATED_K` (3) trials and the other does not (e.g. control has
k=3, treatment has only k=1) is a real, anomalous input shape: `policy.classify_k_plus_outcome()`
would raise `ValueError` if called on it directly (`_require_min_k` requires both arms to meet the
threshold). Per normal operation, `policy.should_escalate()`'s own design escalates both arms
together as a pair — a genuinely mismatched escalation should not occur from well-formed trial
data, but `check_no_critical_regression` does not assume its caller's input is always well-formed.

**Decision: mismatched escalation is treated as a fail-safe blocking condition, not as vacuously
satisfied.** `check_no_critical_regression` never calls `classify_k_plus_outcome()` on a
mismatched-escalation case (avoiding the `ValueError`), and reports the case's `case_id` in a
dedicated `mismatched_escalation_case_ids` tuple, separate from `confirmed_regression_case_ids`.
`RegressionCheckResult.no_critical_regression` is `True` only when **both** tuples are empty. This
is the conservative choice for a safety-relevant gate: inconsistent per-arm trial counts for an
otherwise-escalated case is itself an anomaly worth a human's attention before a promotion decision
is trusted, not a condition that should silently pass through as "no evidence of regression."
`tests/functional/test_golden_harness_promotion.py`'s
`test_mismatched_escalation_is_fail_safe_not_vacuous` and
`test_mismatched_escalation_does_not_raise` prove both halves of this decision directly.

## 4. Function signature — decoupled from how trial data was produced

`evaluate_promotion(control_trials: list[TrialRecord], treatment_trials: list[TrialRecord],
evaluator_hash_check: evaluator_hash.DriftCheckResult, *, known_arm_agnostic_case_ids:
frozenset[str] = frozenset()) -> PromotionResult`.

`control_trials`/`treatment_trials` are plain `TrialRecord` lists (T458's real schema) — this
function embeds **no live-dispatch call of any kind**. This deliberately decouples "how do you
decide promote/reject given trial records" from "how do you obtain those trial records" — the
latter may be a live dispatch (the orchestrator's own real end-to-end validation cycle, per
`task-T504.md`'s "Split ownership" section), a future automated loop-runner, or a persisted
`trial_store.py` file; `evaluate_promotion` does not care which.
`tests/functional/test_golden_harness_promotion.py`'s
`test_control_treatment_inputs_are_plain_trial_record_lists` proves this directly: control/
treatment are constructed as plain lists with no dispatch mechanism anywhere in the test, and
`evaluate_promotion` accepts them unmodified.

## 5. Apply-to-scratch helper: "apply proposal to scratch copy, never a real file"

`apply_proposal_to_scratch(proposal: meta_improver.DiffProposal, scratch_root: Path) -> Path`
writes `proposal.proposed_content` to `scratch_root / proposal.target_path`, creating any needed
parent directories, and returns the written path. This is what makes a real live validation cycle
possible (applying a `DiffProposal` so its effect can actually be measured against the golden
suite) without ever touching a real tracked file.

**Mechanism, mirrored directly from two existing conventions:**

- `golden_harness/scratch.py`'s own scratch-isolation convention
  (`write_candidate_file`'s `case_dir / "fixture" / relative_path` shape) — applied here as
  `scratch_root / target_path`, the same "join a caller-supplied isolated root with a relative
  path, write, return the written path" shape.
- `meta_improver.py`'s own "never writes to a real repo file" discipline (see
  `docs/artifacts/meta-improver-v1.md` §6's adversarial proof for that module) — extended here to
  the *application* side: `meta_improver.py` proves it never writes anywhere; this helper proves it
  only ever writes under a caller-supplied scratch root, never under this repository's own tracked
  tree.

**Defensive guard, not merely an implicit convention.** `apply_proposal_to_scratch` raises
`ValueError` if `scratch_root` resolves to this repository's own root or any path under it — on top
of the fact that the function never derives a write target from `REPO_ROOT` at all (it only ever
joins `scratch_root` with `proposal.target_path`), this guard makes an accidental
`apply_proposal_to_scratch(proposal, REPO_ROOT)` call fail loudly rather than silently writing into
the real tracked tree.
`tests/functional/test_golden_harness_promotion.py`'s
`test_real_tracked_target_file_is_byte_identical_before_and_after` is the real, behavioral proof:
it targets a real, existing file under `implementation/knowledge/instructions/`, snapshots its
bytes, applies a proposal for that exact path to an isolated scratch root, and confirms the real
file's bytes are unchanged afterward — mirroring `test_meta_improver.py`'s own before/after
snapshot pattern exactly. `test_rejects_repo_root_itself_as_scratch_root` and
`test_rejects_a_path_under_repo_root_as_scratch_root` prove the defensive guard fires.

## 6. Module placement: co-located in `promotion.py`, not a separate module

`apply_proposal_to_scratch` is co-located directly in `promotion.py` rather than split into a
separate sibling module. Rationale: it is a small, single function (roughly the same size as
`scratch.py`'s own `write_candidate_file`), it is used by the same caller (the orchestrator's live
validation cycle) in the same call sequence as `evaluate_promotion` (apply a proposal to scratch,
measure it, build `TrialRecord`s, then call `evaluate_promotion`), and it has no dependency any
other part of `promotion.py` lacks (`meta_improver.DiffProposal` is already an import this module
needs for its own type signature). Splitting it into a separate file would add an import
indirection with no corresponding benefit — mirroring `meta_improver.py`'s own §8 module-placement
reasoning ("one schema, one classifier, one clustering function, one generation function is small
enough to stay in one file without losing readability"), applied here to "one regression check, one
combining function, one scratch-apply helper."

## 7. What this does *not* do (scope boundary)

- **No live dispatch of any kind.** Neither `evaluate_promotion` nor `apply_proposal_to_scratch`
  invokes an `Agent` tool call, a nested session, or a `claude` CLI subprocess. Obtaining real
  `TrialRecord`s from a live validation cycle is the orchestrator's job, per `task-T504.md`'s
  "Split ownership" section — this module only consumes the resulting records.
- **No T464-equiv (MR gate), T465-equiv (lineage document), or loop-runner.** This module produces
  a `PromotionResult`; nothing in this repository yet consumes that result to actually gate a merge
  request or run an automated improvement loop. Both remain separate, not-yet-dispatched future
  tasks.
- **No automated resolution of the "arm-agnostic vs. treatment-specific" judgment call.** As
  documented in §2, this remains an explicit, caller-supplied override — this module does not
  attempt to infer it from trial data alone.
- **No import from, reference to, or reuse of `implementation/sia/`,
  `implementation/adapters/sia-target/`, or `implementation/scripts/sia-executor.py`.**

## 8. Verification

- `tests/functional/test_golden_harness_promotion.py` — 18 tests: all three conjuncts exercised
  independently at the `evaluate_promotion` level (each failing alone rejects; all three passing
  promotes; multiple simultaneous failures are all reported in `reason`) —
  `TestEvaluatePromotionThreeConjuncts`; conjunct 2's own per-case mapping exercised directly,
  including the never-escalated vacuous case, the `CONFIRMED_COIN_FLIP` non-regression case, the
  default-fails-closed `CONFIRMED_PERSISTENT_EFFECT` case, the explicit human-override case, the
  mismatched-escalation fail-safe case, and independent multi-case evaluation —
  `TestCheckNoCriticalRegression`; the real, behavioral never-writes-the-real-file proof for
  `apply_proposal_to_scratch`, plus its defensive-guard and git-worktree-isolation tests —
  `TestApplyProposalToScratch`.
- `tests/functional/test_golden_held_out_isolation.py` re-run fresh after adding this task's files:
  8/8 pass — no held-out isolation violation introduced.
- Run directly: `python3 -m unittest tests.functional.test_golden_harness_promotion -v`.
- Included automatically in `python3 tests/run.py` (discovered under `tests/functional/`).
