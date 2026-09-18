# T510 — Implement promotion hardening: per-case minimum-evidence gate + provenance-homogeneity check (Options A + C)

**Status:** pending
**Owner:** backend-developer
**Priority:** P1
**Depends on:** T509 (done — design artifact this brief implements)
**Based on:** `docs/artifacts/promotion-improvement-hardening-design-v1.md` (T509's design pass — read in full before writing any code), `docs/artifacts/t507-closed-loop-cycle-v1.md` (the real incident this closes), `implementation/runtime/golden_harness/promotion.py`, `implementation/runtime/golden_harness/policy.py`, `implementation/runtime/golden_harness/schema.py`.

## Objective

Implement Options A and C from `T509`'s design, per the user's explicit instruction ("build A + C
first"). This closes the real gap `T507` demonstrated: `evaluate_promotion()` returned
`promote=True` on a proposal that was almost certainly not a genuine improvement, for two
independent, now-diagnosed reasons — thin, cross-case-pooled evidence (no case ever reached real
replication) and a provenance mismatch (reused historical control data compared against freshly
dispatched treatment data, a confound unrelated to the proposal's content).

**Read `docs/artifacts/promotion-improvement-hardening-design-v1.md` in full before writing any
code.** Its §5 acceptance-criteria sketch (items 1-9) is this brief's direct source — this task
brief translates that sketch into a concrete implementation scope, but the design document itself
has the full reasoning, trade-off analysis, and the two load-bearing refinements it found during
its own independent verification (most importantly: **the minimum-evidence gate must be per-`case_id`,
not a raw pooled trial count** — §1.2 shows a naive pooled-count check would not have caught `T507`'s
actual failure, since its 3 pooled trials came from 3 different cases at k=1 each).

## What to build

### A. Per-case minimum-evidence gate

1. A new function (suggested name `check_minimum_evidence`, in `policy.py` or `promotion.py` — your
   call, but prefer co-locating with `check_no_critical_regression` if placing it in `promotion.py`,
   since it reuses that function's own `_group_by_case` pattern) that groups `control_trials` +
   `treatment_trials` by `case_id` and reports, per case, whether **both** arms reached
   `policy.MIN_ESCALATED_K`. Return a `NamedTuple` (not a bare bool) — e.g.
   `EvidenceCheckResult(sufficient: bool, insufficient_evidence_case_ids: tuple[str, ...])` —
   following this codebase's existing convention (`RegressionCheckResult`, `PromotionResult`) of
   always naming *which* case(s) triggered a result, never just a boolean.
2. Wire this into `evaluate_promotion()` as a precondition evaluated alongside the existing three
   conjuncts (not nested inside `floor_met`/`check_no_critical_regression`, which stay unchanged in
   their own internal logic) — if any case has insufficient evidence, `promote` is `False`
   regardless of what `floor_met`/`check_no_critical_regression`/the hash check would otherwise
   return, and the `reason` string names every insufficient-evidence case.
3. `PromotionResult` gains new fields reporting this conjunct's result, following the existing
   `confirmed_regression_case_ids`/`mismatched_escalation_case_ids` naming convention (e.g.
   `minimum_evidence_met: bool`, `insufficient_evidence_case_ids: tuple[str, ...]`).

### C. Provenance-homogeneity pre-check

4. `schema.py`: add a `provenance` field to `TrialRecord` (suggested type
   `Literal["fresh", "reused", "unknown"]` or a plain `str` with those three conventional values —
   your call on the exact type, but the three states must exist). **Default to `"unknown"` when
   absent** on `from_dict()`/deserialization, so every already-persisted historical `TrialRecord`
   (e.g. anything cited from `baseline-v6.17.0-retrieval.md`) still deserializes without error and
   without being silently mis-tagged as `"fresh"` or `"reused"`.
5. A new shared pre-check (suggested name `check_provenance_homogeneity`, in `promotion.py`),
   grouped by `case_id`: a case is "provenance-mismatched" if its control-arm and treatment-arm
   trials do not share a uniform, known (`"fresh"` or `"reused"`, not `"unknown"`) provenance value.
   **Fail closed**: `"unknown"` provenance on either arm counts as mismatched, not compatible.
   Include a caller-supplied override parameter (suggested name
   `known_compatible_provenance_case_ids: frozenset[str] = frozenset()`), mirroring
   `check_no_critical_regression`'s existing `known_arm_agnostic_case_ids` parameter exactly in
   spirit — an explicit, human-attested exception, never inferred.
6. **Implement this once, consumed by both conjuncts, not duplicated.** Per the design's own §3
   recommendation: `evaluate_promotion()` calls `check_provenance_homogeneity()` once and its result
   gates the overall `promote` decision directly (a provenance-mismatched case blocks promotion the
   same way an insufficient-evidence case does) — do not write two separate implementations of the
   same grouping/comparison logic for the two conjuncts.
7. `PromotionResult` gains `provenance_homogeneous: bool` and `provenance_mismatched_case_ids:
   tuple[str, ...]`.

### Tests (per the design's §5 items 3, 4, 8, 9 — build all four)

8. A unit test reconstructing `T507`'s real numbers exactly (3 cases, k=1 per arm each: control
   `[True, False, True]` / treatment `[True, True, True]` across
   `code-review-conditional-pass-conditions-gap`, `prepare-release-conditional-pass-conditions-gap`,
   and a third case — read `t507-closed-loop-cycle-v1.md` §3.3 for the exact real values, do not
   invent synthetic numbers) asserting `evaluate_promotion()` now returns `promote=False` with a
   reason naming the insufficient-evidence cases. This is a regression test pinned to the real,
   disclosed incident.
9. A unit test proving the gate is genuinely **per-case**, not a pooled count: construct a synthetic
   case set with exactly 3 pooled trials per arm (satisfying a naive `len(trials) >=
   MIN_ESCALATED_K` check) spread across 3 different cases at k=1 each, and assert the new check
   still reports `sufficient=False` — directly encoding the design's §1.2 finding so a future
   refactor cannot silently regress to the weaker, pooled form.
10. A unit test reconstructing `T507`'s real provenance pattern (2 of the 3 cases: reused control /
    fresh treatment; 1 of 3: fresh/fresh — read `t507-closed-loop-cycle-v1.md` §3.3/§2 step 3 for
    which cases had reused vs. fresh control data) and asserting `check_provenance_homogeneity`
    flags exactly the 2 mismatched cases with no override supplied.
11. An end-to-end test combining both new preconditions against `T507`'s full real dataset
    (transcribed as literal `TrialRecord` fixtures, not paraphrased), confirming
    `evaluate_promotion()` now returns `promote=False` with both the insufficient-evidence and
    provenance-mismatch reasons present in `PromotionResult.reason`.

Existing test files to extend (confirmed present, do not create new files for these):
`tests/functional/test_golden_harness_promotion.py`, `tests/functional/test_golden_harness_policy.py`
(only if you add anything to `policy.py` itself — prefer keeping new logic in `promotion.py` per the
design's own placement rationale for `check_no_critical_regression`, unless there's a strong reason
to put a piece in `policy.py`).

## Explicitly deferred, do not build

- Option B (the symmetric `CONFIRMED_POSITIVE_EFFECT` classification) — the user's instruction was
  "build A + C first," and the design itself recommends B as a separate, later increment.
- Any change to `MIN_ESCALATED_K`'s value, `should_escalate()`'s trigger logic, or any "keep
  dispatching until k>=3" automatic behavior — all explicitly out of scope per the design's §6.
- Updating `t507-closed-loop-cycle-v1.md` itself to record this closure (design's §5 item 10) — a
  documentation/ledger follow-up the top-level session handles at task closure, not part of your
  own diff.

## Constraints

- Real code changes to `implementation/runtime/golden_harness/promotion.py` and
  `implementation/runtime/golden_harness/schema.py` (and `policy.py` only if genuinely needed) are
  in scope and expected — unlike every other Phase 6 task, this one does modify real, already-shipped
  harness code, not just add new modules. Read the existing modules in full before changing them;
  preserve every existing function's current behavior and signature for callers not touching the new
  fields (backward compatibility for `TrialRecord.from_dict()` on records without `provenance` is a
  hard requirement, not a nice-to-have).
- Do not touch `tests/golden/**` or `scripts/scorecard.py` — not relevant to this task, but stated
  per this repo's standing protected-path discipline.
- Do not implement Option B or any deferred item above.
- Standard worktree/branch/MR workflow (`agent/backend-developer/T510`, branched from `develop`).
  No self-merge — hand back to the top-level session for independent review and merge, same as
  every other task this project.
- Run the full verification bar before opening your MR: `python3 tests/run.py`,
  `python3 docs/tasks/validate-tasks.py`, `python3 implementation/scripts/check-maturity.py --verbose`,
  `node implementation/scripts/sync.mjs --root implementation --check`.

## Acceptance criteria

- [ ] `check_minimum_evidence` (or equivalently named) function exists, groups by `case_id`, returns
      a `NamedTuple` naming insufficient-evidence cases, not a bare bool
- [ ] `evaluate_promotion()` returns `promote=False` when any case has insufficient evidence,
      regardless of `floor_met`/regression/hash results, with the reason naming affected cases
- [ ] `TrialRecord.provenance` field added, defaults to `"unknown"` on deserialization of any record
      lacking it, existing persisted-record shapes still deserialize without error
- [ ] `check_provenance_homogeneity` (or equivalently named) function exists, fail-closed on
      mismatched or `"unknown"` provenance, supports a caller-supplied override frozenset mirroring
      `known_arm_agnostic_case_ids`'s exact semantics
- [ ] Implemented once, consumed by `evaluate_promotion()`'s overall decision — not duplicated
      between the two conjuncts
- [ ] `PromotionResult` carries the four new fields (evidence-met/case-ids,
      provenance-homogeneous/case-ids)
- [ ] All four new tests (items 8-11 above) pass, including the real-T507-numbers regression test
      and the per-case-not-pooled proof test
- [ ] Every existing test in `test_golden_harness_promotion.py`/`test_golden_harness_policy.py`
      still passes unmodified (or, if a pre-existing test's fixture data genuinely needs updating
      for the new required field, disclose exactly which and why)
- [ ] Full verification bar green

## Blocker protocol

Standard: `technical | dependency | unclear_requirements | external`, severities
`critical | major | minor`, max 2 retries before escalation.
