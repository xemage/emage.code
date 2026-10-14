"""Focused tests for release note classification logic."""
from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


def _load_publish_release_module():
    module_path = repo_root() / "scripts" / "publish-release.py"
    spec = importlib.util.spec_from_file_location("publish_release", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load publish-release module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPublishReleaseClassification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.publish_release = _load_publish_release_module()

    def test_conventional_subjects_map_to_expected_sections(self):
        grouped = self.publish_release.classify_subjects(
            [
                "feat(api): add release endpoint",
                "fix(ci): correct release gate bootstrap",
                "docs: update release runbook",
            ]
        )
        self.assertIn("add release endpoint", grouped["Features"])
        self.assertIn("correct release gate bootstrap", grouped["Bug Fixes"])
        self.assertIn("update release runbook", grouped["Documentation"])

    def test_merge_bugfix_subject_is_classified_as_bug_fix(self):
        grouped = self.publish_release.classify_subjects(
            ["Merge branch 'bugfix/39-release-docs-gate-python-bootstrap' into 'develop'"]
        )
        self.assertIn(
            "merge bugfix/39-release-docs-gate-python-bootstrap into develop",
            grouped["Bug Fixes"],
        )
        self.assertEqual(grouped["Other"], [])

    def test_release_branch_subject_is_classified_as_chore(self):
        grouped = self.publish_release.classify_subjects(["release/v2.0.2"])
        self.assertIn("release branch release/v2.0.2", grouped["Chores"])
        self.assertEqual(grouped["Other"], [])


def _load_dry_run_module():
    module_path = repo_root() / "scripts" / "dry-run-publish-release.py"
    spec = importlib.util.spec_from_file_location("dry_run_publish_release", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load dry-run-publish-release module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSingleReleaseDocument(unittest.TestCase):
    """T619 / P32 O6: one release document, no root release-notes.md."""

    @classmethod
    def setUpClass(cls):
        cls.publish_release = _load_publish_release_module()
        cls.dry_run = _load_dry_run_module()

    def test_write_artifacts_writes_only_changelog(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = self.publish_release.ROOT
            self.publish_release.ROOT = Path(tmp)
            try:
                self.publish_release.write_artifacts("# Changelog\n")
            finally:
                self.publish_release.ROOT = original
            names = sorted(p.name for p in Path(tmp).iterdir())
        self.assertEqual(names, ["CHANGELOG.md"])

    def _fixture_source(self, tmp: str, tag: str = "v1.2.3", text: str | None = None) -> Path:
        source_dir = Path(tmp) / "fixture-releases"
        source_dir.mkdir(exist_ok=True)
        body = "# v1.2.3\n\nLatest release: v1.2.3\n\n## Install\n\nfixture-install\n\n## Highlights\n\nfixture-highlight\n"
        (source_dir / f"{tag}.md").write_text(body if text is None else text, encoding="utf-8")
        return source_dir

    def _run_fixture(self, tmp: str, tag: str = "v1.2.3", text: str | None = None) -> dict:
        source_dir = self._fixture_source(tmp, tag, text)
        return self.dry_run.run_dry_run(
            tag, Path(tmp) / "work", source_dir=source_dir, copy_changelog=False
        )

    def test_dry_run_publishes_release_document_without_root_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run_fixture(tmp)
            changelog = (Path(tmp) / "work" / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertEqual(result["exit"], 0)
        self.assertNotIn("release-notes.md", result["files"])
        self.assertIn("CHANGELOG.md", result["files"])
        self.assertIn("## [v1.2.3] -", changelog)
        post = [c for c in result["sent"] if c["method"] == "POST"]
        self.assertEqual(len(post), 1)
        payload = post[0]["payload"]
        self.assertEqual(payload["tag_name"], "v1.2.3")
        self.assertEqual(payload["ref"], "v1.2.3")
        self.assertIn("fixture-highlight", payload["description"])
        self.assertIn("## Changelog", payload["description"])
        self.assertNotIn(self.dry_run.PLACEHOLDER_TOKEN, result["stdout"])

    def test_dry_run_against_real_release_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.dry_run.run_dry_run("v7.0.1", Path(tmp))
        self.assertEqual(result["exit"], 0)
        self.assertNotIn("release-notes.md", result["files"])
        post = [c for c in result["sent"] if c["method"] == "POST"]
        description = post[0]["payload"]["description"]
        self.assertIn("Latest release: v7.0.1", description)
        brief = (repo_root() / "docs" / "releases" / "v7.0.1.md").read_text(encoding="utf-8")
        self.assertIn(brief.splitlines()[-1].strip(), description)

    def test_dry_run_does_not_write_the_repository(self):
        def digest(path: Path) -> str | None:
            return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

        changelog = repo_root() / "CHANGELOG.md"
        notes = repo_root() / "release-notes.md"
        before = (digest(changelog), digest(notes))
        with tempfile.TemporaryDirectory() as tmp:
            self.dry_run.run_dry_run("v7.0.1", Path(tmp))
        self.assertEqual((digest(changelog), digest(notes)), before)
        self.assertIsNone(digest(notes))

    def test_missing_release_document_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = self.publish_release.ROOT
            self.publish_release.ROOT = Path(tmp)
            try:
                with self.assertRaises(self.publish_release.ReleasePublishError):
                    self.publish_release.load_release_brief("v9.9.9")
            finally:
                self.publish_release.ROOT = original

    def test_empty_release_document_fails_closed(self):
        for text in ("", "  \n\n\t\n"):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as tmp:
                original = self.publish_release.ROOT
                self.publish_release.ROOT = Path(tmp)
                (Path(tmp) / "docs" / "releases").mkdir(parents=True)
                (Path(tmp) / "docs" / "releases" / "v1.2.3.md").write_text(text, encoding="utf-8")
                try:
                    with self.assertRaises(self.publish_release.ReleasePublishError):
                        self.publish_release.load_release_brief("v1.2.3")
                finally:
                    self.publish_release.ROOT = original

    def test_empty_release_document_fails_closed_through_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                self._run_fixture(tmp, text="\n  \n")
            self.assertFalse((Path(tmp) / "work" / "CHANGELOG.md").exists())

    def test_validate_tag_follows_the_ci_rule(self):
        for good in ("v1.2.3", "v10.0.1", "v1.2.3-rc.1", "v1.2.3-RC1"):
            self.assertEqual(self.publish_release.validate_tag(good), good)
        for bad in ("../../x", "v1.2.3\n", "v1.2.3\nv9.9.9", "-v1.2.3", "main", "v1.2", "", "v1.2.3/x", "--all"):
            with self.subTest(tag=bad), self.assertRaises(self.publish_release.ReleasePublishError):
                self.publish_release.validate_tag(bad)

    def test_main_rejects_invalid_tag_before_any_git_call(self):
        calls: list[list[str]] = []
        original_run_git, original_argv = self.publish_release.run_git, sys.argv
        self.publish_release.run_git = lambda args: calls.append(args) or ""
        try:
            for bad in ("../../x", "v1.2.3\n", "--all"):
                sys.argv = ["publish-release.py", f"--tag={bad}", "--api-v4-url", "https://gitlab.invalid",
                            "--project-id", "0", "--token", "placeholder"]
                with self.subTest(tag=bad), self.assertRaises(self.publish_release.ReleasePublishError):
                    self.publish_release.main()
        finally:
            self.publish_release.run_git, sys.argv = original_run_git, original_argv
        self.assertEqual(calls, [])

    def test_git_calls_put_end_of_options_before_the_tag(self):
        calls: list[list[str]] = []

        def fake(args):
            calls.append(args)
            return "1" if args[0] == "rev-list" else ("sha" if args[0] == "merge-base" else "feat: x")

        original = self.publish_release.run_git
        self.publish_release.run_git = fake
        try:
            self.publish_release.get_commit_subjects("v1.2.3", "v1.2.2")
            self.publish_release.get_commit_subjects("v1.2.3", None)
        finally:
            self.publish_release.run_git = original
        self.assertEqual({c[0] for c in calls}, {"merge-base", "rev-list", "log"})
        for call in calls:
            self.assertIn("--end-of-options", call)
            marker = call.index("--end-of-options")
            for arg in call[:marker]:
                self.assertNotIn("v1.2", arg)
            self.assertTrue(any("v1.2" in arg for arg in call[marker + 1:]))

    def test_dry_run_rejects_traversal_and_newline_tags(self):
        for bad in ("../../x", "v1.2.3\n"):
            with self.subTest(tag=bad), tempfile.TemporaryDirectory() as tmp:
                source_dir = self._fixture_source(tmp)
                with self.assertRaises(RuntimeError):
                    self.dry_run.run_dry_run(bad, Path(tmp) / "work", source_dir=source_dir, copy_changelog=False)
                self.assertFalse((Path(tmp) / "work").exists())

    def test_dry_run_source_must_stay_under_release_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = self._fixture_source(tmp)
            outside = Path(tmp) / "outside.md"
            outside.write_text("# outside\n", encoding="utf-8")
            (source_dir / "v2.0.0.md").symlink_to(outside)
            with self.assertRaises(RuntimeError):
                self.dry_run.resolve_release_source(self.publish_release, "v2.0.0", source_dir)

    def test_ci_release_job_keeps_only_changelog_artifact(self):
        ci = (repo_root() / ".gitlab-ci.yml").read_text(encoding="utf-8")
        match = re.search(r"^release:\n(?P<body>(?:[ \t].*\n|\n)+)", ci, re.M)
        self.assertIsNotNone(match)
        body = match.group("body")
        self.assertNotIn("release-notes.md", body)
        artifacts = re.search(r"paths:\n((?:\s+- .+\n)+)", body)
        self.assertIsNotNone(artifacts)
        self.assertEqual(re.findall(r"- (\S+)", artifacts.group(1)), ["CHANGELOG.md"])
        self.assertIn('needs: ["release-docs-gate", "main-develop-drift-gate"]', body)
        self.assertIn("--token \"${WIKI_TOKEN}\"", body)
        self.assertIn(r"/^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$/", body)


if __name__ == "__main__":
    unittest.main()
