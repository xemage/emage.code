"""Regression tests for scripts/check-version-consistency.py (Gate G0 — Truth)."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests._helpers.repo import repo_root


def _load_module():
    module_path = repo_root() / "scripts" / "check-version-consistency.py"
    spec = importlib.util.spec_from_file_location("check_version_consistency", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load check-version-consistency module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_cli(*args: str) -> tuple[int, str]:
    script = repo_root() / "scripts" / "check-version-consistency.py"
    proc = subprocess.run(
        ["python3", str(script), *args], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestFindMarkerVersion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_parses_standard_marker(self):
        text = "Some text\nLatest release: v6.10.0\nMore text\n"
        raw, key = self.mod.find_marker_version(text)
        self.assertEqual(raw, "v6.10.0")
        self.assertEqual(key, (6, 10, 0))

    def test_returns_none_when_marker_absent(self):
        self.assertIsNone(self.mod.find_marker_version("no marker here"))


class TestIsExcluded(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_excludes_releases_prefix(self):
        self.assertTrue(self.mod.is_excluded(Path("docs/releases/v6.0.1.md")))

    def test_excludes_checkpoints_prefix(self):
        self.assertTrue(self.mod.is_excluded(Path("docs/checkpoints/checkpoint-1.md")))

    def test_excludes_archiv_prefix(self):
        self.assertTrue(self.mod.is_excluded(Path("docs/archiv/old-chat.md")))

    def test_excludes_changelog(self):
        self.assertTrue(self.mod.is_excluded(Path("CHANGELOG.md")))

    def test_excludes_tasks_prefix(self):
        self.assertTrue(self.mod.is_excluded(Path("docs/tasks/task-T400.md")))

    def test_excludes_plans_prefix(self):
        self.assertTrue(self.mod.is_excluded(Path("docs/plans/plan-035-roadmap-v7-ground-up.md")))

    def test_excludes_artifacts_prefix(self):
        self.assertTrue(self.mod.is_excluded(Path("docs/artifacts/cwso-mcp-contract-v1.md")))

    def test_does_not_exclude_other_docs(self):
        self.assertFalse(self.mod.is_excluded(Path("implementation/README.md")))
        self.assertFalse(self.mod.is_excluded(Path("README.md")))
        self.assertFalse(self.mod.is_excluded(Path("docs/wiki/implementation-guide.md")))


class TestScanFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_flags_older_version_near_signal_phrase(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.md"
            f.write_text("The current release is v6.0.1 currently.\n")
            findings = self.mod.scan_file(f, (6, 10, 0))
            self.assertEqual(findings, [(1, "v6.0.1")])

    def test_flags_older_version_split_across_line_wrap(self):
        # Mirrors implementation/README.md's real shape: the signal phrase and the
        # version are on different lines (a wrapped sentence), so the context gate
        # must look across line boundaries, not just within a single line.
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.md"
            f.write_text(
                "Canonical knowledge for the current release stream\n(**v6.0.1**).\n"
            )
            findings = self.mod.scan_file(f, (6, 10, 0))
            self.assertEqual(findings, [(2, "v6.0.1")])

    def test_ignores_equal_or_newer_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.md"
            f.write_text("Current: v6.10.0. Future: v7.0.0.\n")
            findings = self.mod.scan_file(f, (6, 10, 0))
            self.assertEqual(findings, [])

    def test_ignores_illustrative_example_with_no_signal_phrase_or_link(self):
        # Mirrors implementation/knowledge/agents/release-manager.md's "legacy API
        # removal" example: an older-looking version string with no nearby
        # "current release" / "latest release" / "release:" phrase and no
        # docs/releases/ link — this is the documented residual-limitation tradeoff,
        # not a claim about the repo's *current* state.
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.md"
            f.write_text("- Legacy API v1 endpoints (removal in v2.0.0)\n")
            findings = self.mod.scan_file(f, (6, 10, 0))
            self.assertEqual(findings, [])

    def test_flags_releases_link_even_with_no_nearby_release_phrase(self):
        # A docs/releases/vX.Y.Z.md link is always a "current state" claim in its own
        # right, even with no signal phrase nearby at all.
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.md"
            f.write_text(
                "See [notes](docs/releases/v6.0.1.md) for background on the old flow.\n"
            )
            findings = self.mod.scan_file(f, (6, 10, 0))
            self.assertEqual(findings, [(1, "v6.0.1")])

    def test_ignores_historical_style_mention_outside_context_gate(self):
        # Mirrors a docs/tasks/-style historical statement ("T050 | Major release
        # v4.0.0"): an older version string with no current-state signal phrase and
        # no docs/releases/ link. (docs/tasks/ itself is also excluded by path prefix
        # — this test exercises the context gate directly, independent of that
        # exclusion, since a similarly-shaped sentence could appear anywhere.)
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.md"
            f.write_text("| T050 | Major release v4.0.0 shipped | Done |\n")
            findings = self.mod.scan_file(f, (6, 10, 0))
            self.assertEqual(findings, [])


class TestEvaluate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_pass_when_no_drift(self):
        code, lines = self.mod.evaluate("v6.10.0", {})
        self.assertEqual(code, 0)
        self.assertTrue(any("PASS" in line for line in lines))

    def test_fail_when_drift_present(self):
        drift = {Path("implementation/README.md"): [(4, "v6.0.1")]}
        code, lines = self.mod.evaluate("v6.10.0", drift)
        self.assertEqual(code, 1)
        self.assertTrue(any("FAIL" in line for line in lines))
        self.assertTrue(
            any("'implementation/README.md':4" in line and "v6.0.1" in line for line in lines)
        )

    def test_a_drift_line_escapes_the_path(self):
        """SEC-T745-10: a newline or an escape sequence in a file name cannot forge a log line."""
        name = "a\x1b[31m\nversion-consistency: PASS.md"
        code, lines = self.mod.evaluate("v6.10.0", {Path(name): [(4, "v6.0.1")]})
        self.assertEqual(code, 1)
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[1].isascii())
        self.assertNotIn("\x1b", lines[1])
        self.assertNotIn("\n", lines[1])
        self.assertIn(f"{ascii(name)}:4: found v6.0.1", lines[1])

    def test_fail_when_marker_unparseable(self):
        code, lines = self.mod.evaluate(None, {})
        self.assertEqual(code, 1)


class TestStrictRead(unittest.TestCase):
    """T744 (SEC-T741-06): the gate's child read with errors="ignore", so `v8.0.0\\xffabc` hid a stale claim."""

    README = b"Latest release: v9.0.0\n"

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        (self.root / "README.md").write_bytes(self.README)

    def _run(self) -> tuple[int, str]:
        return _run_cli("--root", str(self.root))

    def test_control_the_valid_claim_is_flagged_without_the_byte(self):
        (self.root / "notes.md").write_bytes(b"Latest release: v8.0.0 abc\n")
        code, out = self._run()
        self.assertEqual(code, 1)
        self.assertIn("'notes.md':1: found v8.0.0", out)

    def test_a_byte_hiding_a_stale_claim_fails_naming_path_and_offset_only(self):
        (self.root / "notes.md").write_bytes(b"Latest release: v8.0.0\xffabc\n")
        code, out = self._run()
        self.assertEqual(code, 1, out)
        self.assertIn("'notes.md' is not valid UTF-8: the first invalid byte is at file offset 22 (from 0)", out)
        self.assertIn("VERSION CONSISTENCY: FAIL", out)
        self.assertNotIn("abc", out)
        self.assertNotIn("Traceback", out)

    def test_an_invalid_marker_file_fails(self):
        (self.root / "README.md").write_bytes(b"Latest release: v9.\xff0.0\n")
        code, out = self._run()
        self.assertEqual(code, 1, out)
        self.assertIn("'README.md' is not valid UTF-8", out)
        self.assertIn("file offset 19 ", out)

    def test_an_invalid_marker_file_outside_the_scan_fails(self):
        """A file the scan does not read itself, so only the marker's own read can see the byte."""
        (self.root / "MARKER.txt").write_bytes(b"Latest release: v9.\xff0.0\n")
        code, out = _run_cli("--root", str(self.root), "--marker-file", "MARKER.txt")
        self.assertEqual(code, 1, out)
        self.assertIn("'MARKER.txt' is not valid UTF-8", out)

    def test_the_offset_counts_from_the_start_of_a_large_file(self):
        """Past any read buffer: the offset counts from the start of the file."""
        (self.root / "notes.md").write_bytes(b"x" * 100000 + b"\xff")
        code, out = self._run()
        self.assertEqual(code, 1, out)
        self.assertIn("file offset 100000 ", out)

    def test_a_file_name_cannot_forge_a_log_line(self):
        (self.root / "a\nVERSION CONSISTENCY: PASS\x1b.md").write_bytes(b"\xff")
        code, out = self._run()
        self.assertEqual(code, 1, out)
        self.assertEqual(len(out.splitlines()), 2, out)
        self.assertIn("\\nVERSION CONSISTENCY: PASS\\x1b.md", out)

    def test_an_excluded_file_is_not_read(self):
        (self.root / "docs" / "releases").mkdir(parents=True)
        (self.root / "docs" / "releases" / "v1.0.0.md").write_bytes(b"\xff")
        self.assertEqual(self._run()[0], 0)

    def test_newlines_count_as_they_did_in_text_mode(self):
        mod = _load_module()
        path = self.root / "notes.md"
        path.write_bytes(b"one\r\ntwo\rLatest release: v8.0.0\n")
        self.assertEqual(mod.scan_file(path, (9, 0, 0)), [(3, "v8.0.0")])

    def test_the_gate_fails_and_its_log_line_is_safe(self):
        """The real caller: scripts/verify-release-docs.py folds a non-zero child into its errors."""
        name = "verify_release_docs_t744"
        spec = importlib.util.spec_from_file_location(name, repo_root() / "scripts" / "verify-release-docs.py")
        verify = importlib.util.module_from_spec(spec)
        sys.modules[name] = verify
        self.addCleanup(sys.modules.pop, name, None)
        spec.loader.exec_module(verify)
        (self.root / "scripts").mkdir()
        shutil.copy(repo_root() / "scripts" / "check-version-consistency.py", self.root / "scripts")
        (self.root / "notes\x1b.md").write_bytes(b"secret-content\xff")
        errors: list[str] = []
        with mock.patch.object(verify, "ROOT", self.root):
            verify.check_version_consistency(errors)
        self.assertIn("version-consistency check failed (scripts/check-version-consistency.py exited 1):", errors)
        self.assertTrue(any("'notes\\x1b.md' is not valid UTF-8" in e and "file offset 14 " in e for e in errors), errors)
        self.assertNotIn("secret-content", "\n".join(errors))
        self.assertTrue(all(error.isascii() and error.isprintable() for error in errors), errors)


