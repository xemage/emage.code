"""Focused tests for release note classification logic."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import re
import sys
import tempfile
import types
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
        source = self.dry_run.DryRunSource(source_dir=source_dir, copy_changelog=False)
        return self.dry_run.run_dry_run(tag, Path(tmp) / "work", source)

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
            with self.assertRaisesRegex(RuntimeError, "release brief is empty"):
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
                source = self.dry_run.DryRunSource(source_dir=source_dir, copy_changelog=False)
                with self.assertRaisesRegex(RuntimeError, "invalid release tag"):
                    self.dry_run.run_dry_run(bad, Path(tmp) / "work", source)
                self.assertFalse((Path(tmp) / "work").exists())

    def test_dry_run_source_must_stay_under_release_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = self._fixture_source(tmp)
            outside = Path(tmp) / "outside.md"
            outside.write_text("# outside\n", encoding="utf-8")
            (source_dir / "v2.0.0.md").symlink_to(outside)
            with self.assertRaisesRegex(RuntimeError, "release document escapes"):
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

    def test_tag_re_equals_every_ci_tag_rule(self):
        ci = (repo_root() / ".gitlab-ci.yml").read_text(encoding="utf-8")
        rules = re.findall(r"\$CI_COMMIT_TAG =~ /(.+)/'", ci)
        self.assertGreaterEqual(len(rules), 3)  # release-docs-gate, drift gate, release
        for rule in rules:
            self.assertEqual(self.publish_release.TAG_RE.pattern, rule)


class TestReleaseTitleStrip(unittest.TestCase):
    """T635 / C1: a document starting ``# Release <tag>`` yields exactly one top-level title."""

    @classmethod
    def setUpClass(cls):
        cls.publish_release = _load_publish_release_module()
        cls.dry_run = _load_dry_run_module()

    def _run_document(self, text: str | None) -> str:
        """Dry-run ``v1.2.3``; ``text`` None builds the document from docs/releases/_template.md."""
        with tempfile.TemporaryDirectory() as tmp:
            fixtures = Path(tmp) / "fixture-releases"
            if text is None:
                self.dry_run.write_template_shaped_document(repo_root(), fixtures)
            else:
                fixtures.mkdir()
                (fixtures / "v1.2.3.md").write_text(text, encoding="utf-8")
            source = self.dry_run.DryRunSource(source_dir=fixtures, copy_changelog=False)
            result = self.dry_run.run_dry_run("v1.2.3", Path(tmp) / "work", source)
        post = [c for c in result["sent"] if c["method"] == "POST"]
        self.assertEqual(len(post), 1)
        return post[0]["payload"]["description"]

    def test_title_prefixed_document_has_exactly_one_title_line(self):
        text = "# Release v1.2.3\n\nLatest release: v1.2.3\n\n## Highlights\n\nbody-marker\n"
        description = self._run_document(text)
        self.assertEqual(self.dry_run.top_level_titles(description), ["# Release v1.2.3"])
        self.assertTrue(description.startswith("# Release v1.2.3\n\nLatest release: v1.2.3"))
        self.assertIn("body-marker", description)

    def test_real_template_document_has_exactly_one_title_line(self):
        description = self._run_document(None)
        self.assertEqual(self.dry_run.top_level_titles(description), ["# Release v1.2.3"])

    def test_fenced_comment_lines_are_kept_but_not_counted_as_titles(self):
        """Synthetic document: independent of the content of docs/releases/_template.md."""
        text = (
            "# Release v1.2.3\n\n## Install\n\n```bash\n# Cursor\ncmd-one\n# Gemini CLI\ncmd-two\n```\n\n"
            "## Highlights\n\nbody-marker\n"
        )
        description = self._run_document(text)
        self.assertEqual(self.dry_run.top_level_titles(description), ["# Release v1.2.3"])
        self.assertIn("# Cursor\ncmd-one\n# Gemini CLI", description)

    def test_top_level_titles_ignores_fenced_code(self):
        text = "# One\n\n```bash\n# comment\n```\n\n## Two\n#nospace\n"
        self.assertEqual(self.dry_run.top_level_titles(text), ["# One"])

    def test_removing_the_strip_branch_fails_the_one_title_check(self):
        """Mutation test: with the strip branch disabled the document keeps a second title."""
        source_path = repo_root() / "scripts" / "publish-release.py"
        original = source_path.read_text(encoding="utf-8")
        guard = 'if brief_body.startswith(f"# Release {tag}"):'
        self.assertEqual(original.count(guard), 1, "strip branch moved: update this mutation test")
        mutant = types.ModuleType("publish_release_mutant")
        mutant.__file__ = str(source_path)
        exec(compile(original.replace(guard, "if False:"), str(source_path), "exec"), mutant.__dict__)
        args = ("v1.2.3", None, {}, "# Release v1.2.3\n\nbody\n")
        good = self.publish_release.render_release_description(*args)
        bad = mutant.render_release_description(*args)
        self.assertEqual(len(self.dry_run.top_level_titles(good)), 1)
        self.assertEqual(len(self.dry_run.top_level_titles(bad)), 2)


