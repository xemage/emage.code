"""Functional tests for v3 telemetry replay tooling."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


class TestV3TelemetryReplay(unittest.TestCase):
    def test_replay_detects_regression_for_sample_fixtures(self):
        script = repo_root() / "v3" / "implementation" / "runtime" / "telemetry" / "replay.py"
        baseline = (
            repo_root()
            / "v3"
            / "implementation"
            / "runtime"
            / "telemetry"
            / "examples"
            / "baseline-run.json"
        )
        candidate = (
            repo_root()
            / "v3"
            / "implementation"
            / "runtime"
            / "telemetry"
            / "examples"
            / "candidate-run.json"
        )

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            proc = subprocess.run(
                [
                    "python3",
                    str(script),
                    "--baseline",
                    str(baseline),
                    "--candidate",
                    str(candidate),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertTrue(out.is_file(), "replay report must be created")
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(report["summary"]["hasRegression"])
            self.assertTrue(report["qualityDeltas"], "quality deltas should be populated")


if __name__ == "__main__":
    unittest.main()
