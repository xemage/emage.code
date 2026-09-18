"""Tests for `implementation/runtime/golden_harness/promotion.py` (T504,
Piece 2; hardened by T510) -- the promotion-rule glue code and the
`apply_proposal_to_scratch` helper.

Categories per `docs/tasks/task-T504.md`'s "Expected outputs" #6, plus
`docs/tasks/task-T510.md`'s hardening additions:

1. `TestEvaluatePromotionThreeConjuncts` -- a real promotion-rule test using
   constructed `TrialRecord`s exercising the original three conjuncts
   independently (each one failing alone rejects; all three passing, with
   the T510 gates also satisfied, promotes).
2. `TestCheckNoCriticalRegression` -- exercises conjunct 2's own per-case
   mapping directly, including the documented judgment-call override and the
   mismatched-escalation fail-safe case.
3. `TestApplyProposalToScratch` -- a real, behavioral before/after-snapshot
   test proving the helper never writes to the real tracked target file.
4. `TestCheckMinimumEvidence` -- T510 Option A, the per-case minimum-evidence
   gate, including the T507-real-numbers regression test and the
   per-case-not-pooled proof test.
5. `TestCheckProvenanceHomogeneity` -- T510 Option C, the shared
   provenance-homogeneity pre-check, including the T507-real-pattern
   regression test.
6. `TestEvaluatePromotionT510EndToEnd` -- both new preconditions combined
   against T507's full real dataset.

No live agent session is invoked anywhere in this file.
"""
from __future__ import annotations

import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path

from implementation.runtime import meta_improver as mi
from implementation.runtime.golden_harness import evaluator_hash as eh
from implementation.runtime.golden_harness import policy, promotion
from implementation.runtime.golden_harness.schema import PROVENANCE_FRESH, PROVENANCE_REUSED, TrialRecord
from tests._helpers.repo import repo_root


def _trial(case_id, arm, k, result, cause=None, provenance=None) -> TrialRecord:
    kwargs = dict(case_id=case_id, arm=arm, k_index=k, result=result, diagnosed_cause=cause)
    if provenance is not None:
        kwargs["provenance"] = provenance
    return TrialRecord(**kwargs)


def _no_drift_hash_check() -> eh.DriftCheckResult:
    return eh.DriftCheckResult(
        tests_golden_drift=False,
        scripts_scorecard_drift=False,
        any_drift=False,
        current_digests={"tests_golden": "a", "scripts_scorecard": "b"},
        known_good_digests={"tests_golden": "a", "scripts_scorecard": "b"},
        known_good_commit="deadbeef",
        known_good_path=Path("/tmp/does-not-matter.json"),
        reason="NO DRIFT: both protected paths match the known-good reference.",
    )


def _drifted_hash_check() -> eh.DriftCheckResult:
    return eh.DriftCheckResult(
        tests_golden_drift=True,
        scripts_scorecard_drift=False,
        any_drift=True,
        current_digests={"tests_golden": "a", "scripts_scorecard": "b"},
        known_good_digests={"tests_golden": "z", "scripts_scorecard": "b"},
        known_good_commit="deadbeef",
        known_good_path=Path("/tmp/does-not-matter.json"),
        reason="DRIFT DETECTED on: tests/golden",
    )


