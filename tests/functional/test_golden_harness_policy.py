"""Tests for `implementation/runtime/golden_harness/policy.py` (T458
Objective #4) -- `plan-048-t458-k-threshold-decision.md` §7's decided policy,
exercised against synthetic `TrialRecord`s reconstructed from that document's
own real, already-published trial tables (§2, §3, §5; `task-T493.md`'s k=5
table). No live agent session is invoked anywhere in this file.

Reconstructing real historical results as fixtures (rather than inventing
generic synthetic numbers throughout) directly exercises `task-T458.md`'s
second pre-anticipated blocker case: whether `plan-048`'s stated base rate
(2 of 11, 18%) is reproducible from trial records. See
`TestComputeBaseRate.test_reproduces_plan_048_base_rate_from_reconstructed_records`
below -- it is cleanly reproducible, not ambiguous, so no blocker was raised.
"""
from __future__ import annotations

import unittest

from implementation.runtime.golden_harness.policy import (
    CONFIRMED_COIN_FLIP,
    CONFIRMED_PERSISTENT_EFFECT,
    CONFIRMED_POSITIVE_EFFECT,
    ELEVATED_BUT_HETEROGENEOUS,
    TRIGGER_DISAGREEMENT,
    TRIGGER_REPRODUCIBILITY_CHECK,
    classify_k_plus_improvement_outcome,
    classify_k_plus_outcome,
    compute_base_rate,
    count_category_occurrences,
    count_cause_occurrences,
    floor_met,
    is_floor_miss_actionable,
    pass_rate,
    should_escalate,
)
from implementation.runtime.golden_harness.schema import TrialRecord


def _trial(case_id, arm, k, result, category=None, cause=None) -> TrialRecord:
    return TrialRecord(case_id=case_id, arm=arm, k_index=k, result=result, category=category, diagnosed_cause=cause)


class TestShouldEscalate(unittest.TestCase):
    def test_disagreement_at_k1_escalates(self):
        control = _trial("c", "control", 1, True)
        treatment = _trial("c", "treatment", 1, False)
        decision = should_escalate(control, treatment)
        self.assertTrue(decision.escalate)
        self.assertEqual(decision.trigger, TRIGGER_DISAGREEMENT)

    def test_unanimous_case_with_no_category_3_does_not_escalate(self):
        # prepare-release-changelog-grouping-compliant: unanimous True/True
        # at k=1, treatment classified category 2 -- correctly never
        # escalated (plan-048 §3 Part A, "2 direct non-applications").
        control = _trial("prepare-release-changelog-grouping-compliant", "control", 1, True)
        treatment = _trial("prepare-release-changelog-grouping-compliant", "treatment", 1, True, category="2")
        decision = should_escalate(control, treatment)
        self.assertFalse(decision.escalate)
        self.assertIsNone(decision.trigger)

    def test_unanimous_case_with_category_3_treatment_triggers_reproducibility_check(self):
        # plan-required-sections-compliant: unanimous True/True at k=1, but
        # the treatment trial showed a category-3 finding -- Trigger 2 fires
        # (plan-048 §3, real T490 escalation).
        control = _trial("plan-required-sections-compliant", "control", 1, True)
        treatment = _trial("plan-required-sections-compliant", "treatment", 1, True, category="3")
        decision = should_escalate(control, treatment)
        self.assertTrue(decision.escalate)
        self.assertEqual(decision.trigger, TRIGGER_REPRODUCIBILITY_CHECK)


class TestPassRateAndFloorMet(unittest.TestCase):
    def test_pass_rate_of_empty_list_raises(self):
        with self.assertRaises(ValueError):
            pass_rate([])

    def test_floor_met_when_treatment_at_least_as_good(self):
        control = [_trial("c", "control", k, True) for k in (1, 2, 3)]
        treatment = [_trial("c", "treatment", k, True) for k in (1, 2, 3)]
        self.assertTrue(floor_met(control, treatment))

    def test_floor_missed_when_treatment_strictly_worse(self):
        control = [_trial("c", "control", k, True) for k in (1, 2, 3)]
        treatment = [_trial("c", "treatment", 1, False)] + [_trial("c", "treatment", k, True) for k in (2, 3)]
        self.assertFalse(floor_met(control, treatment))


class TestCauseRecurrence(unittest.TestCase):
    def test_count_cause_occurrences_ignores_passing_and_undiagnosed_failures(self):
        trials = [
            _trial("c", "control", 1, True),
            _trial("c", "control", 2, False, cause="x"),
            _trial("c", "control", 3, False),  # undiagnosed -- excluded
            _trial("c", "treatment", 1, False, cause="x"),
        ]
        self.assertEqual(count_cause_occurrences(trials), {"x": 2})

    def test_is_floor_miss_actionable_requires_recurrence(self):
        self.assertFalse(is_floor_miss_actionable({"x": 1, "y": 1}))
        self.assertTrue(is_floor_miss_actionable({"x": 2}))


