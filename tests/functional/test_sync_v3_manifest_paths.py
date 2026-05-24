"""Regression tests for v3 sync manifest portability and CLI parsing."""
from __future__ import annotations

import json
import subprocess
import unittest

from tests._helpers.repo import repo_root


class TestSyncV3ManifestPaths(unittest.TestCase):
    def test_generated_manifest_uses_posix_paths_and_parses_root_arg(self):
        proc = subprocess.run(
            [
                "node",
                "v3/implementation/scripts/sync-v3.mjs",
                "--platform",
                "github",
                "--root",
                "v3/implementation",
            ],
            cwd=repo_root(),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

        manifest_path = repo_root() / "v3" / "implementation" / ".github" / ".generated-manifest.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertIn("files", payload)
        self.assertTrue(payload["files"], "manifest file list should not be empty")
        self.assertFalse(
            any("\\\\" in p for p in payload["files"]),
            "manifest paths must use forward slashes",
        )


if __name__ == "__main__":
    unittest.main()
