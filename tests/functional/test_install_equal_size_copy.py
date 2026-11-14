"""A changed file of the same size and mtime is still copied (T828, TD-T774-01 / QA-T818-01).

``rsync -a`` decides by its quick check: a source file whose size and mtime equal
the target's is skipped, whatever its content. ``copy_tree_into`` and
``sync_tree_into`` called it that way until T828, so a target whose copy of a
changed file had the same size and an mtime in the same second kept the old
bytes. QA reproduced it on ``--update`` with the two runtime lock files, whose
``opentelemetry-api`` pin moved from 1.45.1 to 1.45.2 at the same size.

Each proof here plants that state directly: a fresh install's file is given
other bytes of the same length and the source file's exact mtime, and the
installer is run again. The file must then hold the source's bytes, under a plain
re-install (``copy_tree_into``), ``--update`` and ``--projections-only`` (both
``sync_tree_into``), with ``rsync`` and with ``rsync`` absent from ``PATH`` (the
``cp`` fallback, which never had the skip).
"""
from __future__ import annotations

import os
import shutil
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root
from tests.functional.test_install_projections_only import run_installer
from tests.functional.test_install_update_root import _CopierMatrix

INSTALLER = repo_root() / "scripts" / "install.sh"
IMPLEMENTATION = repo_root() / "implementation"
# A platform-tree file (every mode copies it) and the lock file of QA-T818-01
# (implementation/ is not touched by --projections-only).
PLATFORM_FILE = ".claude/skills/api-design/SKILL.md"
LOCK_FILE = "implementation/runtime/memory/requirements-mcp-server.lock.txt"
MODES = {
    "plain": ((), (PLATFORM_FILE, LOCK_FILE)),
    "update": (("--update",), (PLATFORM_FILE, LOCK_FILE)),
    "projections-only": (("--projections-only",), (PLATFORM_FILE,)),
}


def source_of(rel: str) -> Path:
    """The installer's source for a target path: ``implementation/runtime/..`` comes from
    ``implementation/runtime/..``, a platform tree such as ``.claude/..`` from ``implementation/.claude/..``."""
    return IMPLEMENTATION / rel.removeprefix("implementation/")


def same_size_other_bytes(data: bytes) -> bytes:
    """``data`` with its first ASCII letter or digit changed: same length, other content."""
    index = next(i for i, b in enumerate(data) if chr(b).isalnum())
    return data[:index] + bytes([data[index] ^ 0x01]) + data[index + 1:]


def plant_stale_copy(target: Path, rel: str) -> bytes:
    """Give ``target/rel`` other bytes of the source's size and the source's mtime.
    Returns the source's bytes, which the installer must write."""
    src = source_of(rel)
    expected = src.read_bytes()
    dest = target / rel
    dest.write_bytes(same_size_other_bytes(expected))
    st = src.stat()
    os.utime(dest, ns=(st.st_atime_ns, st.st_mtime_ns))
    assert dest.stat().st_size == len(expected) and dest.read_bytes() != expected
    return expected


class TestEqualSizeEqualMtimeFileIsCopied(_CopierMatrix):

    def _check(self, mode: str, copier: str, path: str | None) -> None:
        flags, files = MODES[mode]
        target = self.tmp / f"{mode}-{copier}"
        shutil.copytree(self.fresh, target, symlinks=True)
        expected = {rel: plant_stale_copy(target, rel) for rel in files}
        run = run_installer(INSTALLER, target, "--platform", "all", *flags, path=path)
        self.assertEqual(run.returncode, 0, run.stderr)
        for rel, data in expected.items():
            with self.subTest(file=rel):
                self.assertEqual((target / rel).read_bytes(), data,
                                 f"{mode} under {copier} left a stale same-size file")
        shutil.rmtree(target)

    def _each_copier(self, mode: str) -> None:
        for copier, path in self.copiers():
            with self.subTest(copier=copier):
                self._check(mode, copier, path)

    def test_plain_reinstall_copies_a_changed_same_size_file(self) -> None:
        self._each_copier("plain")

    def test_update_copies_a_changed_same_size_file(self) -> None:
        self._each_copier("update")

    def test_projections_only_copies_a_changed_same_size_file(self) -> None:
        self._each_copier("projections-only")


if __name__ == "__main__":
    unittest.main()
