"""Tests for `implementation/runtime/golden_harness/scoring.py` (T458
Objective #2).

Uses the real, unmodified `tests/golden/open/new-feature-plan-doc-compliant/
expect.py` (read-only, imported exactly as `scripts/scorecard.py` already
does) against synthetic scratch-dir content this test writes itself -- no
live agent session is dispatched anywhere in this file, satisfying
`task-T458.md`'s Expected Output #4 ("using recorded/synthetic trial data --
NOT live agent sessions"). This is also the one integration point that
directly answers `task-T458.md`'s first pre-anticipated blocker case (can
`expect.py`'s contract be pointed at a scratch dir without a protected-path
edit?) -- answered here in the negative (no exception needed), matching
`plan-044`'s Finding 1.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from implementation.runtime.golden_harness.scoring import (
    find_golden_case_dir,
    load_expect_module,
    score_scratch_dir,
)
from implementation.runtime.golden_harness.scratch import create_scratch_case_dir, write_candidate_file
from tests._helpers.repo import repo_root

REAL_CASE_ID = "new-feature-plan-doc-compliant"
REQUIRED_HEADERS_TEXT = (
    "## Objective\n\n## Affected Components\n\n## Task Breakdown\n\n## Dependency Impact\n"
)


def _real_golden_root() -> Path:
    return repo_root() / "tests" / "golden"


class TestFindGoldenCaseDir(unittest.TestCase):
    def test_resolves_a_real_open_case_by_id(self):
        case_dir = find_golden_case_dir(REAL_CASE_ID, _real_golden_root())
        self.assertEqual(case_dir, _real_golden_root() / "open" / REAL_CASE_ID)
        self.assertTrue((case_dir / "expect.py").is_file())

    def test_raises_lookup_error_for_unknown_case_id(self):
        with self.assertRaises(LookupError):
            find_golden_case_dir("does-not-exist-anywhere", _real_golden_root())


class TestLoadExpectModule(unittest.TestCase):
    def test_loads_the_real_module_and_exposes_check(self):
        case_dir = _real_golden_root() / "open" / REAL_CASE_ID
        module = load_expect_module(case_dir)
        self.assertTrue(callable(module.check))

    def test_raises_file_not_found_for_a_dir_without_expect_py(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                load_expect_module(Path(tmp))


class TestScoreScratchDirAgainstRealExpectPy(unittest.TestCase):
    """The one live-mechanism regression check: prove the real
    `new-feature-plan-doc-compliant/expect.py`, loaded via this module,
    returns `True` for compliant synthetic output and `False` for
    non-compliant output -- exactly the two real outcomes T484's live trials
    reported, reproduced here without any live dispatch."""

    def setUp(self):
        self.golden_case_dir = _real_golden_root() / "open" / REAL_CASE_ID
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)

    def test_compliant_synthetic_plan_doc_scores_true(self):
        scratch = create_scratch_case_dir(REAL_CASE_ID, "control", 1, self.base_dir)
        write_candidate_file(scratch, "docs/plans/feature-audit-log.md", REQUIRED_HEADERS_TEXT)
        self.assertTrue(score_scratch_dir(self.golden_case_dir, scratch))

    def test_plan_doc_missing_a_required_header_scores_false(self):
        scratch = create_scratch_case_dir(REAL_CASE_ID, "treatment", 1, self.base_dir)
        incomplete = "## Objective\n\n## Affected Components\n"  # missing Task Breakdown / Dependency Impact
        write_candidate_file(scratch, "docs/plans/feature-audit-log.md", incomplete)
        self.assertFalse(score_scratch_dir(self.golden_case_dir, scratch))

    def test_missing_fixture_output_entirely_scores_false(self):
        scratch = create_scratch_case_dir(REAL_CASE_ID, "control", 2, self.base_dir)
        self.assertFalse(score_scratch_dir(self.golden_case_dir, scratch))


if __name__ == "__main__":
    unittest.main()