class TestScanRepositoryFixtures(unittest.TestCase):
    """End-to-end pass/fail paths using temp-directory fixtures (not the real repo)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "README.md").write_text("Project X\n\nLatest release: v6.10.0\n")
        (self.root / "docs" / "releases").mkdir(parents=True)
        self.mod = _load_module()

    def test_pass_on_clean_tree(self):
        (self.root / "notes.md").write_text("Everything is current: v6.10.0.\n")
        canonical, drift = self.mod.scan_repository(self.root, self.root / "README.md")
        code, _lines = self.mod.evaluate(canonical, drift)
        self.assertEqual(code, 0)

    def test_fixture_reverting_implementation_readme_to_v6_0_1_fails(self):
        # Mirrors the real repo's confirmed drift: implementation/README.md claiming
        # a stale version (v6.0.1) while README.md's marker is already v6.10.0.
        impl_dir = self.root / "implementation"
        impl_dir.mkdir()
        (impl_dir / "README.md").write_text(
            "# emage.code implementation\n\n"
            "Canonical knowledge for the current release stream\n(**v6.0.1**).\n"
        )
        canonical, drift = self.mod.scan_repository(self.root, self.root / "README.md")
        code, lines = self.mod.evaluate(canonical, drift)
        self.assertEqual(code, 1)
        rel = Path("implementation/README.md")
        self.assertIn(rel, drift)
        self.assertTrue(any("v6.0.1" in v for _line_no, v in drift[rel]))
        self.assertTrue(
            any("implementation/README.md" in line and "v6.0.1" in line for line in lines)
        )

    def test_exclusion_list_suppresses_historical_release_docs(self):
        (self.root / "docs" / "releases" / "v6.0.1.md").write_text(
            "# v6.0.1\n\nLatest release: v6.0.1\n\nHistorical release notes.\n"
        )
        canonical, drift = self.mod.scan_repository(self.root, self.root / "README.md")
        self.assertEqual(canonical, "v6.10.0")
        self.assertNotIn(Path("docs/releases/v6.0.1.md"), drift)

    def test_exclusion_list_suppresses_task_ledger_history(self):
        # (a) A docs/tasks/-style historical mention — a true past-tense statement
        # about an old release, structurally identical to real rows like
        # "T050 | Major release v4.0.0" — must not be flagged, both because of the
        # path-prefix exclusion and (independently) because it carries no
        # current-state signal phrase.
        tasks_dir = self.root / "docs" / "tasks"
        tasks_dir.mkdir(parents=True)
        (tasks_dir / "completed-tasks.md").write_text(
            "| ID | Title | Done on | Outcome |\n"
            "| T050 | Major release v4.0.0 | 2025-01-01 | Shipped |\n"
        )
        canonical, drift = self.mod.scan_repository(self.root, self.root / "README.md")
        self.assertEqual(canonical, "v6.10.0")
        self.assertNotIn(Path("docs/tasks/completed-tasks.md"), drift)

    def test_docs_releases_link_flagged_with_no_nearby_release_phrase(self):
        # (b) A docs/releases/vX.Y.Z.md-link-style current-doc mention, with no
        # "release" signal phrase anywhere nearby, must still be flagged — the link
        # itself is the signal.
        (self.root / "guide.md").write_text(
            "See [notes](docs/releases/v6.0.1.md) for background on the old flow.\n"
        )
        canonical, drift = self.mod.scan_repository(self.root, self.root / "README.md")
        self.assertEqual(canonical, "v6.10.0")
        rel = Path("guide.md")
        self.assertIn(rel, drift)
        self.assertTrue(any("v6.0.1" in v for _line_no, v in drift[rel]))

    def test_illustrative_semver_example_not_flagged(self):
        # (c) An illustrative semver example — no signal phrase, not a
        # docs/releases/ link — must not be flagged.
        (self.root / "knowledge.md").write_text(
            "- Legacy API v1 endpoints (removal in v2.0.0)\n"
        )
        canonical, drift = self.mod.scan_repository(self.root, self.root / "README.md")
        self.assertEqual(canonical, "v6.10.0")
        self.assertNotIn(Path("knowledge.md"), drift)

    def test_no_side_effects_files_untouched(self):
        target = self.root / "notes.md"
        target.write_text("Old version reference: v6.0.1.\n")
        before_mtime = target.stat().st_mtime_ns
        before_content = target.read_bytes()
        self.mod.scan_repository(self.root, self.root / "README.md")
        self.assertEqual(target.stat().st_mtime_ns, before_mtime)
        self.assertEqual(target.read_bytes(), before_content)


class TestDependencyTrees(unittest.TestCase):
    """SEC-T745-09: only exact paths from the root are skipped, so no committed file can silence the check for docs/wiki."""

    README = b"Latest release: v9.0.0\n"
    STALE = b"Latest release: v8.0.0\n"

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self._write("README.md", self.README)

    def _write(self, relative: str, data: bytes = b"text\n") -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def _found(self) -> list[str]:
        return [path.relative_to(self.root).as_posix() for path in self.mod.find_markdown_files(self.root)]

    def _exit(self) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = self.mod.main(["--root", str(self.root)])
        return code, output.getvalue()

    def test_exact_paths_are_skipped_and_nothing_else(self):
        for skipped in ("ci/js/node_modules/pkg/x.md", ".venv/lib/x.md", ".venv/x.md", "venv/lib/x.md", "venv/x.md", ".git/x.md"):
            self._write(skipped)
        kept = ["README.md", "ci/js/node_modules.md", "ci/js/node_modules2/x.md", "ci/js/x.md", "ci/node_modules/x.md",
                "docs/node_modules/x.md", "docs/wiki/.venv/x.md", "docs/wiki/venv/x.md", "node_modules/x.md",
                "other/x.md", "venv.md", "venv2/x.md", "x/ci/js/node_modules/a.md"]
        for name in kept:
            self._write(name)
        self._write("other/pyvenv.cfg")
        self.assertEqual(self._found(), sorted(kept))

    def test_a_stale_claim_in_docs_wiki_still_fails_with_a_marker_file_beside_it(self):
        self._write("docs/wiki/guide.md", self.STALE)
        for name, marker in (("pyvenv.cfg", "docs/wiki/pyvenv.cfg"), ("node_modules", "docs/wiki/node_modules/x.md")):
            with self.subTest(name):
                self._write(marker)
                code, output = self._exit()
                self.assertEqual(code, 1)
                self.assertIn("'docs/wiki/guide.md':1: found v8.0.0", output)

    def test_a_marker_at_the_root_silences_nothing(self):
        self._write("docs/wiki/guide.md", self.STALE)
        self._write("pyvenv.cfg")
        self.assertEqual(self._exit()[0], 1)

    def test_the_finding_a_byte_under_the_exact_paths_does_not_fail_the_scan(self):
        for path in ("ci/js/node_modules/pkg/bad.md", ".venv/lib/bad.md", "venv/lib/bad.md"):
            self._write(path, b"\xff\n")
        self.assertEqual(self._exit()[0], 0)

    def test_the_accepted_residual_another_virtual_environment_fails_naming_the_path(self):
        self._write("env2/pyvenv.cfg")
        self._write("env2/lib/bad.md", b"\xff\n")
        code, output = self._exit()
        self.assertEqual(code, 1)
        self.assertIn("env2/lib/bad.md", output)


class TestGoldenFixtureExclusion(unittest.TestCase):
    """T642 (audit v2 decision D-1): tests/golden/ is excluded from the scan as frozen
    evidence; the exclusion is a prefix match and must not leak to other paths."""

    STALE = "Latest release: v7.0.1\n"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "README.md").write_text("Project X\n\nLatest release: v8.0.0\n")
        self.mod = _load_module()

    def _drift(self) -> dict:
        canonical, drift = self.mod.scan_repository(self.root, self.root / "README.md")
        self.assertEqual(canonical, "v8.0.0")
        return drift

    def _write(self, rel: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.STALE)
        return Path(rel)

    def test_stale_claim_under_golden_open_case_is_not_reported(self):
        case = "tests/golden/open/some-case"
        fixture_rel = self._write(f"{case}/fixture/docs/releases-copy.md")
        brief_rel = self._write(f"{case}/brief.md")
        drift = self._drift()
        self.assertNotIn(fixture_rel, drift)
        self.assertNotIn(brief_rel, drift)

    def test_stale_claim_in_non_excluded_path_is_still_reported(self):
        rel = self._write("docs/wiki/x.md")
        drift = self._drift()
        self.assertIn(rel, drift)
        self.assertEqual(drift[rel], [(1, "v7.0.1")])

    def test_path_merely_containing_tests_golden_is_still_scanned(self):
        rel = self._write("docs/tests/golden/x.md")
        drift = self._drift()
        self.assertIn(rel, drift)
        self.assertEqual(drift[rel], [(1, "v7.0.1")])


class TestDecisionRecordExclusion(unittest.TestCase):
    """T704 (D-T700-1, the user's 2026-11-01 decision "Exclude docs/decisions/
    (Recommended)"): accepted ADRs are immutable dated records, so their old release
    paths are not current-state claims. The exclusion is a prefix match and must not leak
    to other paths."""

    STALE_PATH = "See [`docs/releases/v8.0.0.md`](../releases/v8.0.0.md).\n"
    STALE_MARKER = "Latest release: v8.0.0\n"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "README.md").write_text("Project X\n\nLatest release: v9.0.0\n")
        self.mod = _load_module()

    def _drift(self) -> dict:
        canonical, drift = self.mod.scan_repository(self.root, self.root / "README.md")
        self.assertEqual(canonical, "v9.0.0")
        return drift

    def _write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return Path(rel)

    def test_is_excluded_matches_decisions_prefix(self):
        self.assertTrue(self.mod.is_excluded(Path("docs/decisions/ADR-010-drop-cursor-platform-support.md")))

    def test_stale_release_path_in_adr_is_not_reported(self):
        adr = self._write("docs/decisions/ADR-010-x.md", self.STALE_PATH + self.STALE_MARKER)
        drift = self._drift()
        self.assertNotIn(adr, drift)
        self.assertEqual(drift, {})

    def test_same_lines_outside_decisions_are_still_reported(self):
        rel = self._write("docs/wiki/x.md", self.STALE_PATH)
        drift = self._drift()
        self.assertIn(rel, drift)
        # Two hits on the one line: the link text and the link target.
        self.assertEqual(drift[rel], [(1, "v8.0.0"), (1, "v8.0.0")])

    def test_path_merely_containing_docs_decisions_is_still_scanned(self):
        rel = self._write("implementation/docs/decisions/x.md", self.STALE_MARKER)
        drift = self._drift()
        self.assertIn(rel, drift)
        self.assertEqual(drift[rel], [(1, "v8.0.0")])

    def test_sibling_prefix_is_still_scanned(self):
        rel = self._write("docs/decisions-draft/x.md", self.STALE_MARKER)
        drift = self._drift()
        self.assertIn(rel, drift)


class TestCli(unittest.TestCase):
    def test_help_exits_zero(self):
        code, out = _run_cli("--help")
        self.assertEqual(code, 0)
        self.assertIn("Version-consistency gate", out)

    def test_cli_against_fixture_root_detects_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("Latest release: v6.10.0\n")
            (root / "stale.md").write_text("Current release: v6.0.1.\n")
            code, out = _run_cli("--root", str(root))
            self.assertEqual(code, 1)
            self.assertIn("stale.md", out)
            self.assertIn("v6.0.1", out)

    def test_cli_against_fixture_root_ignores_illustrative_example(self):
        # No signal phrase, no docs/releases/ link — the documented residual
        # limitation: this is not flagged, by design.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("Latest release: v6.10.0\n")
            (root / "example.md").write_text(
                "Branch naming example: hotfix/v1.2.1\n"
            )
            code, out = _run_cli("--root", str(root))
            self.assertEqual(code, 0)
            self.assertIn("PASS", out)

    def test_cli_against_fixture_root_clean_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("Latest release: v6.10.0\n")
            (root / "fresh.md").write_text("We are on v6.10.0.\n")
            code, out = _run_cli("--root", str(root))
            self.assertEqual(code, 0)
            self.assertIn("PASS", out)

    def test_missing_marker_file_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = _run_cli("--root", tmp, "--marker-file", "NOPE.md")
            self.assertEqual(code, 2)
            self.assertIn("marker file not found", out)

    def test_real_repo_is_clean_after_t401(self):
        # Pre-T401, the repo had confirmed, real drift in these four locations
        # (implementation/README.md:4/:31, README.md:131,
        # docs/wiki/implementation-guide.md:5/:33) and this test asserted the script
        # correctly *detected* it (exit 1). T401 (same branch) has since fixed all
        # four, so the real tree is now expected to be clean — exit 0. Drift-detection
        # capability itself remains covered independently of real-repo state by the
        # synthetic-fixture tests above (test_fixture_reverting_implementation_readme_
        # to_v6_0_1_fails, test_cli_against_fixture_root_detects_drift, etc.), so this
        # test no longer needs to depend on the real tree being in a stale state.
        code, out = _run_cli()
        self.assertEqual(code, 0)
        self.assertIn("PASS", out)

    def test_real_repo_excludes_historical_release_docs(self):
        code, out = _run_cli()
        self.assertNotIn("docs/releases/v6.0.1.md:", out)

    def test_real_repo_excludes_task_ledger_and_plan_history(self):
        # docs/tasks/*.md and docs/plans/*.md are full of true historical statements
        # ("T050 | Major release v4.0.0") that match the bare vX.Y.Z regex but are not
        # current-state claims — widened exclusion per the T400 addendum.
        code, out = _run_cli()
        self.assertNotIn("docs/tasks/", out)
        self.assertNotIn("docs/plans/", out)
        self.assertNotIn("docs/artifacts/", out)

    def test_real_repo_excludes_illustrative_knowledge_examples(self):
        # Illustrative semver examples (branch-naming, semver walkthrough, legacy-API
        # removal example) confirmed present in these three canonical knowledge files
        # — and all of their platform-projected mirrors — must not be flagged now that
        # the context gate is in place.
        code, out = _run_cli()
        canonical_examples = (
            "implementation/knowledge/instructions/git-workflow.md",
            "implementation/knowledge/skills/release-workflow/SKILL.md",
            "implementation/knowledge/agents/release-manager.md",
        )
        for rel in canonical_examples:
            self.assertNotIn(rel, out)

        mirrors = repo_root().glob("implementation/.*/**/*")
        example_basenames = {
            "git-workflow.md",
            "git-workflow.instructions.md",
            "SKILL.md",
            "release-manager.md",
            "release-manager.agent.md",
        }
        checked_any_mirror = False
        for path in mirrors:
            if not path.is_file() or path.suffix != ".md":
                continue
            if path.name not in example_basenames:
                continue
            checked_any_mirror = True
            rel = path.relative_to(repo_root()).as_posix()
            self.assertNotIn(rel, out, f"unexpected flag for illustrative mirror {rel}")
        self.assertTrue(checked_any_mirror, "expected to find at least one platform mirror to check")


if __name__ == "__main__":
    unittest.main()
