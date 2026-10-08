"""Tests for `implementation/runtime/golden_harness/scratch.py` (T458
Objective #1). No live agent session is invoked anywhere in this file --
every trial's "candidate output" is synthetic text this test writes itself."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from implementation.runtime.golden_harness.scratch import (
    cleanup_scratch_dir,
    copy_candidate_file,
    create_scratch_case_dir,
    write_candidate_file,
)


class TestCreateScratchCaseDir(unittest.TestCase):
    def test_returns_dir_with_empty_fixture_subdir(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = create_scratch_case_dir("new-feature-plan-doc-compliant", "control", 1, Path(tmp))
            self.assertTrue((case_dir / "fixture").is_dir())
            self.assertEqual(list((case_dir / "fixture").iterdir()), [])

    def test_never_reuses_a_scratch_dir_across_arms_or_k_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            control = create_scratch_case_dir("case-a", "control", 1, base)
            treatment = create_scratch_case_dir("case-a", "treatment", 1, base)
            control_k2 = create_scratch_case_dir("case-a", "control", 2, base)
            self.assertNotEqual(control, treatment)
            self.assertNotEqual(control, control_k2)

    def test_defaults_to_a_fresh_temp_root_when_no_base_dir_given(self):
        case_dir = create_scratch_case_dir("case-b", "treatment", 1)
        try:
            self.assertTrue((case_dir / "fixture").is_dir())
            self.assertNotIn(str(Path.cwd()), str(case_dir))
        finally:
            cleanup_scratch_dir(case_dir)

    def test_is_never_a_git_worktree_or_the_repo_itself(self):
        # Isolation guarantee: the scratch dir is always freshly created under
        # a plain temp root, never overlapping the caller's own repo checkout.
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = create_scratch_case_dir("case-c", "control", 1, Path(tmp))
            self.assertFalse((case_dir / ".git").exists())
            self.assertTrue(str(case_dir).startswith(tmp))


class TestCandidateFileHelpers(unittest.TestCase):
    def test_write_candidate_file_creates_nested_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = create_scratch_case_dir("case-d", "control", 1, Path(tmp))
            written = write_candidate_file(case_dir, "docs/plans/plan-001-x.md", "## Objective\n")
            self.assertEqual(written, case_dir / "fixture" / "docs" / "plans" / "plan-001-x.md")
            self.assertEqual(written.read_text(encoding="utf-8"), "## Objective\n")

    def test_copy_candidate_file_preserves_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "session-output.md"
            source.write_text("## VERDICT\nStatus: PASS\n", encoding="utf-8")
            case_dir = create_scratch_case_dir("case-e", "treatment", 1, base)
            copied = copy_candidate_file(case_dir, "review.md", source)
            self.assertEqual(copied.read_text(encoding="utf-8"), source.read_text(encoding="utf-8"))


class TestCleanupScratchDir(unittest.TestCase):
    def test_removes_the_scratch_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = create_scratch_case_dir("case-f", "control", 1, Path(tmp))
            self.assertTrue(case_dir.exists())
            cleanup_scratch_dir(case_dir)
            self.assertFalse(case_dir.exists())

    def test_is_safe_on_an_already_removed_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = create_scratch_case_dir("case-g", "control", 1, Path(tmp))
            cleanup_scratch_dir(case_dir)
            cleanup_scratch_dir(case_dir)  # must not raise


if __name__ == "__main__":
    unittest.main()
