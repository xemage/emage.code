"""Excluded paths mean the same thing with and without ``rsync`` (T555).

The installer's tree writers take a list of excluded names. With ``rsync`` each
becomes ``--exclude=<name>``: a path of that name, at any depth, is never
copied from the source, and a destination's own copy is never overwritten or
deleted (``--delete`` spares it). Before T555 the hand-rolled ``cp`` fallbacks
-- the path on every host without ``rsync``, CI's ``python:3.12-alpine`` among
them -- honoured that only partly:

* ``--update`` copied the SOURCE's excluded paths into every target that had
  none of its own. ``implementation/runtime/memory/_index/`` is gitignored but
  populated in an authoring checkout -- a search index of that repository -- so
  updating a client project from one copied it into the client. Information
  disclosure, not clutter.
* Only the top level was examined, so a nested ``__pycache__/`` shipped even on
  a fresh install, and a target's own nested one was deleted by ``--update``.
* A plain re-install deleted a target's own ``_index/`` whenever the source had
  one too.

Every test uses a synthetic source repository (never this repository's root,
never its real ``_index/``) with SYNTHETIC excluded content planted in it, and
runs under ``rsync`` and with ``rsync`` genuinely absent from ``PATH``.
"""
from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from tests.functional.test_install_projections_only import run_installer
from tests.functional.test_install_update_root import _CopierMatrix, synthetic_repo

RUNTIME = Path("implementation/runtime")
SENTINEL = b"SYNTHETIC-SOURCE-ONLY "
# Excluded content an authoring checkout really has (names only; the bytes here
# are synthetic): a built index, a top-level and a NESTED bytecode cache.
SOURCE_ONLY = (
    "memory/_index/em-age-synthetic/chunks.jsonl",
    "memory/_index/em-age-synthetic/manifest.json",
    "memory/__pycache__/build.cpython-312.pyc",
    "memory/context_retriever_mcp_server/__pycache__/server.cpython-312.pyc",
    "security/__pycache__/scanner.cpython-312.pyc",
    "handoff/__pycache__/validator.cpython-312.pyc",
)
TARGET_OWN = {
    "memory/_index/client-org-client-repo/chunks.jsonl": "the client's own index\n",
    "memory/__pycache__/build.cpython-312.pyc": "the client's own bytecode\n",
    "memory/context_retriever_mcp_server/__pycache__/server.cpython-312.pyc":
        "the client's own nested bytecode\n",
}
EXCLUDED_DIRS = ("memory/_index", "memory/__pycache__",
                 "memory/context_retriever_mcp_server/__pycache__",
                 "security/__pycache__", "handoff/__pycache__")


def source_bytes_in(target: Path) -> list[str]:
    """Every file under the target's runtime that came from the planted source."""
    root = target / RUNTIME
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*")
                  if p.is_file() and p.read_bytes().startswith(SENTINEL))


def tree(root: Path) -> dict[str, bytes | str]:
    """Kind and bytes of everything under root; modes are copier-specific."""
    out: dict[str, bytes | str] = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        out[rel] = "dir" if p.is_dir() and not p.is_symlink() else (
            "link:" + str(p.readlink()) if p.is_symlink() else p.read_bytes())
    return out


