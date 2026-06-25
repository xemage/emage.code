#!/usr/bin/env python3
"""Unit tests for the SIA harness entrypoint fallback solution writer."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

_HARNESS_PATH = (
    repo_root()
    / "implementation"
    / "adapters"
    / "sia-target"
    / "harness-entrypoint.py"
)


def _load_harness_module():
    spec = importlib.util.spec_from_file_location("sia_harness_entrypoint", _HARNESS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_harness = _load_harness_module()
write_solution_json_from_output = _harness.write_solution_json_from_output

_EVALUATOR_PATH = (
    repo_root()
    / "implementation"
    / "adapters"
    / "sia-target"
    / "tasks"
    / "emage-agent-task-v1"
    / "data"
    / "public"
    / "evaluate.py"
)


class TestHarnessFallbackSolutionWriter(unittest.TestCase):
    def _evaluate_workspace(self, workspace: Path) -> dict:
        proc = subprocess.run(
            ["python3", str(_EVALUATOR_PATH), "--gen-dir", str(workspace)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with (workspace / "results.json").open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_baseline_fallback_scores_lower_than_v1_ft(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            baseline_workspace = Path(tmp_dir) / "baseline"
            finetuned_workspace = Path(tmp_dir) / "finetuned"
            baseline_workspace.mkdir()
            finetuned_workspace.mkdir()

            baseline_result = {
                "generated_code": "```python\nprint('hello baseline')\n```",
                "model": "baseline",
            }
            finetuned_result = {
                "generated_code": "```python\nprint('hello finetuned')\n```",
                "model": "v1-ft",
            }

            baseline_solution = write_solution_json_from_output(
                baseline_result,
                "Plan a project",
                str(baseline_workspace),
            )
            finetuned_solution = write_solution_json_from_output(
                finetuned_result,
                "Plan a project",
                str(finetuned_workspace),
            )

            self.assertIsNotNone(baseline_solution)
            self.assertIsNotNone(finetuned_solution)

            baseline_results = self._evaluate_workspace(baseline_workspace)
            finetuned_results = self._evaluate_workspace(finetuned_workspace)

        self.assertLess(baseline_results["overall_score"], finetuned_results["overall_score"])
        self.assertFalse(baseline_results["passed"])
        self.assertTrue(finetuned_results["passed"])


if __name__ == "__main__":
    unittest.main()