class TestEvaluatePromotionThreeConjuncts(unittest.TestCase):
    """All three conjuncts satisfied -> promote. Each conjunct failing
    alone (the other two held satisfied) -> reject, with that conjunct's
    failure reflected in both the structured result and the reason string."""

    def _floor_met_trials(self):
        # T510 note: bumped from k=(1,2) to k=(1,2,3) with an explicit,
        # homogeneous "fresh" provenance on every trial. This is the one
        # pre-existing fixture in this file that genuinely needed updating:
        # the new minimum-evidence gate (Option A) requires both arms to
        # reach policy.MIN_ESCALATED_K=3, and the new provenance-homogeneity
        # gate (Option C) fails closed on the schema default ("unknown")
        # that every other pre-existing trial in this file still uses. Every
        # test below that reuses this helper only asserts fields/reason
        # substrings unaffected by these two new gates *except*
        # `test_all_three_conjuncts_satisfied_promotes`, which requires
        # promote=True and so requires both new gates to actually pass.
        control = [_trial("case-a", "control", k, True, provenance=PROVENANCE_FRESH) for k in (1, 2, 3)]
        treatment = [_trial("case-a", "treatment", k, True, provenance=PROVENANCE_FRESH) for k in (1, 2, 3)]
        return control, treatment

    def test_all_three_conjuncts_satisfied_promotes(self):
        control, treatment = self._floor_met_trials()
        result = promotion.evaluate_promotion(control, treatment, _no_drift_hash_check())
        self.assertTrue(result.promote)
        self.assertTrue(result.floor_met)
        self.assertTrue(result.no_critical_regression)
        self.assertTrue(result.evaluator_hash_unchanged)
        self.assertTrue(result.minimum_evidence_met)
        self.assertTrue(result.provenance_homogeneous)
        self.assertEqual(result.insufficient_evidence_case_ids, ())
        self.assertEqual(result.provenance_mismatched_case_ids, ())
        self.assertTrue(result.reason.startswith("PROMOTE"))

    def test_floor_not_met_alone_rejects(self):
        control = [_trial("case-a", "control", k, True) for k in (1, 2)]
        treatment = [_trial("case-a", "treatment", 1, True), _trial("case-a", "treatment", 2, False)]
        result = promotion.evaluate_promotion(control, treatment, _no_drift_hash_check())
        self.assertFalse(result.promote)
        self.assertFalse(result.floor_met)
        self.assertTrue(result.no_critical_regression)
        self.assertTrue(result.evaluator_hash_unchanged)
        self.assertIn("floor not met", result.reason)

    def test_critical_regression_alone_rejects(self):
        # case-a: escalated (k=3 both arms), floor missed at the case level,
        # same cause recurring >=2 times -> CONFIRMED_PERSISTENT_EFFECT, no
        # override supplied. case-b: a compensating, strongly-overperforming
        # escalated case (own floor met -> CONFIRMED_COIN_FLIP, not a
        # regression) added so the *aggregate* floor across all trials is
        # still met -- isolating conjunct 2's failure from conjunct 1's.
        control = [_trial("case-a", "control", k, True) for k in (1, 2, 3)] + [
            _trial("case-b", "control", k, False) for k in (1, 2, 3)
        ]
        treatment = [
            _trial("case-a", "treatment", 1, False, cause="checker-bug"),
            _trial("case-a", "treatment", 2, False, cause="checker-bug"),
            _trial("case-a", "treatment", 3, True),
        ] + [_trial("case-b", "treatment", k, True) for k in (1, 2, 3)]

        # Confirm the aggregate floor really is met despite case-a's own
        # per-case regression, so this test genuinely isolates conjunct 2.
        self.assertTrue(policy.floor_met(control, treatment))

        result = promotion.evaluate_promotion(control, treatment, _no_drift_hash_check())
        self.assertFalse(result.promote)
        self.assertTrue(result.floor_met)
        self.assertFalse(result.no_critical_regression)
        self.assertEqual(result.confirmed_regression_case_ids, ("case-a",))
        self.assertTrue(result.evaluator_hash_unchanged)
        self.assertIn("critical regression confirmed", result.reason)

    def test_evaluator_hash_drift_alone_rejects(self):
        control, treatment = self._floor_met_trials()
        result = promotion.evaluate_promotion(control, treatment, _drifted_hash_check())
        self.assertFalse(result.promote)
        self.assertTrue(result.floor_met)
        self.assertTrue(result.no_critical_regression)
        self.assertFalse(result.evaluator_hash_unchanged)
        self.assertIn("evaluator hash drifted", result.reason)

    def test_multiple_failing_conjuncts_are_all_reported(self):
        control = [_trial("case-a", "control", k, True) for k in (1, 2)]
        treatment = [_trial("case-a", "treatment", k, False) for k in (1, 2)]
        result = promotion.evaluate_promotion(control, treatment, _drifted_hash_check())
        self.assertFalse(result.promote)
        self.assertFalse(result.floor_met)
        self.assertFalse(result.evaluator_hash_unchanged)
        self.assertIn("floor not met", result.reason)
        self.assertIn("evaluator hash drifted", result.reason)

    def test_control_treatment_inputs_are_plain_trial_record_lists(self):
        # No live-dispatch call embedded: evaluate_promotion accepts plain
        # lists constructed directly, with no dispatch of any kind.
        control, treatment = self._floor_met_trials()
        self.assertIsInstance(control, list)
        self.assertTrue(all(isinstance(t, TrialRecord) for t in control))
        promotion.evaluate_promotion(control, treatment, _no_drift_hash_check())  # must not raise


