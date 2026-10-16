"""`docs/**/__pycache__/` is never shipped (T559, P20).

``implementation/docs/tasks/`` ships ``validate-tasks.py``; running it from an
authoring checkout leaves a gitignored ``implementation/docs/tasks/__pycache__/``
behind, and the installer reads the working tree. Before T559 the ``docs/``
copies passed no excludes, so a fresh install shipped every ``docs/**/__pycache__/``
-- with and without ``rsync`` -- and ``--update`` shipped any in a ``docs/``
subdirectory other than ``tasks/`` (which goes through ``merge_task_docs``, a
top-level-files-only copy).

``__pycache__`` now means for ``docs/`` what it already meant for the runtime
trees (T555): never copied from the source, at any depth; a target's own is left
alone. The caches here are SYNTHETIC bytes planted in a synthetic repository;
the real authoring checkout's cache is never read. Every proof runs under
``rsync`` and with ``rsync`` absent from ``PATH``.
"""
from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from tests.functional.test_install_projections_only import run_installer
from tests.functional.test_install_update_root import _CopierMatrix, synthetic_repo

SENTINEL = b"SYNTHETIC-SOURCE-PYC "
PLANTED = (
    "tasks/__pycache__/validate-tasks.cpython-312.pyc",
    "plans/__pycache__/helper.cpython-312.pyc",
    "wiki/__pycache__/deeper/__pycache__/nested.cpython-312.pyc",
    "__pycache__/top.cpython-312.pyc",
)
TARGET_OWN = "plans/__pycache__/own.cpython-312.pyc"


def caches_under(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("__pycache__"))


class TestDocsPycacheNeverShips(_CopierMatrix):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.repo = synthetic_repo(cls.fresh, cls.tmp / "pyc-repo")
        for rel in PLANTED:
            p = cls.repo / "implementation/docs" / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(SENTINEL + rel.encode())
        cls.installer = cls.repo / "scripts" / "install.sh"

    def _install(self, target: Path, path: str | None, *args: str) -> None:
        proc = run_installer(self.installer, target, "--platform", "all", *args, path=path)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def _installed_target(self, name: str) -> Path:
        target = self.tmp / name
        shutil.copytree(self.fresh, target, symlinks=True)
        self.assertEqual(caches_under(target / "docs"), [])
        return target

    def test_fresh_install_ships_no_docs_pycache(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self.tmp / f"fresh-{label}"
                self._install(target, path)
                self.assertEqual(caches_under(target / "docs"), [])
                # non-vacuity: the directories holding the caches did ship
                self.assertTrue((target / "docs/tasks/validate-tasks.py").is_file())
                self.assertTrue((target / "docs/plans/_template.md").is_file())

    def test_update_ships_no_docs_pycache(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self._installed_target(f"update-{label}")
                (target / "docs/plans/_template.md").unlink()
                self._install(target, path, "--update")
                self.assertEqual(caches_under(target / "docs"), [])
                # non-vacuity: the merge into docs/plans/ did run
                self.assertTrue((target / "docs/plans/_template.md").is_file())

    def test_a_targets_own_docs_pycache_is_left_alone(self) -> None:
        for label, path in self.copiers():
            for mode in ((), ("--update",)):
                with self.subTest(copier=label, mode=mode):
                    target = self._installed_target(f"own-{label}-{len(mode)}")
                    own = target / "docs" / TARGET_OWN
                    own.parent.mkdir(parents=True)
                    own.write_text("the project's own bytecode\n")
                    self._install(target, path, *mode)
                    self.assertEqual(own.read_text(), "the project's own bytecode\n")
                    self.assertEqual(sorted(p.name for p in own.parent.iterdir()),
                                     [own.name])


if __name__ == "__main__":
    unittest.main()
