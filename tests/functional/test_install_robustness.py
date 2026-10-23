"""`install.sh` robustness (T672): the tracked-debt items of the v8.0.0 reviews.

One class per item, each with the evidence that the guard is load-bearing (the mutation proof of
T672 removes the guard and shows the named test fails):

* SEC-T658-05  an existing MCP/settings config is merged in every mode (a plain install used to
               overwrite it), an invalid one is refused before anything is written, a replaced
               value is reported, and --projections-only keeps the Opencode/Gemini denials;
* SEC-T662-03  one SUPPORTED_PLATFORMS array drives usage, validation, `all`, the dispatch;
* TL-T649-06 / SEC-015  a missing or dash-leading --target/--platform value is a clear message;
* SEC-008 b    --dry-run creates nothing, the target directory included;
* SEC-004      the no-rsync --update builds the new tree next to the old one and swaps;
* SEC-005      nothing the installer creates is group- or world-writable;
* SEC-009/010  quoted copy-paste hints, a bounded search, no `eval`;
* QA-T648-02   the Playwright browser step and the .playwright-mcp/ advice are printed.

Every test runs against temporary directories; none installs into this repository.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import signal
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from tests._helpers.repo import implementation_root, list_platform_manifests, repo_root
from tests.functional.test_install_projections_only import _snapshot, run_installer
from tests.functional.test_install_script import _bash_array_definition, _bash_functions
from tests.functional.test_install_target_inside_repo import _paths
from tests.functional.test_install_update_root import _CopierMatrix, path_without

INSTALLER = repo_root() / "scripts" / "install.sh"
INSTALL_TEXT = INSTALLER.read_text(encoding="utf-8")
MCP_CONFIG = {
    "github": ".vscode/mcp.json",
    "gemini": ".gemini/settings.json",
    "opencode": ".opencode/opencode.json",
    "pi": ".pi/mcp.json",
    "claude-code": ".mcp.json",
    "cline": ".cline/mcp.json",
}
TREE = {"github": ".github", "gemini": ".gemini", "opencode": ".opencode", "pi": ".pi",
        "claude-code": ".claude", "cline": ".cline"}
DENIED = ("playwright_browser_run_code_unsafe", "playwright_browser_evaluate",
          "playwright_browser_file_upload", "playwright_browser_drag",
          "playwright_browser_drop", "playwright_browser_network_request")
BROWSER_COMMAND = re.search(r"^npx -y @playwright/mcp@\S+ install-browser chrome-for-testing$",
                            (implementation_root() / "PREREQUISITES.md").read_text(encoding="utf-8"),
                            re.M).group(0)


needs_non_root = unittest.skipIf(os.geteuid() == 0, "root ignores directory permission bits, the test would pass vacuously")


def _bash_output(script: str) -> str:
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True).stdout


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class _Scratch(unittest.TestCase):
    """A scratch directory, and a fresh single-platform install per call."""

    @classmethod
    def setUpClass(cls) -> None:
        if not shutil.which("bash"):
            raise unittest.SkipTest("bash not available on PATH")

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="emage-t672-")
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def installed(self, platform: str, name: str = "project", *flags: str) -> Path:
        target = self.tmp / name
        proc = run_installer(INSTALLER, target, "--platform", platform, *flags)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return target


class TestSupportedPlatformsArray(_Scratch):
    """SEC-T662-03: one array, derived everywhere, equal to the manifests."""

    def _array(self) -> list[str]:
        text = _bash_array_definition("SUPPORTED_PLATFORMS")
        return re.search(r"\((.*)\)", text, re.S).group(1).split()

    def test_array_equals_the_outputdir_bearing_manifests(self) -> None:
        manifests = set()
        for path in list_platform_manifests():
            data = json.loads(path.read_text(encoding="utf-8"))
            if "outputDir" in data:
                manifests.add(data["platform"])
        self.assertTrue(manifests)
        self.assertEqual(sorted(self._array()), sorted(manifests))

    def test_every_platform_has_every_per_platform_piece(self) -> None:
        for name in self._array():
            with self.subTest(platform=name):
                self.assertIn(f"install_{name.replace('-', '_')}() {{", INSTALL_TEXT)
                script = ("set -eu\n" + _bash_functions("printable", "internal_unknown_platform",
                                                        "platform_managed_paths", "platform_mcp_config")
                          + f"\nplatform_managed_paths {name}\nplatform_mcp_config {name}\n")
                self.assertIn(MCP_CONFIG[name], _bash_output(script).split())

    def test_usage_validation_and_all_expansion_are_derived_from_the_array(self) -> None:
        names = self._array()
        helptext = subprocess.run(["bash", str(INSTALLER), "--help"], capture_output=True,
                                  text=True, check=True).stdout
        self.assertIn("--platform <name>    " + " | ".join([*names, "all"]) + " (default: all)", helptext)
        bad = subprocess.run(["bash", str(INSTALLER), "--target", str(self.tmp / "t"), "--platform", "nope"],
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("supported: " + ", ".join([*names, "all"]) + ". Nothing was written.", bad.stderr)
        self.assertFalse((self.tmp / "t").exists())
        expanded = _bash_output("set -eu\nPLATFORM=all\n" + _bash_array_definition("SUPPORTED_PLATFORMS")
                                + _bash_functions("selected_platforms") + "\nselected_platforms\n").split()
        self.assertEqual(expanded, names)

    def test_a_platform_added_to_the_array_only_fails_closed(self) -> None:
        """No per-platform map knows `zeta`: the run stops with exit 70, nothing written."""
        repo = self.tmp / "repo"
        shutil.copytree(repo_root() / "scripts", repo / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (repo / "implementation").symlink_to(implementation_root(), target_is_directory=True)
        script = repo / "scripts" / "install.sh"
        script.write_text(INSTALL_TEXT.replace("SUPPORTED_PLATFORMS=(github ",
                                               "SUPPORTED_PLATFORMS=(zeta github ", 1), encoding="utf-8")
        target = self.tmp / "target"
        proc = run_installer(script, target, "--platform", "zeta")
        self.assertEqual(proc.returncode, 70, proc.stdout + proc.stderr)
        self.assertIn("internal: platform 'zeta' is in SUPPORTED_PLATFORMS", proc.stderr)
        self.assertEqual(_paths(target) if target.exists() else set(), set())


class TestMissingOrDashOptionValues(_Scratch):
    """TL-T649-06 and SEC-015: a clear message, never `$2: unbound variable`."""

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["bash", str(INSTALLER), *args], capture_output=True, text=True,
                              cwd=str(self.tmp))

    def test_missing_target_value(self) -> None:
        for args in (("--target",), ("--platform", "pi", "--target"), ("--target", "--update")):
            with self.subTest(args=args):
                proc = self._run(*args)
                self.assertEqual(proc.returncode, 1, proc.stderr)
                self.assertNotIn("unbound variable", proc.stderr)
                self.assertIn("error: --target requires a value", proc.stderr)
                self.assertEqual(os.listdir(self.tmp), [])

    def test_missing_platform_value(self) -> None:
        for args in (("--platform",), ("--target", "t", "--platform"), ("--platform", "--update")):
            with self.subTest(args=args):
                proc = self._run(*args)
                self.assertEqual(proc.returncode, 1, proc.stderr)
                self.assertNotIn("unbound variable", proc.stderr)
                self.assertIn("error: --platform requires a value", proc.stderr)
                self.assertEqual(os.listdir(self.tmp), [])

    def test_leading_dash_target_is_refused_with_the_dot_slash_hint(self) -> None:
        proc = self._run("--target", "-rf")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("error: --target requires a value, but got '-rf', which starts with '-'", proc.stderr)
        self.assertIn("write it as ./-rf", proc.stderr)
        self.assertEqual(os.listdir(self.tmp), [])

    def test_dot_slash_dash_target_is_accepted(self) -> None:
        proc = self._run("--target", "./-ok", "--platform", "pi", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(os.listdir(self.tmp), [], "--dry-run created something")


class TestDryRunCreatesNothing(_Scratch):
    """SEC-008 b: `--dry-run --target <new>/sub` used to create `sub`."""

    def test_new_target_is_not_created_in_any_mode(self) -> None:
        # plain: nothing to refuse, exit 0; --update / --projections-only need an existing install: exit 1
        for flags, code in (((), 0), (("--update",), 1), (("--projections-only",), 1)):
            with self.subTest(flags=flags):
                target = self.tmp / "parent" / "sub"
                proc = run_installer(INSTALLER, target, "--platform", "pi", "--dry-run", *flags)
                self.assertEqual(proc.returncode, code, proc.stdout + proc.stderr)
                if code:
                    self.assertIn("requires an existing emage.code install", proc.stderr)
                self.assertFalse((self.tmp / "parent").exists(), proc.stdout + proc.stderr)

    def test_dry_run_prints_the_actions_and_writes_nothing_over_an_existing_install(self) -> None:
        target = self.installed("claude-code")
        before = _snapshot(target)
        paths = _paths(target)
        for label, path in (("rsync", None), ("cp", path_without(self.tmp, "rsync"))):
            if label == "rsync" and not shutil.which("rsync"):
                continue
            with self.subTest(copier=label):
                proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update",
                                     "--dry-run", path=path)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual(_snapshot(target), before)
                self.assertEqual(_paths(target), paths, "a directory or file was created")
                if label == "cp":
                    self.assertRegex(proc.stdout, r"DRY-RUN: mv (-T )?--")


class TestExistingMcpConfigIsMerged(_Scratch):
    """SEC-T658-05 (a) (c) (d): decision -- merge in every mode, like --update."""

    def _opencode_with_user_rules(self, target: Path) -> None:
        path = target / ".opencode/opencode.json"
        data = _load(path)
        data["permission"] = {"*": "allow", "bash": "ask", DENIED[1]: "allow"}
        data["mcp"]["my-own-server"] = {"type": "local", "command": ["my-server"]}
        data["theme"] = "mine"
        _save(path, data)

    def _check_opencode(self, target: Path, stderr: str) -> None:
        data = _load(target / ".opencode/opencode.json")
        permission = data["permission"]
        self.assertEqual(permission["*"], "allow")
        self.assertEqual(permission["bash"], "ask")
        self.assertEqual(data["theme"], "mine")
        self.assertIn("my-own-server", data["mcp"])
        for name in DENIED:
            self.assertEqual(permission[name], "deny", name)
        self.assertEqual(list(permission)[-len(DENIED):], list(DENIED), "generated denials must come last")
        notes = [ln for ln in stderr.splitlines() if "replaced your value for" in ln]
        self.assertEqual(len(notes), 1, "one line")
        self.assertIn(f"opencode.json: replaced your value for permission.{DENIED[1]}", notes[0])

    def test_plain_install_merges_instead_of_overwriting(self) -> None:
        target = self.installed("opencode")
        self._opencode_with_user_rules(target)
        proc = run_installer(INSTALLER, target, "--platform", "opencode")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self._check_opencode(target, proc.stderr)

    def test_plain_install_keeps_a_hand_added_server_in_every_json_config(self) -> None:
        for platform in ("github", "claude-code", "pi", "cline"):
            with self.subTest(platform=platform):
                target = self.installed(platform, f"p-{platform}")
                path = target / MCP_CONFIG[platform]
                wrapper = "servers" if platform == "github" else "mcpServers"
                data = _load(path)
                data[wrapper]["hand-added"] = {"command": "local"}
                _save(path, data)
                proc = run_installer(INSTALLER, target, "--platform", platform)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual(_load(path)[wrapper]["hand-added"], {"command": "local"})

    def test_plain_install_unions_the_gemini_exclude_tools_and_reports_a_replaced_hook(self) -> None:
        target = self.installed("gemini")
        path = target / ".gemini/settings.json"
        data = _load(path)
        data["mcpServers"]["playwright"]["excludeTools"] = ["my_own_tool"]
        data["hooks"]["AfterTool"] = [{"matcher": "mine", "hooks": []}]
        _save(path, data)
        proc = run_installer(INSTALLER, target, "--platform", "gemini")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        excluded = _load(path)["mcpServers"]["playwright"]["excludeTools"]
        self.assertEqual(excluded[0], "my_own_tool")
        self.assertTrue({d.removeprefix("playwright_") for d in DENIED} <= set(excluded))
        self.assertIn("settings.json: replaced your value for hooks.AfterTool", proc.stderr)

    def test_projections_only_keeps_the_opencode_and_gemini_denials(self) -> None:
        """SEC-T658-05 (d): the end-to-end --projections-only test of the denial merge."""
        target = self.tmp / "both"
        proc = run_installer(INSTALLER, target, "--platform", "all")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self._opencode_with_user_rules(target)
        gemini = target / ".gemini/settings.json"
        data = _load(gemini)
        data["mcpServers"]["playwright"]["excludeTools"] = ["my_own_tool"]
        _save(gemini, data)
        ledger = (target / "docs/tasks/active-tasks.md").read_bytes()
        proc = run_installer(INSTALLER, target, "--platform", "all", "--projections-only")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self._check_opencode(target, proc.stderr)
        excluded = _load(gemini)["mcpServers"]["playwright"]["excludeTools"]
        self.assertEqual(excluded[0], "my_own_tool")
        self.assertTrue({d.removeprefix("playwright_") for d in DENIED} <= set(excluded))
        self.assertEqual((target / "docs/tasks/active-tasks.md").read_bytes(), ledger)

    def test_help_documents_the_decision(self) -> None:
        helptext = subprocess.run(["bash", str(INSTALLER), "--help"], capture_output=True,
                                  text=True, check=True).stdout
        self.assertIn("is MERGED in every mode, a plain\ninstall included, never overwritten", helptext)

    def test_claude_md_replacement_is_announced(self) -> None:
        target = self.installed("claude-code")
        quiet = run_installer(INSTALLER, target, "--platform", "claude-code")
        self.assertNotIn("replacing the existing", quiet.stderr, "an unchanged CLAUDE.md is not announced")
        (target / "CLAUDE.md").write_text("my own notes\n", encoding="utf-8")
        proc = run_installer(INSTALLER, target, "--platform", "claude-code")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("note: replacing the existing", proc.stderr)
        self.assertIn("CLAUDE.md", proc.stderr)


class TestInvalidConfigIsRefusedBeforeAnyWrite(_CopierMatrix):
    """SEC-T658-05 (b), TL-T649-02: validate the destination before the tree sync."""

    def _corrupt(self, platform: str, what: str) -> tuple[Path, Path]:
        target = self.tmp / f"{self._testMethodName}-{platform}-{what}"
        proc = run_installer(INSTALLER, target, "--platform", platform)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        victim = target / MCP_CONFIG[platform]
        if what == "sidecar":
            victim = Path(str(victim) + ".provenance.json")
            victim.write_text('["not", "an object"]', encoding="utf-8")
        else:
            victim.write_text('{"a": 1,  // a comment\n}\n', encoding="utf-8")
        stale = target / TREE[platform] / "stale-agent.md"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("must survive a refused run\n", encoding="utf-8")
        return target, victim

    def test_every_platform_config_and_mode(self) -> None:
        for platform in MCP_CONFIG:
            for flags in ((), ("--update",), ("--projections-only",), ("--update", "--dry-run")):
                with self.subTest(platform=platform, flags=flags):
                    target, victim = self._corrupt(platform, f"config-{'-'.join(flags) or 'plain'}")
                    before, paths = _snapshot(target), _paths(target)
                    proc = run_installer(INSTALLER, target, "--platform", platform, *flags)
                    self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                    self.assertNotIn("Traceback", proc.stderr)
                    lines = [ln for ln in proc.stderr.splitlines() if "is not valid JSON" in ln]
                    self.assertEqual(len(lines), 1, proc.stderr)
                    self.assertIn(str(victim), lines[0])
                    self.assertEqual(_snapshot(target), before, "something was written")
                    self.assertEqual(_paths(target), paths)

    def test_invalid_sidecar_is_refused_too(self) -> None:
        target, victim = self._corrupt("opencode", "sidecar")
        before = _snapshot(target)
        proc = run_installer(INSTALLER, target, "--platform", "opencode", "--update")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertIn(str(victim), proc.stderr)
        self.assertEqual(_snapshot(target), before)

    def test_under_both_copiers(self) -> None:
        for label, path in self.copiers():
            with self.subTest(copier=label):
                target, _victim = self._corrupt("gemini", f"config-{label}")
                before = _snapshot(target)
                proc = run_installer(INSTALLER, target, "--platform", "gemini", "--update", path=path)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertEqual(_snapshot(target), before)

    def test_a_valid_config_is_not_refused(self) -> None:
        target = self.tmp / f"{self._testMethodName}-valid"
        self.assertEqual(run_installer(INSTALLER, target, "--platform", "opencode").returncode, 0)
        proc = run_installer(INSTALLER, target, "--platform", "opencode", "--update")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


def _shim_dir(tmp: Path, name: str, body: str) -> Path:
    """A directory with a `cp` that runs `body` first, then the real cp."""
    shim = tmp / name
    shim.mkdir()
    cp = shim / "cp"
    cp.write_text("#!/bin/bash\n" + body + f'\nexec {shutil.which("cp")} "$@"\n', encoding="utf-8")
    cp.chmod(0o755)
    return shim


class TestSwapKeepsTheOldTreeUntilTheNewOneIsComplete(_CopierMatrix):
    """SEC-004: the no-rsync --update used to `rm -rf` the tree first."""

    def _installed_with_local_state(self) -> tuple[Path, dict]:
        target = self.tmp / f"{self._testMethodName}-t"
        proc = run_installer(INSTALLER, target, "--platform", "claude-code")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        (target / ".claude/settings.json").write_text('{"mine": true}\n', encoding="utf-8")
        (target / ".claude/stale-agent.md").write_text("stale\n", encoding="utf-8")
        return target, _snapshot(target / ".claude")

    def _path(self, shim: Path) -> str:
        return str(shim) + os.pathsep + self.no_rsync

    def _assert_failing_copy_changes_nothing(self, pattern: str, tree: str) -> None:
        """The copy into the sibling `pattern` fails: `tree` must be exactly as it was."""
        target, _ = self._installed_with_local_state()
        before = _snapshot(target / tree)
        self.assertTrue(before)
        shim = _shim_dir(self.tmp, f"failing-{self._testMethodName}",
                         f'for a in "$@"; do case "$a" in {pattern}) exit 1;; esac; done')
        proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update",
                             path=self._path(shim))
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(_snapshot(target / tree), before, f"{tree} changed")
        self.assertEqual([p for p in _paths(target) if ".emage-" in p], [], "a sibling was left behind")

    def test_a_failing_copy_leaves_the_old_tree_untouched(self) -> None:
        self._assert_failing_copy_changes_nothing("*/.claude.emage-new.*", ".claude")

    def test_a_failing_copy_leaves_the_old_runtime_tree_untouched(self) -> None:
        self._assert_failing_copy_changes_nothing("*/memory.emage-new.*", "implementation/runtime/memory")

    def test_a_terminated_run_leaves_the_old_tree_untouched(self) -> None:
        target, before = self._installed_with_local_state()
        marker = self.tmp / "hanging.marker"
        shim = _shim_dir(self.tmp, f"hanging-{self._testMethodName}",
                         'for a in "$@"; do case "$a" in */.claude.emage-new.*) '
                         f': > {marker}; sleep 60;; esac; done')
        env = dict(os.environ, PATH=self._path(shim))
        proc = subprocess.Popen(
            ["bash", str(INSTALLER), "--target", str(target), "--platform", "claude-code", "--update"],
            cwd=str(repo_root()), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True)
        try:
            deadline = time.time() + 60
            while not marker.exists() and time.time() < deadline:
                time.sleep(0.05)
            self.assertTrue(marker.exists(), "the update never reached the copy into the new tree")
            self.assertTrue([p for p in _paths(target) if ".emage-new." in p], "no build directory yet")
            os.killpg(proc.pid, signal.SIGTERM)
            proc.communicate(timeout=60)
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate()
        self.assertEqual(proc.returncode, 143)
        self.assertEqual(_snapshot(target / ".claude"), before, "the old tree changed")
        self.assertEqual([p for p in _paths(target) if ".emage-" in p], [], "a sibling was left behind")

    def test_a_normal_update_swaps_and_keeps_project_local_files(self) -> None:
        target, _ = self._installed_with_local_state()
        proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update",
                             path=self.no_rsync)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual((target / ".claude/settings.json").read_text(encoding="utf-8"), '{"mine": true}\n')
        self.assertFalse((target / ".claude/stale-agent.md").exists())
        self.assertEqual([p for p in _paths(target) if ".emage-" in p], [])


class TestNothingIsGroupOrWorldWritable(_CopierMatrix):
    """SEC-005: rsync -a copied source modes verbatim; a loose umask widened cp's."""

    def _source_repo(self, label: str) -> Path:
        repo = self.tmp / f"src-{label}"
        shutil.copytree(repo_root() / "scripts", repo / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(implementation_root(), repo / "implementation",
                        ignore=shutil.ignore_patterns("__pycache__", "_index"))
        for p in [repo / "implementation", *(repo / "implementation").rglob("*")]:
            if not p.is_symlink():
                p.chmod(p.stat().st_mode | stat.S_IWGRP | stat.S_IWOTH)
        return repo

    def _writable_by_others(self, root: Path) -> list[str]:
        return [p.relative_to(root).as_posix() for p in [root, *root.rglob("*")]
                if not p.is_symlink() and p.stat().st_mode & (stat.S_IWGRP | stat.S_IWOTH)]

    def _install(self, repo: Path, target: Path, path: str | None, *flags: str) -> None:
        env = dict(os.environ)
        if path is not None:
            env["PATH"] = path
        proc = subprocess.run(
            ["bash", str(repo / "scripts/install.sh"), "--target", str(target), "--platform", "all", *flags],
            cwd=str(repo), capture_output=True, text=True, env=env, preexec_fn=lambda: os.umask(0))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_install_and_update_create_nothing_group_or_world_writable(self) -> None:
        for label, path in self.copiers():
            repo = self._source_repo(label)
            with self.subTest(copier=label, mode="plain"):
                target = self.tmp / f"plain-{label}"
                self._install(repo, target, path)
                self.assertEqual(self._writable_by_others(target), [])
            with self.subTest(copier=label, mode="update"):
                target = self.tmp / f"update-{label}"
                target.mkdir(mode=0o755)
                (target / "AGENTS.md").write_text("# existing\n", encoding="utf-8")
                (target / "AGENTS.md").chmod(0o644)
                self._install(repo, target, path, "--update")
                self.assertEqual(self._writable_by_others(target), [])

    def test_a_kept_project_local_file_keeps_its_own_mode_under_the_cp_fallback(self) -> None:
        target = self.tmp / "kept"
        self.assertEqual(run_installer(INSTALLER, target, "--platform", "claude-code").returncode, 0)
        settings = target / ".claude/settings.json"
        settings.write_text("{}\n", encoding="utf-8")
        settings.chmod(0o664)
        env = dict(os.environ, PATH=self.no_rsync)
        proc = subprocess.run(
            ["bash", str(INSTALLER), "--target", str(target), "--platform", "claude-code", "--update"],
            cwd=str(repo_root()), capture_output=True, text=True, env=env,
            preexec_fn=lambda: os.umask(0o002))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(stat.S_IMODE(settings.stat().st_mode), 0o664)


class TestHintsAndShellHygiene(_Scratch):
    """SEC-009, SEC-010, TL-T649-06 (indentation)."""

    def test_hints_are_shell_quoted(self) -> None:
        target = self.tmp / "my proj's $(dir)"
        proc = run_installer(INSTALLER, target, "--platform", "pi")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        quoted = _bash_output(f"printf '%q' {shlex.quote(str(target))}")
        self.assertIn(f"Run from {quoted}:", proc.stdout)
        self.assertNotIn(f"Run from {target}:", proc.stdout)
        rel = "implementation/runtime/memory/requirements-mcp-server.txt"
        self.assertIn(f"pip install -r {rel}\n", proc.stdout)

    def test_only_the_shipped_runtime_directories_are_searched(self) -> None:
        target = self.installed("pi")
        stray = target / "implementation/runtime/other/requirements-mcp-server.txt"
        stray.parent.mkdir(parents=True)
        stray.write_text("mcp==0\n", encoding="utf-8")
        proc = run_installer(INSTALLER, target, "--platform", "pi", "--update")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("runtime/other", proc.stdout)
        self.assertIn("runtime/security/requirements-mcp-server.txt", proc.stdout)

    def test_no_eval_and_the_glob_options_are_restored(self) -> None:
        self.assertNotRegex(INSTALL_TEXT, r"(?m)^\s*eval\b")
        for before_dot, before_null in ((0, 0), (1, 0), (0, 1), (1, 1)):
            script = ("set -eu\n" + _bash_functions("list_dir_entries", "dir_is_empty")
                      + "\nDIR_ENTRIES=()\n"
                      + f"{'shopt -s dotglob' if before_dot else 'shopt -u dotglob'}\n"
                      + f"{'shopt -s nullglob' if before_null else 'shopt -u nullglob'}\n"
                      + "d=$(mktemp -d); : > \"$d/.hidden\"; : > \"$d/shown\"\n"
                      + "list_dir_entries \"$d\"; echo \"n=${#DIR_ENTRIES[@]}\"\n"
                      + "dir_is_empty \"$d\" && echo empty || echo notempty\n"
                      + "shopt -q dotglob && echo dot=1 || echo dot=0\n"
                      + "shopt -q nullglob && echo null=1 || echo null=0\nrm -rf \"$d\"\n")
            self.assertEqual(_bash_output(script).split(),
                             ["n=2", "notempty", f"dot={before_dot}", f"null={before_null}"])

    def test_the_three_blocks_are_indented_like_the_rest_of_the_file(self) -> None:
        self.assertNotRegex(INSTALL_TEXT, r"(?m)^[ \t]+\w+\(\) \{")
        self.assertNotIn("\t", INSTALL_TEXT)
        for name in ("install_agents_doc", "install_mcp_server_runtime", "install_common"):
            body = _bash_functions(name).splitlines()
            self.assertTrue(body[0].startswith(f"{name}() {{"), name)
            for line in body[1:-1]:
                if line.strip() and not line.lstrip().startswith("#"):
                    indent = len(line) - len(line.lstrip(" "))
                    self.assertEqual(indent % 2, 0, line)
                    self.assertGreaterEqual(indent, 2, line)


class TestPlaywrightNotice(_Scratch):
    """QA-T648-02: the browser step and the .playwright-mcp/ advice, from PREREQUISITES.md."""

    def test_command_matches_the_documentation_and_the_server_pin(self) -> None:
        servers = (implementation_root() / "knowledge/mcp/servers.yaml").read_text(encoding="utf-8")
        self.assertIn(BROWSER_COMMAND.split()[2], servers)

    def test_notice_is_printed_by_every_mode_that_ships_the_server(self) -> None:
        for platform in MCP_CONFIG:
            for flags in ((), ("--update",), ("--projections-only",)):
                with self.subTest(platform=platform, flags=flags):
                    target = self.tmp / f"{platform}-{'-'.join(flags) or 'plain'}"
                    if flags:
                        self.assertEqual(run_installer(INSTALLER, target, "--platform", platform).returncode, 0)
                    proc = run_installer(INSTALLER, target, "--platform", platform, *flags)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertIn(f"\n  {BROWSER_COMMAND}\n", proc.stdout)
                    self.assertIn("\n  .playwright-mcp/\n", proc.stdout)
                    self.assertIn("does not edit your .gitignore", proc.stdout)

    def test_notice_is_absent_when_no_selected_config_ships_the_server(self) -> None:
        repo = self.tmp / "repo"
        shutil.copytree(repo_root() / "scripts", repo / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(implementation_root(), repo / "implementation",
                        ignore=shutil.ignore_patterns("__pycache__", "_index"))
        cfg = repo / "implementation" / MCP_CONFIG["pi"]
        cfg.write_text(cfg.read_text(encoding="utf-8").replace('"playwright"', '"other-browser"'),
                       encoding="utf-8")
        proc = run_installer(repo / "scripts/install.sh", self.tmp / "t", "--platform", "pi")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("Playwright", proc.stdout)


def _shim_tool(tmp: Path, name: str, tool: str, body: str) -> Path:
    """A directory whose `tool` runs `body` first, then the real tool."""
    shim = tmp / name
    shim.mkdir()
    script = shim / tool
    script.write_text("#!/bin/bash\n" + body + f'\nexec {shutil.which(tool)} "$@"\n', encoding="utf-8")
    script.chmod(0o755)
    return shim


def _hang_once(marker: Path, pattern: str) -> str:
    """Shim body: the first call with an argument matching `pattern` creates `marker` and hangs."""
    return (f'for a in "$@"; do case "$a" in {pattern}) '
            f'if [ ! -e {marker} ]; then : > {marker}; sleep 60; fi;; esac; done')


class TestSwapInterruptions(_CopierMatrix):
    """SEC-T672-02: the old tree is restored or discarded correctly whenever the run is interrupted."""

    def _installed(self) -> tuple[Path, dict]:
        target = self.tmp / f"{self._testMethodName}-t"
        self.assertEqual(run_installer(INSTALLER, target, "--platform", "claude-code").returncode, 0)
        (target / ".claude/settings.json").write_text('{"mine": true}\n', encoding="utf-8")
        (target / ".claude/stale-agent.md").write_text("stale\n", encoding="utf-8")
        return target, _snapshot(target / ".claude")

    def _interrupt(self, target: Path, shim: Path, marker: Path, sig: int, tmpdir: Path | None = None):
        env = dict(os.environ, PATH=str(shim) + os.pathsep + self.no_rsync)
        if tmpdir is not None:
            env["TMPDIR"] = str(tmpdir)
        proc = subprocess.Popen(
            ["bash", str(INSTALLER), "--target", str(target), "--platform", "claude-code", "--update"],
            cwd=str(repo_root()), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True,
            # a runner started under nohup ignores SIGHUP, and an ignored signal cannot be trapped
            preexec_fn=lambda: signal.signal(signal.SIGHUP, signal.SIG_DFL))
        try:
            deadline = time.time() + 60
            while not marker.exists() and time.time() < deadline:
                time.sleep(0.05)
            self.assertTrue(marker.exists(), "the update never reached the hanging command")
            yield_state = self._state_at_hang(target)
            os.killpg(proc.pid, sig)
            proc.communicate(timeout=60)
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate()
        return proc.returncode, yield_state

    def _state_at_hang(self, target: Path) -> dict:
        return {"dest": (target / ".claude").exists(),
                "old": [p for p in _paths(target) if ".emage-old." in p],
                "new": [p for p in _paths(target) if ".emage-new." in p]}

    def test_hup_and_quit_are_trapped_like_term(self) -> None:
        for sig, code in ((signal.SIGHUP, 129), (signal.SIGQUIT, 131), (signal.SIGINT, 130)):
            with self.subTest(signal=sig.name):
                target, before = self._installed()
                marker = self.tmp / f"hang-{sig.name}.marker"
                shim = _shim_tool(self.tmp, f"cp-{sig.name}", "cp", _hang_once(marker, "*/.claude.emage-new.*"))
                rc, state = self._interrupt(target, shim, marker, sig)
                self.assertEqual(rc, code)
                self.assertTrue(state["new"], "the build sibling existed while hanging")
                self.assertEqual(_snapshot(target / ".claude"), before)
                self.assertEqual([p for p in _paths(target) if ".emage-" in p], [])

    def test_interrupt_between_the_two_renames_restores_the_old_tree(self) -> None:
        target, before = self._installed()
        marker = self.tmp / "between.marker"
        # the second rename is `mv -- <build> <dest>`: hang there, when dest is already moved aside
        shim = _shim_tool(self.tmp, "mv-between", "mv", _hang_once(marker, "*/.claude.emage-new.*"))
        rc, state = self._interrupt(target, shim, marker, signal.SIGTERM)
        self.assertEqual(rc, 143)
        self.assertFalse(state["dest"], ".claude must be absent while the second rename hangs")
        self.assertTrue(state["old"], "the old tree is the only copy at that moment")
        self.assertEqual(_snapshot(target / ".claude"), before, "the old tree must be restored exactly")
        self.assertEqual([p for p in _paths(target) if ".emage-" in p], [])

    def test_interrupt_after_the_second_rename_discards_the_old_tree(self) -> None:
        target, before = self._installed()
        marker = self.tmp / "after.marker"
        shim = _shim_tool(self.tmp, "rm-after", "rm", _hang_once(marker, "*.claude.emage-old.*"))
        rc, state = self._interrupt(target, shim, marker, signal.SIGTERM)
        self.assertEqual(rc, 143)
        self.assertTrue(state["dest"], "the swap itself had completed")
        self.assertFalse(state["new"])
        self.assertEqual([p for p in _paths(target) if ".emage-" in p], [], "the old tree was left behind")
        self.assertTrue((target / ".claude/agents").is_dir())
        self.assertEqual((target / ".claude/settings.json").read_text(encoding="utf-8"), '{"mine": true}\n')
        self.assertFalse((target / ".claude/stale-agent.md").exists(), "the update was applied")

    def test_a_second_signal_during_the_cleanup_does_not_cut_it_short(self) -> None:
        """T682 N-3: TERM hits the hanging second rename, the cleanup restores the old tree with a slow
        `mv`, and a second TERM arrives while it runs; the rest of the cleanup must still run."""
        target, before = self._installed()
        hang, restoring, seen_old = (self.tmp / n for n in ("hang.marker", "restoring.marker", "old.seen"))
        restore_args = self.tmp / "restore.args"
        shim = _shim_tool(self.tmp, "mv-slow-restore", "mv",
                          f'case " $* " in *"/.claude.emage-old."*)\n'
                          f'  if [ -e {seen_old} ]; then echo "$*" > {restore_args}; : > {restoring}; sleep 2;'
                          f' else : > {seen_old}; fi;;\n'
                          f'*.claude.emage-new.*) if [ ! -e {hang} ]; then : > {hang}; sleep 60; fi;; esac')
        scratch = self.tmp / "tmpdir-second-signal"
        scratch.mkdir()
        env = dict(os.environ, PATH=str(shim) + os.pathsep + self.no_rsync, TMPDIR=str(scratch))
        proc = subprocess.Popen(
            ["bash", str(INSTALLER), "--target", str(target), "--platform", "claude-code", "--update"],
            cwd=str(repo_root()), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True)
        try:
            deadline = time.time() + 60
            while not hang.exists() and time.time() < deadline:
                time.sleep(0.05)
            self.assertTrue(hang.exists(), "the update never reached the second rename")
            os.killpg(proc.pid, signal.SIGTERM)      # kills the hanging mv; the trap runs the cleanup
            while not restoring.exists() and time.time() < deadline:
                time.sleep(0.05)
            self.assertTrue(restoring.exists(), "the cleanup never reached the restore")
            # the second signal goes to the whole group, like a repeated Ctrl-C: it kills a cleanup
            # command that does not ignore it (the slow restore `mv`) and re-enters the traps of the installer
            os.killpg(proc.pid, signal.SIGTERM)
            proc.communicate(timeout=60)
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate()
        self.assertEqual(proc.returncode, 143)
        self.assertEqual(_snapshot(target / ".claude"), before, "the old tree must be restored")
        self.assertEqual([p for p in _paths(target) if ".emage-" in p], [], "a sibling tree was left behind")
        self.assertEqual(os.listdir(scratch), [], "the cleanup was cut short: a scan file survived")
        # N-3b: the restore is a `mv -T` too where mv is GNU
        gnu = "GNU coreutils" in subprocess.run(["mv", "--version"], capture_output=True, text=True).stdout
        self.assertEqual(restore_args.read_text(encoding="utf-8").startswith("-T -- "), gnu)

    def test_scan_files_are_removed_when_the_run_is_interrupted(self) -> None:
        target, before = self._installed()
        marker = self.tmp / "scan.marker"
        scratch = self.tmp / "tmpdir"
        scratch.mkdir()
        shim = _shim_tool(self.tmp, "find-scan", "find", _hang_once(marker, "*"))
        rc, _state = self._interrupt(target, shim, marker, signal.SIGTERM, tmpdir=scratch)
        self.assertEqual(rc, 143)
        self.assertEqual(os.listdir(scratch), [], "a scan file survived the interrupt")
        self.assertEqual(_snapshot(target / ".claude"), before)


def _harness(tmp: Path, scenario: str) -> subprocess.CompletedProcess[str]:
    """Run `scenario` in a shell that has only the swap functions of install.sh (and TARGET=tmp/t)."""
    script = (
        "set -euo pipefail\n"
        f"TARGET={shlex.quote(str(tmp / 't'))}\nDRY_RUN=0\nORIG_UMASK=\"$(umask)\"\n"
        'SWAP_BUILD=""\nSWAP_OLD=""\nSWAP_DEST=""\nSWAP_DONE=0\nTEMP_FILES=()\nMADE_TEMP=""\nDIR_ENTRIES=()\n'
        + _bash_functions("printable", "physical_path", "refuse_unsafe_path", "run", "make_temp_file",
                          "list_dir_entries", "copy_contents_excluding", "swap_build_into_place", "replace_tree_by_swap",
                          "copy_kept_path", "discard_old_tree", "detect_mv_flags", "swap_cleanup")
        + "\nMV_T=(); detect_mv_flags\ntrap swap_cleanup EXIT\n"
        'mkdir -p "$TARGET/tree" "$TARGET/src"\necho old > "$TARGET/tree/f"\necho new > "$TARGET/src/f"\n'
        + scenario)
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True)


class TestSwapSiblingHandling(_Scratch):
    """SEC-T672-03, SEC-T672-02 (cleanup branches), SEC-T672-12 (mode), refuse_unsafe_path on the sibling."""

    def _tree(self, name: str) -> Path:
        return self.tmp / "t" / name

    def test_existing_build_sibling_is_refused_and_left_alone(self) -> None:
        proc = _harness(self.tmp, 'mkdir "$TARGET/tree.emage-new.$$"; echo foreign > "$TARGET/tree.emage-new.$$/keep"\n'
                                  'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0\n')
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("already exists; remove it and re-run. Nothing was written.", proc.stderr)
        self.assertEqual((self._tree("tree") / "f").read_text(), "old\n")
        foreign = list((self.tmp / "t").glob("tree.emage-new.*/keep"))
        self.assertEqual([p.read_text() for p in foreign], ["foreign\n"], "a foreign directory must survive the cleanup")

    def test_symlink_at_a_sibling_name_is_refused_as_a_symlink_and_not_followed(self) -> None:
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "canary").write_text("canary\n")
        for sibling in ("new", "old"):
            with self.subTest(sibling=sibling):
                proc = _harness(self.tmp, f'ln -s {shlex.quote(str(outside))} "$TARGET/tree.emage-{sibling}.$$"\n'
                                          'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0\n')
                self.assertEqual(proc.returncode, 1, proc.stderr)
                self.assertIn("refusing to write through a symlink", proc.stderr)
                self.assertEqual(sorted(os.listdir(outside)), ["canary"])
                self.assertEqual((self._tree("tree") / "f").read_text(), "old\n")
                shutil.rmtree(self.tmp / "t")

    def test_an_old_sibling_that_appears_during_the_build_stops_before_the_first_rename(self) -> None:
        proc = _harness(self.tmp, 'copy_contents_excluding() { mkdir "$TARGET/tree.emage-old.$$"; echo foreign > "$TARGET/tree.emage-old.$$/keep"; }\n'
                                  'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0\n')
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("appeared while the new tree was built", proc.stderr)
        self.assertEqual((self._tree("tree") / "f").read_text(), "old\n")
        self.assertEqual([p.name for p in (self.tmp / "t").glob("tree.emage-new.*")], [], "our build is removed")
        self.assertEqual([p.read_text() for p in (self.tmp / "t").glob("tree.emage-old.*/keep")], ["foreign\n"])

    def test_a_build_directory_planted_between_the_check_and_mkdir_is_not_adopted(self) -> None:
        """`mkdir` without -p is the atomic create-or-fail: a directory someone plants in the gap survives."""
        proc = _harness(self.tmp, 'mkdir() { local last="${@: -1}"\n'
                                  '  if [[ "$last" == *.emage-new.* && ! -e "$last" ]]; then\n'
                                  '    command mkdir "$last"; echo foreign > "$last/keep"; fi\n'
                                  '  command mkdir "$@"; }\n'
                                  'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0\n')
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual((self._tree("tree") / "f").read_text(), "old\n")
        self.assertEqual([p.read_text() for p in (self.tmp / "t").glob("tree.emage-new.*/keep")], ["foreign\n"])

    def test_cleanup_restores_the_old_tree_only_when_dest_is_missing(self) -> None:
        proc = _harness(self.tmp, 'mv "$TARGET/tree" "$TARGET/tree.emage-old.$$"\n'
                                  'SWAP_OLD="$TARGET/tree.emage-old.$$"; SWAP_DEST="$TARGET/tree"\nexit 0\n')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self._tree("tree") / "f").read_text(), "old\n", "restored")
        self.assertEqual(list((self.tmp / "t").glob("*.emage-*")), [])
        shutil.rmtree(self.tmp / "t")
        proc = _harness(self.tmp, 'cp -R "$TARGET/tree" "$TARGET/tree.emage-old.$$"; echo newer > "$TARGET/tree/f"\n'
                                  'SWAP_OLD="$TARGET/tree.emage-old.$$"; SWAP_DEST="$TARGET/tree"; SWAP_DONE=1\nexit 0\n')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self._tree("tree") / "f").read_text(), "newer\n", "dest is kept")
        self.assertEqual(list((self.tmp / "t").glob("*.emage-*")), [], "the old tree is discarded")
        shutil.rmtree(self.tmp / "t")
        proc = _harness(self.tmp, 'cp -R "$TARGET/tree" "$TARGET/tree.emage-old.$$"; echo newer > "$TARGET/tree/f"\n'
                                  'SWAP_OLD="$TARGET/tree.emage-old.$$"; SWAP_DEST="$TARGET/tree"\nexit 0\n')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self._tree("tree") / "f").read_text(), "newer\n", "dest is kept")
        self.assertEqual(len(list((self.tmp / "t").glob("tree.emage-old.*"))), 1, "not finished: nothing is deleted")
        self.assertIn("the update did not finish", proc.stderr)

    def test_new_top_directory_gets_the_old_mode_without_group_or_world_write(self) -> None:
        for old_mode, expected in ((0o750, 0o750), (0o700, 0o700), (0o775, 0o755), (0o777, 0o755)):
            with self.subTest(old=oct(old_mode)):
                proc = _harness(self.tmp, f'chmod {old_mode:o} "$TARGET/tree"\n'
                                          'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0\n')
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(stat.S_IMODE(self._tree("tree").stat().st_mode), expected)
                self.assertEqual((self._tree("tree") / "f").read_text(), "new\n")
                shutil.rmtree(self.tmp / "t")

    @needs_non_root
    def test_a_read_only_or_unsearchable_old_tree_does_not_break_the_swap(self) -> None:
        """T682 N-2: the old mode is applied to the build directory after the copy, not before."""
        for old_mode in (0o555, 0o500, 0o600, 0o000):
            with self.subTest(old=oct(old_mode)):
                proc = _harness(self.tmp, f'chmod {old_mode:o} "$TARGET/tree"\n'
                                          'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0\n')
                tree = self._tree("tree")
                try:
                    self.assertEqual(proc.returncode, 0, proc.stderr)
                    self.assertEqual(stat.S_IMODE(tree.stat().st_mode), old_mode & ~0o022)
                    tree.chmod(0o700)
                    self.assertEqual((tree / "f").read_text(), "new\n")
                    self.assertEqual(list((self.tmp / "t").glob("*.emage-*")), [], "the old tree was left behind")
                finally:
                    for path in (self.tmp / "t").glob("tree*"):
                        path.chmod(0o700)
                    shutil.rmtree(self.tmp / "t")

    @needs_non_root
    def test_a_kept_path_is_copied_into_a_build_directory_that_ends_up_read_only(self) -> None:
        proc = _harness(self.tmp, 'echo mine > "$TARGET/tree/local"; chmod 555 "$TARGET/tree"\n'
                                  'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0 local\n')
        tree = self._tree("tree")
        try:
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(stat.S_IMODE(tree.stat().st_mode), 0o555)
            self.assertEqual((tree / "local").read_text(), "mine\n")
        finally:
            tree.chmod(0o700)

    @needs_non_root
    def test_a_read_only_installed_tree_can_be_updated_without_rsync(self) -> None:
        target = self.tmp / "ro-target"
        self.assertEqual(run_installer(INSTALLER, target, "--platform", "claude-code").returncode, 0)
        (target / ".claude").chmod(0o555)
        try:
            proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update",
                                 path=path_without(self.tmp, "rsync"))
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(stat.S_IMODE((target / ".claude").stat().st_mode), 0o555)
            self.assertEqual([p for p in _paths(target) if ".emage-" in p], [])
        finally:
            (target / ".claude").chmod(0o755)