class TestClassifyKPlusOutcomeAgainstRealHistoricalCases(unittest.TestCase):
    """Each case below reconstructs a real, already-published trial table
    (see docstrings) and asserts `classify_k_plus_outcome` reproduces the
    real, already-reported classification -- not an invented expectation."""

    def test_code_review_fail_blocker_details_is_confirmed_coin_flip(self):
        # plan-048 §2/§3: control True/False/False (causes: -, verdict_
        # severity_flip, owner_field_inline_prose); treatment False/True/
        # False (causes: owner_field_table_header, -, owner_field_inline_
        # prose). Floor met (1/3 vs 1/3) -> confirmed_coin_flip, even though
        # owner_field_inline_prose recurs twice across the two arms.
        trials = [
            _trial("code-review-fail-blocker-details", "control", 1, True),
            _trial("code-review-fail-blocker-details", "control", 2, False, cause="verdict_severity_flip"),
            _trial("code-review-fail-blocker-details", "control", 3, False, cause="owner_field_inline_prose"),
            _trial("code-review-fail-blocker-details", "treatment", 1, False, cause="owner_field_table_header"),
            _trial("code-review-fail-blocker-details", "treatment", 2, True),
            _trial("code-review-fail-blocker-details", "treatment", 3, False, cause="owner_field_inline_prose"),
        ]
        self.assertEqual(classify_k_plus_outcome(trials), CONFIRMED_COIN_FLIP)

    def test_security_audit_coverage_consistency_k3_is_elevated_but_heterogeneous(self):
        # plan-048 §3/§4, T490's k=3 snapshot: control 3/3; treatment 1/3
        # (two distinct causes, each occurring exactly once). Floor missed,
        # no cause recurs -> elevated_but_heterogeneous (open).
        trials = [
            _trial("security-audit-coverage-consistency", "control", 1, True),
            _trial("security-audit-coverage-consistency", "control", 2, True),
            _trial("security-audit-coverage-consistency", "control", 3, True),
            _trial("security-audit-coverage-consistency", "treatment", 1, False, cause="field_format_bolded_sentence"),
            _trial("security-audit-coverage-consistency", "treatment", 2, False, cause="matrix_self_consistency_slip"),
            _trial("security-audit-coverage-consistency", "treatment", 3, True),
        ]
        self.assertEqual(classify_k_plus_outcome(trials), ELEVATED_BUT_HETEROGENEOUS)

    def test_security_audit_coverage_consistency_k5_is_confirmed_persistent_effect(self):
        # task-T493.md's real k=5 table: control 4/5 (control-4 fails with
        # matrix_self_consistency_slip); treatment 1/5 (treatment-1 fails
        # with field_format_bolded_sentence; treatment-2/4/5 fail with
        # matrix_self_consistency_slip). That cause now recurs 4 times ->
        # confirmed_persistent_effect, matching T493's real conclusion.
        trials = [
            _trial("security-audit-coverage-consistency", "control", 1, True),
            _trial("security-audit-coverage-consistency", "control", 2, True),
            _trial("security-audit-coverage-consistency", "control", 3, True),
            _trial("security-audit-coverage-consistency", "control", 4, False, cause="matrix_self_consistency_slip"),
            _trial("security-audit-coverage-consistency", "control", 5, True),
            _trial("security-audit-coverage-consistency", "treatment", 1, False, cause="field_format_bolded_sentence"),
            _trial("security-audit-coverage-consistency", "treatment", 2, False, cause="matrix_self_consistency_slip"),
            _trial("security-audit-coverage-consistency", "treatment", 3, True),
            _trial("security-audit-coverage-consistency", "treatment", 4, False, cause="matrix_self_consistency_slip"),
            _trial("security-audit-coverage-consistency", "treatment", 5, False, cause="matrix_self_consistency_slip"),
        ]
        self.assertEqual(classify_k_plus_outcome(trials), CONFIRMED_PERSISTENT_EFFECT)

    def test_raises_below_the_minimum_k_per_arm(self):
        trials = [_trial("c", "control", 1, True), _trial("c", "treatment", 1, True)]
        with self.assertRaises(ValueError):
            classify_k_plus_outcome(trials)


