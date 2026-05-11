"""Sync engine determinism — running sync.mjs twice produces identical output.

This duplicates the CI `sync-no-diff` job at the unit-test level so a developer
can catch the regression locally before pushing.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root


def _run_sync(cwd: Path) -> None:
    subprocess.run(
        ["node", "scripts/sync.mjs"],
        cwd=cwd, check=True, capture_output=True,
    )


def _run_verify(cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        ["node", "scripts/verify.mjs"],
        cwd=cwd, capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def _hash_dir(directory: Path) -> dict[str, str]:
    """Return {relative_path: sha256(content)} for every file under directory."""
    import hashlib
    out: dict[str, str] = {}
    for f in sorted(directory.rglob("*")):
        if not f.is_file():
            continue
        out[str(f.relative_to(directory))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


class TestSyncDeterminism(unittest.TestCase):
    """Verify that the sync engine is idempotent on the committed knowledge base."""

    def test_verify_passes_on_committed_state(self):
        rc, out = _run_verify(implementation_root())
        self.assertEqual(
            rc, 0,
            f"verify.mjs failed on committed state — generated mirrors are stale.\n{out}",
        )

    def test_sync_is_idempotent(self):
        """Run sync.mjs twice in a copy of the implementation tree, compare outputs."""
        node_available = shutil.which("node")
        if not node_available:
            self.skipTest("node not available on PATH")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "impl"
            shutil.copytree(implementation_root(), tmp_path, symlinks=False)

            _run_sync(tmp_path)
            first = _hash_dir(tmp_path)

            _run_sync(tmp_path)
            second = _hash_dir(tmp_path)

            differing = sorted(k for k in set(first) | set(second) if first.get(k) != second.get(k))
            self.assertFalse(
                differing,
                msg=(
                    "sync.mjs is not idempotent — second run differs from first.\n"
                    f"Differing files ({len(differing)}):\n  " + "\n  ".join(differing[:20])
                ),
            )


if __name__ == "__main__":
    unittest.main()
