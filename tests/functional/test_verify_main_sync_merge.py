"""Regression tests for scripts/verify-main-sync-merge.py.

Fixture MR records for MR !103 and MR !109 are the exact GitLab API field values
independently verified in docs/tasks/task-T340.md § Findings §2 (`glab api
projects/em-age%2Femage.code/merge_requests/103` and `/109`, both read-only `GET`). Both MRs
were squashed by GitLab despite an explicit `squash: false` override — this is documented,
already-verified fact from T340, not re-derived here. These fixtures prove the script
correctly FAILS (detects the squash) against both historical incidents.
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from unittest import mock

from tests._helpers.repo import repo_root


def _load_module():
    module_path = repo_root() / "scripts" / "verify-main-sync-merge.py"
    spec = importlib.util.spec_from_file_location("verify_main_sync_merge", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load verify-main-sync-merge module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Exact API field values from docs/tasks/task-T340.md § Findings §2.
MR_103_SQUASHED = {
    "iid": 103,
    "merge_commit_sha": "5d5fd007c7f0065a593dc7014d29ce6608c73d6f",
    "squash_commit_sha": "6b2d680c5499d0e12f1e4c9f910bcfc2984728d6",
    "squash": True,
    "squash_on_merge": True,
    "sha": "1f4fe60a62fa8dc1e8e0dfcfbf1ead98561ac893",
}

MR_109_SQUASHED = {
    "iid": 109,
    "merge_commit_sha": "c14bf7903b8cdaa1e845a57069c7fc5888b64bd9",
    "squash_commit_sha": "25fa98efe5c8c9aea9a72d40b9de651d085a1e7b",
    "squash": True,
    "squash_on_merge": True,
    "sha": "618cd86be649ac22cb5f3df7aa1e2c61e2ea586a",
}

# A hypothetical genuinely non-squashed merge, for the positive/PASS case.
MR_GENUINE_NON_SQUASH = {
    "iid": 999,
    "merge_commit_sha": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
    "squash_commit_sha": None,
    "squash": False,
    "squash_on_merge": False,
    "sha": "cafefeedcafefeedcafefeedcafefeedcafefeed",
}


class TestEvaluateRegressionMR103(unittest.TestCase):
    """MR !103 (T331 incident) — must FAIL the check, reproducing T340's finding."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_mr_103_fails_check(self):
        code, lines = self.mod.evaluate(MR_103_SQUASHED)
        self.assertEqual(code, self.mod._EXIT_SQUASHED)
        self.assertTrue(any("FAIL" in line for line in lines))
        self.assertTrue(any("103" in line for line in lines))


class TestEvaluateRegressionMR109(unittest.TestCase):
    """MR !109 (T339 incident) — must FAIL the check, reproducing T340's finding."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_mr_109_fails_check(self):
        code, lines = self.mod.evaluate(MR_109_SQUASHED)
        self.assertEqual(code, self.mod._EXIT_SQUASHED)
        self.assertTrue(any("FAIL" in line for line in lines))
        self.assertTrue(any("109" in line for line in lines))


class TestEvaluateGenuineNonSquash(unittest.TestCase):
    """A genuinely non-squashed merge must PASS the check."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_genuine_non_squash_passes_check(self):
        code, lines = self.mod.evaluate(MR_GENUINE_NON_SQUASH)
        self.assertEqual(code, self.mod._EXIT_OK)
        self.assertTrue(any("PASS" in line for line in lines))


class TestEvaluateEdgeCases(unittest.TestCase):
    """squash=false alone is not sufficient — squash_commit_sha must also be null."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_squash_false_but_squash_commit_sha_present_still_fails(self):
        mr = dict(MR_GENUINE_NON_SQUASH)
        mr["squash"] = False
        mr["squash_commit_sha"] = "abc123"
        code, _lines = self.mod.evaluate(mr)
        self.assertEqual(code, self.mod._EXIT_SQUASHED)

    def test_squash_true_but_squash_commit_sha_null_still_fails(self):
        mr = dict(MR_GENUINE_NON_SQUASH)
        mr["squash"] = True
        code, _lines = self.mod.evaluate(mr)
        self.assertEqual(code, self.mod._EXIT_SQUASHED)


class TestFetchMrErrorShapes(unittest.TestCase):
    """`glab api` exits 0 even on HTTP errors (e.g. a 404), returning an error body on stdout
    instead of a merge request record. fetch_mr must detect that and error out, not misread it
    as a valid (falsely "squashed") MR record.
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_404_error_body_is_treated_as_lookup_error_not_a_squashed_mr(self):
        with mock.patch.object(
            self.mod, "_run_glab", return_value='{"message":"404 Not found"}'
        ):
            result = self.mod.fetch_mr("999999")
        self.assertIsNone(result)

    def test_valid_mr_record_is_returned_as_is(self):
        with mock.patch.object(
            self.mod, "_run_glab", return_value=json.dumps(MR_GENUINE_NON_SQUASH)
        ):
            result = self.mod.fetch_mr("999")
        self.assertEqual(result, MR_GENUINE_NON_SQUASH)


if __name__ == "__main__":
    unittest.main()
