"""Type conflicts mean the same thing with and without ``rsync`` (T559, P21).

A path can be a file in the source and a directory or symlink in the target, or
the reverse. ``rsync -a`` (3.2.7, measured) replaces the target's path, except
that it refuses ("could not make way", exit 23) to replace a NON-EMPTY directory
with a file or symlink. Before T559 the ``cp`` fallback -- the path on every
host without ``rsync``, CI's ``python:3.12-alpine`` among them -- did neither:

* ``copy_tree_into`` (fresh install, plain re-install) exited 1 part-way through
  for every directory/non-directory conflict, and for a file over a symlink to a
  file it wrote THROUGH the link, into whatever file it pointed at;
* ``sync_tree_into`` (``--update``) deleted the target tree first, then either
  failed (the target's kept project-local path gone, its backup left in a
  temporary directory) or restored a kept path through a symlink shipped by the
  source, writing outside the target and exiting 0.

The fallback now removes what ``rsync`` removes and refuses what ``rsync``
refuses, before writing anything to that tree. Each end-to-end proof runs the
worktree's installer against temporary targets under ``rsync`` and with
``rsync`` absent from ``PATH``; the differential test drives the tree writers
directly against real ``rsync``.
"""
from __future__ import annotations

import os
import random
import shutil
import stat
import subprocess
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root
from tests.functional.test_install_projections_only import _snapshot, run_installer
from tests.functional.test_install_target_inside_repo import _paths
from tests.functional.test_install_update_root import _CopierMatrix

INSTALLER = repo_root() / "scripts" / "install.sh"
SHIPPED_FILE = ".cursor/rules/coding-standards.mdc"
SHIPPED_DIR = ".claude/skills/api-design"
OUTSIDE_TEXT = "outside the target; never written\n"


def kind(p: Path) -> str:
    if p.is_symlink():
        return "link"
    return "dir" if p.is_dir() else "file"