class TestCheckNoCriticalRegression(unittest.TestCase):
    """Conjunct 2's own per-case mapping, exercised directly."""

    def test_never_escalated_case_is_vacuously_satisfied(self):
        # Only k=1 on both arms -- never reaches MIN_ESCALATED_K.
        control = [_trial("case-a", "control", 1, True)]
        treatment = [_trial("case-a", "treatment", 1, False, cause="x")]
        result = promotion.check_no_critical_regression(control, treatment)
        self.assertTrue(result.no_critical_regression)
        self.assertEqual(result.confirmed_regression_case_ids, ())
        self.assertEqual(result.mismatched_escalation_case_ids, ())
        self.assertEqual(result.classified_case_ids, ())

    def test_escalated_confirmed_coin_flip_does_not_count_as_regression(self):
        # Floor met at k=3 -> classify_k_plus_outcome returns
        # CONFIRMED_COIN_FLIP, not CONFIRMED_PERSISTENT_EFFECT.
        control = [_trial("case-a", "control", k, True) for k in (1, 2, 3)]
        treatment = [_trial("case-a", "treatment", k, True) for k in (1, 2, 3)]
        result = promotion.check_no_critical_regression(control, treatment)
        self.assertTrue(result.no_critical_regression)
        self.assertEqual(result.classified_case_ids, ("case-a",))

    def test_escalated_confirmed_persistent_effect_counts_as_regression_by_default(self):
        control = [_trial("case-a", "control", k, True) for k in (1, 2, 3)]
        treatment = [
            _trial("case-a", "treatment", 1, False, cause="checker-bug"),
            _trial("case-a", "treatment", 2, False, cause="checker-bug"),
            _trial("case-a", "treatment", 3, True),
        ]
        result = promotion.check_no_critical_regression(control, treatment)
        self.assertFalse(result.no_critical_regression)
        self.assertEqual(result.confirmed_regression_case_ids, ("case-a",))

    def test_known_arm_agnostic_override_excuses_the_case(self):
        # Same fixture as above, but the caller supplies an explicit,
        # human-attested override naming this case as arm-agnostic
        # checker-brittleness, not a real regression.
        control = [_trial("case-a", "control", k, True) for k in (1, 2, 3)]
        treatment = [
            _trial("case-a", "treatment", 1, False, cause="checker-bug"),
            _trial("case-a", "treatment", 2, False, cause="checker-bug"),
            _trial("case-a", "treatment", 3, True),
        ]
        result = promotion.check_no_critical_regression(
            control, treatment, known_arm_agnostic_case_ids=frozenset({"case-a"})
        )
        self.assertTrue(result.no_critical_regression)
        self.assertEqual(result.confirmed_regression_case_ids, ())
        # The override does not hide that the case was classified -- it's
        # still visible in classified_case_ids for audit purposes.
        self.assertEqual(result.classified_case_ids, ("case-a",))

    def test_mismatched_escalation_is_fail_safe_not_vacuous(self):
        # control reaches k=3 (escalated); treatment stays at k=1 -- a real,
        # anomalous edge case classify_k_plus_outcome() cannot handle
        # (would raise ValueError on mismatched per-arm counts). Must not
        # be silently treated as vacuously satisfied.
        control = [_trial("case-a", "control", k, True) for k in (1, 2, 3)]
        treatment = [_trial("case-a", "treatment", 1, True)]
        result = promotion.check_no_critical_regression(control, treatment)
        self.assertFalse(result.no_critical_regression)
        self.assertEqual(result.mismatched_escalation_case_ids, ("case-a",))
        self.assertEqual(result.confirmed_regression_case_ids, ())
        self.assertEqual(result.classified_case_ids, ())

    def test_mismatched_escalation_does_not_raise(self):
        # classify_k_plus_outcome itself would raise on this input --
        # check_no_critical_regression must never call it in this shape.
        control = [_trial("case-a", "control", k, True) for k in (1, 2, 3)]
        treatment = [_trial("case-a", "treatment", 1, True)]
        promotion.check_no_critical_regression(control, treatment)  # must not raise

    def test_multiple_cases_evaluated_independently(self):
        control = (
            [_trial("case-ok", "control", k, True) for k in (1, 2, 3)]
            + [_trial("case-bad", "control", k, True) for k in (1, 2, 3)]
        )
        treatment = (
            [_trial("case-ok", "treatment", k, True) for k in (1, 2, 3)]
            + [
                _trial("case-bad", "treatment", 1, False, cause="c"),
                _trial("case-bad", "treatment", 2, False, cause="c"),
                _trial("case-bad", "treatment", 3, True),
            ]
        )
        result = promotion.check_no_critical_regression(control, treatment)
        self.assertFalse(result.no_critical_regression)
        self.assertEqual(result.confirmed_regression_case_ids, ("case-bad",))
        self.assertEqual(set(result.classified_case_ids), {"case-ok", "case-bad"})


