"""Functional smoke tests for v3 experimental adapters."""
from __future__ import annotations

import json
import os
import subprocess
import unittest

from tests._helpers.repo import repo_root


class TestV3AdapterSmoke(unittest.TestCase):
    def test_antigravity_smoke_passes_with_flags(self):
        script = repo_root() / "v3" / "implementation" / "adapters" / "smoke.py"
        fixture = repo_root() / "tests" / "fixtures" / "adapters" / "sample-input.json"
        env = os.environ.copy()
        env["V3_EXPERIMENTAL_ADAPTERS"] = "1"
        env["V3_ADAPTER_ANTIGRAVITY"] = "1"

        proc = subprocess.run(
            [
                "python3",
                str(script),
                "--adapter",
                "antigravity",
                "--input",
                str(fixture),
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["adapter"], "antigravity")

    def test_opencode_smoke_passes_with_flags(self):
        script = repo_root() / "v3" / "implementation" / "adapters" / "smoke.py"
        fixture = repo_root() / "tests" / "fixtures" / "adapters" / "sample-input.json"
        env = os.environ.copy()
        env["V3_EXPERIMENTAL_ADAPTERS"] = "1"
        env["V3_ADAPTER_OPENCODE"] = "1"

        proc = subprocess.run(
            [
                "python3",
                str(script),
                "--adapter",
                "opencode",
                "--input",
                str(fixture),
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["adapter"], "opencode")

    def test_smoke_fails_when_flags_are_disabled(self):
        script = repo_root() / "v3" / "implementation" / "adapters" / "smoke.py"
        fixture = repo_root() / "tests" / "fixtures" / "adapters" / "sample-input.json"
        env = os.environ.copy()
        env.pop("V3_EXPERIMENTAL_ADAPTERS", None)
        env.pop("V3_ADAPTER_ANTIGRAVITY", None)

        proc = subprocess.run(
            [
                "python3",
                str(script),
                "--adapter",
                "antigravity",
                "--input",
                str(fixture),
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("adapter_disabled", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
