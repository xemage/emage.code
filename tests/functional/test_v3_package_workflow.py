"""Functional tests for v3 package install/update/uninstall workflow."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


class TestV3PackageWorkflow(unittest.TestCase):
    def test_local_install_update_uninstall_flow(self):
        script = repo_root() / "v3" / "implementation" / "scripts" / "package-v3.py"
        schema = repo_root() / "v3" / "implementation" / "registry" / "package.schema.json"
        fixture = repo_root() / "tests" / "fixtures" / "packs" / "sample-pack"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "impl"
            (root / "registry").mkdir(parents=True)
            (root / "packs" / "installed").mkdir(parents=True)
            (root / "registry" / "package.schema.json").write_text(
                schema.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            install = subprocess.run(
                [
                    "python3",
                    str(script),
                    "install",
                    "--root",
                    str(root),
                    "--source",
                    str(fixture),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            index_path = root / "packs" / "installed" / "index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(len(index["packages"]), 1)
            self.assertEqual(index["packages"][0]["packId"], "sample-core-pack")

            update = subprocess.run(
                [
                    "python3",
                    str(script),
                    "update",
                    "--root",
                    str(root),
                    "--pack-id",
                    "sample-core-pack",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)

            uninstall = subprocess.run(
                [
                    "python3",
                    str(script),
                    "uninstall",
                    "--root",
                    str(root),
                    "--pack-id",
                    "sample-core-pack",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(uninstall.returncode, 0, uninstall.stdout + uninstall.stderr)

            final_index = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(final_index["packages"], [])


if __name__ == "__main__":
    unittest.main()