# ---------------------------------------------------------------------------
# T510 (T509 design, Options A + C): promotion hardening
# ---------------------------------------------------------------------------

# T507's real 3 cases (`t507-closed-loop-cycle-v1.md` §3.3): the two open
# golden-suite cases plus the aliased held-out case actually used
# (`HO-2` -- `HO-1` was substituted out per §3.4's disclosed structural
# exclusion, unrelated to this task).
_T507_CASE_CODE_REVIEW = "code-review-conditional-pass-conditions-gap"
_T507_CASE_PREPARE_RELEASE = "prepare-release-conditional-pass-conditions-gap"
_T507_CASE_HELD_OUT = "HO-2"


def _t507_real_trials(*, with_provenance: bool):
    """T507's real, disclosed trial data (`t507-closed-loop-cycle-v1.md`
    §3.3's table), transcribed as literal `TrialRecord`s -- not paraphrased,
    not synthetic. All three cases are k=1 per arm (no case ever escalated).

    §3.3 / §2 step 3's real reuse-vs-fresh disclosure: the two open cases'
    **control** trials are reused from `baseline-v6.17.0-retrieval.md`
    (unaffected by T498's checker fix); every other trial (both open cases'
    treatment, and both of HO-2's arms) is a fresh live dispatch from that
    same session. When `with_provenance` is False, no `provenance` is set on
    any trial (schema default "unknown"), isolating the evidence gate alone.
    """
    def control(case_id, result, provenance):
        return _trial(case_id, "control", 1, result, provenance=provenance if with_provenance else None)

    def treatment(case_id, result, provenance):
        return _trial(case_id, "treatment", 1, result, provenance=provenance if with_provenance else None)

    control_trials = [
        control(_T507_CASE_CODE_REVIEW, True, PROVENANCE_REUSED),
        control(_T507_CASE_PREPARE_RELEASE, False, PROVENANCE_REUSED),
        control(_T507_CASE_HELD_OUT, True, PROVENANCE_FRESH),
    ]
    treatment_trials = [
        treatment(_T507_CASE_CODE_REVIEW, True, PROVENANCE_FRESH),
        treatment(_T507_CASE_PREPARE_RELEASE, True, PROVENANCE_FRESH),
        treatment(_T507_CASE_HELD_OUT, True, PROVENANCE_FRESH),
    ]
    return control_trials, treatment_trials


