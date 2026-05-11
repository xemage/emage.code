"""Sync engine timing budgets.

These guard against accidental performance regressions in scripts/sync.mjs and
scripts/verify.mjs. Budgets live in tests/_baselines/sync-timings.json so they
can be intentionally raised with justification in the MR description.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import time
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root, repo_root


def _baselines() -> dict:
    return json.loads((repo_root() / "tests" / "_baselines" / "sync-timings.json").read_text())


class TestSyncPerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("node"):
            raise unittest.SkipTest("node not available on PATH")
        cls.budgets = _baselines()

    def test_verify_within_budget(self):
        budget = self.budgets["verify_max_seconds"]
        t0 = time.monotonic()
        proc = subprocess.run(
            ["node", "scripts/verify.mjs"],
            cwd=implementation_root(), capture_output=True, text=True,
        )
        elapsed = time.monotonic() - t0
        self.assertEqual(proc.returncode, 0, f"verify.mjs failed:\n{proc.stdout}\n{proc.stderr}")
        self.assertLess(
            elapsed, budget,
            msg=(
                f"verify.mjs took {elapsed:.2f}s, budget is {budget:.2f}s. "
                "Either optimise the script or raise the budget in "
                "tests/_baselines/sync-timings.json (with justification)."
            ),
        )

    def test_sync_within_budget(self):
        """Run sync in a temp copy so we don't dirty the working tree."""
        budget = self.budgets["sync_max_seconds"]
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "impl"
            shutil.copytree(implementation_root(), tmp_path, symlinks=False)
            t0 = time.monotonic()
            proc = subprocess.run(
                ["node", "scripts/sync.mjs"],
                cwd=tmp_path, capture_output=True, text=True,
            )
            elapsed = time.monotonic() - t0
            self.assertEqual(proc.returncode, 0, f"sync.mjs failed:\n{proc.stdout}\n{proc.stderr}")
            self.assertLess(
                elapsed, budget,
                msg=(
                    f"sync.mjs took {elapsed:.2f}s, budget is {budget:.2f}s. "
                    "Either optimise the script or raise the budget in "
                    "tests/_baselines/sync-timings.json (with justification)."
                ),
            )


if __name__ == "__main__":
    unittest.main()
