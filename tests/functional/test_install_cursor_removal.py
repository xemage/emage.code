"""`install.sh` after Cursor support was removed (T662, ADR-010 D3, adopter behaviour B).

* ``--platform cursor`` and any other unknown value are rejected right after argument
  parsing: exit 1, a removal message for ``cursor``, and nothing written -- not even
  the target directory (before this change a typo created it first).
* A project that still holds an emage.code ``.cursor/`` from an earlier release gets a
  read-only notice on ``--update`` and ``--projections-only``; every byte under
  ``.cursor/`` stays as it was. Before this change the same run deleted the files a
  user had added there.
* The installer never deletes or modifies ``.cursor``, under rsync and under the cp
  fallback.
* End to end: a real ``git archive v8.0.0`` install (``--platform all``, which wrote
  ``.cursor/``) is updated with this tree's installer.

The proofs run under rsync (when present) and with rsync genuinely absent from PATH.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root
from tests.functional.test_install_projections_only import (
    _snapshot,
    path_without_rsync,
    run_installer,
)
from tests.functional.test_install_update_root import _CopierMatrix

INSTALLER = repo_root() / "scripts" / "install.sh"
REMOVED = "platform 'cursor' was removed in v9.0.0"
NOTICE = "holds a Cursor install written by an earlier emage.code release"
CONCRETE_STEP = (
    "Open .cursor/mcp.json and remove the 'filesystem' entry if it runs @anthropic/mcp-filesystem, "
    "and the keys e2b, redis, figma and notion if present (M-9 of the v8.0.0 release notes). "
    "--force-prune-keys exists only in the v8.0.0 installer."
)
USER_RULE = "# my own cursor rule; the installer must never delete it\n"
PROVENANCE = {"schemaVersion": 1, "generatorOwnedKeys": ["context7", "gitlab"]}


def plant_cursor_install(target: Path, *, manifest: bool = True, sidecar: bool = True) -> Path:
    """A .cursor/ shaped like the one a v8.x install wrote, plus the user's own edits."""
    root = target / ".cursor"
    (root / "rules").mkdir(parents=True)
    (root / "agents").mkdir()
    if manifest:
        (root / ".generated-manifest.json").write_text(json.dumps(
            {"generatedFrom": "knowledge/", "platform": "cursor", "files": ["agents/x.mdc"]},
            indent=2) + "\n", encoding="utf-8")
    if sidecar:
        (root / "mcp.json.provenance.json").write_text(
            json.dumps(PROVENANCE, indent=2) + "\n", encoding="utf-8")
    (root / "agents" / "x.mdc").write_text("generated\n", encoding="utf-8")
    (root / "rules" / "own.mdc").write_text(USER_RULE, encoding="utf-8")
    (root / "mcp.json").write_text(json.dumps(
        {"mcpServers": {"my-server": {"url": "https://example.invalid/mcp"},
                        "context7": {"url": "https://stale.example.invalid/mcp"}}},
        indent=2) + "\n", encoding="utf-8")
    return root


def unavailable(reason: str) -> None:
    """A missing prerequisite skips locally but FAILS in CI (env var CI set): a gate that
    silently skips there is not a gate (SEC-T662-02)."""
    if os.environ.get("CI"):
        raise AssertionError(f"{reason} -- CI must run this test")
    raise unittest.SkipTest(reason)


class _InstallCase(_CopierMatrix):
    def _target(self, name: str) -> Path:
        target = self.tmp / name
        shutil.copytree(self.fresh, target, symlinks=True)
        return target


