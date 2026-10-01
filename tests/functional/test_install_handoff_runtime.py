"""`install.sh` ships `implementation/runtime/handoff/` (T553).

``/handoff`` (maturity ``stable``) step 3 drafts its payload against
``implementation/runtime/handoff/schema-v1.json``, and the shipped security
guidelines require handoff JSON to pass ``runtime/handoff/validator.py``. Before
T553 the installer copied only ``runtime/memory/`` and ``runtime/security/``, so
in an installed project both references dangled. The whole tree now ships --
schema, validator and worked example -- minus ``__pycache__/``.

The new directory joins ``install_mcp_server_runtime``, the function whose
``src == dest`` self-copy at the repository root deleted source under the
``cp`` fallback (T552). The survival tests below prove ``runtime/handoff/`` is
not on that path: ``--update`` is refused at the root, and a self-copy anywhere
else is a no-op.

Every test runs against temporary directories; the root cases use a synthetic
repository whose own installer targets its own root. Behavioural proofs run
under ``rsync`` and with ``rsync`` genuinely absent from ``PATH``.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from tests.functional.test_install_projections_only import _snapshot, run_installer
from tests.functional.test_install_update_root import _CopierMatrix, synthetic_repo

HANDOFF = Path("implementation/runtime/handoff")
SHIPPED = {"schema-v1.json", "validator.py", "examples/valid-handoff.json"}
# A reference to the handoff runtime in shipped harness text, with or without
# the leading implementation/ (the security guidelines omit it).
HANDOFF_REF = re.compile(r"(?:implementation/)?runtime/handoff/([\w./-]+\w)")


def files_under(path: Path) -> set[str]:
    return {p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file()}


class TestHandoffRuntimeIsInstalled(_CopierMatrix):

    def _repo_with_pycache(self, name: str) -> Path:
        repo = synthetic_repo(self.fresh, self.tmp / name)
        cache = repo / HANDOFF / "__pycache__" / "validator.cpython-312.pyc"
        cache.parent.mkdir(parents=True)
        cache.write_bytes(b"\x00stale bytecode")
        return repo

    def test_fresh_install_ships_the_handoff_tree(self) -> None:
        for label, path in self.copiers():
            for platform in ("all", "claude-code"):
                with self.subTest(copier=label, platform=platform):
                    repo = self._repo_with_pycache(f"repo-fresh-{label}-{platform}")
                    target = self.tmp / f"fresh-{label}-{platform}"
                    proc = run_installer(repo / "scripts" / "install.sh", target,
                                         "--platform", platform, path=path)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertEqual(files_under(target / HANDOFF), SHIPPED)
                    for rel in SHIPPED:
                        self.assertEqual((target / HANDOFF / rel).read_bytes(),
                                         (repo / HANDOFF / rel).read_bytes(), rel)
                    self.assertFalse((target / HANDOFF / "__pycache__").exists())

    def test_every_handoff_path_the_harness_names_exists_after_install(self) -> None:
        """/handoff step 3 (all platforms) and the security guidelines resolve."""
        refs: dict[str, set[str]] = {}
        for p in self.fresh.rglob("*"):
            if not p.is_file() or HANDOFF in p.relative_to(self.fresh).parents:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for m in HANDOFF_REF.finditer(text):
                refs.setdefault(m.group(1), set()).add(p.relative_to(self.fresh).as_posix())
        self.assertIn("schema-v1.json", refs)  # non-vacuity: /handoff is installed
        self.assertTrue(any("handoff" in f for f in refs["schema-v1.json"]))
        self.assertIn("validator.py", refs)
        missing = {r: sorted(f)[:3] for r, f in refs.items()
                   if not (self.fresh / HANDOFF / r).is_file()}
        self.assertEqual(missing, {}, "handoff paths named by the harness but not installed")

    def test_installed_validator_accepts_the_installed_example(self) -> None:
        """The shipped trio is self-consistent in the target, not only in source."""
        code = (
            "import importlib.util, json, sys\n"
            "spec = importlib.util.spec_from_file_location('v', sys.argv[1])\n"
            "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
            "r = m.validate_handoff_payload(json.load(open(sys.argv[2])))\n"
            "print(r.ok, r.errors); sys.exit(0 if r.ok else 1)\n"
        )
        target = self.tmp / "validator-target"
        shutil.copytree(self.fresh, target, symlinks=True)
        proc = subprocess.run(
            [sys.executable, "-B", "-c", code, str(target / HANDOFF / "validator.py"),
             str(target / HANDOFF / "examples" / "valid-handoff.json")],
            capture_output=True, text=True, check=False, cwd=str(target))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_update_adds_the_tree_to_an_older_install_and_syncs_it(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                # synthetic_repo copies the source without __pycache__/, so the
                # result does not depend on whether a test imported validator.py.
                repo = synthetic_repo(self.fresh, self.tmp / f"repo-older-{label}")
                installer = repo / "scripts" / "install.sh"
                target = self.tmp / f"older-{label}"
                shutil.copytree(self.fresh, target, symlinks=True)
                shutil.rmtree(target / HANDOFF)  # an install from before T553
                proc = run_installer(installer, target, "--platform", "all", "--update",
                                     path=path)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual(files_under(target / HANDOFF), SHIPPED)

                (target / HANDOFF / "examples" / "retired.json").write_text("{}\n")
                cache = target / HANDOFF / "__pycache__" / "validator.cpython-312.pyc"
                cache.parent.mkdir()
                cache.write_bytes(b"target-local bytecode")
                proc = run_installer(installer, target, "--platform", "all", "--update",
                                     path=path)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertFalse((target / HANDOFF / "examples" / "retired.json").exists(),
                                 "a file removed upstream survived --update")
                self.assertEqual(cache.read_bytes(), b"target-local bytecode")

    def _update_ships_no_source_pycache(self, path: str | None, name: str) -> None:
        repo = self._repo_with_pycache(f"repo-{name}")
        target = self.tmp / f"target-{name}"
        shutil.copytree(self.fresh, target, symlinks=True)
        shutil.rmtree(target / HANDOFF)
        proc = run_installer(repo / "scripts" / "install.sh", target, "--platform", "all",
                             "--update", path=path)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(files_under(target / HANDOFF), SHIPPED)

    def test_update_ships_no_source_pycache_with_rsync(self) -> None:
        if not shutil.which("rsync"):
            self.skipTest("rsync not on PATH")
        self._update_ships_no_source_pycache(None, "pycache-rsync")

    def test_update_ships_no_source_pycache_with_cp_fallback(self) -> None:
        """Pinned by T553 as an expected failure; fixed by T555.

        sync_tree_into's cp fallback protected a *destination's* excluded paths
        but never stopped the *source's* from being copied, as rsync --exclude
        does: under --update without rsync, a target lacking its own
        __pycache__/ (or memory/_index/) received the installer's. The fallback
        now never copies an excluded source path. The _index/ side, nested
        caches and a target's own copies: test_install_exclude_parity."""
        self._update_ships_no_source_pycache(self.no_rsync, "pycache-cp")


