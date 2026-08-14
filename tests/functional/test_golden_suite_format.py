"""Proves the golden-suite expect.py contract discriminates pass from fail (T410).

Loads tests/golden/_example-scaffold/expect.py's check(case_dir) -> bool function
the same way scripts/scorecard.py (T413) will, and asserts:
  1. it returns a bool
  2. it returns True against the scaffold's as-shipped (correct) fixture
  3. it returns False against a deliberately-broken copy of that fixture
  4. it returns False when the checked file is missing entirely

Without this, expect.py could always return True and nothing would catch that —
this is the mechanical proof required by task T410 acceptance criterion 2.
"""
from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

SCAFFOLD_DIR = repo_root() / "tests" / "golden" / "_example-scaffold"


def _load_check(expect_py: Path):
    spec = importlib.util.spec_from_file_location("scaffold_expect", expect_py)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load expect.py module from {expect_py}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "check"):
        raise AttributeError(f"{expect_py} does not define check(case_dir) -> bool")
    return module.check


class TestGoldenSuiteScaffoldContract(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(SCAFFOLD_DIR.is_dir(), f"scaffold missing: {SCAFFOLD_DIR}")
        for required in ("brief.md", "fixture", "expect.py", "case.yaml"):
            self.assertTrue(
                (SCAFFOLD_DIR / required).exists(),
                f"scaffold missing required member: {required}",
            )
        self.check = _load_check(SCAFFOLD_DIR / "expect.py")

    def test_check_returns_bool(self):
        result = self.check(SCAFFOLD_DIR)
        self.assertIsInstance(result, bool)

    def test_passes_on_correct_fixture(self):
        self.assertTrue(self.check(SCAFFOLD_DIR))

    def test_fails_on_deliberately_broken_fixture(self):
        # Copy the whole case dir so the checked-in scaffold is never mutated.
        with tempfile.TemporaryDirectory() as tmp:
            broken_case = Path(tmp) / "_example-scaffold-broken"
            shutil.copytree(SCAFFOLD_DIR, broken_case)
            status_file = broken_case / "fixture" / "workspace" / "STATUS.md"
            status_file.write_text("# Widget Tracker\n\nStatus: TODO\n", encoding="utf-8")

            check = _load_check(broken_case / "expect.py")
            self.assertFalse(check(broken_case))

    def test_fails_when_status_file_missing_entirely(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken_case = Path(tmp) / "_example-scaffold-missing"
            shutil.copytree(SCAFFOLD_DIR, broken_case)
            (broken_case / "fixture" / "workspace" / "STATUS.md").unlink()

            check = _load_check(broken_case / "expect.py")
            self.assertFalse(check(broken_case))


if __name__ == "__main__":
    unittest.main()
