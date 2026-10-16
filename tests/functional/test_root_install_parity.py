"""Root self-install parity gate (T543).

The repo-root harness -- the eight platform trees, ``AGENTS.md``, ``CLAUDE.md``
and the MCP configs -- is ``scripts/install.sh`` output, not ``sync.mjs``
output (``AGENTS.md`` § Knowledge Base). ``sync.mjs --check`` and
``generate-registry.py --check`` inspect only ``implementation/``, so until this
test nothing noticed when the root fell behind (see
``docs/artifacts/root-projection-resolution-v1.md``).

The installer itself is the oracle. This test runs a *fresh* install (never
``--update``) into a temporary directory and compares its output with the repo
root under the installer's own ownership rules:

* every shipped file must be byte-identical at the root;
* a merge-owned MCP config (one shipped with a ``<file>.provenance.json``
  sidecar, ADR-002) must be a fixed point of ``merge-mcp-json.py``'s
  ``merge_json`` and carry a byte-identical sidecar -- i.e. ``--update`` would
  change nothing, and hand-added servers/``inputs`` stay legal;
* inside every tree ``install.sh`` replaces with ``rsync --delete``, a
  root-only file is drift unless ``install.sh`` declares it project-local.

Drift that is known and not yet refreshed is *declared* in
``tests/_baselines/root-install-drift.json``. The gate is bidirectional: an
undeclared divergence fails, and a declared path that no longer diverges fails
too, so the declaration can neither hide new drift nor outlive a refresh.

Print the current divergence set (for updating the declaration in the same MR
that causes or cures it) with::

    python3 -m tests.functional.test_root_install_parity --print-drift
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

BASELINE = repo_root() / "tests" / "_baselines" / "root-install-drift.json"
INSTALLER = repo_root() / "scripts" / "install.sh"
MERGER = repo_root() / "scripts" / "merge-mcp-json.py"
# Top-level fresh-install output that is NOT a root-tracking artifact:
# docs/ is merge-preserve-existing (project-owned once installed) and
# implementation/ at the repo root *is* the source the installer reads.
NOT_ROOT_OWNED = {"docs", "implementation"}
SIDECAR_SUFFIX = ".provenance.json"

_TREE_CALL_RE = re.compile(
    r'^\s*install_tree_into "\$IMPLEMENTATION/(\.[\w-]+)" "\$TARGET/\1"(.*)$', re.M
)
_ARRAY_REF_RE = re.compile(r'^"\$\{(\w+)\[@\]\}"$')


def _load_merge_json():
    spec = importlib.util.spec_from_file_location("merge_mcp_json", MERGER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.merge_json


def _bash_array(text: str, name: str) -> list[str]:
    match = re.search(rf"^{name}=\((.*?)\)", text, re.M | re.S)
    if match is None:
        raise AssertionError(f"install.sh no longer defines {name}; update this test")
    return match.group(1).split()


def parse_replaced_trees(text: str) -> dict[str, list[str]]:
    """Map each tree install.sh replaces wholesale to its protected paths."""
    trees: dict[str, list[str]] = {}
    for tree, rest in _TREE_CALL_RE.findall(text):
        protected: list[str] = []
        for token in rest.split():
            ref = _ARRAY_REF_RE.match(token)
            if ref:
                protected.extend(_bash_array(text, ref.group(1)))
            else:
                protected.append(token.strip('"'))
        trees[tree] = protected
    return trees


def run_fresh_install(target: Path) -> None:
    subprocess.run(
        ["bash", str(INSTALLER), "--target", str(target), "--platform", "all"],
        check=True, capture_output=True, text=True, timeout=300,
        cwd=str(repo_root()),
    )


def _files_under(base: Path) -> set[str]:
    return {p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()}


def _is_protected(rel: str, protected: list[str]) -> bool:
    return any(rel == p or rel.startswith(p + "/") for p in protected)


def _mcp_config_current(rel: str, fresh: Path, root: Path, merge_json) -> bool:
    shipped = json.loads((fresh / rel).read_text(encoding="utf-8"))
    installed = json.loads((root / rel).read_text(encoding="utf-8"))
    sidecar = rel + SIDECAR_SUFFIX
    same_sidecar = (root / sidecar).is_file() and (
        (root / sidecar).read_bytes() == (fresh / sidecar).read_bytes()
    )
    return same_sidecar and merge_json(installed, shipped) == installed


def _shipped_file_drifts(rel: str, fresh: Path, root: Path, merge_json) -> bool:
    if not (root / rel).is_file():
        return True
    if (fresh / (rel + SIDECAR_SUFFIX)).is_file():
        return not _mcp_config_current(rel, fresh, root, merge_json)
    return (root / rel).read_bytes() != (fresh / rel).read_bytes()


def _root_only_drift(fresh: Path, root: Path, trees: dict[str, list[str]]) -> set[str]:
    drift: set[str] = set()
    for tree, protected in trees.items():
        if not (root / tree).is_dir():
            continue
        shipped = _files_under(fresh / tree) if (fresh / tree).is_dir() else set()
        for rel in _files_under(root / tree) - shipped:
            if not _is_protected(rel, protected):
                drift.add(f"{tree}/{rel}")
    return drift


def compute_drift(fresh: Path, root: Path) -> set[str]:
    """Root paths that a `--platform all --update` would change or delete."""
    merge_json = _load_merge_json()
    trees = parse_replaced_trees(INSTALLER.read_text(encoding="utf-8"))
    shipped = {
        rel for rel in _files_under(fresh)
        if rel.split("/", 1)[0] not in NOT_ROOT_OWNED
    }
    drift = {r for r in shipped if _shipped_file_drifts(r, fresh, root, merge_json)}
    return drift | _root_only_drift(fresh, root, trees)


def current_drift() -> set[str]:
    with tempfile.TemporaryDirectory(prefix="emage-root-parity-") as tmp:
        fresh = Path(tmp) / "fresh"
        run_fresh_install(fresh)
        return compute_drift(fresh, repo_root())


def load_declared() -> set[str]:
    return set(json.loads(BASELINE.read_text(encoding="utf-8"))["drift"])


class TestRootInstallParity(unittest.TestCase):
    def test_install_contract_is_parsed(self) -> None:
        """Guard against a vacuous gate: an unparsed installer yields no trees."""
        trees = parse_replaced_trees(INSTALLER.read_text(encoding="utf-8"))
        for tree in (".claude", ".cursor", ".gemini", ".github", ".opencode",
                     ".pi", ".cline", ".clinerules"):
            self.assertIn(tree, trees, f"install.sh no longer replaces {tree}")
        self.assertIn("settings.json", trees[".claude"])
        self.assertIn("workflows", trees[".github"])

    def test_root_matches_fresh_install_modulo_declared_drift(self) -> None:
        actual, declared = current_drift(), load_declared()
        undeclared = sorted(actual - declared)
        cured = sorted(declared - actual)
        self.assertFalse(
            undeclared or cured,
            "Root harness diverges from a fresh `install.sh --platform all` of "
            "implementation/ in ways tests/_baselines/root-install-drift.json "
            "does not declare.\n"
            f"  Undeclared drift (refresh the root, or declare it): {undeclared}\n"
            f"  Declared but no longer drifting (remove): {cured}\n"
            "Regenerate the list with: python3 -m "
            "tests.functional.test_root_install_parity --print-drift",
        )


class TestRootInstallParityDetector(unittest.TestCase):
    """The detector itself, against a synthetic root -- proves it is load-bearing."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="emage-root-parity-self-")
        cls.fresh = Path(cls._tmp.name) / "fresh"
        run_fresh_install(cls.fresh)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def setUp(self) -> None:
        import shutil
        self.root = Path(self._tmp.name) / f"root-{self._testMethodName}"
        shutil.copytree(self.fresh, self.root)

    def _write(self, rel: str, text: str) -> None:
        (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.root / rel).write_text(text, encoding="utf-8")

    def _edit_json(self, rel: str, mutate) -> None:
        data = json.loads((self.root / rel).read_text(encoding="utf-8"))
        mutate(data)
        self._write(rel, json.dumps(data, indent=4, sort_keys=True))

    def test_fresh_install_has_no_drift(self) -> None:
        self.assertEqual(compute_drift(self.fresh, self.root), set())

    def test_edited_projection_and_agents_md_are_drift(self) -> None:
        self._write(".claude/rules/git-workflow.md", "stale\n")
        self._write("AGENTS.md", "stale\n")
        self.assertEqual(compute_drift(self.fresh, self.root),
                         {".claude/rules/git-workflow.md", "AGENTS.md"})

    def test_missing_and_root_only_files_are_drift(self) -> None:
        (self.root / ".pi/agents/orchestrator.md").unlink()
        self._write(".clinerules/hand-written.md", "x\n")
        self.assertEqual(compute_drift(self.fresh, self.root),
                         {".pi/agents/orchestrator.md", ".clinerules/hand-written.md"})

    def test_project_local_paths_are_not_drift(self) -> None:
        self._write(".claude/settings.json", "{}\n")
        self._write(".claude/settings.local.json", "{}\n")
        self._write(".github/workflows/ci.yml", "on: push\n")
        self._write(".vscode/settings.json", "{}\n")
        self.assertEqual(compute_drift(self.fresh, self.root), set())

    def test_mcp_config_follows_merge_semantics(self) -> None:
        def add_local(d):
            d["mcpServers"]["local-only"] = {"command": "x"}
            d["inputs"] = []
        self._edit_json(".mcp.json", add_local)  # reordered + hand-added: legal
        self.assertEqual(compute_drift(self.fresh, self.root), set())

        def stale_value(d):  # an existing leaf the source would overwrite
            d["mcpServers"]["gitlab"]["command"] = "stale"
        self._edit_json(".pi/mcp.json", stale_value)
        (self.root / ".cursor/mcp.json.provenance.json").unlink()
        self.assertEqual(compute_drift(self.fresh, self.root),
                         {".pi/mcp.json", ".cursor/mcp.json",
                          ".cursor/mcp.json.provenance.json"})


def _main(argv: list[str]) -> int:
    if argv != ["--print-drift"]:
        print(__doc__)
        return 2
    print(json.dumps(sorted(current_drift()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
