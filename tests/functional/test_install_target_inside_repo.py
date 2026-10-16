"""`install.sh` refuses every target inside the emage.code repository (T559, P17).

The repository root has had its own rules since T550/T552 (only
``--projections-only --platform all``). Below the root nothing was refused, and
two kinds of target did damage:

* ``implementation/`` and anything below it is the source the installer reads.
  Measured on the pre-T559 script against a synthetic repository:
  ``--target <repo>/implementation --update`` re-rendered ``AGENTS.md`` over its
  own source, created ``implementation/implementation/`` and exited 1 at the
  ``CLAUDE.md`` self-copy; ``--target <repo>/implementation/.cursor`` under
  ``rsync`` copied ``.cursor`` into its own subdirectory, several levels deep;
  ``--target <repo>/implementation/new-dir`` exited 0 having written a second
  harness into the source tree.
* Anywhere else below the root, an install writes a second copy of the harness
  into the repository's own working tree.

The check compares with ``-ef`` on every ancestor of the target's physical path,
so a symlink to ``implementation/`` (or to the root) is caught, and a sibling
whose *name* merely starts with the repository's is not.

Every test builds a synthetic repository (a copy of ``scripts/`` and
``implementation/``) and runs that copy's own installer; none targets this
repository. Each refusal is proven under ``rsync`` and with ``rsync`` absent.
"""
from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root
from tests.functional.test_install_projections_only import _snapshot, run_installer
from tests.functional.test_install_update_root import _CopierMatrix, synthetic_repo

SOURCE_TREE = "refusing to install into the emage.code source tree"
INSIDE_REPO = "refusing to install inside the emage.code source repository"


def _paths(root: Path) -> set[str]:
    """Every path under root, directories and symlinks included."""
    out = set()
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            out.add((Path(dirpath) / name).relative_to(root).as_posix())
    return out


class TestTargetInsideRepositoryIsRefused(_CopierMatrix):

    def _assert_refused(self, rel_target: str | None, args: tuple[str, ...],
                        message: str, *, via_alias_of: str | None = None) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                repo = synthetic_repo(
                    self.fresh, self.tmp / f"repo-{self._testMethodName}-{label}")
                if via_alias_of is not None:
                    alias = self.tmp / f"alias-{self._testMethodName}-{label}"
                    alias.symlink_to(repo / via_alias_of, target_is_directory=True)
                    target = alias / rel_target if rel_target else alias
                else:
                    target = repo / rel_target
                before, paths = _snapshot(repo), _paths(repo)
                proc = run_installer(repo / "scripts" / "install.sh", target, *args, path=path)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn(message, proc.stderr)
                self.assertIn("--target /tmp/emage-test", proc.stderr)
                # Bytes, mode and mtime of every file, and the set of paths.
                self.assertEqual(_snapshot(repo), before, "the refused run wrote a file")
                self.assertEqual(_paths(repo), paths, "the refused run created a path")

    def test_update_at_implementation_is_refused(self) -> None:
        self._assert_refused("implementation", ("--platform", "all", "--update"), SOURCE_TREE)

    def test_plain_install_at_implementation_is_refused(self) -> None:
        self._assert_refused("implementation", ("--platform", "all"), SOURCE_TREE)

    def test_projections_only_at_implementation_is_refused(self) -> None:
        self._assert_refused("implementation", ("--platform", "all", "--projections-only"),
                             SOURCE_TREE)

    def test_update_dry_run_at_implementation_is_refused(self) -> None:
        self._assert_refused("implementation",
                             ("--platform", "all", "--update", "--dry-run"), SOURCE_TREE)

    def test_a_platform_tree_inside_implementation_is_refused(self) -> None:
        """Under rsync this nested .cursor inside itself before T559."""
        self._assert_refused("implementation/.cursor", ("--platform", "cursor"), SOURCE_TREE)

    def test_a_new_directory_inside_implementation_is_refused(self) -> None:
        """Exited 0 before T559, writing a whole harness into the source."""
        self._assert_refused("implementation/new-dir", ("--platform", "pi"), SOURCE_TREE)

    def test_a_symlink_to_implementation_is_refused(self) -> None:
        self._assert_refused(None, ("--platform", "all", "--update"), SOURCE_TREE,
                             via_alias_of="implementation")

    def test_a_directory_elsewhere_in_the_repository_is_refused(self) -> None:
        self._assert_refused("tmp/scratch-install", ("--platform", "pi"), INSIDE_REPO)

    def test_an_existing_repository_directory_is_refused(self) -> None:
        self._assert_refused("docs", ("--platform", "pi"), INSIDE_REPO)

    def test_a_subdirectory_of_an_alias_of_the_root_is_refused(self) -> None:
        self._assert_refused("tmp/x", ("--platform", "pi"), INSIDE_REPO, via_alias_of=".")

    def test_a_sibling_sharing_the_repository_name_prefix_is_allowed(self) -> None:
        """Non-vacuity: `<repo>-extra` is outside `<repo>`; a string-prefix check
        would refuse it."""
        repo = synthetic_repo(self.fresh, self.tmp / "repo-prefix")
        target = self.tmp / "repo-prefix-extra"
        proc = run_installer(repo / "scripts" / "install.sh", target, "--platform", "pi")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((target / "AGENTS.md").is_file())

    def test_help_states_the_refusal(self) -> None:
        proc = subprocess.run(["bash", str(repo_root() / "scripts" / "install.sh"), "--help"],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("any\n                       directory below its root is refused in every mode",
                      proc.stdout)


if __name__ == "__main__":
    unittest.main()