class TestCountCategoryOccurrences(unittest.TestCase):
    """T511 (T509 design, Option B): mirrors `TestCauseRecurrence`'s own
    coverage of `count_cause_occurrences`, applied to `category` instead."""

    def test_counts_matching_category_only(self):
        trials = [
            _trial("c", "treatment", 1, True, category="3"),
            _trial("c", "treatment", 2, True, category="3"),
            _trial("c", "treatment", 3, True, category="2"),
            _trial("c", "treatment", 4, False),  # uncategorized -- excluded
        ]
        self.assertEqual(count_category_occurrences(trials, "3"), 2)

    def test_does_not_restrict_to_failing_trials(self):
        # Unlike count_cause_occurrences (failing trials only), category is
        # counted regardless of result -- a category-3 finding is not
        # defined only for failures. Both trials below pass, yet both count.
        trials = [
            _trial("c", "treatment", 1, True, category="3"),
            _trial("c", "treatment", 2, True, category="3"),
        ]
        self.assertEqual(count_category_occurrences(trials, "3"), 2)

    def test_absent_category_returns_zero(self):
        trials = [_trial("c", "treatment", 1, True, category="2")]
        self.assertEqual(count_category_occurrences(trials, "3"), 0)


class TestClassifyKPlusImprovementOutcome(unittest.TestCase):
    """T511 (T509 design §2 "Option B", §5 item 11): the improvement-side
    sibling of `TestClassifyKPlusOutcomeAgainstRealHistoricalCases`."""

    def test_floor_met_with_recurring_category_3_in_treatment_is_confirmed_positive_effect(self):
        control = [_trial("c", "control", k, True) for k in (1, 2, 3)]
        treatment = [
            _trial("c", "treatment", 1, True, category="3"),
            _trial("c", "treatment", 2, True, category="3"),
            _trial("c", "treatment", 3, True),
        ]
        self.assertEqual(classify_k_plus_improvement_outcome(control + treatment), CONFIRMED_POSITIVE_EFFECT)

    def test_floor_met_with_single_category_3_occurrence_is_confirmed_coin_flip(self):
        # Category-3 present but does not recur (exactly one occurrence) --
        # the existing CONFIRMED_COIN_FLIP outcome, reused not renamed.
        control = [_trial("c", "control", k, True) for k in (1, 2, 3)]
        treatment = [
            _trial("c", "treatment", 1, True, category="3"),
            _trial("c", "treatment", 2, True),
            _trial("c", "treatment", 3, True),
        ]
        self.assertEqual(classify_k_plus_improvement_outcome(control + treatment), CONFIRMED_COIN_FLIP)

    def test_t507_real_pattern_floor_met_with_no_category_ever_recorded_is_confirmed_coin_flip(self):
        # `t507-closed-loop-cycle-v1.md` §3.3: none of T507's real treatment
        # trials had a `category` recorded at all (unset/None throughout).
        # T507's real cases never escalated past k=1 -- reconstructed here
        # at k=3 (this function's own minimum) with the floor met and zero
        # category-3 occurrences, preserving that same "never categorized"
        # characteristic. This directly confirms this classification alone
        # would independently have withheld CONFIRMED_POSITIVE_EFFECT from
        # T507's real proposal -- a second, independent line of defense
        # beyond T510's own two gates (`check_minimum_evidence` /
        # `check_provenance_homogeneity`), which block T507's actual k=1
        # data on different grounds entirely (see
        # `test_golden_harness_promotion.py`'s `_t507_real_trials`).
        control = [_trial("c", "control", k, True) for k in (1, 2, 3)]
        treatment = [_trial("c", "treatment", k, True) for k in (1, 2, 3)]  # category never set, matching T507
        self.assertEqual(classify_k_plus_improvement_outcome(control + treatment), CONFIRMED_COIN_FLIP)

    def test_floor_missed_delegates_to_classify_k_plus_outcome_confirmed_persistent_effect(self):
        # Same real task-T493.md k=5 table as
        # TestClassifyKPlusOutcomeAgainstRealHistoricalCases's own
        # confirmed_persistent_effect test -- confirms delegation returns
        # classify_k_plus_outcome()'s result verbatim, not a reimplementation.
        trials = [
            _trial("security-audit-coverage-consistency", "control", 1, True),
            _trial("security-audit-coverage-consistency", "control", 2, True),
            _trial("security-audit-coverage-consistency", "control", 3, True),
            _trial("security-audit-coverage-consistency", "control", 4, False, cause="matrix_self_consistency_slip"),
            _trial("security-audit-coverage-consistency", "control", 5, True),
            _trial("security-audit-coverage-consistency", "treatment", 1, False, cause="field_format_bolded_sentence"),
            _trial("security-audit-coverage-consistency", "treatment", 2, False, cause="matrix_self_consistency_slip"),
            _trial("security-audit-coverage-consistency", "treatment", 3, True),
            _trial("security-audit-coverage-consistency", "treatment", 4, False, cause="matrix_self_consistency_slip"),
            _trial("security-audit-coverage-consistency", "treatment", 5, False, cause="matrix_self_consistency_slip"),
        ]
        self.assertEqual(classify_k_plus_improvement_outcome(trials), CONFIRMED_PERSISTENT_EFFECT)
        self.assertEqual(classify_k_plus_improvement_outcome(trials), classify_k_plus_outcome(trials))

    def test_floor_missed_delegates_to_classify_k_plus_outcome_elevated_but_heterogeneous(self):
        # Same real T490 k=3 snapshot as
        # TestClassifyKPlusOutcomeAgainstRealHistoricalCases's own
        # elevated_but_heterogeneous test.
        trials = [
            _trial("security-audit-coverage-consistency", "control", 1, True),
            _trial("security-audit-coverage-consistency", "control", 2, True),
            _trial("security-audit-coverage-consistency", "control", 3, True),
            _trial("security-audit-coverage-consistency", "treatment", 1, False, cause="field_format_bolded_sentence"),
            _trial("security-audit-coverage-consistency", "treatment", 2, False, cause="matrix_self_consistency_slip"),
            _trial("security-audit-coverage-consistency", "treatment", 3, True),
        ]
        self.assertEqual(classify_k_plus_improvement_outcome(trials), ELEVATED_BUT_HETEROGENEOUS)
        self.assertEqual(classify_k_plus_improvement_outcome(trials), classify_k_plus_outcome(trials))

    def test_raises_below_the_minimum_k_per_arm(self):
        trials = [_trial("c", "control", 1, True), _trial("c", "treatment", 1, True)]
        with self.assertRaises(ValueError):
            classify_k_plus_improvement_outcome(trials)


