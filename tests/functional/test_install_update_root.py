"""`install.sh --update` at the repository root, and self-copies anywhere (T552).

Before T552, ``install.sh --target <repo root> --update`` on a host without
``rsync`` deleted source code: at the root ``install_mcp_server_runtime`` passes
the same directory as source and destination, and ``sync_tree_into``'s ``cp``
fallback runs ``rm -rf "$dest"`` before copying from ``$src``. T550 measured
``implementation/runtime/memory/`` going from 22 files to 0. Two independent
repairs are proven here:

1. ``--update`` is refused at the repository root -- and at any alias of it --
   before anything is written. ``--projections-only`` (T550) is the sanctioned
   root refresh.
2. The tree writers (``copy_tree_into``, ``sync_tree_into``,
   ``merge_tree_preserve_existing``) return early when source and destination
   are the same directory, which is what ``rsync`` already did. That fixes the
   class at any target, e.g. one whose ``implementation/runtime`` is a symlink
   back to the installer's own.

Plus T550's third finding: ``validate_github_agents`` used ``rg``, which CI's
alpine image lacks, so its ``name:`` check was silently skipped there.

Every test runs against temporary directories. None runs the installer against
this repository's root: the root cases build a *synthetic* repository (a copy
of ``scripts/`` and ``implementation/``) and run that copy's own installer
against that copy's own root, as ``test_install_projections_only`` does. Each
behavioural proof runs under ``rsync`` and with ``rsync`` genuinely absent from
``PATH`` (the ``cp`` fallback, which is what CI runs).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root
from tests.functional.test_install_projections_only import (
    _FreshInstallFixture,
    _snapshot,
    make_stale_root,
    run_installer,
)

RUNTIME_TREES = ("memory", "security")


def path_without(tmp: Path, *tools: str) -> str:
    """A PATH identical to the current one minus ``tools``, genuinely absent.

    A stub would not do: install.sh dispatches on ``command -v``, which a stub
    satisfies."""
    farm = tmp / ("no-" + "-".join(tools) + "-bin")
    if farm.is_dir():
        return str(farm)
    farm.mkdir(parents=True)
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry or not os.path.isdir(entry):
            continue
        for name in os.listdir(entry):
            link = farm / name
            if name in tools or link.exists() or link.is_symlink():
                continue
            try:
                link.symlink_to(os.path.join(entry, name))
            except OSError:
                pass
    return str(farm)


def synthetic_repo(fresh: Path, repo: Path) -> Path:
    """A stale installed root that is also an emage.code source repository.

    Its own ``scripts/install.sh`` resolves ``REPO_ROOT`` to ``repo``, so running
    it with ``--target repo`` takes exactly the repository-root code path."""
    make_stale_root(fresh, repo)
    shutil.rmtree(repo / "implementation")  # the fresh install's runtime copy
    shutil.copytree(repo_root() / "scripts", repo / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(repo_root() / "implementation", repo / "implementation",
                    ignore=shutil.ignore_patterns("__pycache__", "_index"))
    return repo


def count_files(path: Path) -> int:
    return sum(1 for p in path.rglob("*") if p.is_file())


class _CopierMatrix(_FreshInstallFixture):
    """Runs a proof under rsync (when present) and under the cp fallback."""

    def copiers(self):
        out = [("cp", self.no_rsync)]
        if shutil.which("rsync"):
            out.insert(0, ("rsync", None))
        return out


class TestUpdateRefusedAtRepositoryRoot(_CopierMatrix):
    """--update at the root exits 1 before writing anything, under both copiers."""

    def _assert_refused(self, repo: Path, target: Path, path: str | None,
                        *extra: str) -> None:
        before = _snapshot(repo)
        runtime = {t: count_files(repo / "implementation/runtime" / t) for t in RUNTIME_TREES}
        self.assertTrue(all(runtime.values()), f"fixture has an empty runtime tree: {runtime}")
        proc = run_installer(repo / "scripts" / "install.sh", target, "--platform", "all",
                             "--update", *extra, path=path)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("refusing --update at the emage.code source repository root", proc.stderr)
        self.assertIn("--target . --platform all --projections-only", proc.stderr)
        self.assertNotIn("merge ledger", proc.stdout + proc.stderr)
        # Bytes, mode AND mtime of every file in the repository: nothing written.
        self.assertEqual(_snapshot(repo), before, "--update wrote at the repository root")
        self.assertEqual(
            {t: count_files(repo / "implementation/runtime" / t) for t in RUNTIME_TREES},
            runtime)

    def test_update_at_repo_root_is_refused(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                repo = synthetic_repo(self.fresh, self.tmp / f"repo-refused-{label}")
                self._assert_refused(repo, repo, path)

    def test_update_dry_run_at_repo_root_is_refused(self) -> None:
        repo = synthetic_repo(self.fresh, self.tmp / "repo-refused-dry-run")
        self._assert_refused(repo, repo, self.no_rsync, "--dry-run")

    def test_update_at_an_alias_of_the_repo_root_is_refused(self) -> None:
        """A symlink to the root is the root: the string check alone missed it."""
        for label, path in self.copiers():
            with self.subTest(copier=label):
                repo = synthetic_repo(self.fresh, self.tmp / f"repo-alias-{label}")
                alias = self.tmp / f"alias-{label}"
                alias.symlink_to(repo, target_is_directory=True)
                self._assert_refused(repo, alias, path)

    def test_projections_only_at_an_alias_still_requires_platform_all(self) -> None:
        repo = synthetic_repo(self.fresh, self.tmp / "repo-alias-pi")
        alias = self.tmp / "alias-pi"
        alias.symlink_to(repo, target_is_directory=True)
        before = _snapshot(repo)
        proc = run_installer(repo / "scripts" / "install.sh", alias, "--platform", "pi",
                             "--projections-only")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("requires --platform all", proc.stderr)
        self.assertEqual(_snapshot(repo), before)

    def test_help_says_update_is_refused_at_the_root(self) -> None:
        proc = subprocess.run(["bash", str(repo_root() / "scripts" / "install.sh"), "--help"],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Refused at the emage.code repository root; use --projections-only.",
                      proc.stdout)
        self.assertIn("The only mode permitted at the emage.code repository", proc.stdout)
        self.assertNotIn("The one mode besides --update", proc.stdout)


class TestSelfCopyIsANoOp(_CopierMatrix):
    """src == dest reaches the tree writers at a target that is NOT the root.

    The target's ``implementation/runtime`` is a symlink to the synthetic
    repository's own, so ``$TARGET/implementation/runtime/memory`` is the
    installer's ``$IMPLEMENTATION/runtime/memory``. Before T552 the cp fallback
    deleted the source there under --update (22 files to 0, exit 1); now the
    writers return early, as rsync always effectively did."""

    def _linked_target(self, repo: Path, name: str) -> Path:
        target = self.tmp / name
        shutil.copytree(self.fresh, target, symlinks=True)
        shutil.rmtree(target / "implementation" / "runtime")
        (target / "implementation" / "runtime").symlink_to(
            repo / "implementation" / "runtime", target_is_directory=True)
        return target

    def _assert_source_intact(self, *extra: str) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                repo = synthetic_repo(self.fresh, self.tmp / f"repo-{self._testMethodName}-{label}")
                target = self._linked_target(repo, f"linked-{self._testMethodName}-{label}")
                source = _snapshot(repo / "implementation")
                self.assertGreaterEqual(count_files(repo / "implementation/runtime/memory"), 20)
                proc = run_installer(repo / "scripts" / "install.sh", target,
                                     "--platform", "all", *extra, path=path)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("itself; nothing to copy", proc.stderr)
                self.assertEqual(_snapshot(repo / "implementation"), source,
                                 "the installer's own source moved")

    def test_update_through_a_symlinked_runtime_keeps_the_source(self) -> None:
        self._assert_source_intact("--update")

    def test_plain_install_through_a_symlinked_runtime_keeps_the_source(self) -> None:
        self._assert_source_intact()


class TestGithubAgentsCheckNeedsNoRipgrep(_CopierMatrix):
    """validate_github_agents no longer passes silently when a tool is missing."""

    def _corrupted_repo(self, name: str) -> Path:
        repo = synthetic_repo(self.fresh, self.tmp / name)
        agent = next(iter(sorted((repo / "implementation/.github/agents").glob("*.agent.md"))))
        agent.write_text("---\nname: Display Name\n" + agent.read_text(encoding="utf-8")[4:],
                         encoding="utf-8")
        return repo

    def test_name_key_is_caught_without_rg(self) -> None:
        repo = self._corrupted_repo("repo-corrupt-agents")
        target = self.tmp / "target-corrupt-agents"
        shutil.copytree(self.fresh, target, symlinks=True)
        before = _snapshot(target)
        proc = run_installer(repo / "scripts" / "install.sh", target, "--platform", "all",
                             "--update", path=path_without(self.tmp, "rg", "rsync"))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("corrupted 'name:' keys", proc.stderr)
        self.assertEqual(_snapshot(target), before)

    def test_a_failed_scan_fails_loudly(self) -> None:
        """grep missing entirely: exit 1 naming the scan, not a silent pass."""
        repo = synthetic_repo(self.fresh, self.tmp / "repo-no-grep")
        target = self.tmp / "target-no-grep"
        shutil.copytree(self.fresh, target, symlinks=True)
        before = _snapshot(target)
        proc = run_installer(repo / "scripts" / "install.sh", target, "--platform", "all",
                             "--update", path=path_without(self.tmp, "grep", "rg"))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("could not scan", proc.stderr)
        self.assertIn("refusing to run --update unchecked", proc.stderr)
        self.assertEqual(_snapshot(target), before)

    def test_clean_source_still_passes_without_rg(self) -> None:
        """Non-vacuity of the two above: the uncorrupted source updates fine."""
        target = self.tmp / "target-clean"
        shutil.copytree(self.fresh, target, symlinks=True)
        proc = run_installer(repo_root() / "scripts" / "install.sh", target,
                             "--platform", "all", "--update",
                             path=path_without(self.tmp, "rg", "rsync"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