class TestHandoffRuntimeSurvivesSelfCopies(_CopierMatrix):
    """runtime/handoff/ is not on T552's data-loss path, under either copier."""

    def test_survives_update_at_the_repository_root(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                repo = synthetic_repo(self.fresh, self.tmp / f"repo-root-{label}")
                self.assertEqual(files_under(repo / HANDOFF), SHIPPED)
                before = _snapshot(repo / HANDOFF)
                proc = run_installer(repo / "scripts" / "install.sh", repo,
                                     "--platform", "all", "--update", path=path)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn("refusing --update", proc.stderr)
                self.assertEqual(_snapshot(repo / HANDOFF), before)

    def test_survives_update_through_a_symlinked_runtime(self) -> None:
        """src == dest at a non-root target: the self-copy guard, not the refusal."""
        for label, path in self.copiers():
            with self.subTest(copier=label):
                repo = synthetic_repo(self.fresh, self.tmp / f"repo-linked-{label}")
                target = self.tmp / f"linked-{label}"
                shutil.copytree(self.fresh, target, symlinks=True)
                shutil.rmtree(target / "implementation" / "runtime")
                (target / "implementation" / "runtime").symlink_to(
                    repo / "implementation" / "runtime", target_is_directory=True)
                before = _snapshot(repo / HANDOFF)
                proc = run_installer(repo / "scripts" / "install.sh", target,
                                     "--platform", "all", "--update", path=path)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn(f"{HANDOFF.as_posix()} itself; nothing to copy", proc.stderr)
                self.assertEqual(_snapshot(repo / HANDOFF), before)
                self.assertEqual(files_under(repo / HANDOFF), SHIPPED)


if __name__ == "__main__":
    unittest.main()
