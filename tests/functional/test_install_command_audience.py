"""Authoring-only commands never reach a target project (T725, TD-T671-P5).

Every command declares ``audience: authoring | target | both`` (T556). Until
T725 nothing acted on it, so ``/prepare-release`` (``authoring``) was installed
into every target project, where it names paths that do not exist there.

The contract under test:

* ``sync.mjs`` keeps every command in the generated trees (the authoring set)
  and lists the ``authoring`` ones, relative to the tree, under
  ``authoringOnly`` in each tree's ``.generated-manifest.json``; a missing or
  unknown ``audience:`` stops the generator.
* ``install.sh`` removes those paths from a target after installing a tree, in
  every mode, so a plain install never leaves one and ``--update`` /
  ``--projections-only`` delete a copy an older install left behind -- under
  ``rsync`` and under the ``cp`` fallback.
* An authoring checkout -- recognised, as ``/discover-skills`` does, by the
  registry file ``implementation/registry/index.json`` -- keeps them; the
  repository root is one (its parity oracle is such an install, see
  ``test_root_install_parity``).
* A bad ``authoringOnly`` entry stops the installer before anything is written.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root, knowledge_root, repo_root
from tests.functional.test_install_projections_only import path_without_rsync, run_installer

INSTALLER = repo_root() / "scripts" / "install.sh"
PLATFORMS_DIR = implementation_root() / "platforms"
MANIFEST_NAME = ".generated-manifest.json"
AUTHORING_MARKER = Path("implementation") / "registry" / "index.json"
SINGLE_PLATFORMS = ("github", "gemini", "opencode", "pi", "claude-code", "cline")
_AUDIENCE_RE = re.compile(r"^audience:\s*(\S+)\s*$", re.M)


def platform_manifests() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(PLATFORMS_DIR.glob("*.json")) if not p.name.startswith("_")]


def authoring_commands() -> set[str]:
    """Base names of the knowledge commands that declare ``audience: authoring``."""
    names = set()
    for path in sorted((knowledge_root() / "commands").glob("*.md")):
        match = _AUDIENCE_RE.search(path.read_text(encoding="utf-8").split("\n---\n", 1)[0])
        if match and match.group(1) == "authoring":
            names.add(path.stem)
    return names


def expected_authoring_only(manifest: dict) -> list[str]:
    commands = manifest["fileMap"].get("commands")
    if commands is None:
        return []
    return sorted(f"{commands['dir']}/{name}{commands['ext']}" for name in authoring_commands())


def generated_lists() -> dict[str, list[str]]:
    """outputDir -> the authoringOnly list of its generated manifest."""
    out = {}
    for manifest in platform_manifests():
        tree = manifest["outputDir"]
        data = json.loads((implementation_root() / tree / MANIFEST_NAME).read_text(encoding="utf-8"))
        out[tree] = data["authoringOnly"]
    return out


def withheld_present(target: Path) -> set[str]:
    """Every authoring-only path that exists in the target."""
    return {f"{tree}/{rel}" for tree, rels in generated_lists().items()
            for rel in rels if (target / tree / rel).exists()}


def all_withheld() -> set[str]:
    return {f"{tree}/{rel}" for tree, rels in generated_lists().items() for rel in rels}


class TestGeneratorListsAuthoringCommands(unittest.TestCase):
    def test_prepare_release_is_the_authoring_command(self) -> None:
        # Guards against a vacuous suite: today exactly one command is authoring-only.
        self.assertEqual(authoring_commands(), {"prepare-release"})

    def test_manifest_lists_exactly_the_authoring_commands(self) -> None:
        for manifest in platform_manifests():
            tree = manifest["outputDir"]
            with self.subTest(platform=manifest["platform"]):
                data = json.loads((implementation_root() / tree / MANIFEST_NAME)
                                  .read_text(encoding="utf-8"))
                self.assertEqual(data["authoringOnly"], expected_authoring_only(manifest))
                for rel in data["authoringOnly"]:
                    self.assertIn(rel, data["files"])
                    self.assertTrue((implementation_root() / tree / rel).is_file(),
                                    f"the mirror must keep {tree}/{rel}")

    def test_generator_rejects_unknown_or_missing_audience(self) -> None:
        if not shutil.which("node"):
            self.skipTest("node not on PATH")
        for frontmatter_line in ("audience: Authoring", None):
            with self.subTest(audience=frontmatter_line), \
                    tempfile.TemporaryDirectory(prefix="emage-audience-") as tmp:
                knowledge = Path(tmp) / "knowledge"
                shutil.copytree(knowledge_root(), knowledge)
                command = knowledge / "commands" / "prepare-release.md"
                text = command.read_text(encoding="utf-8")
                replacement = "" if frontmatter_line is None else frontmatter_line + "\n"
                command.write_text(text.replace("audience: authoring\n", replacement, 1),
                                   encoding="utf-8")
                proc = subprocess.run(
                    ["node", str(implementation_root() / "scripts" / "sync.mjs"),
                     "--root", str(implementation_root()), "--knowledge", str(knowledge),
                     "--check"],
                    capture_output=True, text=True, timeout=300, check=False)
                self.assertNotEqual(proc.returncode, 0, proc.stdout)
                self.assertIn("audience:", proc.stderr)
                self.assertIn("prepare-release.md", proc.stderr)


class _InstallFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("bash"):
            raise unittest.SkipTest("bash not available on PATH")
        cls._tmp = tempfile.TemporaryDirectory(prefix="emage-command-audience-")
        cls.tmp = Path(cls._tmp.name)
        cls.no_rsync = path_without_rsync(cls.tmp)
        if not all_withheld():
            raise AssertionError("no authoring-only command is listed; the suite would be vacuous")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def copiers(self):
        out = [("cp", self.no_rsync)]
        if shutil.which("rsync"):
            out.insert(0, ("rsync", None))
        return out

    def install(self, target: Path, *args: str, path: str | None = None) -> None:
        proc = run_installer(INSTALLER, target, *args, path=path)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def plant_stale_copies(self, target: Path) -> None:
        """What an install before T725 left: every authoring-only command."""
        for rel in all_withheld():
            (target / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(implementation_root() / rel, target / rel)


class TestTargetInstallWithholds(_InstallFixture):
    def test_platform_all_target_has_no_authoring_command(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self.tmp / f"all-{label}"
                self.install(target, "--platform", "all", path=path)
                self.assertEqual(withheld_present(target), set())
                self.assertEqual(list(target.rglob("*prepare-release*")), [])
                # A `both` command still ships: the filter is not over-broad.
                self.assertTrue((target / ".claude/commands/plan.md").is_file())
                self.assertTrue((target / ".github/prompts/plan.prompt.md").is_file())

    def test_each_single_platform_target_has_no_authoring_command(self) -> None:
        for platform in SINGLE_PLATFORMS:
            with self.subTest(platform=platform):
                target = self.tmp / f"single-{platform}"
                self.install(target, "--platform", platform)
                self.assertEqual(list(target.rglob("*prepare-release*")), [])

    def test_dry_run_of_a_target_install_writes_nothing(self) -> None:
        target = self.tmp / "dry-run"
        proc = run_installer(INSTALLER, target, "--platform", "all", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse(target.exists())


class TestAuthoringCheckoutKeeps(_InstallFixture):
    def test_registry_file_marks_an_authoring_checkout(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target = self.tmp / f"authoring-{label}"
                (target / AUTHORING_MARKER).parent.mkdir(parents=True)
                (target / AUTHORING_MARKER).write_text("{}\n", encoding="utf-8")
                self.install(target, "--platform", "all", path=path)
                self.assertEqual(withheld_present(target), all_withheld())
                for rel in all_withheld():
                    self.assertEqual((target / rel).read_bytes(),
                                     (implementation_root() / rel).read_bytes())

    def test_implementation_dir_alone_is_not_an_authoring_checkout(self) -> None:
        # Every target has implementation/runtime/; only the registry file counts.
        target = self.tmp / "runtime-only"
        (target / "implementation" / "registry").mkdir(parents=True)
        self.install(target, "--platform", "all")
        self.assertEqual(withheld_present(target), set())

    def test_repository_root_is_an_authoring_checkout(self) -> None:
        self.assertTrue((repo_root() / AUTHORING_MARKER).is_file())
        self.assertEqual(withheld_present(repo_root()), all_withheld())


class TestStaleCopiesAreRemoved(_InstallFixture):
    def _refresh_removes(self, mode: str) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label, mode=mode):
                target = self.tmp / f"stale{mode}-{label}"
                self.install(target, "--platform", "all", path=path)
                self.plant_stale_copies(target)
                self.assertEqual(withheld_present(target), all_withheld())
                proc = run_installer(INSTALLER, target, "--platform", "all", mode,
                                     "--dry-run", path=path)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("prepare-release", proc.stdout)
                self.assertEqual(withheld_present(target), all_withheld(), "dry-run removed")
                self.install(target, "--platform", "all", mode, path=path)
                self.assertEqual(withheld_present(target), set())

    def test_update_removes_a_stale_copy(self) -> None:
        self._refresh_removes("--update")

    def test_projections_only_removes_a_stale_copy(self) -> None:
        self._refresh_removes("--projections-only")


class TestBadAuthoringOnlyEntryIsRefused(_InstallFixture):
    def _repo_with_entry(self, name: str, entry) -> Path:
        repo = self.tmp / name
        shutil.copytree(repo_root() / "scripts", repo / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(implementation_root(), repo / "implementation",
                        ignore=shutil.ignore_patterns("__pycache__", "_index"))
        manifest = repo / "implementation" / ".claude" / MANIFEST_NAME
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["authoringOnly"] = entry
        manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return repo

    def test_unsafe_entries_stop_the_install_before_any_write(self) -> None:
        cases = {"parent": ["../AGENTS.md"], "absolute": ["/etc/passwd"],
                 "not-a-list": "commands/plan.md", "newline": ["a\nb"]}
        for name, entry in cases.items():
            with self.subTest(case=name):
                repo = self._repo_with_entry(f"bad-repo-{name}", entry)
                target = self.tmp / f"bad-target-{name}"
                proc = run_installer(repo / "scripts" / "install.sh", target,
                                     "--platform", "claude-code")
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn("authoringOnly", proc.stderr)
                self.assertFalse(target.exists(), "the installer wrote before refusing")


if __name__ == "__main__":
    unittest.main()
