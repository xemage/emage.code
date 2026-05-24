"""Regression tests for sync manifest portability behavior."""
from __future__ import annotations

import json
import subprocess
import unittest

from tests._helpers.repo import implementation_root, repo_root


class TestSyncManifestPaths(unittest.TestCase):
    def test_generated_manifest_uses_posix_paths(self):
        proc = subprocess.run(
            ["node", "scripts/sync.mjs", "--platform=github"],
            cwd=implementation_root(),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

        manifest_path = implementation_root() / ".github" / ".generated-manifest.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertIn("files", payload)
        self.assertTrue(payload["files"], "manifest file list should not be empty")
        self.assertFalse(
            any("\\\\" in p for p in payload["files"]),
            "manifest paths must use forward slashes",
        )


if __name__ == "__main__":
    unittest.main()
