"""Tests for `implementation/runtime/golden_harness/promotion.py` (T504,
Piece 2) -- the promotion-rule glue code and the `apply_proposal_to_scratch`
helper.

Three required categories per `docs/tasks/task-T504.md`'s "Expected
outputs" #6:

1. `TestEvaluatePromotionThreeConjuncts` -- a real promotion-rule test using
   constructed `TrialRecord`s exercising all three conjuncts independently
   (each one failing alone rejects; all three passing promotes).
2. `TestCheckNoCriticalRegression` -- exercises conjunct 2's own per-case
   mapping directly, including the documented judgment-call override and the
   mismatched-escalation fail-safe case.
3. `TestApplyProposalToScratch` -- a real, behavioral before/after-snapshot
   test proving the helper never writes to the real tracked target file.

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
from implementation.runtime.golden_harness.schema import TrialRecord
from tests._helpers.repo import repo_root


def _trial(case_id, arm, k, result, cause=None) -> TrialRecord:
    return TrialRecord(case_id=case_id, arm=arm, k_index=k, result=result, diagnosed_cause=cause)


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
        control = [_trial("case-a", "control", k, True) for k in (1, 2)]
        treatment = [_trial("case-a", "treatment", k, True) for k in (1, 2)]
        return control, treatment

    def test_all_three_conjuncts_satisfied_promotes(self):
        control, treatment = self._floor_met_trials()
        result = promotion.evaluate_promotion(control, treatment, _no_drift_hash_check())
        self.assertTrue(result.promote)
        self.assertTrue(result.floor_met)
        self.assertTrue(result.no_critical_regression)
        self.assertTrue(result.evaluator_hash_unchanged)
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