class TestSwapRenamesUseMvDashT(_CopierMatrix):
    """T682 N-3b: where `mv` is GNU the renames of the swap are `mv -T`, elsewhere the plain rename."""

    def _update_logging_mv(self, version_line: str, reject_t: bool) -> tuple[subprocess.CompletedProcess, list[str]]:
        target = self.tmp / f"{self._testMethodName}-t"
        self.assertEqual(run_installer(INSTALLER, target, "--platform", "claude-code").returncode, 0)
        log = self.tmp / f"{self._testMethodName}.log"
        reject = '[ "$1" = "-T" ] && { echo "mv: invalid option -- T" >&2; exit 1; }\n' if reject_t else ""
        version = f'[ "$1" = "--version" ] && {{ echo {shlex.quote(version_line)}; exit 0; }}\n' if version_line else ""
        shim = _shim_tool(self.tmp, f"mv-{self._testMethodName}", "mv",
                          version + reject + f'case " $* " in *.emage-*) echo "$*" >> {log};; esac')
        proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update",
                             path=str(shim) + os.pathsep + self.no_rsync)
        calls = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
        return proc, calls

    def test_gnu_mv_gets_dash_t_for_both_renames(self) -> None:
        if "GNU coreutils" not in subprocess.run(["mv", "--version"], capture_output=True, text=True).stdout:
            self.skipTest("mv is not GNU here")
        proc, calls = self._update_logging_mv("", reject_t=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(calls and len(calls) % 2 == 0, calls)
        self.assertTrue(all(c.startswith("-T -- ") for c in calls), calls)
        for first, second in zip(calls[::2], calls[1::2]):   # dest -> old, then new -> dest
            self.assertIn(".emage-old.", first.split()[-1])
            self.assertIn(".emage-new.", second.split()[-2])

    def test_the_rename_into_a_missing_destination_uses_dash_t_too(self) -> None:
        if "GNU coreutils" not in subprocess.run(["mv", "--version"], capture_output=True, text=True).stdout:
            self.skipTest("mv is not GNU here")
        target = self.tmp / f"{self._testMethodName}-t"
        self.assertEqual(run_installer(INSTALLER, target, "--platform", "claude-code").returncode, 0)
        shutil.rmtree(target / ".claude")
        log = self.tmp / f"{self._testMethodName}.log"
        shim = _shim_tool(self.tmp, f"mv-{self._testMethodName}", "mv",
                          f'case " $* " in *"/.claude.emage-"*) echo "$*" >> {log};; esac')
        proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update",
                             path=str(shim) + os.pathsep + self.no_rsync)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        calls = log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(calls), 1, calls)
        self.assertTrue(calls[0].startswith("-T -- ") and ".claude.emage-new." in calls[0], calls)
        self.assertTrue((target / ".claude/agents").is_dir())

    def test_a_non_gnu_mv_keeps_the_plain_rename(self) -> None:
        proc, calls = self._update_logging_mv("mv (BusyBox v1.36)", reject_t=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(calls and len(calls) % 2 == 0, calls)
        self.assertTrue(all(c.startswith("-- ") for c in calls), calls)
        self.assertEqual([p for p in _paths(self.tmp / f"{self._testMethodName}-t") if ".emage-" in p], [])


class TestSwapCleanupStates(_Scratch):
    """T682 SEC-T682-01/-02/-05: swap_cleanup acts on an explicit SWAP_DONE, not on what exists."""

    def _gnu(self) -> None:
        if "GNU coreutils" not in subprocess.run(["mv", "--version"], capture_output=True, text=True).stdout:
            self.skipTest("mv is not GNU here (-T is what makes the rename fail instead of nest)")

    def test_a_failed_second_rename_with_a_recreated_dest_deletes_nothing(self) -> None:
        proc = _harness(self.tmp,
                        'mv() { if [[ "${@: -1}" == "$TARGET/tree" && "$*" == *.emage-new.* ]]; then\n'
                        '    command mkdir "$TARGET/tree"; echo recreated > "$TARGET/tree/mine"; return 1; fi\n'
                        '  command mv "$@"; }\n'
                        'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0\n')
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        tree = self.tmp / "t" / "tree"
        self.assertEqual((tree / "mine").read_text(), "recreated\n", "dest is left as it was found")
        olds = list((self.tmp / "t").glob("tree.emage-old.*"))
        self.assertEqual([(o / "f").read_text() for o in olds], ["old\n"], "the user's tree must not be deleted")
        self.assertIn("the update did not finish", proc.stderr)
        self.assertEqual(list((self.tmp / "t").glob("tree.emage-new.*")), [], "our build is still removed")

    @needs_non_root
    def test_a_foreign_old_directory_planted_after_the_check_is_never_touched(self) -> None:
        self._gnu()
        proc = _harness(self.tmp,
                        'mv() { local last="${@: -1}"\n'
                        '  if [[ "$last" == *.emage-old.* && ! -e "$last" ]]; then\n'
                        '    command mkdir "$last"; echo foreign > "$last/keep"; chmod 500 "$last"; fi\n'
                        '  command mv "$@"; }\n'
                        'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0\n')
        foreign = list((self.tmp / "t").glob("tree.emage-old.*"))
        try:
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertEqual((self.tmp / "t" / "tree" / "f").read_text(), "old\n", "dest is still the user's tree")
            self.assertEqual([(p / "keep").read_text() for p in foreign], ["foreign\n"])
            self.assertEqual([stat.S_IMODE(p.stat().st_mode) for p in foreign], [0o500], "chmod-ed")
            self.assertIn("were both left in place", proc.stderr)
        finally:
            for p in foreign:
                p.chmod(0o700)

    @needs_non_root
    def test_the_build_tree_is_removed_even_when_it_was_made_read_only(self) -> None:
        proc = _harness(self.tmp,
                        'chmod 555 "$TARGET/tree"\n'
                        'copy_contents_excluding() { echo x > "$3/f"; mkdir "$TARGET/tree.emage-old.$$"; }\n'
                        'replace_tree_by_swap "$TARGET/src" "$TARGET/tree" 0\n')
        (self.tmp / "t" / "tree").chmod(0o700)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("appeared while the new tree was built", proc.stderr)
        leftovers = list((self.tmp / "t").glob("tree.emage-new.*"))
        for p in leftovers:
            p.chmod(0o700)
        self.assertEqual(leftovers, [], "the read-only build tree was left behind")

    def test_discard_old_tree_never_chmods_through_a_symlink(self) -> None:
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "canary").write_text("canary\n")
        outside.chmod(0o500)
        try:
            proc = _harness(self.tmp, f'ln -s {shlex.quote(str(outside))} "$TARGET/link"\n'
                                      'discard_old_tree "$TARGET/link"\n')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(stat.S_IMODE(outside.stat().st_mode), 0o500, "the link target was chmod-ed")
            self.assertFalse((self.tmp / "t" / "link").is_symlink(), "the link itself is removed")
            self.assertTrue((outside / "canary").exists())
        finally:
            outside.chmod(0o700)