class TestPlatformValidationIsEarly(_InstallCase):
    MODES = ((), ("--update",), ("--projections-only",), ("--dry-run",), ("--update", "--dry-run"))

    def test_cursor_is_refused_with_the_removal_message_and_nothing_is_written(self) -> None:
        for label, path in self.copiers():
            for flags in self.MODES:
                with self.subTest(copier=label, flags=flags):
                    target = self.tmp / f"never-{label}-{'-'.join(f.strip('-') for f in flags) or 'plain'}"
                    proc = run_installer(INSTALLER, target, "--platform", "cursor", *flags, path=path)
                    out = proc.stdout + proc.stderr
                    self.assertEqual(proc.returncode, 1, out)
                    self.assertIn(REMOVED, proc.stderr)
                    self.assertIn("the v8.x releases are the last that support it", proc.stderr)
                    self.assertNotIn("v8.0.0 is the last", proc.stderr)
                    self.assertIn("Existing .cursor/ files in your project are not touched. Nothing was written.",
                                  proc.stderr)
                    self.assertFalse(target.exists(), "the target directory was created")
                    self.assertNotIn("Installed emage.code", out)
                    self.assertNotIn("Updated emage.code", out)

    def test_cursor_leaves_an_existing_install_and_its_cursor_folder_unchanged(self) -> None:
        for label, path in self.copiers():
            for flags in self.MODES:
                with self.subTest(copier=label, flags=flags):
                    target = self._target(f"existing-{label}-{'-'.join(f.strip('-') for f in flags) or 'plain'}")
                    plant_cursor_install(target)
                    before = _snapshot(target)
                    proc = run_installer(INSTALLER, target, "--platform", "cursor", *flags, path=path)
                    self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                    self.assertIn(REMOVED, proc.stderr)
                    self.assertEqual(_snapshot(target), before)

    def test_the_removed_value_is_matched_in_any_letter_case(self) -> None:
        for value in ("Cursor", "CURSOR", "cUrSoR"):
            with self.subTest(value=value):
                target = self.tmp / f"case-{value}"
                proc = run_installer(INSTALLER, target, "--platform", value)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn(REMOVED, proc.stderr)
                self.assertFalse(target.exists())

    def test_cursor_is_refused_even_without_a_target(self) -> None:
        proc = subprocess.run(["bash", str(INSTALLER), "--platform", "cursor"],
                              capture_output=True, text=True, check=False, cwd=str(repo_root()))
        self.assertEqual(proc.returncode, 1)
        self.assertIn(REMOVED, proc.stderr)

    def test_an_unknown_platform_creates_no_target_and_lists_the_supported_ones(self) -> None:
        for flags in ((), ("--update",), ("--projections-only",)):
            with self.subTest(flags=flags):
                target = self.tmp / f"typo-{'-'.join(f.strip('-') for f in flags) or 'plain'}"
                proc = run_installer(INSTALLER, target, "--platform", "curser", *flags)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn("error: unknown platform 'curser'", proc.stderr)
                for name in ("github", "gemini", "opencode", "pi", "claude-code", "cline", "all"):
                    self.assertIn(name, proc.stderr)
                self.assertNotIn(REMOVED, proc.stderr)
                self.assertFalse(target.exists(), "the target directory was created")

    def test_unknown_platform_message_neutralises_control_characters(self) -> None:
        """ESC, BEL, a newline (line injection) and a UTF-8 bidi override (U+202E) in the
        echoed value are replaced, whatever locale the caller runs in."""
        values = ("a\x1b[31mred\x07", "x\nerror: injected line", "evil\u202egnp.exe", "caf\u00e9")
        for locale_env in ({}, {"LC_ALL": "C.UTF-8"}, {"LC_ALL": "C"}):
            for value in values:
                with self.subTest(value=value, locale=locale_env):
                    target = self.tmp / "ctrl-typo"
                    env = dict(os.environ, **locale_env)
                    proc = subprocess.run(
                        ["bash", str(INSTALLER), "--target", str(target), "--platform", value],
                        capture_output=True, text=True, check=False, env=env, cwd=str(repo_root()))
                    self.assertEqual(proc.returncode, 1)
                    self.assertIn("error: unknown platform '", proc.stderr)
                    self.assertEqual([c for c in proc.stderr if ord(c) < 32 and c != "\n"], [], repr(proc.stderr))
                    self.assertNotIn("\u202e", proc.stderr)
                    self.assertNotIn("\x7f", proc.stderr)
                    self.assertNotIn("\nerror: injected line", proc.stderr)
                    self.assertTrue(all(ord(c) < 128 for c in proc.stderr), repr(proc.stderr))
                    self.assertFalse(target.exists())

    def test_help_and_the_default_do_not_list_cursor_as_a_platform(self) -> None:
        proc = subprocess.run(["bash", str(INSTALLER), "--help"], capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("github | gemini | opencode | pi | claude-code | cline | all", proc.stdout)
        self.assertNotIn("cursor", proc.stdout.lower())

    def test_all_installs_six_platforms_and_no_cursor_folder(self) -> None:
        self.assertFalse((self.fresh / ".cursor").exists())
        for tree in (".github", ".gemini", ".opencode", ".pi", ".claude", ".cline"):
            self.assertTrue((self.fresh / tree).is_dir(), tree)


class TestPreviousCursorInstallIsNoticedAndNeverTouched(_InstallCase):
    REFRESH = (("--update",), ("--projections-only",), ("--update", "--dry-run"))

    def _run(self, target: Path, flags, path):
        return run_installer(INSTALLER, target, "--platform", "all", *flags, path=path)

    def test_notice_is_printed_and_every_byte_under_cursor_is_unchanged(self) -> None:
        """The data-loss regression: before ADR-010 the same run deleted rules/own.mdc."""
        for label, path in self.copiers():
            for flags in self.REFRESH:
                with self.subTest(copier=label, flags=flags):
                    target = self._target(f"notice-{label}-{'-'.join(f.strip('-') for f in flags)}")
                    cursor = plant_cursor_install(target)
                    before = _snapshot(cursor)
                    proc = self._run(target, flags, path)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertIn(NOTICE, proc.stderr)
                    self.assertIn("removed in v9.0.0", proc.stderr)
                    self.assertIn("does not delete it", proc.stderr)
                    self.assertIn("@anthropic/mcp-filesystem", proc.stderr)
                    self.assertIn("M-9", proc.stderr)
                    self.assertIn(CONCRETE_STEP, proc.stderr)
                    self.assertIn("docs/releases/v9.0.0.md", proc.stderr)
                    self.assertIn("MCP server versions are frozen", proc.stderr)
                    # claims only what the installer can know: no statement about hardening
                    self.assertNotIn("Playwright", proc.stderr)
                    # the old "replaces <target>/.cursor entirely (rsync --delete)" warning is gone
                    self.assertNotIn(f"{target}/.cursor entirely", proc.stderr)
                    self.assertEqual(_snapshot(cursor), before, ".cursor changed")
                    self.assertEqual((cursor / "rules" / "own.mdc").read_text(encoding="utf-8"), USER_RULE)

    def test_detection_by_either_marker_alone(self) -> None:
        for label, kwargs in (("manifest-only", dict(sidecar=False)), ("sidecar-only", dict(manifest=False))):
            with self.subTest(marker=label):
                target = self._target(f"marker-{label}")
                cursor = plant_cursor_install(target, **kwargs)
                before = _snapshot(cursor)
                proc = self._run(target, ("--update",), None)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn(NOTICE, proc.stderr)
                self.assertEqual(_snapshot(cursor), before)

    def test_manifest_of_another_platform_does_not_count(self) -> None:
        target = self._target("marker-other-platform")
        cursor = plant_cursor_install(target, sidecar=False)
        (cursor / ".generated-manifest.json").write_text('{"platform": "pi"}\n', encoding="utf-8")
        before = _snapshot(cursor)
        proc = self._run(target, ("--update",), None)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn(NOTICE, proc.stderr)
        self.assertEqual(_snapshot(cursor), before)

    def test_no_cursor_folder_means_no_notice(self) -> None:
        for flags in self.REFRESH:
            with self.subTest(flags=flags):
                target = self._target(f"clean-{'-'.join(f.strip('-') for f in flags)}")
                proc = self._run(target, flags, None)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertNotIn("Cursor", proc.stderr)
                self.assertFalse((target / ".cursor").exists())

    def test_a_users_own_cursor_folder_without_markers_is_left_alone_silently(self) -> None:
        target = self._target("own-cursor")
        own = target / ".cursor"
        (own / "rules").mkdir(parents=True)
        (own / "rules" / "mine.mdc").write_text(USER_RULE, encoding="utf-8")
        (own / "mcp.json").write_text('{"mcpServers": {}}\n', encoding="utf-8")
        before = _snapshot(own)
        for flags in self.REFRESH:
            proc = self._run(target, flags, None)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertNotIn(NOTICE, proc.stderr)
        self.assertEqual(_snapshot(own), before)

    def test_a_plain_install_does_not_print_the_notice_and_does_not_touch_cursor(self) -> None:
        """By design only --update and --projections-only (dry-run included) print the notice:
        the check lives in validate_before_update, which a plain install does not run."""
        target = self._target("plain-with-cursor")
        cursor = plant_cursor_install(target)
        before = _snapshot(cursor)
        proc = self._run(target, (), None)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn(NOTICE, proc.stderr)
        self.assertEqual(_snapshot(cursor), before)

    def test_a_symlinked_cursor_is_neither_read_nor_written_through(self) -> None:
        for label, path in self.copiers():
            for flags in self.REFRESH:
                with self.subTest(copier=label, flags=flags):
                    target = self._target(f"link-{label}-{'-'.join(f.strip('-') for f in flags)}")
                    outside = self.tmp / f"outside-{label}-{'-'.join(f.strip('-') for f in flags)}"
                    plant_cursor_install(outside)
                    (target / ".cursor").symlink_to(outside, target_is_directory=True)
                    before = _snapshot(outside)
                    proc = self._run(target, flags, path)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertNotIn(NOTICE, proc.stderr)
                    self.assertTrue((target / ".cursor").is_symlink())
                    self.assertEqual(_snapshot(outside), before)

    def test_a_symlinked_marker_is_not_followed(self) -> None:
        target = self._target("link-marker")
        cursor = target / ".cursor"
        cursor.mkdir()
        elsewhere = self.tmp / "marker-elsewhere.json"
        elsewhere.write_text('{"platform": "cursor"}\n', encoding="utf-8")
        (cursor / ".generated-manifest.json").symlink_to(elsewhere)
        proc = self._run(target, ("--update",), None)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn(NOTICE, proc.stderr)

    def test_installer_source_has_no_delete_or_write_path_for_cursor(self) -> None:
        """The only mentions of .cursor in the installer are the read-only detection and
        the messages: no rm, mv, cp, rsync, mkdir, tee or redirection names it."""
        for number, line in enumerate(INSTALLER.read_text(encoding="utf-8").splitlines(), 1):
            if ".cursor" not in line:
                continue
            code = line.split("#", 1)[0]
            with self.subTest(line=number):
                self.assertNotRegex(code, r"\b(rm|mv|cp|rsync|mkdir|tee|touch|chmod|ln|sed|install_tree_into|run)\b")
                self.assertNotRegex(code, r">\s*\S*\.cursor")


class TestUpgradeFromARealV8Install(unittest.TestCase):
    """ADR-010 Validation 3: a real pre-removal install, updated by this tree's installer.

    Needs the tag v8.0.0 (``git fetch --depth=1 origin tag v8.0.0`` in a shallow clone; the
    ``unit-tests`` CI job does it). Without the tag the class skips locally and FAILS when
    the environment variable CI is set. The rsync variant runs only where rsync is on PATH;
    the CI image (python:3.12-alpine) has none, so there only the cp-fallback variant runs --
    it is never skipped.
    """

    @classmethod
    def setUpClass(cls) -> None:
        git = shutil.which("git")
        if not git or not shutil.which("bash"):
            unavailable("git or bash not available on PATH")
        probe = subprocess.run([git, "-C", str(repo_root()), "rev-parse", "--verify", "-q",
                                "refs/tags/v8.0.0^{commit}"], capture_output=True, text=True, check=False)
        if probe.returncode != 0:
            unavailable("tag v8.0.0 is not available (run: git fetch --depth=1 origin tag v8.0.0)")
        cls._tmp = tempfile.TemporaryDirectory(prefix="emage-v8-upgrade-")
        cls.tmp = Path(cls._tmp.name)
        cls.v8 = cls.tmp / "v8-source"
        cls.v8.mkdir()
        archive = subprocess.run([git, "-C", str(repo_root()), "archive", "--format=tar", "v8.0.0"],
                                 capture_output=True, check=True).stdout
        archive_path = cls.tmp / "v8.tar"
        archive_path.write_bytes(archive)
        with tarfile.open(archive_path) as tar:
            tar.extractall(cls.v8, filter="data")
        cls.no_rsync = path_without_rsync(cls.tmp)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _v8_install(self, name: str, path: str | None) -> Path:
        target = self.tmp / name
        proc = run_installer(self.v8 / "scripts" / "install.sh", target, "--platform", "all", path=path)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((target / ".cursor" / ".generated-manifest.json").is_file(), "v8.0.0 wrote no .cursor")
        # the user's own edits inside the folder the old installer used to sweep
        (target / ".cursor" / "rules" / "own.mdc").write_text(USER_RULE, encoding="utf-8")
        mcp = target / ".cursor" / "mcp.json"
        data = json.loads(mcp.read_text(encoding="utf-8"))
        data["mcpServers"]["my-server"] = {"url": "https://example.invalid/mcp"}
        mcp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return target

    def _variants(self):
        if shutil.which("rsync"):
            yield "rsync", None
        yield "cp", self.no_rsync

    def test_update_and_projections_only_notice_and_never_touch_cursor(self) -> None:
        for label, path in self._variants():
            for flags in (("--update",), ("--projections-only",)):
                with self.subTest(copier=label, flags=flags):
                    target = self._v8_install(f"t-{label}-{flags[0].strip('-')}", path)
                    before = _snapshot(target / ".cursor")
                    proc = run_installer(INSTALLER, target, "--platform", "all", *flags, path=path)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertIn(NOTICE, proc.stderr)
                    self.assertEqual(_snapshot(target / ".cursor"), before,
                                     "this installer changed a file under .cursor/")
                    self.assertEqual((target / ".cursor" / "rules" / "own.mdc").read_text(encoding="utf-8"),
                                     USER_RULE)
                    # the other six platforms were refreshed as usual
                    for tree in (".github", ".gemini", ".opencode", ".pi", ".claude", ".cline"):
                        self.assertTrue((target / tree).is_dir(), tree)

    def test_platform_cursor_fails_early_and_writes_nothing(self) -> None:
        for label, path in self._variants():
            with self.subTest(copier=label):
                target = self._v8_install(f"c-{label}", path)
                before = _snapshot(target)
                for flags in ((), ("--update",), ("--projections-only",), ("--dry-run",)):
                    proc = run_installer(INSTALLER, target, "--platform", "cursor", *flags, path=path)
                    self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                    self.assertIn(REMOVED, proc.stderr)
                self.assertEqual(_snapshot(target), before, "--platform cursor wrote something")
                fresh_target = self.tmp / f"c-new-{label}"
                proc = run_installer(INSTALLER, fresh_target, "--platform", "cursor", path=path)
                self.assertEqual(proc.returncode, 1)
                self.assertFalse(fresh_target.exists())


if __name__ == "__main__":
    unittest.main()
