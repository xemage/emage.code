"""`plan-048-t458-k-threshold-decision.md` §7's decided policy, as callable
functions (T458 Objective #4).

This module implements an already-decided policy; it does not re-derive it.
Every function below is mapped to the exact `plan-048` §7 sentence it
implements in `docs/artifacts/golden-live-harness-v1.md` -- read that mapping
before changing any function here, since a change that isn't also a change to
`plan-048` itself would silently desync code from decided policy.
"""
from __future__ import annotations

from collections import Counter
from typing import NamedTuple

from implementation.runtime.golden_harness.schema import ARM_CONTROL, ARM_TREATMENT, TrialRecord

# plan-048 §7: "default k=1".
DEFAULT_K = 1

# plan-048 §7: "escalate to k>=3 on k=1 arm disagreement" / "classify every
# k>=3 result". `classify_k_plus_outcome` requires at least this many trials
# per arm; real evidence has gone as high as k=5 (T493) under the same rule.
MIN_ESCALATED_K = 3

CATEGORY_TRACEABLE_POSITIVE_INFLUENCE = "3"  # plan-048 §5's rubric, category 3.

TRIGGER_DISAGREEMENT = "disagreement"
TRIGGER_REPRODUCIBILITY_CHECK = "reproducibility_check"

CONFIRMED_COIN_FLIP = "confirmed_coin_flip"
CONFIRMED_PERSISTENT_EFFECT = "confirmed_persistent_effect"
ELEVATED_BUT_HETEROGENEOUS = "elevated_but_heterogeneous"


class EscalationDecision(NamedTuple):
    escalate: bool
    trigger: str | None


def should_escalate(control_k1: TrialRecord, treatment_k1: TrialRecord) -> EscalationDecision:
    """plan-048 §7 / §3 Part A + Trigger 2: escalate a case from k=1 to
    k>=3 when either (a) the two arms disagree at k=1 (Part A), or
    (b) the arms agree but the treatment trial showed a category-3
    ("traceable positive influence") finding, to test reproducibility
    (Trigger 2). Otherwise, stay at k=1."""
    if control_k1.result != treatment_k1.result:
        return EscalationDecision(True, TRIGGER_DISAGREEMENT)
    if treatment_k1.category == CATEGORY_TRACEABLE_POSITIVE_INFLUENCE:
        return EscalationDecision(True, TRIGGER_REPRODUCIBILITY_CHECK)
    return EscalationDecision(False, None)


def pass_rate(trials: list[TrialRecord]) -> float:
    if not trials:
        raise ValueError("pass_rate requires at least one trial")
    return sum(1 for t in trials if t.result) / len(trials)


def floor_met(control_trials: list[TrialRecord], treatment_trials: list[TrialRecord]) -> bool:
    """plan-048 §4: the non-regression floor is met when the treatment arm's
    pass rate is not below the control arm's."""
    return pass_rate(treatment_trials) >= pass_rate(control_trials)


def count_cause_occurrences(trials: list[TrialRecord]) -> dict[str, int]:
    """How many times each diagnosed cause appears among `trials`' *failing*
    records, arm-agnostic (plan-048 §4: "regardless of which arm each
    occurrence falls in"). Failing trials with no diagnosed cause are
    excluded -- recurrence cannot be confirmed for an undiagnosed failure."""
    causes = [t.diagnosed_cause for t in trials if not t.result and t.diagnosed_cause]
    return dict(Counter(causes))


def is_floor_miss_actionable(cause_occurrences: dict[str, int]) -> bool:
    """plan-048 §4's floor-tolerance recurrence rule: a floor miss becomes
    actionable only once the same diagnosed cause recurs across >=2 trials
    within the case's own evidence set. A floor miss whose causes have each
    occurred exactly once stays open (not actionable)."""
    return any(count >= 2 for count in cause_occurrences.values())


def classify_k_plus_outcome(trials: list[TrialRecord]) -> str:
    """plan-048 §3's three-outcome classification for a k>=3 case, applied
    honestly rather than forced into a binary call:

    1. If the non-regression floor is met, the case is a
       `confirmed_coin_flip` (fluctuation) -- even a recurring cause that
       strikes both arms roughly evenly does not turn a met floor into a
       regression (plan-048 §7's own worked example,
       `code-review-fail-blocker-details`).
    2. If the floor is missed and the floor-tolerance recurrence rule
       (`is_floor_miss_actionable`) finds a cause recurring >=2 times, the
       case is a `confirmed_persistent_effect` -- a real, actionable
       checker/template-brittleness bug (T493's real
       `security-audit-coverage-consistency` k=5 result).
    3. If the floor is missed and no cause recurs, the case is
       `elevated_but_heterogeneous` -- durably worse, but not yet
       attributable to any one repeating cause; stays open, neither
       dismissed nor confirmed (T490's k=3 `security-audit-coverage-
       consistency` result, before T493 escalated further).
    """
    control = [t for t in trials if t.arm == ARM_CONTROL]
    treatment = [t for t in trials if t.arm == ARM_TREATMENT]
    _require_min_k(control, treatment)

    if floor_met(control, treatment):
        return CONFIRMED_COIN_FLIP

    occurrences = count_cause_occurrences(control + treatment)
    if is_floor_miss_actionable(occurrences):
        return CONFIRMED_PERSISTENT_EFFECT
    return ELEVATED_BUT_HETEROGENEOUS


def _require_min_k(control: list[TrialRecord], treatment: list[TrialRecord]) -> None:
    if len(control) < MIN_ESCALATED_K or len(treatment) < MIN_ESCALATED_K:
        raise ValueError(
            f"classify_k_plus_outcome requires >= {MIN_ESCALATED_K} trials per arm, "
            f"got control={len(control)}, treatment={len(treatment)}"
        )


class BaseRateResult(NamedTuple):
    classified_count: int
    category_3_count: int
    total_treatment_count: int
    rate_of_classified: float
    rate_conservative: float


def compute_base_rate(trials: list[TrialRecord]) -> BaseRateResult:
    """plan-048 §5's base-rate statement, reproduced from raw trial records
    rather than hardcoded: of all treatment-arm trials, how many were
    qualitatively classified at all (`category is not None`), and of those,
    how many landed in category 3 ("traceable positive influence")? Reports
    both the rate among classified trials and the conservative rate treating
    every unclassified trial as non-category-3 (plan-048 §5's own "2 of 11
    (18%) ... or, conservatively, 2 of 14 (14%)" framing)."""
    treatment = [t for t in trials if t.arm == ARM_TREATMENT]
    classified = [t for t in treatment if t.category is not None]
    category_3 = [t for t in classified if t.category == CATEGORY_TRACEABLE_POSITIVE_INFLUENCE]

    rate_of_classified = (len(category_3) / len(classified)) if classified else 0.0
    rate_conservative = (len(category_3) / len(treatment)) if treatment else 0.0

    return BaseRateResult(
        classified_count=len(classified),
        category_3_count=len(category_3),
        total_treatment_count=len(treatment),
        rate_of_classified=rate_of_classified,
        rate_conservative=rate_conservative,
    )