class TestComputeBaseRate(unittest.TestCase):
    def test_reproduces_plan_048_base_rate_from_reconstructed_records(self):
        # plan-048 §5's real 14-trial treatment-arm table, reconstructed
        # exactly: 5x category 2, 2x category 3, 1x category 4, 3x category
        # 5, 3x unclassified (category=None). Expected: 2/11 classified
        # (~18.18%), 2/14 conservative (~14.29%) -- matching plan-048's own
        # "18%, or 14% conservatively" statement.
        trials = [
            _trial("prepare-release-changelog-grouping-compliant", "treatment", 1, True, category="2"),
            _trial("code-review-fail-blocker-details", "treatment", 1, False, category="2"),
            _trial("security-audit-coverage-consistency", "treatment", 1, False, category="2"),
            _trial("security-audit-coverage-consistency", "treatment", 2, False, category="2"),
            _trial("security-audit-verdict-fields-compliant", "treatment", 1, True, category="2"),
            _trial("plan-required-sections-compliant", "treatment", 1, True, category="3"),
            _trial("new-feature-plan-doc-compliant", "treatment", 1, True, category="3"),
            _trial("new-feature-plan-doc-compliant", "treatment", 2, False, category="4"),
            _trial("plan-required-sections-compliant", "treatment", 2, True, category="5"),
            _trial("plan-required-sections-compliant", "treatment", 3, True, category="5"),
            _trial("new-feature-plan-doc-compliant", "treatment", 3, True, category="5"),
            _trial("code-review-fail-blocker-details", "treatment", 2, True, category=None),
            _trial("code-review-fail-blocker-details", "treatment", 3, False, category=None),
            _trial("security-audit-coverage-consistency", "treatment", 3, True, category=None),
        ]
        result = compute_base_rate(trials)
        self.assertEqual(result.classified_count, 11)
        self.assertEqual(result.category_3_count, 2)
        self.assertEqual(result.total_treatment_count, 14)
        self.assertAlmostEqual(result.rate_of_classified, 2 / 11)
        self.assertAlmostEqual(result.rate_conservative, 2 / 14)

    def test_control_arm_trials_are_excluded_from_the_treatment_only_base_rate(self):
        trials = [
            _trial("c", "control", 1, True, category="3"),
            _trial("c", "treatment", 1, True, category="3"),
        ]
        result = compute_base_rate(trials)
        self.assertEqual(result.total_treatment_count, 1)
        self.assertEqual(result.category_3_count, 1)

    def test_empty_trial_list_returns_zeroed_rates_not_a_division_error(self):
        result = compute_base_rate([])
        self.assertEqual(result.total_treatment_count, 0)
        self.assertEqual(result.rate_of_classified, 0.0)
        self.assertEqual(result.rate_conservative, 0.0)


if __name__ == "__main__":
    unittest.main()
