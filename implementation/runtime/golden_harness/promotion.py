"""Promotion-rule glue code (T504, `plan-035` nominal `T463`).

`plan-035`'s literal promotion rule: **"improvement > regression AND no
critical regression AND evaluator hash unchanged."** This module combines
three already-real pieces into one promote/reject decision -- it does not
reimplement any of their logic:

(a) `golden_harness.policy.floor_met()` -- the aggregate before/after
    golden-suite comparison.
(b) `golden_harness.policy.classify_k_plus_outcome()` -- the critical
    regression check, applied only to cases that were actually escalated.
(c) `golden_harness.evaluator_hash.check_evaluator_hash()` -- Piece 1's
    tamper-evidence check.

See `docs/artifacts/promotion-rule-v1.md` for the full design write-up,
including the three-conjunct mapping, the documented judgment-call
resolution for "arm-agnostic checker-brittleness bug" vs. "treatment-specific
regression," and the mismatched-escalation fail-safe behavior; this
docstring states the load-bearing properties only.

**T510 hardening (T509 design, Options A + C):** `T507` ran this loop for
real and got `promote=True` on a proposal that was almost certainly not a
genuine improvement, for two independent, disclosed reasons (see
`docs/artifacts/t507-closed-loop-cycle-v1.md` and
`docs/artifacts/promotion-improvement-hardening-design-v1.md`). Two new,
promotion-level preconditions close both gaps -- evaluated once, ahead of
(not nested inside) the original three conjuncts, which keep their own
internal logic unchanged:

(d) `check_minimum_evidence()` -- every `case_id` present in the compared
    trial set must reach `policy.MIN_ESCALATED_K` in *both* arms, evaluated
    per-case (never as a raw pooled trial count -- see that function's own
    docstring for why a pooled count would not have caught `T507`).
(e) `check_provenance_homogeneity()` -- every `case_id`'s trials must share a
    single, known (`"fresh"` or `"reused"`) provenance across both arms;
    `"unknown"` or a mixed provenance fails closed. Implemented once here,
    consumed by `evaluate_promotion()`'s overall decision (not duplicated
    per-conjunct), per the design's §3 recommendation that this check should
    protect both the improvement and the regression conjuncts.

**T511 hardening (T509 design, Option B):** the third and final option T509
scoped after `T507`. `T510` closed the evidence-thinness and provenance-
confound gaps; this closes the third, independent gap: conjunct 1
("improvement > regression") was purely `policy.floor_met()`, a bare
"treatment pass rate not below control's" statistic with no qualitative
corroboration at all.

(f) `check_confirmed_positive_effect()` -- every `case_id` present must
    reach `policy.CONFIRMED_POSITIVE_EFFECT` under
    `policy.classify_k_plus_improvement_outcome()` (see that function's own
    docstring for the full four-outcome mapping). Evaluated per-case
    (mirroring `check_no_critical_regression`'s own per-case grouping and
    its "only classify a case that actually reached k>=3 in both arms"
    discipline), reported as a required, conservative sixth conjunct
    (T511's own disclosed judgment call, not the design's -- see
    `docs/tasks/task-T511.md` design decision 5), not merely an advisory
    field: `evaluate_promotion()` requires every compared case to reach
    `CONFIRMED_POSITIVE_EFFECT` before `promote` can be `True`.

Also builds `apply_proposal_to_scratch` -- the apply-to-scratch helper that
writes a `meta_improver.DiffProposal`'s `proposed_content` to an isolated
scratch copy, never a git worktree, never the real tracked file, mirroring
`golden_harness/scratch.py`'s existing scratch-isolation convention and
`meta_improver.py`'s own "never writes to a real repo file" discipline.
Co-located here rather than in a separate sibling module -- see
`docs/artifacts/promotion-rule-v1.md` SS6 for the placement rationale.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import NamedTuple

from implementation.runtime import meta_improver
from implementation.runtime.golden_harness import evaluator_hash, policy
from implementation.runtime.golden_harness.schema import (
    ARM_CONTROL,
    ARM_TREATMENT,
    PROVENANCE_FRESH,
    PROVENANCE_REUSED,
    TrialRecord,
)

_KNOWN_PROVENANCES = frozenset({PROVENANCE_FRESH, PROVENANCE_REUSED})

# implementation/runtime/golden_harness/promotion.py -> golden_harness ->
# runtime -> implementation -> repo root. Mirrors evaluator_hash.py's own
# REPO_ROOT derivation exactly (same package depth).
REPO_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Conjunct 2: "no critical regression"
# ---------------------------------------------------------------------------


class RegressionCheckResult(NamedTuple):
    """Result of applying conjunct 2 ("no critical regression") across every
    case present in the combined control/treatment trial set. Never a bare
    boolean -- reports exactly which case(s) (if any) triggered a confirmed
    regression, and which case(s) (if any) had a mismatched escalation and
    could not be classified at all."""

    no_critical_regression: bool
    confirmed_regression_case_ids: tuple[str, ...]
    mismatched_escalation_case_ids: tuple[str, ...]
    classified_case_ids: tuple[str, ...]


def _group_by_case(trials: list[TrialRecord]) -> dict[str, list[TrialRecord]]:
    groups: dict[str, list[TrialRecord]] = {}
    for trial in trials:
        groups.setdefault(trial.case_id, []).append(trial)
    return groups


def check_no_critical_regression(
    control_trials: list[TrialRecord],
    treatment_trials: list[TrialRecord],
    *,
    known_arm_agnostic_case_ids: frozenset[str] = frozenset(),
) -> RegressionCheckResult:
    """Conjunct 2's mapping, per `docs/artifacts/promotion-rule-v1.md` SS4:

    For every `case_id` present in the combined control+treatment trial set:

    - If **both** arms reach `policy.MIN_ESCALATED_K` (>=3) trials for that
      case, the case was actually escalated -- call
      `policy.classify_k_plus_outcome()` on its combined trials. If the
      result is `policy.CONFIRMED_PERSISTENT_EFFECT`, this is a candidate
      critical regression.

      **Documented judgment-call resolution** (the distinction
      `task-T499.md`'s criterion 2 drew via human judgment, not a mechanical
      formula -- see the design doc for the full disclosure): a candidate is
      treated as a real, treatment-specific critical regression **unless**
      its `case_id` appears in the caller-supplied
      `known_arm_agnostic_case_ids` -- an explicit, human-attested override
      for a case a reviewer has already judged to be an arm-agnostic
      checker-brittleness bug (affecting both arms roughly equally), not a
      real regression. This fails closed by default: a case is only ever
      excused from counting as a critical regression by an explicit,
      disclosed human judgment call supplied by the caller, never by this
      function inferring "arm-agnostic" on its own.

    - If **exactly one** arm reaches `MIN_ESCALATED_K` for that case (a
      mismatched escalation -- `policy.classify_k_plus_outcome()` would
      raise `ValueError` on such an input), this function does not call it.
      Fail-safe default: a mismatched-escalation case counts as blocking
      conjunct 2 (reported separately in `mismatched_escalation_case_ids`),
      since inconsistent per-arm trial counts for an escalated case is
      itself an anomaly a human should resolve before a promotion decision
      is trusted.

    - If **neither** arm reaches `MIN_ESCALATED_K` for that case (the
      comparison never escalated past k=1/k=2), this conjunct is vacuously
      satisfied for that case, per the task brief's own explicit statement:
      "there is no k>=3 case to classify as a critical regression."

    `no_critical_regression` is `True` only if there are zero confirmed
    regressions AND zero mismatched-escalation cases across the entire
    compared set.
    """
    all_trials = list(control_trials) + list(treatment_trials)
    by_case = _group_by_case(all_trials)

    confirmed: list[str] = []
    mismatched: list[str] = []
    classified: list[str] = []

    for case_id in sorted(by_case):
        case_trials = by_case[case_id]
        control_k = sum(1 for t in case_trials if t.arm == ARM_CONTROL)
        treatment_k = sum(1 for t in case_trials if t.arm == ARM_TREATMENT)

        control_escalated = control_k >= policy.MIN_ESCALATED_K
        treatment_escalated = treatment_k >= policy.MIN_ESCALATED_K

        if control_escalated and treatment_escalated:
            outcome = policy.classify_k_plus_outcome(case_trials)
            classified.append(case_id)
            if outcome == policy.CONFIRMED_PERSISTENT_EFFECT and case_id not in known_arm_agnostic_case_ids:
                confirmed.append(case_id)
        elif control_escalated != treatment_escalated:
            mismatched.append(case_id)
        # else: neither arm escalated for this case -- vacuously fine.

    no_critical_regression = not confirmed and not mismatched
    return RegressionCheckResult(
        no_critical_regression=no_critical_regression,
        confirmed_regression_case_ids=tuple(confirmed),
        mismatched_escalation_case_ids=tuple(mismatched),
        classified_case_ids=tuple(classified),
    )


# ---------------------------------------------------------------------------
# T510 (T509 design, Option A): per-case minimum-evidence gate
# ---------------------------------------------------------------------------


class EvidenceCheckResult(NamedTuple):
    """Result of the per-case minimum-evidence gate. Never a bare boolean --
    reports exactly which case(s), if any, have not reached
    `policy.MIN_ESCALATED_K` in both arms."""

    sufficient: bool
    insufficient_evidence_case_ids: tuple[str, ...]


def check_minimum_evidence(
    control_trials: list[TrialRecord],
    treatment_trials: list[TrialRecord],
) -> EvidenceCheckResult:
    """T509 design §5 item 1-2 (Option A): every `case_id` present in the
    combined control/treatment trial set must reach `policy.MIN_ESCALATED_K`
    trials in *both* arms before a promotion decision can be trusted.

    **Evaluated per-`case_id`, deliberately not as a raw pooled trial
    count.** This is the design's own §1.2 load-bearing correction: `T507`'s
    real pooled arrays were exactly 3 trials per arm -- satisfying a naive
    `len(control_trials) >= policy.MIN_ESCALATED_K` check -- but those 3
    trials came from 3 different cases at k=1 each, zero real replication in
    any single case. Grouping by `case_id` first (mirroring
    `check_no_critical_regression`'s own `_group_by_case` step) is what
    makes this gate actually catch that failure mode; a pooled-count
    shortcut would not have.
    """
    all_trials = list(control_trials) + list(treatment_trials)
    by_case = _group_by_case(all_trials)

    insufficient: list[str] = []
    for case_id in sorted(by_case):
        case_trials = by_case[case_id]
        control_k = sum(1 for t in case_trials if t.arm == ARM_CONTROL)
        treatment_k = sum(1 for t in case_trials if t.arm == ARM_TREATMENT)
        if control_k < policy.MIN_ESCALATED_K or treatment_k < policy.MIN_ESCALATED_K:
            insufficient.append(case_id)

    return EvidenceCheckResult(
        sufficient=not insufficient,
        insufficient_evidence_case_ids=tuple(insufficient),
    )


# ---------------------------------------------------------------------------
# T510 (T509 design, Option C): provenance-homogeneity pre-check
# ---------------------------------------------------------------------------


class ProvenanceCheckResult(NamedTuple):
    """Result of the provenance-homogeneity pre-check. Never a bare boolean
    -- reports exactly which case(s), if any, mix or lack known provenance
    across their control/treatment trials."""

    homogeneous: bool
    mismatched_case_ids: tuple[str, ...]


def check_provenance_homogeneity(
    control_trials: list[TrialRecord],
    treatment_trials: list[TrialRecord],
    *,
    known_compatible_provenance_case_ids: frozenset[str] = frozenset(),
) -> ProvenanceCheckResult:
    """T509 design §5 items 5-6 (Option C): every `case_id` present in the
    combined control/treatment trial set must have a single, known
    (`"fresh"` or `"reused"`) `TrialRecord.provenance` value shared across
    *all* of its trials, in both arms.

    **Fails closed.** A case is "provenance-mismatched" if its trials show
    more than one distinct provenance value, or if any trial's provenance is
    `"unknown"` (including every already-persisted record that predates this
    field, per `schema.TrialRecord.from_dict`'s default). `"unknown"` is
    never treated as compatible-by-default -- doing so would silently reopen
    the exact gap this check exists to close (T507 §3.5: two of its three
    cases mixed reused-historical control data against freshly-dispatched
    treatment data, a prompt-fidelity confound unrelated to the proposal's
    content).

    `known_compatible_provenance_case_ids` mirrors
    `check_no_critical_regression`'s `known_arm_agnostic_case_ids` exactly in
    spirit: an explicit, human-attested, caller-supplied override for a case
    a reviewer has already judged to be provenance-compatible despite this
    check's own default classification -- never inferred by this function.

    Implemented once, here -- both `evaluate_promotion()`'s improvement
    conjunct and its regression conjunct are gated by this single result
    (see `evaluate_promotion()`'s docstring), not by two separate
    grouping/comparison implementations.
    """
    all_trials = list(control_trials) + list(treatment_trials)
    by_case = _group_by_case(all_trials)

    mismatched: list[str] = []
    for case_id in sorted(by_case):
        provenances = {t.provenance for t in by_case[case_id]}
        is_uniform_and_known = len(provenances) == 1 and provenances <= _KNOWN_PROVENANCES
        if not is_uniform_and_known and case_id not in known_compatible_provenance_case_ids:
            mismatched.append(case_id)

    return ProvenanceCheckResult(
        homogeneous=not mismatched,
        mismatched_case_ids=tuple(mismatched),
    )


# ---------------------------------------------------------------------------
# T511 (T509 design, Option B): confirmed-positive-effect classification
# ---------------------------------------------------------------------------


class ImprovementClassificationResult(NamedTuple):
    """Result of applying `policy.classify_k_plus_improvement_outcome()` to
    every case present in the combined control/treatment trial set. Unlike
    `EvidenceCheckResult`/`ProvenanceCheckResult` (whose own underlying check
    is a simple per-case pass/fail), this conjunct's underlying result is
    itself a multi-outcome classification -- so this reports every actually-
    classified case's real outcome (`classifications`), not just an
    aggregate boolean, per this module's "never just a bare boolean, always
    name which case(s)" convention."""

    all_confirmed_positive_effect: bool
    classifications: dict[str, str]  # case_id -> policy classify_k_plus_improvement_outcome() result
    unconfirmed_case_ids: tuple[str, ...]
    classified_case_ids: tuple[str, ...]


def check_confirmed_positive_effect(
    control_trials: list[TrialRecord],
    treatment_trials: list[TrialRecord],
) -> ImprovementClassificationResult:
    """T511 (T509 design §2 "Option B", §5 item 11): for every `case_id`
    present in the combined control/treatment trial set (grouped via
    `_group_by_case`, mirroring `check_no_critical_regression`'s own
    per-case grouping):

    - If **both** arms reach `policy.MIN_ESCALATED_K` (>=3) trials for that
      case, the case was actually escalated -- call
      `policy.classify_k_plus_improvement_outcome()` on its combined trials
      and record the result in `classifications`. Any result other than
      `policy.CONFIRMED_POSITIVE_EFFECT` is added to `unconfirmed_case_ids`.

    - If **either** arm has fewer than `MIN_ESCALATED_K` trials for that case
      (mismatched escalation, or the case never escalated past k=1/k=2), this
      function does not call `classify_k_plus_improvement_outcome()` on it --
      that call would raise `ValueError` on such an input, exactly mirroring
      `check_no_critical_regression`'s own "only classify what actually
      escalated" discipline. Such a case can never be
      `CONFIRMED_POSITIVE_EFFECT` (that outcome itself requires k>=3), so it
      is still added to `unconfirmed_case_ids` -- but it has no entry in
      `classifications`, since none was computed. In `evaluate_promotion()`'s
      real pipeline this branch is not expected to fire: `check_minimum_
      evidence()` is already a required, prior precondition there, so every
      compared case is guaranteed to have reached k>=3 in both arms by the
      time this function is called. It remains here so this function is
      still safe and correct when called standalone (e.g. from a test) on
      data that has not first passed `check_minimum_evidence()`.

    `all_confirmed_positive_effect` is `True` only if every case's
    classification is exactly `policy.CONFIRMED_POSITIVE_EFFECT` --
    the required, conservative gate T511's own brief calls for (design
    decision 5): a `CONFIRMED_PERSISTENT_EFFECT`/`ELEVATED_BUT_HETEROGENEOUS`
    result here does not itself mean "critical regression" (that judgment
    belongs solely to `check_no_critical_regression`) -- it only means this
    conjunct's own bar (a traceable, recurring positive signal) was not met.
    """
    all_trials = list(control_trials) + list(treatment_trials)
    by_case = _group_by_case(all_trials)

    classifications: dict[str, str] = {}
    unconfirmed: list[str] = []
    classified: list[str] = []

    for case_id in sorted(by_case):
        case_trials = by_case[case_id]
        control_k = sum(1 for t in case_trials if t.arm == ARM_CONTROL)
        treatment_k = sum(1 for t in case_trials if t.arm == ARM_TREATMENT)

        if control_k >= policy.MIN_ESCALATED_K and treatment_k >= policy.MIN_ESCALATED_K:
            outcome = policy.classify_k_plus_improvement_outcome(case_trials)
            classifications[case_id] = outcome
            classified.append(case_id)
            if outcome != policy.CONFIRMED_POSITIVE_EFFECT:
                unconfirmed.append(case_id)
        else:
            unconfirmed.append(case_id)

    return ImprovementClassificationResult(
        all_confirmed_positive_effect=not unconfirmed,
        classifications=classifications,
        unconfirmed_case_ids=tuple(unconfirmed),
        classified_case_ids=tuple(classified),
    )


# ---------------------------------------------------------------------------
# The combined six-conjunct promotion decision
# ---------------------------------------------------------------------------


class PromotionResult(NamedTuple):
    """The combined promote/reject decision. Never a bare boolean -- a human
    reviewer (T464-equiv's eventual MR gate) needs to know *why* a proposal
    was rejected, so every conjunct's individual result is reported
    alongside the final `promote` boolean and a human-readable `reason`."""

    promote: bool
    reason: str
    floor_met: bool
    no_critical_regression: bool
    evaluator_hash_unchanged: bool
    minimum_evidence_met: bool
    provenance_homogeneous: bool
    confirmed_positive_effect_met: bool
    confirmed_regression_case_ids: tuple[str, ...]
    mismatched_escalation_case_ids: tuple[str, ...]
    insufficient_evidence_case_ids: tuple[str, ...]
    provenance_mismatched_case_ids: tuple[str, ...]
    improvement_classifications: dict[str, str]
    unconfirmed_positive_effect_case_ids: tuple[str, ...]
    evaluator_hash_check: evaluator_hash.DriftCheckResult


def _build_promotion_reason(
    floor_ok: bool,
    regression: RegressionCheckResult,
    hash_ok: bool,
    hash_check: evaluator_hash.DriftCheckResult,
    evidence: EvidenceCheckResult,
    provenance: ProvenanceCheckResult,
    improvement: ImprovementClassificationResult,
) -> str:
    if (
        floor_ok
        and regression.no_critical_regression
        and hash_ok
        and evidence.sufficient
        and provenance.homogeneous
        and improvement.all_confirmed_positive_effect
    ):
        return (
            "PROMOTE: all conjuncts satisfied (floor met, no critical regression, evaluator hash "
            "unchanged, minimum evidence met, provenance homogeneous, confirmed positive effect)."
        )

    failures: list[str] = []
    if not floor_ok:
        failures.append("floor not met (treatment aggregate pass rate is below control's)")
    if not regression.no_critical_regression:
        if regression.confirmed_regression_case_ids:
            failures.append(
                "critical regression confirmed in case(s): " + ", ".join(regression.confirmed_regression_case_ids)
            )
        if regression.mismatched_escalation_case_ids:
            failures.append(
                "mismatched escalation (one arm reached k>=3, the other did not) in case(s): "
                + ", ".join(regression.mismatched_escalation_case_ids)
            )
    if not hash_ok:
        failures.append("evaluator hash drifted: " + hash_check.reason)
    if not evidence.sufficient:
        failures.append(
            f"insufficient evidence (case(s) below k={policy.MIN_ESCALATED_K} in at least one arm): "
            + ", ".join(evidence.insufficient_evidence_case_ids)
        )
    if not provenance.homogeneous:
        failures.append(
            "provenance mismatch (case(s) with non-uniform or unknown trial provenance across arms): "
            + ", ".join(provenance.mismatched_case_ids)
        )
    if not improvement.all_confirmed_positive_effect:
        failures.append(
            "no confirmed positive effect (case(s) that did not reach a traceable, recurring "
            "category-3 finding at floor-met): " + ", ".join(improvement.unconfirmed_case_ids)
        )

    return "REJECT: " + "; ".join(failures)


def evaluate_promotion(
    control_trials: list[TrialRecord],
    treatment_trials: list[TrialRecord],
    evaluator_hash_check: evaluator_hash.DriftCheckResult,
    *,
    known_arm_agnostic_case_ids: frozenset[str] = frozenset(),
    known_compatible_provenance_case_ids: frozenset[str] = frozenset(),
) -> PromotionResult:
    """Combine `plan-035`'s three original promotion-rule conjuncts, plus
    `T510`'s two hardening preconditions (T509 design, Options A + C), into
    one promote/reject decision:

    1. "improvement > regression" -> `policy.floor_met(control_trials,
       treatment_trials)` is `True`.
    2. "no critical regression" -> `check_no_critical_regression(...)`
       reports `no_critical_regression=True` (see that function's docstring
       for the full per-case mapping, including the documented judgment-call
       and mismatched-escalation resolutions).
    3. "evaluator hash unchanged" -> `evaluator_hash_check.any_drift` is
       `False`.
    4. **[T510, Option A]** "minimum evidence met" ->
       `check_minimum_evidence(...)` reports `sufficient=True` -- every
       `case_id` present reached `policy.MIN_ESCALATED_K` in both arms.
       Evaluated as its own precondition, not nested inside `floor_met` or
       `check_no_critical_regression` (both of which keep their own
       internal logic unchanged): if any case has insufficient evidence,
       `promote` is `False` regardless of what the other four conjuncts
       would otherwise return.
    5. **[T510, Option C]** "provenance homogeneous" ->
       `check_provenance_homogeneity(...)` reports `homogeneous=True` --
       every `case_id` present has a single, known provenance shared across
       both arms. Implemented once (`check_provenance_homogeneity`) and its
       result gates this overall decision directly, protecting both the
       improvement conjunct (1) and the regression conjunct (2) from a
       provenance-confounded comparison without duplicating the
       grouping/comparison logic.
    6. **[T511, Option B]** "confirmed positive effect" ->
       `check_confirmed_positive_effect(...)` reports
       `all_confirmed_positive_effect=True` -- every `case_id` present
       reaches `policy.CONFIRMED_POSITIVE_EFFECT` under
       `policy.classify_k_plus_improvement_outcome()`. A required,
       conservative sixth conjunct (T511's own disclosed judgment call, per
       `docs/tasks/task-T511.md` design decision 5): gives conjunct 1 a real
       qualitative, traceable, recurring-signal requirement, not just an
       absence-of-regression statistic. If any compared case has not
       reached `CONFIRMED_POSITIVE_EFFECT`, `promote` is `False` regardless
       of what the other five conjuncts would otherwise return.

    All six conjuncts AND together.

    `control_trials`/`treatment_trials` are plain `TrialRecord` lists --
    this function embeds no live-dispatch call of any kind. How those
    records were produced (a live dispatch, a future automated
    loop-runner, or a persisted `trial_store.py` file) is entirely the
    caller's concern; this function only consumes the resulting records.
    Likewise, `evaluator_hash_check` is a caller-supplied
    `evaluator_hash.DriftCheckResult` (typically produced by calling
    `evaluator_hash.check_evaluator_hash()` once per validation cycle) --
    this function does not call it internally, so a caller can reuse one
    hash-check result across multiple promotion evaluations in the same
    cycle without re-hashing the protected paths each time.
    """
    floor_ok = policy.floor_met(control_trials, treatment_trials)
    regression = check_no_critical_regression(
        control_trials, treatment_trials, known_arm_agnostic_case_ids=known_arm_agnostic_case_ids
    )
    hash_ok = not evaluator_hash_check.any_drift
    evidence = check_minimum_evidence(control_trials, treatment_trials)
    provenance = check_provenance_homogeneity(
        control_trials,
        treatment_trials,
        known_compatible_provenance_case_ids=known_compatible_provenance_case_ids,
    )
    improvement = check_confirmed_positive_effect(control_trials, treatment_trials)

    promote = (
        floor_ok
        and regression.no_critical_regression
        and hash_ok
        and evidence.sufficient
        and provenance.homogeneous
        and improvement.all_confirmed_positive_effect
    )
    reason = _build_promotion_reason(
        floor_ok, regression, hash_ok, evaluator_hash_check, evidence, provenance, improvement
    )

    return PromotionResult(
        promote=promote,
        reason=reason,
        floor_met=floor_ok,
        no_critical_regression=regression.no_critical_regression,
        evaluator_hash_unchanged=hash_ok,
        minimum_evidence_met=evidence.sufficient,
        provenance_homogeneous=provenance.homogeneous,
        confirmed_positive_effect_met=improvement.all_confirmed_positive_effect,
        confirmed_regression_case_ids=regression.confirmed_regression_case_ids,
        mismatched_escalation_case_ids=regression.mismatched_escalation_case_ids,
        insufficient_evidence_case_ids=evidence.insufficient_evidence_case_ids,
        provenance_mismatched_case_ids=provenance.mismatched_case_ids,
        improvement_classifications=improvement.classifications,
        unconfirmed_positive_effect_case_ids=improvement.unconfirmed_case_ids,
        evaluator_hash_check=evaluator_hash_check,
    )


# ---------------------------------------------------------------------------
# Apply-to-scratch helper
# ---------------------------------------------------------------------------


def apply_proposal_to_scratch(proposal: meta_improver.DiffProposal, scratch_root: Path) -> Path:
    """Write `proposal.proposed_content` to an isolated scratch copy of
    `proposal.target_path`, under `scratch_root` -- a plain directory,
    never a git worktree, never the real tracked file. Mirrors
    `golden_harness/scratch.py`'s existing scratch-isolation convention
    (`write_candidate_file`'s `case_dir / "fixture" / relative_path` shape,
    applied here as `scratch_root / target_path`) and `meta_improver.py`'s
    own "never writes to a real repo file" discipline exactly: this
    function never resolves or writes to any path under this repository's
    own tracked tree.

    Raises `ValueError` if `scratch_root` resolves to this repository's own
    root or any path under it -- a defensive guard against accidentally
    pointing this helper at the real checkout, on top of the fact that it
    never targets any path derived from the real repo tree in the first
    place (it only ever joins `scratch_root` with `proposal.target_path`,
    never `REPO_ROOT`).

    Returns the path of the written scratch file.
    """
    resolved_scratch_root = scratch_root.resolve()
    if resolved_scratch_root == REPO_ROOT or REPO_ROOT in resolved_scratch_root.parents:
        raise ValueError(
            f"scratch_root must not be this repository's own tracked tree or a path under it, "
            f"got {resolved_scratch_root} (repo root is {REPO_ROOT})"
        )

    resolved_scratch_root.mkdir(parents=True, exist_ok=True)
    target = resolved_scratch_root / PurePosixPath(proposal.target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(proposal.proposed_content, encoding="utf-8")
    return target