class TestCheckMinimumEvidence(unittest.TestCase):
    """T510 Option A: the per-case minimum-evidence gate."""

    def test_t507_real_numbers_are_insufficient_evidence_on_every_case(self):
        # `t507-closed-loop-cycle-v1.md` §3.3: 3 cases, k=1 per arm each --
        # control pooled [True, False, True] (2/3), treatment pooled
        # [True, True, True] (3/3). Reconstructed exactly, provenance
        # deliberately unset here to isolate the evidence gate alone.
        control, treatment = _t507_real_trials(with_provenance=False)
        self.assertEqual([t.result for t in control], [True, False, True])
        self.assertEqual([t.result for t in treatment], [True, True, True])

        result = promotion.check_minimum_evidence(control, treatment)
        self.assertFalse(result.sufficient)
        # Sorted case-id order (matching check_minimum_evidence's own
        # `sorted(by_case)` iteration): "HO-2" sorts before the two
        # lowercase-leading case ids under plain ASCII/str ordering.
        self.assertEqual(
            result.insufficient_evidence_case_ids,
            (_T507_CASE_HELD_OUT, _T507_CASE_CODE_REVIEW, _T507_CASE_PREPARE_RELEASE),
        )

    def test_t507_real_numbers_reject_promotion_via_evaluate_promotion(self):
        # The brief's item 8: assert evaluate_promotion() itself now returns
        # promote=False with a reason naming the insufficient-evidence
        # cases, not just the standalone check function.
        control, treatment = _t507_real_trials(with_provenance=False)
        result = promotion.evaluate_promotion(control, treatment, _no_drift_hash_check())
        self.assertFalse(result.promote)
        self.assertFalse(result.minimum_evidence_met)
        self.assertEqual(
            set(result.insufficient_evidence_case_ids),
            {_T507_CASE_CODE_REVIEW, _T507_CASE_PREPARE_RELEASE, _T507_CASE_HELD_OUT},
        )
        self.assertIn("insufficient evidence", result.reason)
        for case_id in (_T507_CASE_CODE_REVIEW, _T507_CASE_PREPARE_RELEASE, _T507_CASE_HELD_OUT):
            self.assertIn(case_id, result.reason)

    def test_gate_is_per_case_not_a_pooled_trial_count(self):
        # Directly encodes the design's §1.2 finding: a synthetic case set
        # with exactly 3 pooled trials per arm, spread across 3 *different*
        # cases at k=1 each, satisfies a naive `len(trials) >=
        # MIN_ESCALATED_K` pooled check -- but every individual case has
        # zero replication, so the real, per-case gate must still report
        # sufficient=False. A future refactor that silently regresses to
        # the pooled form would fail this test.
        control = [
            _trial("synth-case-1", "control", 1, True),
            _trial("synth-case-2", "control", 1, True),
            _trial("synth-case-3", "control", 1, False),
        ]
        treatment = [
            _trial("synth-case-1", "treatment", 1, True),
            _trial("synth-case-2", "treatment", 1, True),
            _trial("synth-case-3", "treatment", 1, True),
        ]
        # The naive, pooled-count implementation this test guards against:
        self.assertEqual(len(control), policy.MIN_ESCALATED_K)
        self.assertEqual(len(treatment), policy.MIN_ESCALATED_K)
        self.assertTrue(len(control) >= policy.MIN_ESCALATED_K and len(treatment) >= policy.MIN_ESCALATED_K)

        result = promotion.check_minimum_evidence(control, treatment)
        self.assertFalse(result.sufficient)
        self.assertEqual(
            result.insufficient_evidence_case_ids, ("synth-case-1", "synth-case-2", "synth-case-3")
        )

    def test_case_with_both_arms_at_min_k_is_sufficient(self):
        control = [_trial("case-a", "control", k, True) for k in (1, 2, 3)]
        treatment = [_trial("case-a", "treatment", k, True) for k in (1, 2, 3)]
        result = promotion.check_minimum_evidence(control, treatment)
        self.assertTrue(result.sufficient)
        self.assertEqual(result.insufficient_evidence_case_ids, ())

    def test_case_with_only_one_arm_at_min_k_is_insufficient(self):
        control = [_trial("case-a", "control", k, True) for k in (1, 2, 3)]
        treatment = [_trial("case-a", "treatment", 1, True)]
        result = promotion.check_minimum_evidence(control, treatment)
        self.assertFalse(result.sufficient)
        self.assertEqual(result.insufficient_evidence_case_ids, ("case-a",))

    def test_multiple_cases_mixed_sufficiency_reported_independently(self):
        control = (
            [_trial("case-ok", "control", k, True) for k in (1, 2, 3)]
            + [_trial("case-thin", "control", 1, True)]
        )
        treatment = (
            [_trial("case-ok", "treatment", k, True) for k in (1, 2, 3)]
            + [_trial("case-thin", "treatment", 1, True)]
        )
        result = promotion.check_minimum_evidence(control, treatment)
        self.assertFalse(result.sufficient)
        self.assertEqual(result.insufficient_evidence_case_ids, ("case-thin",))


