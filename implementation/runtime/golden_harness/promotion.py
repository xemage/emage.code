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
from implementation.runtime.golden_harness.schema import ARM_CONTROL, ARM_TREATMENT, TrialRecord

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
# The combined three-conjunct promotion decision
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
    confirmed_regression_case_ids: tuple[str, ...]
    mismatched_escalation_case_ids: tuple[str, ...]
    evaluator_hash_check: evaluator_hash.DriftCheckResult


def _build_promotion_reason(
    floor_ok: bool,
    regression: RegressionCheckResult,
    hash_ok: bool,
    hash_check: evaluator_hash.DriftCheckResult,
) -> str:
    if floor_ok and regression.no_critical_regression and hash_ok:
        return "PROMOTE: all three conjuncts satisfied (floor met, no critical regression, evaluator hash unchanged)."

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

    return "REJECT: " + "; ".join(failures)


def evaluate_promotion(
    control_trials: list[TrialRecord],
    treatment_trials: list[TrialRecord],
    evaluator_hash_check: evaluator_hash.DriftCheckResult,
    *,
    known_arm_agnostic_case_ids: frozenset[str] = frozenset(),
) -> PromotionResult:
    """Combine all three of `plan-035`'s promotion-rule conjuncts into one
    promote/reject decision:

    1. "improvement > regression" -> `policy.floor_met(control_trials,
       treatment_trials)` is `True`.
    2. "no critical regression" -> `check_no_critical_regression(...)`
       reports `no_critical_regression=True` (see that function's docstring
       for the full per-case mapping, including the documented judgment-call
       and mismatched-escalation resolutions).
    3. "evaluator hash unchanged" -> `evaluator_hash_check.any_drift` is
       `False`.

    All three conjuncts AND together.

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

    promote = floor_ok and regression.no_critical_regression and hash_ok
    reason = _build_promotion_reason(floor_ok, regression, hash_ok, evaluator_hash_check)

    return PromotionResult(
        promote=promote,
        reason=reason,
        floor_met=floor_ok,
        no_critical_regression=regression.no_critical_regression,
        evaluator_hash_unchanged=hash_ok,
        confirmed_regression_case_ids=regression.confirmed_regression_case_ids,
        mismatched_escalation_case_ids=regression.mismatched_escalation_case_ids,
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
