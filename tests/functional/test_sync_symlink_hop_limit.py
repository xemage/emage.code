"""T723 (SEC-T684-06): the 40-hop bound of `physicalFolded` in implementation/scripts/sync.mjs is tested.

The T684 mutation log reported "hop limit removed" (T04j) as an equivalent mutant: a plain dangling chain
of more than 40 links makes fs.realpath fail with ELOOP before the hand-followed loop runs. A link whose
target goes through a missing directory (`nodir/../next`) is different: realpath stops at the missing
`nodir` with ENOENT after one link, and the loop resolves `..` lexically, so each link costs one hand hop.
A chain of 41 such links reaches the bound; without the bound it would be followed to its end (and a
cycle of them would never end). This file is new, so it does not edit the sync.mjs test files.
"""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.functional.test_sync_inline_array import _run_sync_with_manifests

HOP_MESSAGE = "more than 40 symbolic links to follow"


def _chain(tmp: Path, length: int) -> None:
    """ln1 -> nodir/../ln2 -> ... -> ln<length> -> nodir/../end; nodir and end do not exist."""
    for i in range(1, length + 1):
        nxt = f"ln{i + 1}" if i < length else "end"
        os.symlink(f"nodir/../{nxt}", tmp / f"ln{i}")


class PhysicalFoldedHopLimitTests(unittest.TestCase):
    def _run(self, length: int):
        proc, tmp = _run_sync_with_manifests({"aaa": lambda m: None, "zzz": lambda m: m.update(outputDir="ln1")},
                                             prepare=lambda root: _chain(root, length))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        return proc, tmp

    def test_a_chain_of_41_links_through_a_missing_directory_is_refused(self):
        proc, tmp = self._run(41)
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn(HOP_MESSAGE, proc.stdout + proc.stderr)
        self.assertFalse((tmp / ".aaa").exists(), "a manifest was written before the refusal")
        self.assertTrue((tmp / "knowledge" / "mcp" / "servers.yaml").is_file(), "a generator input was deleted")

    def test_the_chain_is_not_refused_by_realpath_itself(self):
        """The input is not vacuous: resolving the first link fails with ENOENT, not ELOOP."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            _chain(tmp, 41)
            with self.assertRaises(FileNotFoundError):
                os.stat(tmp / "ln1")
            self.assertEqual(os.readlink(tmp / "ln41"), "nodir/../end")


if __name__ == "__main__":
    unittest.main()