class TestCheckProvenanceHomogeneity(unittest.TestCase):
    """T510 Option C: the shared provenance-homogeneity pre-check."""

    def test_t507_real_provenance_pattern_flags_exactly_the_two_mixed_cases(self):
        # `t507-closed-loop-cycle-v1.md` §3.3 / §2 step 3: the two open
        # cases (code-review, prepare-release) mix reused control / fresh
        # treatment; the held-out case (HO-2) is fresh/fresh throughout.
        control, treatment = _t507_real_trials(with_provenance=True)
        result = promotion.check_provenance_homogeneity(control, treatment)
        self.assertFalse(result.homogeneous)
        self.assertEqual(
            result.mismatched_case_ids, (_T507_CASE_CODE_REVIEW, _T507_CASE_PREPARE_RELEASE)
        )
        self.assertNotIn(_T507_CASE_HELD_OUT, result.mismatched_case_ids)

    def test_uniform_known_provenance_across_arms_is_homogeneous(self):
        control = [_trial("case-a", "control", 1, True, provenance=PROVENANCE_FRESH)]
        treatment = [_trial("case-a", "treatment", 1, True, provenance=PROVENANCE_FRESH)]
        result = promotion.check_provenance_homogeneity(control, treatment)
        self.assertTrue(result.homogeneous)
        self.assertEqual(result.mismatched_case_ids, ())

    def test_uniform_reused_provenance_across_arms_is_also_homogeneous(self):
        control = [_trial("case-a", "control", 1, True, provenance=PROVENANCE_REUSED)]
        treatment = [_trial("case-a", "treatment", 1, True, provenance=PROVENANCE_REUSED)]
        result = promotion.check_provenance_homogeneity(control, treatment)
        self.assertTrue(result.homogeneous)

    def test_unset_provenance_fails_closed_as_unknown(self):
        # Neither trial sets provenance -- the schema default "unknown"
        # applies to both. Fail-closed: "unknown" is never compatible, even
        # when both arms agree on it.
        control = [_trial("case-a", "control", 1, True)]
        treatment = [_trial("case-a", "treatment", 1, True)]
        result = promotion.check_provenance_homogeneity(control, treatment)
        self.assertFalse(result.homogeneous)
        self.assertEqual(result.mismatched_case_ids, ("case-a",))

    def test_known_compatible_override_excuses_the_case(self):
        control, treatment = _t507_real_trials(with_provenance=True)
        result = promotion.check_provenance_homogeneity(
            control,
            treatment,
            known_compatible_provenance_case_ids=frozenset(
                {_T507_CASE_CODE_REVIEW, _T507_CASE_PREPARE_RELEASE}
            ),
        )
        self.assertTrue(result.homogeneous)
        self.assertEqual(result.mismatched_case_ids, ())

    def test_override_is_per_case_not_global(self):
        control, treatment = _t507_real_trials(with_provenance=True)
        result = promotion.check_provenance_homogeneity(
            control, treatment, known_compatible_provenance_case_ids=frozenset({_T507_CASE_CODE_REVIEW})
        )
        self.assertFalse(result.homogeneous)
        self.assertEqual(result.mismatched_case_ids, (_T507_CASE_PREPARE_RELEASE,))


class TestEvaluatePromotionT510EndToEnd(unittest.TestCase):
    """The brief's item 11: both new preconditions combined against T507's
    full real dataset, literal `TrialRecord` fixtures, confirming
    `evaluate_promotion()` now returns `promote=False` with both the
    insufficient-evidence and provenance-mismatch reasons present."""

    def test_t507_full_real_dataset_now_rejects_on_both_new_gates(self):
        control, treatment = _t507_real_trials(with_provenance=True)

        # Sanity check this really is T507's real, reported aggregate
        # (`t507-closed-loop-cycle-v1.md` §3.6: "control 2/3 (66.7%),
        # treatment 3/3 (100%)") before asserting the hardened outcome.
        self.assertAlmostEqual(policy.pass_rate(control), 2 / 3)
        self.assertAlmostEqual(policy.pass_rate(treatment), 1.0)
        self.assertTrue(policy.floor_met(control, treatment))

        result = promotion.evaluate_promotion(control, treatment, _no_drift_hash_check())

        self.assertFalse(result.promote)
        # The original three conjuncts are exactly as T507 actually reported
        # them (§3.6) -- this hardening does not change their own logic.
        self.assertTrue(result.floor_met)
        self.assertTrue(result.no_critical_regression)
        self.assertTrue(result.evaluator_hash_unchanged)
        # The two new T510 gates are what now block this real promotion.
        self.assertFalse(result.minimum_evidence_met)
        self.assertFalse(result.provenance_homogeneous)
        self.assertEqual(
            set(result.insufficient_evidence_case_ids),
            {_T507_CASE_CODE_REVIEW, _T507_CASE_PREPARE_RELEASE, _T507_CASE_HELD_OUT},
        )
        self.assertEqual(
            result.provenance_mismatched_case_ids, (_T507_CASE_CODE_REVIEW, _T507_CASE_PREPARE_RELEASE)
        )
        self.assertIn("insufficient evidence", result.reason)
        self.assertIn("provenance mismatch", result.reason)
        self.assertTrue(result.reason.startswith("REJECT"))


