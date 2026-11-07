"""`install.sh` after Pi support was removed (T771, ADR-013 D5, the user's answer Q2
"Error + notice, never delete (Recommended)").

* ``--platform pi`` is rejected right after argument parsing in every mode: exit 1, the
  removal message of ADR-013 D5.1, and nothing written -- not even the target directory.
* A project that still holds an emage.code ``.pi/`` from an earlier release (detected by
  ``.pi/.generated-manifest.json`` declaring ``"platform": "pi"`` or by
  ``.pi/mcp.json.provenance.json``) gets a read-only notice on ``--update`` and
  ``--projections-only``; every byte under ``.pi/`` stays as it was.
* No ``.pi/``, a ``.pi/`` without the markers, or a symlinked ``.pi`` or marker: no notice,
  nothing read through the link, nothing written.
* End to end: a real ``git archive v10.0.0`` install (``--platform all``, which wrote
  ``.pi/``), with a file of the user's own and an edited ``.pi/mcp.json``, is updated with
  this tree's installer under rsync (when present) and the cp fallback.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root
from tests.functional.test_install_cursor_removal import _InstallCase, unavailable
from tests.functional.test_install_projections_only import (
    _snapshot,
    path_without_rsync,
    run_installer,
)

INSTALLER = repo_root() / "scripts" / "install.sh"
REMOVED = ("error: platform 'pi' was removed in v11.0.0 (see docs/releases/v11.0.0.md). "
           "Existing .pi/ files in your project are not touched. Nothing was written.")
NOTICE = "holds a Pi install written by an earlier emage.code release"
USER_FILE = "# my own Pi note; the installer must never delete it\n"
PROVENANCE = {"schemaVersion": 1, "generatorOwnedKeys": ["context7", "gitlab"]}


def plant_pi_install(target: Path, *, manifest: bool = True, sidecar: bool = True) -> Path:
    """A .pi/ shaped like the one a v10.x install wrote, plus the user's own edits."""
    root = target / ".pi"
    (root / "agents").mkdir(parents=True)
    if manifest:
        (root / ".generated-manifest.json").write_text(json.dumps(
            {"generatedFrom": "knowledge/", "platform": "pi", "files": ["agents/x.md"]},
            indent=2) + "\n", encoding="utf-8")
    if sidecar:
        (root / "mcp.json.provenance.json").write_text(
            json.dumps(PROVENANCE, indent=2) + "\n", encoding="utf-8")
    (root / "agents" / "x.md").write_text("generated\n", encoding="utf-8")
    (root / "own-note.md").write_text(USER_FILE, encoding="utf-8")
    (root / "mcp.json").write_text(json.dumps(
        {"mcpServers": {"my-server": {"url": "https://example.invalid/mcp"},
                        "context7": {"url": "https://stale.example.invalid/mcp"}}},
        indent=2) + "\n", encoding="utf-8")
    return root