class TestGuardsAndApiPaths(unittest.TestCase):
    """T635 / N3, N4, N2: git log separator, API target validation, PUT path, cwd isolation."""

    @classmethod
    def setUpClass(cls):
        cls.publish_release = _load_publish_release_module()
        cls.dry_run = _load_dry_run_module()

    def test_git_log_ends_with_double_dash_after_the_revision(self):
        calls: list[list[str]] = []
        original = self.publish_release.run_git
        self.publish_release.run_git = lambda args: calls.append(args) or "feat: x"
        try:
            self.publish_release.get_commit_subjects("v1.2.3", None)
        finally:
            self.publish_release.run_git = original
        self.assertEqual(calls, [["log", "--pretty=%s", "--end-of-options", "v1.2.3", "--"]])

    def test_api_target_validation_fails_closed(self):
        ok = self.publish_release.validate_api_target
        ok("https://gitlab.example.com/api/v4", "12345")
        error = self.publish_release.ReleasePublishError
        for url in ("http://gitlab.example.com/api/v4", "file:///etc/passwd", "ftp://x", ""):
            with self.subTest(url=url), self.assertRaisesRegex(error, "invalid --api-v4-url"):
                ok(url, "1")
        for pid in ("", "abc", "1/2", "12 ", "-1", "\u00b2", "1\n"):
            with self.subTest(project_id=pid), self.assertRaisesRegex(error, "invalid --project-id"):
                ok("https://gitlab.example.com/api/v4", pid)

    def test_main_rejects_bad_api_target_before_any_git_call(self):
        calls: list[list[str]] = []
        original_run_git, original_argv = self.publish_release.run_git, sys.argv
        self.publish_release.run_git = lambda args: calls.append(args) or ""
        try:
            for url, pid in (("http://gitlab.invalid/api/v4", "1"), ("https://gitlab.invalid/api/v4", "x")):
                sys.argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", url,
                            "--project-id", pid, "--token", "placeholder"]
                with self.subTest(url=url, project_id=pid), self.assertRaises(self.publish_release.ReleasePublishError):
                    self.publish_release.main()
        finally:
            self.publish_release.run_git, sys.argv = original_run_git, original_argv
        self.assertEqual(calls, [])

    def _release_calls(self, get_result):
        """Run create_or_update_release against a fake API; ``get_result`` answers the GET."""
        sent: list[tuple[str, str, dict | None]] = []
        error = self.publish_release.ReleasePublishError

        def fake(method, url, token, payload=None):
            sent.append((method, url, payload))
            if method == "GET":
                if isinstance(get_result, str):
                    raise error(get_result)
                return get_result
            return {"tag_name": "v1.2.3"}

        original = self.publish_release.gitlab_request
        self.publish_release.gitlab_request = fake
        try:
            self.publish_release.create_or_update_release(
                "v1.2.3", "https://gitlab.invalid/api/v4", "7", "placeholder", "desc"
            )
        finally:
            self.publish_release.gitlab_request = original
        return sent

    def test_existing_release_is_updated_with_one_put(self):
        sent = self._release_calls({"tag_name": "v1.2.3"})
        endpoint = "https://gitlab.invalid/api/v4/projects/7/releases/v1.2.3"
        self.assertEqual([m for m, _, _ in sent], ["GET", "PUT"])
        self.assertEqual(sent[1][1], endpoint)
        self.assertEqual(sent[1][2]["description"], "desc")
        self.assertEqual(sent[1][2]["tag_name"], "v1.2.3")

    def test_missing_release_is_created_with_one_post(self):
        sent = self._release_calls("GitLab API GET u failed: 404 not found")
        self.assertEqual([m for m, _, _ in sent], ["GET", "POST"])
        self.assertEqual(sent[1][1], "https://gitlab.invalid/api/v4/projects/7/releases")

    def test_non_404_lookup_error_is_not_swallowed(self):
        with self.assertRaisesRegex(RuntimeError, "failed: 500 boom"):
            self._release_calls("GitLab API GET u failed: 500 boom")

    def test_dry_run_restores_cwd_and_runs_inside_the_work_dir(self):
        seen: list[str] = []
        original_write = self.publish_release.write_artifacts
        before = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            fixtures = Path(tmp) / "fixture-releases"
            self.dry_run.write_template_shaped_document(repo_root(), fixtures)
            source = self.dry_run.DryRunSource(source_dir=fixtures, copy_changelog=False)
            original_load = self.dry_run.load_publish_release

            def load(repo):
                module = original_load(repo)
                real_write = module.write_artifacts
                module.write_artifacts = lambda text: (seen.append(os.getcwd()), real_write(text))[1]
                return module

            self.dry_run.load_publish_release = load
            try:
                result = self.dry_run.run_dry_run("v1.2.3", Path(tmp) / "work", source)
            finally:
                self.dry_run.load_publish_release = original_load
            self.assertEqual(result["exit"], 0)
            self.assertEqual([Path(p).resolve() for p in seen], [(Path(tmp) / "work").resolve()])
        self.assertEqual(os.getcwd(), before)
        self.assertIs(self.publish_release.write_artifacts, original_write)

    def test_dry_run_restores_cwd_when_main_fails(self):
        before = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            fixtures = Path(tmp) / "fixture-releases"
            fixtures.mkdir()
            (fixtures / "v1.2.3.md").write_text("  \n", encoding="utf-8")
            source = self.dry_run.DryRunSource(source_dir=fixtures, copy_changelog=False)
            with self.assertRaisesRegex(RuntimeError, "release brief is empty"):
                self.dry_run.run_dry_run("v1.2.3", Path(tmp) / "work", source)
        self.assertEqual(os.getcwd(), before)


if __name__ == "__main__":
    unittest.main()
