"""Functional tests for Task T222 SIA-style evaluator."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


class TestT222SiaTaskEvaluator(unittest.TestCase):
    def setUp(self) -> None:
        self.task_root = (
            repo_root()
            / "implementation"
            / "adapters"
            / "sia-target"
            / "tasks"
            / "emage-agent-task-v1"
        )
        self.evaluator = self.task_root / "data" / "public" / "evaluate.py"

    def run_evaluator(self, sample_name: str) -> dict:
        submission = self.task_root / "submissions" / sample_name / "solution.json"
        with tempfile.TemporaryDirectory() as temp_dir:
            gen_dir = Path(temp_dir)
            shutil.copyfile(submission, gen_dir / "solution.json")

            proc = subprocess.run(
                ["python3", str(self.evaluator), "--gen-dir", str(gen_dir)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

            results_path = gen_dir / "results.json"
            self.assertTrue(results_path.exists(), "results.json was not written")
            with results_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)

    def test_sample_good_submission_passes(self) -> None:
        results = self.run_evaluator("sample_good")

        self.assertTrue(results["passed"])
        self.assertGreaterEqual(results["overall_score"], 0.9)

    def test_sample_bad_submission_fails_with_lower_score(self) -> None:
        good_results = self.run_evaluator("sample_good")
        bad_results = self.run_evaluator("sample_bad")

        self.assertFalse(bad_results["passed"])
        self.assertLess(bad_results["overall_score"], good_results["overall_score"])

    def test_results_include_required_keys(self) -> None:
        results = self.run_evaluator("sample_good")

        required_keys = {
            "overall_score",
            "primary_metric",
            "metrics",
            "passed",
            "diagnostics",
        }
        self.assertTrue(required_keys.issubset(results.keys()))
        self.assertIsInstance(results["metrics"], dict)
        self.assertIsInstance(results["diagnostics"], list)


if __name__ == "__main__":
    unittest.main()
