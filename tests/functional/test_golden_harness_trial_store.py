"""Tests for `implementation/runtime/golden_harness/trial_store.py` (T458
Objective #3). All data here is synthetic/recorded -- no live agent session
is invoked."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from implementation.runtime.golden_harness.schema import TrialRecord, validate_trial_record
from implementation.runtime.golden_harness.trial_store import (
    append_trial,
    load_trials,
    next_k_index,
    trials_for_case,
)


class TestTrialRecordSchema(unittest.TestCase):
    def test_trial_id_is_deterministic_per_case_arm_k(self):
        record = TrialRecord(case_id="case-a", arm="control", k_index=2, result=True)
        self.assertEqual(record.trial_id(), "case-a:control:2")

    def test_round_trips_through_to_dict_from_dict(self):
        record = TrialRecord(
            case_id="security-audit-coverage-consistency", arm="treatment", k_index=4,
            result=False, category=None, diagnosed_cause="matrix_self_consistency_slip",
            command="/security-audit", recorded_at="2026-09-16T00:00:00Z",
        )
        restored = TrialRecord.from_dict(record.to_dict())
        self.assertEqual(record, restored)

    def test_validate_rejects_bad_arm_and_bad_k_index(self):
        record = TrialRecord(case_id="case-a", arm="both", k_index=0, result=True)
        errors = validate_trial_record(record)
        self.assertTrue(any("arm" in e for e in errors))
        self.assertTrue(any("k_index" in e for e in errors))

    def test_validate_rejects_unknown_category(self):
        record = TrialRecord(case_id="case-a", arm="treatment", k_index=1, result=True, category="9")
        errors = validate_trial_record(record)
        self.assertTrue(any("category" in e for e in errors))

    def test_validate_accepts_a_well_formed_record(self):
        record = TrialRecord(case_id="case-a", arm="control", k_index=1, result=True)
        self.assertEqual(validate_trial_record(record), [])

    def test_provenance_defaults_to_unknown_on_construction(self):
        record = TrialRecord(case_id="case-a", arm="control", k_index=1, result=True)
        self.assertEqual(record.provenance, "unknown")
        self.assertEqual(validate_trial_record(record), [])

    def test_from_dict_defaults_provenance_to_unknown_when_key_absent(self):
        # T510 backward-compatibility hard requirement: every already-
        # persisted TrialRecord predates the `provenance` field entirely --
        # its serialized dict simply has no "provenance" key at all. Must
        # deserialize without error, and must not be silently mis-tagged as
        # "fresh" or "reused".
        legacy_dict = {
            "trial_id": "case-a:control:1",
            "case_id": "case-a",
            "arm": "control",
            "k_index": 1,
            "result": True,
            "category": None,
            "diagnosed_cause": None,
            "command": None,
            "recorded_at": "2026-01-01T00:00:00Z",
        }
        self.assertNotIn("provenance", legacy_dict)
        restored = TrialRecord.from_dict(legacy_dict)
        self.assertEqual(restored.provenance, "unknown")

    def test_from_dict_defaults_provenance_to_unknown_when_value_is_none(self):
        legacy_dict = {
            "case_id": "case-a", "arm": "control", "k_index": 1, "result": True, "provenance": None,
        }
        restored = TrialRecord.from_dict(legacy_dict)
        self.assertEqual(restored.provenance, "unknown")

    def test_round_trips_a_record_with_explicit_provenance(self):
        record = TrialRecord(
            case_id="case-a", arm="treatment", k_index=1, result=True,
            provenance="fresh", recorded_at="2026-09-19T00:00:00Z",
        )
        restored = TrialRecord.from_dict(record.to_dict())
        self.assertEqual(record, restored)
        self.assertEqual(restored.provenance, "fresh")

    def test_validate_rejects_unknown_provenance_value(self):
        record = TrialRecord(case_id="case-a", arm="control", k_index=1, result=True, provenance="stale")
        errors = validate_trial_record(record)
        self.assertTrue(any("provenance" in e for e in errors))


class TestTrialStore(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store_path = Path(self._tmp.name) / "trials" / "case-a.jsonl"

    def test_load_trials_on_nonexistent_store_returns_empty_list(self):
        self.assertEqual(load_trials(self.store_path), [])

    def test_append_then_load_round_trips(self):
        record = TrialRecord(case_id="case-a", arm="control", k_index=1, result=True)
        append_trial(self.store_path, record)
        loaded = load_trials(self.store_path)
        self.assertEqual(loaded, [record])

    def test_append_is_additive_across_multiple_calls(self):
        append_trial(self.store_path, TrialRecord(case_id="case-a", arm="control", k_index=1, result=True))
        append_trial(self.store_path, TrialRecord(case_id="case-a", arm="treatment", k_index=1, result=False))
        loaded = load_trials(self.store_path)
        self.assertEqual(len(loaded), 2)

    def test_trials_for_case_filters_and_sorts_by_k_index(self):
        for k in (3, 1, 2):
            append_trial(self.store_path, TrialRecord(case_id="case-a", arm="control", k_index=k, result=True))
        append_trial(self.store_path, TrialRecord(case_id="case-b", arm="control", k_index=1, result=True))
        loaded = load_trials(self.store_path)
        filtered = trials_for_case(loaded, "case-a", "control")
        self.assertEqual([t.k_index for t in filtered], [1, 2, 3])

    def test_next_k_index_starts_at_one_and_increments(self):
        loaded: list[TrialRecord] = []
        self.assertEqual(next_k_index(loaded, "case-a", "control"), 1)
        loaded.append(TrialRecord(case_id="case-a", arm="control", k_index=1, result=True))
        self.assertEqual(next_k_index(loaded, "case-a", "control"), 2)

    def test_next_k_index_is_independent_per_arm(self):
        loaded = [TrialRecord(case_id="case-a", arm="control", k_index=1, result=True)]
        self.assertEqual(next_k_index(loaded, "case-a", "treatment"), 1)


if __name__ == "__main__":
    unittest.main()
