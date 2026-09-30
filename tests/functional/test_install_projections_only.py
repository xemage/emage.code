"""`install.sh --projections-only` (T550): a harness-only refresh.

The mode refreshes the derived harness -- the platform trees, their MCP configs,
``AGENTS.md`` and ``CLAUDE.md`` -- and touches nothing the project owns. It
exists because the only other mode ``install.sh`` permits at the emage.code
repository root is ``--update``, which also runs the ``docs/tasks`` ledger merge;
the last root refresh that way (``fee245a``) took ``active-tasks.md`` from 2460
lines to 11. See ``docs/artifacts/root-refresh-mode-v1.md``.

Every test here runs against temporary directories. None runs the mode, or
``--update``, against this repository's root. The repository-root cases build a
*synthetic* repository (a copy of ``scripts/`` and ``implementation/``) and run
that copy's own installer against that copy's own root.

Each behavioural proof runs twice: with ``rsync``, and with ``rsync`` genuinely
absent from ``PATH`` so ``install.sh`` takes its ``cp`` fallback -- the path CI's
``python:3.12-alpine`` ``unit-tests`` job takes, since it installs no ``rsync``.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import tests.functional.test_install_script as install_script_tests
import tests.functional.test_root_install_parity as parity
from tests._helpers.repo import repo_root

INSTALLER = repo_root() / "scripts" / "install.sh"
HARNESS_TREES = (".claude", ".cursor", ".gemini", ".github", ".opencode", ".pi",
                 ".cline", ".clinerules")
HARNESS_FILES = ("AGENTS.md", "CLAUDE.md")
# Harness-tree paths the installer declares project-local (parsed from
# install.sh by the T543 gate, so this cannot silently fall out of step).
_PROTECTED = parity.parse_replaced_trees(INSTALLER.read_text(encoding="utf-8"))

# A ledger that the --update ledger merge would REWRITE (it drops the
# non-conforming `T42` row and adds a missing trailing newline), so "byte-identical
# after --projections-only" proves the merge never ran, not merely that it
# happened to be a no-op. The control test below proves --update does rewrite it.
ACTIVE_LEDGER = (
    "# Active Tasks\n\nProject-owned prose: 312 tasks have run to completion.\n\n"
    "| ID | Title | Owner | Status | Priority | Depends on | Last update |\n"
    "|----|-------|-------|--------|----------|-----------|-------------|\n"
    + "".join(
        f"| T{n:03d} | Task {n} | devops-engineer | pending | P1 | — | 2026-09-30 |\n"
        for n in range(500, 560)
    )
    + "| T42 | legacy short id | qa-engineer | blocked | P2 | — | 2026-09-01 |\n"
    "\n> Orchestrator note: this footer is the project's own record."
)
COMPLETED_LEDGER = (
    "# Completed Tasks\n\n| ID | Title | Owner | Done on | Outcome / artifact |\n"
    "|----|-------|-------|---------|--------------------|\n"
    + "".join(f"| T{n:03d} | Done {n} | devops-engineer | 2026-09-01 | x.md |\n"
              for n in range(1, 312))
)
PROJECT_OWNED = {
    "docs/tasks/active-tasks.md": ACTIVE_LEDGER,
    "docs/tasks/completed-tasks.md": COMPLETED_LEDGER,
    "docs/tasks/task-T500.md": "# T500\n**Status:** pending\n",
    "docs/checkpoints/checkpoint-001-plan.md": "# checkpoint\n",
    ".claude/settings.json": '{"permissions": {"allow": ["Bash(git status:*)"]}}\n',
    ".claude/settings.local.json": '{"permissions": {"allow": ["Bash(ls:*)"]}}\n',
    ".github/workflows/ci.yml": "name: ci\non: [push]\n",
    ".github/ISSUE_TEMPLATE/bug.md": "name: Bug\n",
    ".github/CODEOWNERS": "* @org/maintainers\n",
    ".github/dependabot.yml": "version: 2\n",
    ".github/PULL_REQUEST_TEMPLATE.md": "## Summary\n",
    ".github/FUNDING.yml": "github: [org]\n",
    ".github/copilot-instructions.md": "project-specific\n",
    ".vscode/settings.json": "{}\n",
    "README.md": "# The project\n",
    "src/app.py": "print('app')\n",
    "implementation/runtime/memory/_index/demo/index.json": "{}\n",
}
# Harness paths made stale in the synthetic root, and removed-upstream files.
STALE_EDITS = (
    ".claude/agents/orchestrator.md",
    ".cursor/commands/plan.mdc",
    ".github/prompts/plan.prompt.md",
    ".cline/skills/skillify/SKILL.md",
    "AGENTS.md",
    "CLAUDE.md",
)
REMOVED_UPSTREAM = (".claude/commands/retired.md", ".clinerules/retired.md",
                    ".pi/prompts/retired.md")
DELETED_SHIPPED = ".opencode/agents/orchestrator.md"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(root: Path) -> dict[str, tuple[str, int, int]]:
    """Every file under root -> (sha256, mode, mtime_ns).

    An unchanged mtime proves a file was not rewritten at all, not merely
    rewritten to the same bytes."""
    snap = {}
    for p in root.rglob("*"):
        if p.is_file():
            st = p.stat()
            snap[p.relative_to(root).as_posix()] = (_digest(p), st.st_mode, st.st_mtime_ns)
    return snap


def _in_harness_tree(rel: str) -> bool:
    return rel.partition("/")[0] in HARNESS_TREES


def merge_owned_configs(fresh: Path) -> frozenset[str]:
    """MCP configs the installer merges (shipped with an ADR-002 sidecar), plus
    their sidecars. Inside a tree they are excluded from the tree replace only
    because a later merge step owns them -- they are harness, not project-local."""
    configs = {
        rel[: -len(parity.SIDECAR_SUFFIX)]
        for rel in (p.relative_to(fresh).as_posix() for p in fresh.rglob("*"))
        if rel.endswith(parity.SIDECAR_SUFFIX)
    }
    return frozenset(configs | {c + parity.SIDECAR_SUFFIX for c in configs})


def _is_harness(rel: str, merge_owned: frozenset[str]) -> bool:
    """True for a path --projections-only may write: a shipped harness path."""
    if rel in HARNESS_FILES or rel in merge_owned:
        return True
    tree, _, inner = rel.partition("/")
    if tree not in HARNESS_TREES:
        return False
    protected = _PROTECTED.get(tree, [])
    return not any(inner == p or inner.startswith(p + "/") for p in protected)


def _write(root: Path, rel: str, text: str) -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


def make_stale_root(fresh: Path, root: Path) -> None:
    """A previously installed project whose harness has fallen behind."""
    shutil.copytree(fresh, root, symlinks=True)
    for rel, text in PROJECT_OWNED.items():
        _write(root, rel, text)
    (root / "docs/tasks/validate-tasks.py").unlink()  # --update would re-seed it
    (root / "implementation/runtime/security/__init__.py").write_text("# local edit\n")
    for rel in STALE_EDITS:
        _write(root, rel, "Docs (docs) -> commit directly to develop\n")
    for rel in REMOVED_UPSTREAM:
        _write(root, rel, "removed upstream\n")
    (root / DELETED_SHIPPED).unlink()
    pi = json.loads((root / ".pi/mcp.json").read_text(encoding="utf-8"))
    pi["mcpServers"]["gitlab"]["command"] = "stale"
    _write(root, ".pi/mcp.json", json.dumps(pi, indent=2))
    vscode = json.loads((root / ".vscode/mcp.json").read_text(encoding="utf-8"))
    vscode["servers"]["hand-added"] = {"command": "local"}
    vscode["inputs"] = [{"id": "tok", "type": "promptString", "password": True}]
    _write(root, ".vscode/mcp.json", json.dumps(vscode, indent=2))


def path_without_rsync(tmp: Path) -> str:
    return install_script_tests.TestInstallPreservesProjectLocalFiles._path_without_rsync(tmp)


def run_installer(installer: Path, target: Path, *args: str,
                  path: str | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if path is not None:
        env["PATH"] = path
    return subprocess.run(
        ["bash", str(installer), "--target", str(target), *args],
        cwd=str(installer.parent.parent), capture_output=True, text=True,
        timeout=300, check=False, env=env,
    )


class _FreshInstallFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("bash"):
            raise unittest.SkipTest("bash not available on PATH")
        cls._tmp = tempfile.TemporaryDirectory(prefix="emage-projections-only-")
        cls.tmp = Path(cls._tmp.name)
        cls.fresh = cls.tmp / "fresh"
        parity.run_fresh_install(cls.fresh)
        cls.no_rsync = path_without_rsync(cls.tmp)
        cls.merge_owned = merge_owned_configs(cls.fresh)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _root(self, suffix: str = "") -> Path:
        root = self.tmp / f"root-{self._testMethodName}{suffix}"
        make_stale_root(self.fresh, root)
        return root

    def _require_rsync(self) -> None:
        if not shutil.which("rsync"):
            self.skipTest("rsync not on PATH; the cp-fallback variant covers this host")


class TestProjectionsOnlyRefresh(_FreshInstallFixture):
    """The mode cures harness drift and leaves every project-owned byte alone."""

    def _refresh_and_verify(self, path: str | None) -> None:
        root = self._root()
        self.assertTrue(parity.compute_drift(self.fresh, root), "fixture is not stale")
        before = _snapshot(root)

        proc = run_installer(INSTALLER, root, "--platform", "all",
                             "--projections-only", path=path)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        after = _snapshot(root)

        owned = {k for k in before.keys() | after.keys()
                 if not _is_harness(k, self.merge_owned)}
        # Outside the harness trees (docs/, implementation/, the project's own
        # files): bytes, mode AND mtime -- never even rewritten, either copier.
        # Project-local paths INSIDE .claude/ and .github/: bytes and mode under
        # both copiers; mtime too under rsync. The cp fallback in sync_tree_into
        # saves and restores them around its rm -rf of the tree (identical bytes,
        # new mtime) -- pre-existing --update behaviour this task must not change.
        def key(rel: str, entry):
            if entry is None or (path is not None and _in_harness_tree(rel)):
                return entry and entry[:2]
            return entry
        moved = sorted(k for k in owned if key(k, before.get(k)) != key(k, after.get(k)))
        self.assertEqual(moved, [], "project-owned files written, created or deleted")
        self.assertIn("docs/tasks/active-tasks.md", owned)  # classifier sanity
        self.assertIn(".claude/settings.json", owned)
        self.assertIn(".github/workflows/ci.yml", owned)
        self.assertEqual(parity.compute_drift(self.fresh, root), set())
        for rel in REMOVED_UPSTREAM:
            self.assertFalse((root / rel).exists(), f"{rel} survived the refresh")
        vscode = json.loads((root / ".vscode/mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(vscode["servers"]["hand-added"], {"command": "local"})
        self.assertIn("inputs", vscode)
        self.assertNotIn("Updated emage.code", proc.stdout)
        self.assertIn("docs/ and implementation/ were not touched", proc.stdout)

    def test_refresh_with_rsync(self) -> None:
        self._require_rsync()
        self._refresh_and_verify(path=None)

    def test_refresh_with_cp_fallback(self) -> None:
        self._refresh_and_verify(path=self.no_rsync)

    def _assert_ledger_survives(self, path: str | None) -> None:
        root = self._root()
        tasks = root / "docs" / "tasks"
        before = {f: (tasks / f).read_bytes() for f in
                  ("active-tasks.md", "completed-tasks.md")}
        mtimes = {f: (tasks / f).stat().st_mtime_ns for f in before}
        proc = run_installer(INSTALLER, root, "--platform", "all",
                             "--projections-only", path=path)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        for name, data in before.items():
            self.assertEqual((tasks / name).read_bytes(), data, f"{name} changed")
            self.assertEqual((tasks / name).stat().st_mtime_ns, mtimes[name],
                             f"{name} was rewritten (even if to the same bytes)")
        self.assertEqual(len(ACTIVE_LEDGER.splitlines()),
                         len((tasks / "active-tasks.md").read_text().splitlines()))
        self.assertFalse((tasks / "validate-tasks.py").exists(),
                         "the mode seeded a docs/tasks template file")

    def test_task_ledger_survives_byte_for_byte_with_rsync(self) -> None:
        self._require_rsync()
        self._assert_ledger_survives(path=None)

    def test_task_ledger_survives_byte_for_byte_with_cp_fallback(self) -> None:
        self._assert_ledger_survives(path=self.no_rsync)

    def test_control_update_would_rewrite_this_ledger(self) -> None:
        """Non-vacuity: the same fixture under --update DOES get rewritten."""
        root = self._root()
        before = (root / "docs/tasks/active-tasks.md").read_bytes()
        proc = run_installer(INSTALLER, root, "--platform", "all", "--update")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotEqual((root / "docs/tasks/active-tasks.md").read_bytes(), before)
        self.assertTrue((root / "docs/tasks/validate-tasks.py").exists())

    def test_single_platform_refresh_touches_only_that_platform(self) -> None:
        root = self._root()
        before = _snapshot(root)
        proc = run_installer(INSTALLER, root, "--platform", "pi", "--projections-only")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        after = _snapshot(root)
        changed = {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
        self.assertTrue(changed)
        self.assertEqual({k for k in changed if not (k.startswith(".pi/") or k == "AGENTS.md")},
                         set(), "a pi-only refresh wrote outside .pi/ and AGENTS.md")
        self.assertIn("`.pi/skills/`", (root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_dry_run_writes_nothing(self) -> None:
        for label, path in (("rsync", None), ("cp", self.no_rsync)):
            if label == "rsync" and not shutil.which("rsync"):
                continue
            with self.subTest(copier=label):
                root = self._root(f"-{label}")
                before = _snapshot(root)
                proc = run_installer(INSTALLER, root, "--platform", "all",
                                     "--projections-only", "--dry-run", path=path)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual(_snapshot(root), before)
                self.assertNotIn("merge-task-docs", proc.stdout)


class TestProjectionsOnlyContract(_FreshInstallFixture):
    """Flag contract: opt-in, exclusive, refresh-only, documented."""

    def test_mutually_exclusive_with_update(self) -> None:
        root = self._root()
        before = _snapshot(root)
        proc = run_installer(INSTALLER, root, "--platform", "all",
                             "--projections-only", "--update")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("mutually exclusive", proc.stderr)
        self.assertEqual(_snapshot(root), before)

    def test_requires_an_existing_install(self) -> None:
        target = self.tmp / "empty-target"
        proc = run_installer(INSTALLER, target, "--platform", "all", "--projections-only")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("--projections-only requires an existing emage.code install",
                      proc.stderr)
        self.assertEqual([p for p in target.rglob("*")], [])

    def test_merge_owned_config_set_is_complete(self) -> None:
        """Guard against a vacuous classifier: all seven MCP configs are found."""
        self.assertEqual(
            {c for c in self.merge_owned if not c.endswith(parity.SIDECAR_SUFFIX)},
            {".mcp.json", ".vscode/mcp.json", ".cursor/mcp.json", ".gemini/settings.json",
             ".opencode/opencode.json", ".pi/mcp.json", ".cline/mcp.json"},
        )

    def test_help_documents_the_contract(self) -> None:
        proc = subprocess.run(["bash", str(INSTALLER), "--help"], capture_output=True,
                              text=True, check=False)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--projections-only", proc.stdout)
        self.assertIn("never writes or deletes anything under the target's docs/", proc.stdout)


class TestProjectionsOnlyAtRepositoryRoot(_FreshInstallFixture):
    """The repository-root branch, against a synthetic copy of the repository.

    `REPO_ROOT` is derived from the script's own location, so a copy of
    `scripts/` + `implementation/` whose installer targets its own root exercises
    exactly the code path a real root refresh takes -- without touching the real
    root.
    """

    def _synthetic_repo(self, name: str) -> Path:
        repo = self.tmp / name
        make_stale_root(self.fresh, repo)
        shutil.rmtree(repo / "implementation")  # the fresh install's runtime copy
        shutil.copytree(repo_root() / "scripts", repo / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(repo_root() / "implementation", repo / "implementation",
                        ignore=shutil.ignore_patterns("__pycache__", "_index"))
        return repo

    def _refresh_repo_root(self, path: str | None) -> None:
        repo = self._synthetic_repo(f"repo-{self._testMethodName}")
        installer = repo / "scripts" / "install.sh"
        docs = _snapshot(repo / "docs")
        impl = _snapshot(repo / "implementation")
        proc = run_installer(installer, repo, "--platform", "all",
                             "--projections-only", path=path)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("in-place at the repository root", proc.stderr)
        self.assertEqual(_snapshot(repo / "docs"), docs, "docs/ moved at the repo root")
        self.assertEqual(_snapshot(repo / "implementation"), impl,
                         "implementation/ (the source) moved at the repo root")
        self.assertEqual(parity.compute_drift(self.fresh, repo), set())

    def test_repo_root_refresh_with_rsync(self) -> None:
        self._require_rsync()
        self._refresh_repo_root(path=None)

    def test_repo_root_refresh_with_cp_fallback(self) -> None:
        """Under the cp fallback, --update at a repo root deletes
        implementation/runtime/memory/ (sync_tree_into with src == dest). The
        projections-only mode never reaches that code."""
        self._refresh_repo_root(path=self.no_rsync)

    def test_repo_root_requires_platform_all(self) -> None:
        repo = self._synthetic_repo("repo-single-platform")
        before = _snapshot(repo)
        proc = run_installer(repo / "scripts" / "install.sh", repo, "--platform", "pi",
                             "--projections-only")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("requires --platform all", proc.stderr)
        self.assertEqual(_snapshot(repo), before)

    def test_plain_install_at_repo_root_is_still_refused(self) -> None:
        repo = self._synthetic_repo("repo-plain")
        before = _snapshot(repo)
        proc = run_installer(repo / "scripts" / "install.sh", repo, "--platform", "all")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refusing to install", proc.stderr)
        self.assertIn("--projections-only", proc.stderr)
        self.assertEqual(_snapshot(repo), before)


if __name__ == "__main__":
    unittest.main()