class TestConflictsResolvedAsRsyncDoes(_CopierMatrix):

    def _target(self, name: str) -> tuple[Path, Path]:
        target = self.tmp / name
        shutil.copytree(self.fresh, target, symlinks=True)
        outside = self.tmp / f"{name}-outside"
        (outside / "d").mkdir(parents=True)
        (outside / "o.txt").write_text(OUTSIDE_TEXT)
        return target, outside

    def _plant(self, target: Path, outside: Path, case: str) -> str:
        f, d = target / SHIPPED_FILE, target / SHIPPED_DIR
        if case == "empty-dir-over-file":
            f.unlink(); f.mkdir(); return SHIPPED_FILE
        if case == "symlink-over-file":
            f.unlink(); f.symlink_to(outside / "o.txt"); return SHIPPED_FILE
        if case == "dangling-symlink-over-file":
            f.unlink(); f.symlink_to(outside / "missing.txt"); return SHIPPED_FILE
        if case == "file-over-dir":
            shutil.rmtree(d); d.write_text("a file where a skill ships\n"); return SHIPPED_DIR
        if case == "symlink-over-dir":
            shutil.rmtree(d); d.symlink_to(outside / "d", target_is_directory=True)
            return SHIPPED_DIR
        raise AssertionError(case)

    def test_plain_reinstall_replaces_conflicting_paths(self) -> None:
        cases = ("empty-dir-over-file", "symlink-over-file", "dangling-symlink-over-file",
                 "file-over-dir", "symlink-over-dir")
        for label, path in self.copiers():
            for case in cases:
                with self.subTest(copier=label, case=case):
                    target, outside = self._target(f"{case}-{label}")
                    rel = self._plant(target, outside, case)
                    proc = run_installer(INSTALLER, target, "--platform", "all", path=path)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertEqual(kind(target / rel), kind(self.fresh / rel))
                    if kind(self.fresh / rel) == "dir":
                        self.assertEqual(_paths(target / rel), _paths(self.fresh / rel))
                    else:
                        self.assertEqual((target / rel).read_bytes(),
                                         (self.fresh / rel).read_bytes())
                    # Never written through a link.
                    self.assertEqual((outside / "o.txt").read_text(), OUTSIDE_TEXT)
                    self.assertEqual(sorted(_paths(outside)), ["d", "o.txt"])

    def test_non_empty_directory_over_a_file_is_refused(self) -> None:
        """rsync: exit 23 ("could not make way"), the directory kept. The
        fallback refuses before writing anything to that tree."""
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target, _ = self._target(f"nonempty-{label}")
                (target / SHIPPED_FILE).unlink()
                (target / SHIPPED_FILE).mkdir()
                (target / SHIPPED_FILE / "own.md").write_text("the project's own\n")
                # A stale shipped file in the same tree: rewritten only if the
                # copy into .cursor/ started.
                (target / ".cursor/commands/plan.mdc").write_text("stale\n")
                tree = target / ".cursor"
                before, paths = _snapshot(tree), _paths(tree)
                proc = run_installer(INSTALLER, target, "--platform", "all", path=path)
                self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual((target / SHIPPED_FILE / "own.md").read_text(),
                                 "the project's own\n")
                if label == "cp":
                    self.assertIn("the target has a directory that is not empty", proc.stderr)
                    self.assertIn(str(target / SHIPPED_FILE), proc.stderr)
                    self.assertEqual(_snapshot(tree), before, "the fallback wrote to .cursor/")
                    self.assertEqual(_paths(tree), paths)

    def test_dry_run_writes_nothing(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target, outside = self._target(f"dry-{label}")
                self._plant(target, outside, "symlink-over-file")
                self._plant(target, outside, "file-over-dir")
                before, paths = _snapshot(target), _paths(target)
                proc = run_installer(INSTALLER, target, "--platform", "all", "--dry-run",
                                     path=path)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual(_snapshot(target), before)
                self.assertEqual(_paths(target), paths)
                if label == "cp":  # the plan names the replacements it would make
                    self.assertIn(f"DRY-RUN: rm -f {target}/{SHIPPED_FILE}\n", proc.stdout)
                    self.assertIn(f"DRY-RUN: rm -f {target}/{SHIPPED_DIR}\n", proc.stdout)

    def test_update_refuses_a_kept_path_below_a_shipped_file(self) -> None:
        """sync_tree_into: the target's own mcp.json (excluded, so kept) sits in
        a directory where the source ships a file. rsync refuses; the fallback
        used to delete .cursor/ and then fail, losing the kept file."""
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target, _ = self._target(f"kept-{label}")
                (target / SHIPPED_FILE).unlink()
                (target / SHIPPED_FILE).mkdir()
                (target / SHIPPED_FILE / "mcp.json").write_text('{"own": true}\n')
                tree = target / ".cursor"
                before, paths = _snapshot(tree), _paths(tree)
                proc = run_installer(INSTALLER, target, "--platform", "all", "--update",
                                     path=path)
                self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual((target / SHIPPED_FILE / "mcp.json").read_text(),
                                 '{"own": true}\n')
                if label == "cp":
                    self.assertIn("the target has a directory that is not empty", proc.stderr)
                    self.assertEqual(_snapshot(tree), before, "the fallback wrote to .cursor/")
                    self.assertEqual(_paths(tree), paths)


# --- Differential: the tree writers against real rsync ----------------------

NAMES = ("a", "b", ".h", "_index", "__pycache__")
EXCLUDES = ("_index", "__pycache__")


def _build(rng: random.Random, root: Path, depth: int, up: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for name in rng.sample(NAMES, rng.randint(0, 4)):
        p, r = root / name, rng.random()
        if r < 0.3 or depth >= 3:
            p.write_text(f"{name}:{rng.randint(0, 3)}\n")
        elif r < 0.4:
            p.symlink_to(rng.choice(["nowhere", up + "outside/o.txt", up + "outside/d", "a"]))
        else:
            _build(rng, p, depth + 1, "../" + up)


def _tree(root: Path) -> dict[str, str]:
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            p = Path(dirpath) / name
            st = p.lstat()
            out[p.relative_to(root).as_posix()] = (
                "l:" + os.readlink(p) if stat.S_ISLNK(st.st_mode)
                else "d" if stat.S_ISDIR(st.st_mode) else "f:" + p.read_text())
    return out


class TestTreeWritersMatchRsync(_CopierMatrix):
    """Seeded random trees, conflicts deliberately left in (one small name
    alphabet on both sides). Measured on the pre-T559 script, these 120 seeds
    gave 28 copy_tree_into mismatches (21 rsync-ok/cp-fails, 6 cp failures after
    a partial write, 1 write outside dest) and 9 sync_tree_into mismatches (8
    failures after writing, 1 write outside dest); now none."""

    SEEDS = range(120)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        text = INSTALLER.read_text(encoding="utf-8")
        cls.chunk = cls.tmp / "tree-writers.sh"
        cls.chunk.write_text(text[text.index("run() {"):text.index("install_tree_into() {")])

    def _run(self, func: str, base: Path, seed: int, excl: tuple[str, ...],
             path: str | None) -> tuple[int, dict, dict, dict]:
        rng = random.Random(seed * 7 + 1)
        _build(rng, base / "src", 0, "../")
        _build(rng, base / "dest", 0, "../")
        (base / "outside/d").mkdir(parents=True)
        (base / "outside/o.txt").write_text("OUTSIDE\n")
        for dirpath, _, filenames in os.walk(base / "dest"):
            for name in filenames:  # defeat rsync's size+mtime quick check
                p = Path(dirpath) / name
                if not p.is_symlink():
                    os.utime(p, (1_000_000, 1_000_000))
        before = _tree(base / "dest")
        env = dict(os.environ)
        if path is not None:
            env["PATH"] = path
        proc = subprocess.run(
            ["bash", "-c", 'set -euo pipefail; DRY_RUN=0; source "$0"; f="$1"; shift; "$f" "$@"',
             str(self.chunk), func, str(base / "src"), str(base / "dest"), *excl],
            capture_output=True, text=True, env=env, check=False)
        return proc.returncode, _tree(base / "dest"), _tree(base / "outside"), before

    def _differential(self, func: str) -> None:
        if not shutil.which("rsync"):
            self.skipTest("rsync not on PATH; the comparison needs the real thing")
        mismatches = []
        for seed in self.SEEDS:
            excl = EXCLUDES if random.Random(seed).random() < 0.7 else ()
            base = self.tmp / f"{func}-{seed}"
            rc_r, tree_r, out_r, _ = self._run(func, base / "rsync", seed, excl, None)
            rc_c, tree_c, out_c, before_c = self._run(func, base / "cp", seed, excl,
                                                      self.no_rsync)
            shutil.rmtree(base)
            if out_c != {"d": "d", "o.txt": "f:OUTSIDE\n"}:
                mismatches.append((seed, "cp wrote outside dest"))
            elif (rc_r == 0) != (rc_c == 0):
                mismatches.append((seed, f"rsync exit {rc_r}, cp exit {rc_c}"))
            elif rc_r == 0 and (tree_r, out_r) != (tree_c, out_c):
                mismatches.append((seed, "trees differ"))
            elif rc_c != 0 and tree_c != before_c:
                mismatches.append((seed, "cp failed after writing"))
        self.assertEqual(mismatches, [])

    def test_copy_tree_into_matches_rsync(self) -> None:
        self._differential("copy_tree_into")

    def test_sync_tree_into_matches_rsync(self) -> None:
        self._differential("sync_tree_into")


if __name__ == "__main__":
    unittest.main()