class TestStaleSwapSiblingsAreRefused(_Scratch):
    """T682 N-7: a `<tree>.emage-old.<pid>` / `.emage-new.<pid>` left by a killed run stops the next run."""

    MODES = {"plain": (), "update": ("--update",), "dry-run": ("--update", "--dry-run"),
             "projections-only": ("--projections-only",)}

    def _stale(self, rel: str, kind: str) -> Path:
        sibling = self.tmp / "project" / f"{rel}.emage-{kind}.4242"
        sibling.mkdir(parents=True)
        (sibling / "settings.json").write_text('{"mine": true}\n', encoding="utf-8")
        return sibling

    def test_every_mode_refuses_and_writes_and_removes_nothing(self) -> None:
        target = self.installed("claude-code")
        for rel, kind in ((".claude", "old"), (".claude", "new"), ("implementation/runtime/memory", "old"),
                          ("implementation/runtime/handoff", "new")):
            sibling = self._stale(rel, kind)
            before, paths = _snapshot(target), _paths(target)
            for label, flags in self.MODES.items():
                if label == "projections-only" and rel.startswith("implementation/"):
                    continue    # that mode does not manage the runtime trees
                with self.subTest(sibling=sibling.name, mode=label, rel=rel):
                    proc = run_installer(INSTALLER, target, "--platform", "claude-code", *flags)
                    self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                    self.assertIn("a previous update of this target was interrupted", proc.stderr)
                    self.assertIn(str(sibling), proc.stderr)
                    self.assertIn("Nothing was written and nothing was removed", proc.stderr)
                    self.assertEqual(_snapshot(target), before)
                    self.assertEqual(_paths(target), paths)
                    self.assertEqual((sibling / "settings.json").read_text(encoding="utf-8"), '{"mine": true}\n')
            shutil.rmtree(sibling)

    def test_an_old_tree_whose_destination_is_missing_gets_the_restore_command(self) -> None:
        target = self.installed("claude-code")
        os.rename(target / ".claude", target / ".claude.emage-old.4242")
        proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn(f"[ ! -e {shlex.quote(str(target / '.claude'))} ] && "
                      f"mv -- {shlex.quote(str(target / '.claude.emage-old.4242'))} {shlex.quote(str(target / '.claude'))}",
                      proc.stderr)
        self.assertFalse((target / ".claude").exists(), "nothing may be installed over the missing tree")
        self.assertTrue((target / ".claude.emage-old.4242" / "agents").is_dir())

    HOSTILE = {
        "semicolon": "4242;touch MARKER;",
        "command-substitution": "4242$(touch MARKER)",
        "backtick": "4242`touch MARKER`",
        "space": "4242 touch MARKER",
        "newline": "4242\ntouch MARKER\n",
        "bidi-override": "4242\u202etxt.exe",
        "quote-and-ampersand": "4242'; touch MARKER &",
    }

    def _hint(self, stderr: str) -> str:
        lines = [line.strip() for line in stderr.splitlines() if line.startswith("      [ ! -e ")]
        self.assertEqual(len(lines), 1, stderr)
        return lines[0]

    def _refused_with_hostile_sibling(self, target: Path, suffix: str, utf8: bool) -> tuple[Path, str]:
        old = target / f".claude.emage-old.{suffix}"
        os.rename(target / ".claude", old)
        env = dict(os.environ, LC_ALL="C.UTF-8" if utf8 else "C")
        proc = subprocess.run(["bash", str(INSTALLER), "--target", str(target), "--platform", "claude-code", "--update"],
                              capture_output=True, text=True, errors="surrogateescape", env=env, timeout=120)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        return old, proc.stderr

    def test_the_printed_hint_is_data_not_code_for_a_hostile_name(self) -> None:
        """The hint is run through `bash -c`: no marker appears and the tree is restored (SEC-T682-03)."""
        for utf8 in (True, False):
            for label, suffix in self.HOSTILE.items():
                with self.subTest(name=label, utf8=utf8):
                    case = f"{label}-{'utf8' if utf8 else 'c'}"
                    target = self.installed("claude-code", f"project-{case}")
                    old, stderr = self._refused_with_hostile_sibling(target, suffix, utf8)
                    work = self.tmp / f"work-{case}"
                    work.mkdir()
                    hint = self._hint(stderr)
                    self.assertTrue(hint.startswith("[ ! -e "), hint)
                    self.assertIn("] && mv -- ", hint)
                    self.assertTrue(stderr.isascii(), "the message must be byte-wise ASCII, whatever the locale")
                    # Run once while DEST is missing: restores, and nothing else happens.
                    ran = subprocess.run(["bash", "-c", hint], cwd=work, capture_output=True, text=True,
                                         errors="surrogateescape", env=dict(os.environ, LC_ALL="C"))
                    self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
                    self.assertEqual(os.listdir(work), [], "a side effect of the hint (a marker in the cwd)")
                    self.assertTrue((target / ".claude" / "agents").is_dir(), "the old tree was not restored")
                    self.assertFalse(os.path.lexists(old))
                    # Pasting it again, with DEST recreated, does nothing at all (no nesting).
                    os.rename(target / ".claude", old)
                    (target / ".claude").mkdir()
                    before = _paths(target)
                    again = subprocess.run(["bash", "-c", hint], cwd=work, capture_output=True, text=True,
                                           errors="surrogateescape", env=dict(os.environ, LC_ALL="C"))
                    self.assertNotEqual(again.returncode, 0)
                    self.assertEqual(_paths(target), before, "the hint nested the old tree inside the recreated one")
                    self.assertEqual(os.listdir(work), [])

    def test_a_hostile_unfinished_new_tree_name_is_ascii(self) -> None:
        for label, suffix in (("bidi", "4242\u202etxt"), ("escape", "\x1b[31mx"), ("newline", "4242\nx")):
            with self.subTest(name=label):
                target = self.installed("claude-code", f"project-{label}")
                (target / f".claude.emage-new.{suffix}").mkdir()
                env = dict(os.environ, LC_ALL="C.UTF-8")
                proc = subprocess.run(["bash", str(INSTALLER), "--target", str(target), "--platform", "claude-code",
                                       "--update"], capture_output=True, text=True, errors="surrogateescape", env=env,
                                      timeout=120)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertTrue(proc.stderr.isascii(), proc.stderr)
                self.assertNotIn("\x1b", proc.stderr)

    def test_a_hostile_target_directory_name_is_ascii_in_the_message_and_data_in_the_hint(self) -> None:
        """The target's own name reaches the second display line and both hint operands."""
        names = {"bidi": "pro\u202eject", "escape": "pro\x1b[31mject", "command": "pro$(touch MARKER)ject",
                 "newline": "pro\ntouch MARKER\nject"}
        for label, name in names.items():
            with self.subTest(name=label):
                target = self.installed("claude-code", name)
                old, stderr = self._refused_with_hostile_sibling(target, "4242", True)
                self.assertTrue(stderr.isascii(), stderr)
                self.assertNotIn("\x1b", stderr)
                work = self.tmp / f"work-{label}"
                work.mkdir()
                ran = subprocess.run(["bash", "-c", self._hint(stderr)], cwd=work, capture_output=True, text=True,
                                     errors="surrogateescape", env=dict(os.environ, LC_ALL="C"))
                self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
                self.assertEqual(os.listdir(work), [])
                self.assertTrue((target / ".claude" / "agents").is_dir())

    def test_the_hint_names_are_octal_escaped_in_every_locale(self) -> None:
        target = self.installed("claude-code")
        _, stderr = self._refused_with_hostile_sibling(target, "4242\u202etxt", True)
        self.assertIn("\\342\\200\\256", self._hint(stderr))
        self.assertNotIn("\u202e", stderr)
        self.assertTrue(stderr.isascii(), stderr)

    def test_a_symlink_at_a_sibling_name_is_refused_and_not_followed(self) -> None:
        target = self.installed("claude-code")
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "canary").write_text("canary\n")
        for label, link_target in (("to a directory", outside), ("dangling", self.tmp / "does-not-exist")):
            with self.subTest(label):
                link = target / ".claude.emage-new.4242"
                link.symlink_to(link_target, target_is_directory=True)
                proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update")
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn(".claude.emage-new.4242", proc.stderr)
                self.assertEqual(os.listdir(outside), ["canary"])
                link.unlink()

    def test_the_name_is_printed_without_control_characters(self) -> None:
        target = self.installed("claude-code")
        (target / ".claude.emage-old.\x1b[31mx").mkdir()
        proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertNotIn("\x1b", proc.stderr)

    def test_a_sibling_of_a_platform_that_is_not_selected_is_left_alone(self) -> None:
        target = self.installed("claude-code")
        (target / ".gemini.emage-old.4242").mkdir()
        proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((target / ".gemini.emage-old.4242").is_dir())

    def test_a_clean_target_is_not_refused(self) -> None:
        target = self.installed("claude-code")
        proc = run_installer(INSTALLER, target, "--platform", "claude-code", "--update")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class TestPlatformMapsAreVerifiedBeforeAnyWrite(_Scratch):
    """SEC-T672-04: a platform missing from any one per-platform piece stops the run up front."""

    BREAKS = {
        "install function": ("install_pi() {", "install_pix() {"),
        "managed paths": ("    pi) printf '%s\\n' .pi .pi/mcp.json .pi/mcp.json.provenance.json ;;\n", ""),
        "mcp config": ("    pi) printf '%s\\n' .pi/mcp.json ;;\n", ""),
    }

    def _broken_installer(self, label: str) -> Path:
        repo = self.tmp / f"repo-{label.replace(' ', '-')}"
        shutil.copytree(repo_root() / "scripts", repo / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        (repo / "implementation").symlink_to(implementation_root(), target_is_directory=True)
        old, new = self.BREAKS[label]
        script = repo / "scripts" / "install.sh"
        text = script.read_text(encoding="utf-8")
        self.assertEqual(text.count(old), 1, f"the {label} break does not apply: {old!r}")
        script.write_text(text.replace(old, new), encoding="utf-8")
        return script

    def test_each_missing_piece_stops_all_and_pi_runs_before_the_target_exists(self) -> None:
        for label in self.BREAKS:
            script = self._broken_installer(label)
            for platform in ("all", "pi"):
                with self.subTest(missing=label, platform=platform):
                    target = self.tmp / f"t-{label.replace(' ', '-')}-{platform}"
                    proc = run_installer(script, target, "--platform", platform)
                    self.assertEqual(proc.returncode, 70, proc.stdout + proc.stderr)
                    self.assertIn("internal: platform 'pi' is in SUPPORTED_PLATFORMS", proc.stderr)
                    self.assertFalse(target.exists(), "something was written before the check")

    def test_only_selected_platforms_are_verified(self) -> None:
        script = self._broken_installer("install function")
        target = self.tmp / "github-only"
        proc = run_installer(script, target, "--platform", "github")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