class _PlantedSource(_CopierMatrix):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.repo = synthetic_repo(cls.fresh, cls.tmp / "planted-repo")
        for rel in SOURCE_ONLY:
            p = cls.repo / RUNTIME / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(SENTINEL + rel.encode())
        cls.installer = cls.repo / "scripts" / "install.sh"
        # An installed project with no excluded content of its own.
        cls.clean = cls.tmp / "clean-target"
        shutil.copytree(cls.fresh, cls.clean, symlinks=True)
        for rel in EXCLUDED_DIRS:
            shutil.rmtree(cls.clean / RUNTIME / rel, ignore_errors=True)

    def _target(self, name: str, own: bool = False) -> Path:
        target = self.tmp / name
        shutil.copytree(self.clean, target, symlinks=True)
        if own:
            for rel, text in TARGET_OWN.items():
                p = target / RUNTIME / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
        return target

    def _install(self, target: Path, path: str | None, *args: str) -> None:
        proc = run_installer(self.installer, target, "--platform", "all", *args, path=path)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class TestSourceExcludesNeverShip(_PlantedSource):

    def test_update_ships_no_source_index_into_a_target_without_one(self) -> None:
        """The T555 leak: --update, no rsync, target without its own _index/."""
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self._target(f"no-own-index-{label}")
                self.assertFalse((target / RUNTIME / "memory/_index").exists())
                self._install(target, path, "--update")
                self.assertFalse((target / RUNTIME / "memory/_index").exists(),
                                 "the installer's memory index was copied into the target")
                self.assertEqual(source_bytes_in(target), [])

    def test_fresh_install_ships_no_source_excludes_at_any_depth(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self.tmp / f"fresh-planted-{label}"
                self._install(target, path)
                self.assertEqual(source_bytes_in(target), [])
                self.assertFalse((target / RUNTIME / "memory/_index").exists())
                # non-vacuity: the tree that holds the nested cache did ship
                self.assertTrue((target / RUNTIME / "memory/context_retriever_mcp_server"
                                 / "server.py").is_file())

    def test_update_ships_no_nested_source_pycache(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self._target(f"nested-{label}")
                self._install(target, path, "--update")
                self.assertFalse((target / RUNTIME / "memory/context_retriever_mcp_server"
                                  / "__pycache__").exists())
                self.assertEqual(source_bytes_in(target), [])


class TestTargetExcludesAreKept(_PlantedSource):

    def _assert_own_kept(self, target: Path) -> None:
        for rel, text in TARGET_OWN.items():
            self.assertEqual((target / RUNTIME / rel).read_text(), text, rel)
        # Kept as it was, not merged with the source's copy of the same path.
        self.assertEqual(sorted(p.name for p in (target / RUNTIME / "memory/_index").iterdir()),
                         ["client-org-client-repo"])
        self.assertEqual(source_bytes_in(target), [])

    def test_update_keeps_the_targets_own_index_and_nested_pycache(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self._target(f"own-update-{label}", own=True)
                self._install(target, path, "--update")
                self._assert_own_kept(target)

    def test_plain_reinstall_keeps_the_targets_own_index(self) -> None:
        """Pre-T555 the cp fallback deleted it whenever the source had one too."""
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self._target(f"own-reinstall-{label}", own=True)
                self._install(target, path)
                self._assert_own_kept(target)

    def test_update_keeps_a_nested_project_local_file_in_a_retired_directory(self) -> None:
        """A directory removed upstream goes, except what an exclude protects in it.

        rsync --delete keeps such a directory ("cannot delete non-empty
        directory") holding only the protected path; the fallback must too."""
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self._target(f"retired-dir-{label}")
                retired = target / ".claude/skills/zz-retired-skill"
                retired.mkdir(parents=True)
                (retired / "SKILL.md").write_text("removed upstream\n")
                (retired / "settings.json").write_text('{"own": true}\n')
                self._install(target, path, "--update")
                self.assertFalse((retired / "SKILL.md").exists())
                self.assertEqual((retired / "settings.json").read_text(), '{"own": true}\n')


class TestCopiersAgree(_PlantedSource):
    """Same source, same starting target: rsync and cp leave identical trees."""

    def test_rsync_and_cp_fallback_write_identical_trees(self) -> None:
        if not shutil.which("rsync"):
            self.skipTest("rsync not on PATH; nothing to compare the fallback with")
        for mode, args in (("update", ("--update",)), ("install", ())):
            for own in (False, True):
                with self.subTest(mode=mode, own=own):
                    results = {}
                    for label, path in self.copiers():
                        target = self._target(f"agree-{mode}-{own}-{label}", own=own)
                        retired = target / ".github/skills/zz-retired/workflows"
                        retired.mkdir(parents=True)
                        (retired / "ci.yml").write_text("own\n")
                        self._install(target, path, *args)
                        results[label] = tree(target)
                    a, b = results["rsync"], results["cp"]
                    self.assertEqual(sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k)),
                                     [], "paths where rsync and the cp fallback disagree")
                    self.assertIn(".github/skills/zz-retired/workflows/ci.yml", a)  # non-vacuity


if __name__ == "__main__":
    unittest.main()