class TestPlatformPiIsRefusedEarly(_InstallCase):
    MODES = ((), ("--update",), ("--projections-only",), ("--dry-run",), ("--update", "--dry-run"))

    def test_pi_is_refused_with_the_removal_message_and_nothing_is_written(self) -> None:
        for label, path in self.copiers():
            for flags in self.MODES:
                with self.subTest(copier=label, flags=flags):
                    target = self.tmp / f"never-{label}-{'-'.join(f.strip('-') for f in flags) or 'plain'}"
                    proc = run_installer(INSTALLER, target, "--platform", "pi", *flags, path=path)
                    out = proc.stdout + proc.stderr
                    self.assertEqual(proc.returncode, 1, out)
                    self.assertEqual(proc.stderr.strip().splitlines(), [REMOVED])
                    self.assertFalse(target.exists(), "the target directory was created")
                    self.assertNotIn("Installed emage.code", out)
                    self.assertNotIn("Updated emage.code", out)

    def test_pi_leaves_an_existing_install_and_its_pi_folder_unchanged(self) -> None:
        for label, path in self.copiers():
            for flags in self.MODES:
                with self.subTest(copier=label, flags=flags):
                    target = self._target(f"existing-{label}-{'-'.join(f.strip('-') for f in flags) or 'plain'}")
                    plant_pi_install(target)
                    before = _snapshot(target)
                    proc = run_installer(INSTALLER, target, "--platform", "pi", *flags, path=path)
                    self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                    self.assertIn(REMOVED, proc.stderr)
                    self.assertEqual(_snapshot(target), before)

    def test_the_removed_value_is_matched_in_any_letter_case(self) -> None:
        for value in ("Pi", "PI", "pI"):
            with self.subTest(value=value):
                target = self.tmp / f"case-{value}"
                proc = run_installer(INSTALLER, target, "--platform", value)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn(REMOVED, proc.stderr)
                self.assertFalse(target.exists())

    def test_help_and_the_unknown_platform_list_do_not_name_pi(self) -> None:
        proc = subprocess.run(["bash", str(INSTALLER), "--help"], capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("github | gemini | opencode | claude-code | cline | all", proc.stdout)
        self.assertNotRegex(proc.stdout, r"(?i)(\.pi\b|\bpi\b)")
        typo = run_installer(INSTALLER, self.tmp / "typo", "--platform", "pii")
        self.assertEqual(typo.returncode, 1)
        self.assertIn("supported: github, gemini, opencode, claude-code, cline, all.", typo.stderr)

    def test_all_installs_no_pi_folder(self) -> None:
        self.assertFalse((self.fresh / ".pi").exists())


class TestPreviousPiInstallIsNoticedAndNeverTouched(_InstallCase):
    REFRESH = (("--update",), ("--projections-only",), ("--update", "--dry-run"))

    def _run(self, target: Path, flags, path):
        return run_installer(INSTALLER, target, "--platform", "all", *flags, path=path)

    def test_notice_is_printed_and_every_byte_under_pi_is_unchanged(self) -> None:
        for label, path in self.copiers():
            for flags in self.REFRESH:
                with self.subTest(copier=label, flags=flags):
                    target = self._target(f"notice-{label}-{'-'.join(f.strip('-') for f in flags)}")
                    pi = plant_pi_install(target)
                    before = _snapshot(pi)
                    proc = self._run(target, flags, path)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertIn(NOTICE, proc.stderr)
                    self.assertIn("removed in v11.0.0", proc.stderr)
                    self.assertIn("no longer updated, pruned or checked", proc.stderr)
                    self.assertIn("does not delete it", proc.stderr)
                    self.assertIn("frozen at the version that wrote them", proc.stderr)
                    self.assertIn("docs/releases/v11.0.0.md", proc.stderr)
                    self.assertNotIn(f"{target}/.pi entirely", proc.stderr)
                    self.assertEqual(_snapshot(pi), before, ".pi changed")
                    self.assertEqual((pi / "own-note.md").read_text(encoding="utf-8"), USER_FILE)

    def test_detection_by_either_marker_alone(self) -> None:
        for label, kwargs in (("manifest-only", dict(sidecar=False)), ("sidecar-only", dict(manifest=False))):
            with self.subTest(marker=label):
                target = self._target(f"marker-{label}")
                pi = plant_pi_install(target, **kwargs)
                before = _snapshot(pi)
                proc = self._run(target, ("--update",), None)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn(NOTICE, proc.stderr)
                self.assertEqual(_snapshot(pi), before)

    def test_manifest_of_another_platform_does_not_count(self) -> None:
        target = self._target("marker-other-platform")
        pi = plant_pi_install(target, sidecar=False)
        (pi / ".generated-manifest.json").write_text('{"platform": "cline"}\n', encoding="utf-8")
        before = _snapshot(pi)
        proc = self._run(target, ("--update",), None)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn(NOTICE, proc.stderr)
        self.assertEqual(_snapshot(pi), before)

    def test_no_pi_folder_means_no_notice(self) -> None:
        for flags in self.REFRESH:
            with self.subTest(flags=flags):
                target = self._target(f"clean-{'-'.join(f.strip('-') for f in flags)}")
                proc = self._run(target, flags, None)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertNotIn(NOTICE, proc.stderr)
                self.assertFalse((target / ".pi").exists())

    def test_a_users_own_pi_folder_without_markers_is_left_alone_silently(self) -> None:
        target = self._target("own-pi")
        own = target / ".pi"
        own.mkdir()
        (own / "settings.json").write_text('{"mine": true}\n', encoding="utf-8")
        (own / "mcp.json").write_text('{"mcpServers": {}}\n', encoding="utf-8")
        before = _snapshot(own)
        for flags in self.REFRESH:
            proc = self._run(target, flags, None)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertNotIn(NOTICE, proc.stderr)
        self.assertEqual(_snapshot(own), before)

    def test_a_plain_install_does_not_print_the_notice_and_does_not_touch_pi(self) -> None:
        target = self._target("plain-with-pi")
        pi = plant_pi_install(target)
        before = _snapshot(pi)
        proc = self._run(target, (), None)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn(NOTICE, proc.stderr)
        self.assertEqual(_snapshot(pi), before)

    def test_a_symlinked_pi_is_neither_read_nor_written_through(self) -> None:
        for label, path in self.copiers():
            for flags in self.REFRESH:
                with self.subTest(copier=label, flags=flags):
                    suffix = f"{label}-{'-'.join(f.strip('-') for f in flags)}"
                    target = self._target(f"link-{suffix}")
                    outside = self.tmp / f"outside-{suffix}"
                    plant_pi_install(outside)
                    (target / ".pi").symlink_to(outside / ".pi", target_is_directory=True)
                    before = _snapshot(outside)
                    proc = self._run(target, flags, path)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertNotIn(NOTICE, proc.stderr)
                    self.assertTrue((target / ".pi").is_symlink())
                    self.assertEqual(_snapshot(outside), before)

    def test_a_symlinked_marker_is_not_followed(self) -> None:
        for name, content in ((".generated-manifest.json", '{"platform": "pi"}\n'),
                              ("mcp.json.provenance.json", json.dumps(PROVENANCE) + "\n")):
            with self.subTest(marker=name):
                target = self._target(f"link-marker-{name.strip('.')}")
                pi = target / ".pi"
                pi.mkdir()
                elsewhere = self.tmp / f"elsewhere-{name.strip('.')}"
                elsewhere.write_text(content, encoding="utf-8")
                (pi / name).symlink_to(elsewhere)
                proc = self._run(target, ("--update",), None)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertNotIn(NOTICE, proc.stderr)

    def test_installer_source_has_no_delete_or_write_path_for_pi(self) -> None:
        """The only mentions of .pi in the installer are the read-only detection and the
        messages: no rm, mv, cp, rsync, mkdir, tee or redirection names it."""
        for number, line in enumerate(INSTALLER.read_text(encoding="utf-8").splitlines(), 1):
            if not re.search(r"\.pi\b", line):
                continue
            code = line.split("#", 1)[0]
            with self.subTest(line=number):
                self.assertNotRegex(code, r"\b(rm|mv|cp|rsync|mkdir|tee|touch|chmod|ln|sed|install_tree_into|run)\b")
                self.assertNotRegex(code, r">\s*\S*\.pi\b")


class TestUpgradeFromARealV10Install(unittest.TestCase):
    """ADR-013 D5.5 (b) and (e): a real pre-removal install, updated by this tree's installer.

    Needs the tag v10.0.0 (``git fetch --depth=1 origin tag v10.0.0``; the ``unit-tests`` CI job
    does it). Without the tag the class skips locally and FAILS when CI is set. The rsync variant
    runs only where rsync is on PATH; the cp-fallback variant always runs.
    """

    @classmethod
    def setUpClass(cls) -> None:
        git = shutil.which("git")
        if not git or not shutil.which("bash"):
            unavailable("git or bash not available on PATH")
        probe = subprocess.run([git, "-C", str(repo_root()), "rev-parse", "--verify", "-q",
                                "refs/tags/v10.0.0^{commit}"], capture_output=True, text=True, check=False)
        if probe.returncode != 0:
            unavailable("tag v10.0.0 is not available (run: git fetch --depth=1 origin tag v10.0.0)")
        cls._tmp = tempfile.TemporaryDirectory(prefix="emage-v10-upgrade-")
        cls.tmp = Path(cls._tmp.name)
        cls.v10 = cls.tmp / "v10-source"
        cls.v10.mkdir()
        archive = subprocess.run([git, "-C", str(repo_root()), "archive", "--format=tar", "v10.0.0"],
                                 capture_output=True, check=True).stdout
        archive_path = cls.tmp / "v10.tar"
        archive_path.write_bytes(archive)
        with tarfile.open(archive_path) as tar:
            tar.extractall(cls.v10, filter="data")
        cls.no_rsync = path_without_rsync(cls.tmp)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _v10_install(self, name: str, path: str | None) -> Path:
        target = self.tmp / name
        proc = run_installer(self.v10 / "scripts" / "install.sh", target, "--platform", "all", path=path)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        manifest = json.loads((target / ".pi" / ".generated-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["platform"], "pi", "v10.0.0 wrote no .pi")
        (target / ".pi" / "own-note.md").write_text(USER_FILE, encoding="utf-8")
        mcp = target / ".pi" / "mcp.json"
        data = json.loads(mcp.read_text(encoding="utf-8"))
        data["mcpServers"]["my-server"] = {"url": "https://example.invalid/mcp"}
        mcp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return target

    def _variants(self):
        if shutil.which("rsync"):
            yield "rsync", None
        yield "cp", self.no_rsync

    def test_update_and_projections_only_notice_and_never_touch_pi(self) -> None:
        for label, path in self._variants():
            for flags in (("--update",), ("--projections-only",)):
                with self.subTest(copier=label, flags=flags):
                    target = self._v10_install(f"t-{label}-{flags[0].strip('-')}", path)
                    before = _snapshot(target / ".pi")
                    proc = run_installer(INSTALLER, target, "--platform", "all", *flags, path=path)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertIn(NOTICE, proc.stderr)
                    self.assertEqual(_snapshot(target / ".pi"), before,
                                     "this installer changed a file under .pi/")
                    self.assertEqual((target / ".pi" / "own-note.md").read_text(encoding="utf-8"), USER_FILE)
                    for tree in (".github", ".gemini", ".opencode", ".claude", ".cline"):
                        self.assertTrue((target / tree).is_dir(), tree)

    def test_platform_pi_fails_early_and_writes_nothing(self) -> None:
        for label, path in self._variants():
            with self.subTest(copier=label):
                target = self._v10_install(f"p-{label}", path)
                before = _snapshot(target)
                for flags in ((), ("--update",), ("--projections-only",), ("--dry-run",)):
                    proc = run_installer(INSTALLER, target, "--platform", "pi", *flags, path=path)
                    self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                    self.assertIn(REMOVED, proc.stderr)
                self.assertEqual(_snapshot(target), before, "--platform pi wrote something")


if __name__ == "__main__":
    unittest.main()