class TestApplyProposalToScratch(unittest.TestCase):
    """Real, behavioral before/after-snapshot proof that the helper never
    writes to the real tracked target file -- mirrors
    `test_meta_improver.py`'s before/after snapshot pattern."""

    def _make_proposal(self, target_path: str) -> mi.DiffProposal:
        return mi.DiffProposal(
            target_path=target_path,
            rationale="test proposal",
            base_content="original content\n",
            proposed_content="original content\nPROPOSED ADDITION\n",
            based_on=("some-case",),
            cluster_cause="c",
            cluster_behavior="b",
            cluster_mechanism="m",
        )

    def test_writes_proposed_content_into_scratch_root(self):
        proposal = self._make_proposal("implementation/knowledge/instructions/example.md")
        with tempfile.TemporaryDirectory() as tmp:
            scratch_root = Path(tmp)
            written = promotion.apply_proposal_to_scratch(proposal, scratch_root)
            self.assertEqual(
                written, scratch_root / "implementation" / "knowledge" / "instructions" / "example.md"
            )
            self.assertEqual(written.read_text(encoding="utf-8"), proposal.proposed_content)

    def test_real_tracked_target_file_is_byte_identical_before_and_after(self):
        # Target a real file that actually exists in this repo's tracked
        # tree, snapshot it, apply the proposal to an isolated scratch
        # root, and confirm the real file's bytes never changed.
        root = repo_root()
        real_target = root / "implementation" / "knowledge" / "instructions"
        real_files = sorted(p for p in real_target.glob("*.md"))
        self.assertTrue(real_files, "expected at least one real instruction file to snapshot")
        sample = real_files[0]
        relative_path = sample.relative_to(root).as_posix()

        before_bytes = sample.read_bytes()
        before_hash = hashlib.sha256(before_bytes).hexdigest()

        proposal = self._make_proposal(relative_path)
        with tempfile.TemporaryDirectory() as tmp:
            written = promotion.apply_proposal_to_scratch(proposal, Path(tmp))
            # The scratch copy really did receive the proposed content...
            self.assertEqual(written.read_text(encoding="utf-8"), proposal.proposed_content)
            # ...but the real tracked file is untouched.
            after_bytes = sample.read_bytes()
            after_hash = hashlib.sha256(after_bytes).hexdigest()
            self.assertEqual(before_bytes, after_bytes)
            self.assertEqual(before_hash, after_hash)
            self.assertNotEqual(written.resolve(), sample.resolve())

    def test_rejects_repo_root_itself_as_scratch_root(self):
        proposal = self._make_proposal("implementation/knowledge/instructions/example.md")
        with self.assertRaises(ValueError):
            promotion.apply_proposal_to_scratch(proposal, promotion.REPO_ROOT)

    def test_rejects_a_path_under_repo_root_as_scratch_root(self):
        proposal = self._make_proposal("implementation/knowledge/instructions/example.md")
        with self.assertRaises(ValueError):
            promotion.apply_proposal_to_scratch(proposal, promotion.REPO_ROOT / "tmp" / "not-real-scratch")

    def test_is_never_a_git_worktree(self):
        proposal = self._make_proposal("implementation/knowledge/instructions/example.md")
        with tempfile.TemporaryDirectory() as tmp:
            scratch_root = Path(tmp)
            promotion.apply_proposal_to_scratch(proposal, scratch_root)
            self.assertFalse((scratch_root / ".git").exists())


if __name__ == "__main__":
    unittest.main()
