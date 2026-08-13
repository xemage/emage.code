"""Regression tests for scripts/check-version-consistency.py (Gate G0 — Truth)."""
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

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
            any("implementation/README.md:4" in line and "v6.0.1" in line for line in lines)
        )

    def test_fail_when_marker_unparseable(self):
        code, lines = self.mod.evaluate(None, {})
        self.assertEqual(code, 1)


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
            "release-manager.mdc",
        }
        checked_any_mirror = False
        for path in mirrors:
            if not path.is_file() or path.suffix != ".md" and path.suffix != ".mdc":
                continue
            if path.name not in example_basenames:
                continue
            checked_any_mirror = True
            rel = path.relative_to(repo_root()).as_posix()
            self.assertNotIn(rel, out, f"unexpected flag for illustrative mirror {rel}")
        self.assertTrue(checked_any_mirror, "expected to find at least one platform mirror to check")


if __name__ == "__main__":
    unittest.main()
