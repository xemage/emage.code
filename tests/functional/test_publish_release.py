"""Focused tests for release note classification logic."""
from __future__ import annotations

import hashlib
import http.server
import importlib.util
import os
import re
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

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
        self.assertEqual(payload["description"], result["document"])  # T640 / C3: the document, whole
        self.assertIn("fixture-highlight", payload["description"])
        self.assertNotIn("## Changelog", payload["description"])
        self.assertIn("### Features", changelog)
        self.assertNotIn(self.dry_run.PLACEHOLDER_TOKEN, result["stdout"])

    def test_dry_run_against_real_release_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.dry_run.run_dry_run("v7.0.1", Path(tmp))
        self.assertEqual(result["exit"], 0)
        self.assertNotIn("release-notes.md", result["files"])
        post = [c for c in result["sent"] if c["method"] == "POST"]
        description = post[0]["payload"]["description"]
        self.assertIn("Latest release: v7.0.1", description)
        brief = (repo_root() / "docs" / "releases" / "v7.0.1.md").read_bytes().decode("utf-8")
        self.assertEqual(description, brief)

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
        self.assertIn("--token-env WIKI_TOKEN", body)  # T675: the name, never the value, is in argv
        self.assertNotIn("--token \"", body)
        self.assertNotIn("${WIKI_TOKEN}", body)
        self.assertIn(r"/^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$/", body)

    def test_tag_re_equals_every_ci_tag_rule(self):
        ci = (repo_root() / ".gitlab-ci.yml").read_text(encoding="utf-8")
        rules = re.findall(r"\$CI_COMMIT_TAG =~ /(.+)/'", ci)
        self.assertGreaterEqual(len(rules), 3)  # release-docs-gate, drift gate, release
        for rule in rules:
            self.assertEqual(self.publish_release.TAG_RE.pattern, rule)


class TestReleaseDescriptionIsTheDocument(unittest.TestCase):
    """T640 / C3: description == release document byte-for-byte; the commit list is CHANGELOG.md only.

    Builds on T635's one-title tests; the title-strip branch is gone (dead under C3).
    """

    @classmethod
    def setUpClass(cls):
        cls.publish_release = _load_publish_release_module()
        cls.dry_run = _load_dry_run_module()

    def _run_document(self, text: str | None, repo: Path | None = None, tmp: str | None = None) -> dict:
        """Dry-run ``v1.2.3``; ``text`` None builds the document from docs/releases/_template.md."""
        with tempfile.TemporaryDirectory() as made:
            base = Path(tmp or made)
            fixtures = base / "fixture-releases"
            if text is None:
                self.dry_run.write_template_shaped_document(repo_root(), fixtures)
            else:
                fixtures.mkdir(parents=True)
                (fixtures / "v1.2.3.md").write_bytes(text.encode("utf-8"))
            source = self.dry_run.DryRunSource(repo=repo or repo_root(), source_dir=fixtures, copy_changelog=False)
            return self.dry_run.run_dry_run("v1.2.3", base / "work", source)

    def _description(self, result: dict) -> str:
        post = [c for c in result["sent"] if c["method"] == "POST"]
        self.assertEqual(len(post), 1)
        return post[0]["payload"]["description"]

    def test_description_equals_the_document_byte_for_byte(self):
        text = "# Release v1.2.3\r\n\nLatest release: v1.2.3\n\n## Highlights\n\nbody-marker\n\n\n  trailing  \n"
        result = self._run_document(text)
        self.assertEqual(self._description(result), text)
        self.assertEqual(self.dry_run.check_result(result, "v1.2.3"), [])

    def test_description_has_no_generated_section_and_no_commit_list(self):
        description = self._description(self._run_document("# Release v1.2.3\n\nbody-marker\n"))
        for generated in ("## Changelog", "_Commits since", "### Features", "single release document", "\n---\n"):
            self.assertNotIn(generated, description)

    def test_real_template_document_has_exactly_one_title_line(self):
        result = self._run_document(None)
        template = (repo_root() / "docs" / "releases" / "_template.md").read_text(encoding="utf-8")
        self.assertEqual(self._description(result), template.replace("vX.Y.Z", "v1.2.3"))
        self.assertEqual(self.dry_run.top_level_titles(self._description(result)), ["# Release v1.2.3"])

    def test_fenced_comment_lines_are_kept_but_not_counted_as_titles(self):
        """Synthetic document: independent of the content of docs/releases/_template.md."""
        text = (
            "# Release v1.2.3\n\n## Install\n\n```bash\n# Cursor\ncmd-one\n# Gemini CLI\ncmd-two\n```\n\n"
            "## Highlights\n\nbody-marker\n"
        )
        description = self._description(self._run_document(text))
        self.assertEqual(self.dry_run.top_level_titles(description), ["# Release v1.2.3"])
        self.assertIn("# Cursor\ncmd-one\n# Gemini CLI", description)

    def test_top_level_titles_ignores_fenced_code(self):
        text = "# One\n\n```bash\n# comment\n```\n\n## Two\n#nospace\n"
        self.assertEqual(self.dry_run.top_level_titles(text), ["# One"])

    def test_changelog_lists_no_merge_commits_and_keeps_group_headings(self):
        result = self._run_document("# Release v1.2.3\n\nbody\n")
        entry = self.dry_run.changelog_entry(result["changelog"], "v1.2.3")
        for heading in ("### Features", "### Bug Fixes", "### Documentation"):
            self.assertIn(heading, entry)
        self.assertNotIn("## Changelog", entry)
        for merge in self.dry_run.MERGE_SUBJECTS:
            self.assertNotIn(merge, entry)
        self.assertNotIn("merge feature/", entry)
        self.assertNotIn("merge bugfix/", entry)

    def test_update_changelog_drops_h1_h2_lines_and_keeps_h3_groups(self):
        section = "## Changelog\n_Commits since v1.0.0._\n\n### Features\n- a\n- # not a heading\n"
        with tempfile.TemporaryDirectory() as tmp:
            original = self.publish_release.ROOT
            self.publish_release.ROOT = Path(tmp)
            try:
                text = self.publish_release.update_changelog("v1.2.3", section)
            finally:
                self.publish_release.ROOT = original
        self.assertIn("### Features\n- a\n- # not a heading", text)
        self.assertNotIn("## Changelog", text)

    def _mutated_run(self, old: str, new: str) -> dict:
        """Dry-run with scripts/publish-release.py copied into a temp repo and ``old`` replaced by ``new``."""
        original = (repo_root() / "scripts" / "publish-release.py").read_text(encoding="utf-8")
        self.assertEqual(original.count(old), 1, f"{old!r} moved: update this mutation test")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / "scripts").mkdir(parents=True)
            (repo / "scripts" / "publish-release.py").write_text(original.replace(old, new), encoding="utf-8")
            return self._run_document("# Release v1.2.3\n\nbody\n", repo=repo, tmp=str(Path(tmp) / "run"))

    def test_unmutated_script_passes_the_dry_run_checks(self):
        result = self._mutated_run("def update_changelog", "def update_changelog")
        self.assertEqual(self.dry_run.check_result(result, "v1.2.3"), [])

    def test_mutation_appending_the_commit_list_to_the_description_is_detected(self):
        result = self._mutated_run(
            "    return brief\n\n\ndef update_changelog",
            "    return brief + '\\n---\\n'\n\n\ndef update_changelog",
        )
        self.assertIn("description differs from the release document", self.dry_run.check_result(result, "v1.2.3"))

    def test_mutation_stripping_the_title_is_detected(self):
        result = self._mutated_run(
            "    return brief\n\n\ndef update_changelog",
            "    return brief.split('\\n', 1)[1]\n\n\ndef update_changelog",
        )
        self.assertIn("description differs from the release document", self.dry_run.check_result(result, "v1.2.3"))

    def test_mutation_dropping_no_merges_is_detected(self):
        result = self._mutated_run('["log", "--no-merges", ', '["log", ')
        self.assertIn("CHANGELOG.md section lists a merge commit", self.dry_run.check_result(result, "v1.2.3"))

    def test_mutation_feeding_the_description_to_the_changelog_is_detected(self):
        result = self._mutated_run(
            "update_changelog(args.tag, render_changelog_section(previous_tag, grouped))",
            "update_changelog(args.tag, description)",
        )
        self.assertIn(
            "CHANGELOG.md section misses commit 'feat(release): single release document'",
            self.dry_run.check_result(result, "v1.2.3"),
        )


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
        self.assertEqual(calls, [["log", "--no-merges", "--pretty=%s", "--end-of-options", "v1.2.3", "--"]])

    def test_api_target_validation_fails_closed(self):
        ok = self.publish_release.validate_api_target
        ok("https://gitlab.example.com/api/v4", "12345")
        error = self.publish_release.ReleasePublishError
        for url in ("http://gitlab.example.com/api/v4", "file:///etc/passwd", "ftp://x", "", "https://"):
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
                if isinstance(get_result, tuple):
                    raise error(get_result[1], get_result[0])
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
        sent = self._release_calls((404, "GitLab API GET u failed: 404 not found"))
        self.assertEqual([m for m, _, _ in sent], ["GET", "POST"])
        self.assertEqual(sent[1][1], "https://gitlab.invalid/api/v4/projects/7/releases")

    def test_non_404_lookup_error_is_not_swallowed(self):
        with self.assertRaisesRegex(RuntimeError, "failed: 500 boom"):
            self._release_calls((500, "GitLab API GET u failed: 500 boom"))

    def test_only_the_status_code_decides_that_a_release_does_not_exist(self):
        """SEC-T675-10: a message that merely contains ' 404 ' (a 500 body, say) is not a 404."""
        with self.assertRaisesRegex(RuntimeError, "boom"):
            self._release_calls((500, "GitLab API GET u failed: 500 body says 404 not found boom"))
        with self.assertRaisesRegex(RuntimeError, "no status"):
            self._release_calls((None, "GitLab API GET u failed: 404 no status"))

    def test_dry_run_restores_cwd_and_runs_inside_the_work_dir(self):
        seen: list[str] = []
        before = os.getcwd()
        argv_before, urlopen_before = list(sys.argv), urllib.request.urlopen
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
        # SEC-T635-04: the old assertIs compared two untouched objects (the dry run patches its own
        # copy of the module). What the dry run really patches in this process is checked here.
        self.assertEqual(sys.argv, argv_before)
        self.assertIs(urllib.request.urlopen, urlopen_before)

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


class TestApiTargetIsParsed(unittest.TestCase):
    """SEC-T635-01 / SEC-T640-04: validate_api_target parses the URL; the host can be pinned."""

    @classmethod
    def setUpClass(cls):
        cls.pr = _load_publish_release_module()

    def test_accepts_clean_https_api_v4_urls(self):
        for url in (
            "https://gitlab.com/api/v4",
            "https://gitlab.example.com:8443/api/v4",
            "https://gitlab.example.com/sub/path/api/v4",
            "https://GITLAB.example.com/api/v4",
        ):
            with self.subTest(url=url):
                self.pr.validate_api_target(url, "1")

    def test_rejects_what_the_prefix_check_let_through(self):
        for url in (
            "https://user@gitlab.example.com/api/v4",
            "https://user:pw@gitlab.example.com/api/v4",
            "https://gitlab.example.com@evil.example/api/v4",
            "https://gitlab.example.com/api/v4?x=1",
            "https://gitlab.example.com/api/v4#frag",
            "https://gitlab.example.com/api/v4/",
            "https://gitlab.example.com/other",
            "https://gitlab.example.com",
            "https:///api/v4",
            "https://gitlab.example.com:99999/api/v4",
            "https://gitlab.example.com:abc/api/v4",
            "https://gitlab.example.com/api/v4 ",
            "https://gitlab.example.com/api/v4\n",
            "https://gitlab.example.com\\@evil.example/api/v4",
            "https://gitlab.example.com/a pi/v4",
            "https://gitlab.example.com/../api/v4",
            "https://gitlab.example.com/./api/v4",
            "https://gitlab.example.com/a/../api/v4",
            "https://gitlab.example.com/a/./b/api/v4",
        ):
            with self.subTest(url=url), self.assertRaisesRegex(self.pr.ReleasePublishError, "invalid --api-v4-url"):
                self.pr.validate_api_target(url, "1")

    def test_dot_like_names_that_are_not_dot_segments_are_allowed(self):
        self.pr.validate_api_target("https://gitlab.example.com/..a/.b/api/v4", "1")

    def test_an_empty_host_pin_is_an_error_not_no_pin(self):
        with self.assertRaisesRegex(self.pr.ReleasePublishError, "host does not match"):
            self.pr.validate_api_target("https://gitlab.example.com/api/v4", "1", expected_host="")

    def test_resolve_expected_host(self):
        r = self.pr.resolve_expected_host
        error = self.pr.ReleasePublishError
        self.assertEqual(r("gitlab.com", {}), "gitlab.com")
        self.assertEqual(r(" gitlab.com ", {"CI": "true"}), "gitlab.com")
        self.assertEqual(r(None, {"CI_SERVER_HOST": "gitlab.example.com"}), "gitlab.example.com")
        self.assertIsNone(r(None, {}))  # a local run without CI may go unpinned
        for flag, environ, message in (
            ("", {}, "must not be empty"),
            ("  ", {}, "must not be empty"),
            (None, {"CI_SERVER_HOST": ""}, "must not be empty"),
            (None, {"CI": "true"}, "required in CI"),
            (None, {"CI": "true", "CI_SERVER_HOST_X": "x"}, "required in CI"),
        ):
            with self.subTest(flag=flag, environ=environ), self.assertRaisesRegex(error, message):
                r(flag, environ)

    def test_main_refuses_an_empty_host_pin_and_a_missing_one_in_ci_before_any_git_call(self):
        calls: list[list[str]] = []
        original_run_git, original_argv = self.pr.run_git, sys.argv
        self.pr.run_git = lambda args: calls.append(args) or ""
        base = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", "https://gitlab.com/api/v4",
                "--project-id", "1", "--token-env", "X"]
        try:
            for extra, environ, message in (
                (["--expected-host", ""], {}, "must not be empty"),
                ([], {"CI": "true"}, "required in CI"),
            ):
                sys.argv = base + extra
                clean = {k: v for k, v in os.environ.items() if k not in ("CI", "CI_SERVER_HOST")}
                with self.subTest(extra=extra), mock.patch.dict(os.environ, {**clean, **environ}, clear=True):
                    with self.assertRaisesRegex(self.pr.ReleasePublishError, message):
                        self.pr.main()
        finally:
            self.pr.run_git, sys.argv = original_run_git, original_argv
        self.assertEqual(calls, [])

    def test_host_pin(self):
        ok = "https://gitlab.example.com/api/v4"
        self.pr.validate_api_target(ok, "1", expected_host="gitlab.example.com")
        self.pr.validate_api_target(ok, "1", expected_host="GitLab.Example.com")
        self.pr.validate_api_target(ok, "1", expected_host=None)
        for host in ("evil.example", "gitlab.example.com.evil.example", "example.com"):
            with self.subTest(host=host), self.assertRaisesRegex(self.pr.ReleasePublishError, "host does not match"):
                self.pr.validate_api_target(ok, "1", expected_host=host)

    def test_main_pins_the_host_from_the_expected_host_flag_before_any_git_call(self):
        calls: list[list[str]] = []
        original_run_git, original_argv = self.pr.run_git, sys.argv
        self.pr.run_git = lambda args: calls.append(args) or ""
        sys.argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", "https://evil.example/api/v4",
                    "--expected-host", "gitlab.com", "--project-id", "1", "--token-env", "X"]
        try:
            with self.assertRaisesRegex(self.pr.ReleasePublishError, "host does not match"):
                self.pr.main()
        finally:
            self.pr.run_git, sys.argv = original_run_git, original_argv
        self.assertEqual(calls, [])


class TestTokenFromEnvironment(unittest.TestCase):
    """SEC-T619-05 / SEC-003: the token is read from the environment; --token still works, loudly."""

    SECRET = "glpat-FAKE-not-a-real-token"

    @classmethod
    def setUpClass(cls):
        cls.pr = _load_publish_release_module()
        cls.dry_run = _load_dry_run_module()

    def test_token_env_value_is_read_from_the_named_variable(self):
        self.assertEqual(self.pr.resolve_token(None, "MY_TOKEN", {"MY_TOKEN": self.SECRET}), self.SECRET)

    def test_deprecated_token_flag_still_works_and_warns_without_printing_the_value(self):
        with mock.patch("sys.stderr") as err, mock.patch("sys.stdout") as out:
            self.assertEqual(self.pr.resolve_token(self.SECRET, None, {}), self.SECRET)
        written = "".join(c.args[0] for c in err.write.call_args_list + out.write.call_args_list)
        self.assertIn("--token-env", written)
        self.assertNotIn(self.SECRET, written)

    def test_refusals_name_the_variable_never_the_value(self):
        error = self.pr.ReleasePublishError
        cases = (
            (self.SECRET, "X", {}, "either --token-env or --token"),
            (None, None, {}, "no API token"),
            (None, "MISSING", {}, "MISSING is not set or empty"),
            (None, "EMPTY", {"EMPTY": ""}, "EMPTY is not set or empty"),
            (None, "bad name", {"bad name": self.SECRET}, "invalid --token-env"),
            (None, "T", {"T": self.SECRET + "\nX-Evil: 1"}, "control character"),
            (self.SECRET + "\r", None, {}, "control character"),
        )
        for token, env_name, environ, message in cases:
            with self.subTest(message=message), mock.patch("sys.stderr"):
                with self.assertRaisesRegex(error, message) as ctx:
                    self.pr.resolve_token(token, env_name, environ)
                self.assertNotIn(self.SECRET, str(ctx.exception))

    def test_main_reads_the_token_from_the_environment_and_passes_it_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            sent = self._run_main(tmp, ["--token-env", "T675_TEST_TOKEN"], {"T675_TEST_TOKEN": self.SECRET})
        self.assertEqual({token for _, token in sent}, {self.SECRET})

    def test_main_without_a_token_fails_before_any_git_call_unless_skip_api(self):
        calls: list[list[str]] = []
        original, argv = self.pr.run_git, sys.argv
        self.pr.run_git = lambda args: calls.append(args) or ""
        sys.argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", "https://gitlab.invalid/api/v4",
                    "--expected-host", "gitlab.invalid", "--project-id", "1"]
        try:
            with self.assertRaisesRegex(self.pr.ReleasePublishError, "no API token"):
                self.pr.main()
        finally:
            self.pr.run_git, sys.argv = original, argv
        self.assertEqual(calls, [])

    def _run_main(self, tmp: str, token_args: list[str], environ: dict[str, str]) -> list[tuple[str, str]]:
        """Run main() against a temp root with a fake API; return (method, token) per call."""
        root = Path(tmp)
        (root / "docs" / "releases").mkdir(parents=True)
        (root / "docs" / "releases" / "v1.2.3.md").write_text("# Release v1.2.3\n\nbody\n", encoding="utf-8")
        seen: list[tuple[str, str]] = []

        def fake_request(method, url, token, payload=None):
            seen.append((method, token))
            if method == "GET":
                raise self.pr.ReleasePublishError("GitLab API GET u failed: 404 fake", 404)
            return {"tag_name": "v1.2.3"}

        def fake_git(args):
            return {"tag": "v1.2.3\nv1.2.2", "rev-parse": "false", "merge-base": "sha", "rev-list": "1"}.get(
                args[0], "feat: x")

        argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", "https://gitlab.invalid/api/v4",
                "--expected-host", "gitlab.invalid", "--project-id", "1", *token_args]
        with mock.patch.object(self.pr, "ROOT", root), mock.patch.object(self.pr, "run_git", fake_git), \
                mock.patch.object(self.pr, "gitlab_request", fake_request), mock.patch.object(sys, "argv", argv), \
                mock.patch.dict(os.environ, environ), mock.patch("sys.stdout") as out:
            self.assertEqual(self.pr.main(), 0)
            printed = "".join(c.args[0] for c in out.write.call_args_list)
        self.assertNotIn(self.SECRET, printed)
        return seen

    def test_dry_run_passes_the_token_by_environment_and_restores_it(self):
        self.assertNotIn(self.dry_run.TOKEN_ENV, os.environ)
        argv_seen: list[list[str]] = []
        original_load = self.dry_run.load_publish_release

        def load(repo):
            module = original_load(repo)
            real_main = module.main
            module.main = lambda: (argv_seen.append(list(sys.argv)), real_main())[1]
            return module

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(self.dry_run, "load_publish_release", load):
            fixtures = Path(tmp) / "f"
            self.dry_run.write_template_shaped_document(repo_root(), fixtures)
            result = self.dry_run.run_dry_run(
                "v1.2.3", Path(tmp) / "work", self.dry_run.DryRunSource(source_dir=fixtures, copy_changelog=False))
        self.assertEqual(result["exit"], 0)
        flat = " ".join(argv_seen[0])
        self.assertIn("--token-env " + self.dry_run.TOKEN_ENV, flat)
        self.assertNotIn(self.dry_run.PLACEHOLDER_TOKEN, flat)
        self.assertNotIn(self.dry_run.TOKEN_ENV, os.environ)


class _RecordingHandler(http.server.BaseHTTPRequestHandler):
    seen: list[str | None] = []
    redirect_to: str | None = None

    def do_GET(self):  # noqa: N802
        type(self).seen.append(self.headers.get("PRIVATE-TOKEN"))
        if self.redirect_to:
            self.send_response(302)
            self.send_header("Location", self.redirect_to)
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")

    def log_message(self, *args):  # silence
        pass


class TestRequestHardening(unittest.TestCase):
    """SEC-T635-02: no redirect is followed; TL-T649-07: read-time failures are ReleasePublishError."""

    @classmethod
    def setUpClass(cls):
        cls.pr = _load_publish_release_module()

    def _serve(self, handler):
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"http://127.0.0.1:{server.server_address[1]}"

    def test_a_redirect_is_refused_and_the_token_is_not_resent(self):
        target = type("Target", (_RecordingHandler,), {"seen": [], "redirect_to": None})
        target_url = self._serve(target)
        origin = type("Origin", (_RecordingHandler,), {"seen": [], "redirect_to": target_url + "/leak"})
        origin_url = self._serve(origin)
        with self.assertRaisesRegex(self.pr.ReleasePublishError, "failed: 302"):
            self.pr.gitlab_request("GET", origin_url + "/x", "tok-fake")
        self.assertEqual(origin.seen, ["tok-fake"])  # sent once to the intended host ...
        self.assertEqual(target.seen, [])  # ... and never to the redirect target

    def test_the_default_opener_would_have_followed_the_redirect(self):
        """Control: without the refusing handler the same server pair leaks the header."""
        target = type("Target", (_RecordingHandler,), {"seen": [], "redirect_to": None})
        target_url = self._serve(target)
        origin = type("Origin", (_RecordingHandler,), {"seen": [], "redirect_to": target_url + "/leak"})
        origin_url = self._serve(origin)
        with mock.patch.object(self.pr, "OPENER", urllib.request.build_opener()):
            self.pr.gitlab_request("GET", origin_url + "/x", "tok-fake")
        self.assertEqual(target.seen, ["tok-fake"])

    def test_an_http_error_response_carries_its_status_code(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                code = int(self.path.strip("/"))
                self.send_response(code)
                self.end_headers()
                self.wfile.write(b"body mentions 404 here")

            def log_message(self, *args):
                pass

        base = self._serve(Handler)
        for code in (404, 500):
            with self.subTest(code=code), self.assertRaises(self.pr.ReleasePublishError) as ctx:
                self.pr.gitlab_request("GET", f"{base}/{code}", "tok-fake")
            self.assertEqual(ctx.exception.status, code)
        with self.assertRaises(self.pr.ReleasePublishError) as ctx:
            self.pr.gitlab_request("GET", "http://127.0.0.1:1/x", "tok-fake")
        self.assertIsNone(ctx.exception.status)

    def _opener_returning(self, response):
        class Opener:
            def open(self, request, timeout=None):
                return response
        return mock.patch.object(self.pr, "OPENER", Opener())

    def _response(self, read):
        class Response:
            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, *exc):
                return False

            def read(self_inner):
                return read()
        return Response()

    def test_socket_timeout_and_reset_during_read_are_release_errors(self):
        for exc in (TimeoutError("timed out"), ConnectionResetError("reset")):
            with self.subTest(exc=type(exc).__name__), self._opener_returning(self._response(mock.Mock(side_effect=exc))):
                with self.assertRaisesRegex(self.pr.ReleasePublishError, type(exc).__name__):
                    self.pr.gitlab_request("GET", "https://gitlab.invalid/api/v4/x", "tok")

    def test_incomplete_read_and_non_json_or_non_utf8_bodies_are_release_errors(self):
        import http.client
        bodies = (
            mock.Mock(side_effect=http.client.IncompleteRead(b"")),
            lambda: b"\xff\xfe",
            lambda: b"not json",
        )
        for read in bodies:
            with self.subTest(read=repr(read)[:30]), self._opener_returning(self._response(read)):
                with self.assertRaises(self.pr.ReleasePublishError):
                    self.pr.gitlab_request("GET", "https://gitlab.invalid/api/v4/x", "tok")


class TestReleaseBriefAndTagGuards(unittest.TestCase):
    """SEC-T640-01..03 and the K-12 changelog placement."""

    @classmethod
    def setUpClass(cls):
        cls.pr = _load_publish_release_module()

    def _root(self, tmp: str):
        original = self.pr.ROOT
        self.pr.ROOT = Path(tmp)
        self.addCleanup(setattr, self.pr, "ROOT", original)
        releases = Path(tmp) / "docs" / "releases"
        releases.mkdir(parents=True)
        return releases

    def test_a_symlinked_release_document_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            releases = self._root(tmp)
            secret = Path(tmp) / "outside.txt"
            secret.write_text("not a release document\n", encoding="utf-8")
            (releases / "v1.2.3.md").symlink_to(secret)
            with self.assertRaisesRegex(self.pr.ReleasePublishError, "regular file under docs/releases"):
                self.pr.load_release_brief("v1.2.3")

    def test_a_symlinked_release_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            elsewhere = Path(tmp) / "elsewhere"
            elsewhere.mkdir()
            (elsewhere / "v1.2.3.md").write_text("# Release v1.2.3\n", encoding="utf-8")
            (Path(tmp) / "docs").mkdir()
            (Path(tmp) / "docs" / "releases").symlink_to(elsewhere)
            original = self.pr.ROOT
            self.pr.ROOT = Path(tmp)
            self.addCleanup(setattr, self.pr, "ROOT", original)
            with self.assertRaisesRegex(self.pr.ReleasePublishError, "regular file under docs/releases"):
                self.pr.load_release_brief("v1.2.3")

    def test_a_regular_release_document_is_still_returned_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            releases = self._root(tmp)
            (releases / "v1.2.3.md").write_bytes(b"# Release v1.2.3\r\n\nbody\n")
            self.assertEqual(self.pr.load_release_brief("v1.2.3"), "# Release v1.2.3\r\n\nbody\n")

    def test_non_utf8_release_document_is_a_release_error_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            releases = self._root(tmp)
            (releases / "v1.2.3.md").write_bytes(b"# Release \xff\xfe\n")
            with self.assertRaisesRegex(self.pr.ReleasePublishError, "not readable UTF-8"):
                self.pr.load_release_brief("v1.2.3")

    def test_get_tag_list_keeps_only_release_tags(self):
        listing = "v1.2.3\nbackup/pre-rewrite\n-v9\nv1.2.3\n--all\nv1.2.2-rc.1\nv1.2\nfoo\"bar"
        with mock.patch.object(self.pr, "run_git", lambda args: listing):
            self.assertEqual(self.pr.get_tag_list(), ["v1.2.3", "v1.2.3", "v1.2.2-rc.1"])

    def test_previous_tag_skips_a_stray_tag(self):
        with mock.patch.object(self.pr, "run_git", lambda args: "v2.0.0\nstray-tag\nv1.9.0"):
            tags = self.pr.get_tag_list()
        self.assertEqual(self.pr.resolve_previous_tag("v2.0.0", tags), "v1.9.0")

    def test_commit_subjects_lose_control_characters(self):
        log = "feat: ok\x1b[31m red\nfix(x): tab\there\x00 end\n  \x07\n"
        calls = {"log": log}
        with mock.patch.object(self.pr, "run_git", lambda args: calls.get(args[0], "1")):
            subjects = self.pr.get_commit_subjects("v1.2.3", None)
        self.assertEqual(subjects, ["feat: ok[31m red", "fix(x): tabhere end"])

    def test_git_runs_without_the_token_variable_but_with_the_rest_of_the_environment(self):
        seen: list[dict] = []
        fake = mock.Mock(returncode=0, stdout="ok\n", stderr="")

        def run(argv, **kwargs):
            seen.append(kwargs)
            return fake

        with mock.patch.dict(os.environ, {"WIKI_TOKEN": "glpat-FAKE", "MY_TOKEN_VAR": "glpat-FAKE2", "KEEP_ME": "1"}), \
                mock.patch.object(self.pr.subprocess, "run", run), \
                mock.patch.object(self.pr, "WITHHELD_ENV_NAMES", {"WIKI_TOKEN", "MY_TOKEN_VAR"}):
            self.assertEqual(self.pr.run_git(["status"]), "ok")
        env = seen[0]["env"]
        self.assertNotIn("WIKI_TOKEN", env)
        self.assertNotIn("MY_TOKEN_VAR", env)
        self.assertEqual(env["KEEP_ME"], "1")
        self.assertIn("PATH", env)

    def test_main_withholds_the_named_token_variable_from_git(self):
        names = set(self.pr.WITHHELD_ENV_NAMES)
        self.addCleanup(lambda: (self.pr.WITHHELD_ENV_NAMES.clear(), self.pr.WITHHELD_ENV_NAMES.update(names)))
        argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", "https://gitlab.invalid/api/v4",
                "--expected-host", "gitlab.invalid", "--project-id", "1", "--token-env", "T675_ODD_NAME"]
        with mock.patch.object(sys, "argv", argv), mock.patch.dict(os.environ, {"T675_ODD_NAME": "x"}), \
                mock.patch.object(self.pr, "run_git", side_effect=RuntimeError("stop")):
            with self.assertRaisesRegex(RuntimeError, "stop"):
                self.pr.main()
        self.assertIn("T675_ODD_NAME", self.pr.WITHHELD_ENV_NAMES)

    def test_a_changelog_that_is_not_utf8_is_a_release_error(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(self.pr, "ROOT", Path(tmp)):
            (Path(tmp) / "CHANGELOG.md").write_bytes(b"# Changelog\n\xff\xfe\n")
            with self.assertRaisesRegex(self.pr.ReleasePublishError, "CHANGELOG.md is not readable"):
                self.pr.update_changelog("v1.2.3", "### Features\n- x\n")

    def _changelog(self, existing: str | None) -> str:
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(self.pr, "ROOT", Path(tmp)):
            if existing is not None:
                (Path(tmp) / "CHANGELOG.md").write_text(existing, encoding="utf-8")
            return self.pr.update_changelog("v1.2.3", "## Changelog\n### Features\n- new thing\n")

    def test_changelog_entry_goes_below_the_intro_and_above_the_newest_entry(self):
        existing = "# Changelog\n\nIntro paragraph one.\n\nIntro paragraph two.\n\n> note\n\n## [v1.2.2] - 2026-01-01\n\n- old\n"
        text = self._changelog(existing)
        intro_at, new_at, old_at = text.index("Intro paragraph two."), text.index("## [v1.2.3]"), text.index("## [v1.2.2]")
        self.assertLess(intro_at, new_at)
        self.assertLess(new_at, old_at)
        self.assertTrue(text.startswith("# Changelog\n\nIntro paragraph one."))
        self.assertEqual(text.count("## [v1.2.2]"), 1)
        self.assertIn("- new thing", text)

    def test_changelog_with_intro_and_no_entry_gets_the_entry_after_the_intro(self):
        text = self._changelog("# Changelog\n\nOnly an intro.\n")
        self.assertLess(text.index("Only an intro."), text.index("## [v1.2.3]"))

    def test_changelog_edge_shapes_are_unchanged(self):
        self.assertTrue(self._changelog(None).startswith("# Changelog\n\n## [v1.2.3]"))
        self.assertTrue(self._changelog("# Changelog\n").startswith("# Changelog\n\n## [v1.2.3]"))
        text = self._changelog("no title here\n")
        self.assertTrue(text.startswith("# Changelog\n\n## [v1.2.3]"))
        self.assertTrue(text.endswith("no title here\n"))
        self.assertEqual(self._changelog("# Changelog\n\n## [v1.2.3] - " + __import__("datetime").date.today().isoformat() + "\n"),
                         "# Changelog\n\n## [v1.2.3] - " + __import__("datetime").date.today().isoformat() + "\n")


class TestDryRunHardening(unittest.TestCase):
    """SEC-T635-03 / -04 and TL-T649-05."""

    @classmethod
    def setUpClass(cls):
        cls.dry_run = _load_dry_run_module()

    def test_write_template_shaped_document_validates_the_tag(self):
        for bad in ("../../x", "v1.2.3\n", "--all", ""):
            with self.subTest(tag=bad), tempfile.TemporaryDirectory() as tmp:
                with self.assertRaisesRegex(RuntimeError, "invalid release tag"):
                    self.dry_run.write_template_shaped_document(repo_root(), Path(tmp) / "d", bad)
                self.assertFalse((Path(tmp) / "d").exists())
                self.assertFalse((Path(tmp) / "x.md").exists())

    def test_a_failing_getcwd_still_restores_argv_urlopen_and_environment(self):
        argv_before, urlopen_before = list(sys.argv), urllib.request.urlopen
        env_before = dict(os.environ)
        with tempfile.TemporaryDirectory() as tmp:
            fixtures = Path(tmp) / "f"
            self.dry_run.write_template_shaped_document(repo_root(), fixtures)
            source = self.dry_run.DryRunSource(source_dir=fixtures, copy_changelog=False)
            with mock.patch("os.getcwd", side_effect=FileNotFoundError("cwd gone")):
                with self.assertRaises(FileNotFoundError):
                    self.dry_run.run_dry_run("v1.2.3", Path(tmp) / "work", source)
        self.assertEqual(sys.argv, argv_before)
        self.assertIs(urllib.request.urlopen, urlopen_before)
        self.assertEqual(dict(os.environ), env_before)

    def test_the_dry_run_replaces_the_modules_opener_and_keeps_the_urlopen_guard(self):
        """SEC-T675-07: both network entry points of publish-release.py refuse during the rehearsal."""
        original_load = self.dry_run.load_publish_release
        outcomes: dict[str, str] = {}

        def load(repo):
            module = original_load(repo)
            real_main = module.main

            def main():
                for name, call in (
                    ("opener", lambda: module.OPENER.open("https://gitlab.invalid/x")),
                    ("urlopen", lambda: urllib.request.urlopen("https://gitlab.invalid/x")),
                ):
                    try:
                        call()
                    except AssertionError as exc:
                        outcomes[name] = str(exc)
                return real_main()

            module.main = main
            return module

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(self.dry_run, "load_publish_release", load):
            fixtures = Path(tmp) / "f"
            self.dry_run.write_template_shaped_document(repo_root(), fixtures)
            self.dry_run.run_dry_run(
                "v1.2.3", Path(tmp) / "work", self.dry_run.DryRunSource(source_dir=fixtures, copy_changelog=False))
        self.assertEqual(set(outcomes), {"opener", "urlopen"})
        self.assertIn("attempted network access", outcomes["opener"])

    def test_the_token_variable_is_set_inside_the_try_and_restored_when_getcwd_fails(self):
        before = dict(os.environ)
        with tempfile.TemporaryDirectory() as tmp:
            fixtures = Path(tmp) / "f"
            self.dry_run.write_template_shaped_document(repo_root(), fixtures)
            source = self.dry_run.DryRunSource(source_dir=fixtures, copy_changelog=False)
            seen: list[bool] = []

            def failing_getcwd():
                seen.append(self.dry_run.TOKEN_ENV in os.environ)  # set by the time getcwd runs: inside the try
                raise FileNotFoundError("gone")

            with mock.patch("os.getcwd", failing_getcwd), self.assertRaises(FileNotFoundError):
                self.dry_run.run_dry_run("v1.2.3", Path(tmp) / "work", source)
        self.assertEqual(seen, [True])
        self.assertEqual(dict(os.environ), before)

    def test_current_release_tag_reads_the_readme_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertIsNone(self.dry_run.current_release_tag(repo))
            (repo / "README.md").write_text("no marker\n", encoding="utf-8")
            self.assertIsNone(self.dry_run.current_release_tag(repo))
            (repo / "README.md").write_text("x\nLatest release: v9.8.7-rc.1\ny\n", encoding="utf-8")
            self.assertEqual(self.dry_run.current_release_tag(repo), "v9.8.7-rc.1")
        self.assertRegex(self.dry_run.current_release_tag() or "", r"^v\d+\.\d+\.\d+")

    def test_main_without_tag_uses_the_marker_and_refuses_when_there_is_none(self):
        with mock.patch.object(self.dry_run, "current_release_tag", return_value=None), \
                mock.patch.object(sys, "argv", ["dry-run"]), mock.patch("sys.stdout") as out:
            self.assertEqual(self.dry_run.main(), 2)
        self.assertIn("no --tag", "".join(c.args[0] for c in out.write.call_args_list))
        with mock.patch.object(self.dry_run, "current_release_tag", return_value="v1.2.3"), \
                mock.patch.object(self.dry_run, "run_dry_run", side_effect=RuntimeError("reached")) as run, \
                mock.patch.object(sys, "argv", ["dry-run"]):
            with self.assertRaisesRegex(RuntimeError, "reached"):
                self.dry_run.main()
        self.assertEqual(run.call_args.args[0], "v1.2.3")


class TestCiSupplyChainPins(unittest.TestCase):
    """SEC-T650-04: every image is pinned by digest and every `apk add` package by version."""

    @classmethod
    def setUpClass(cls):
        cls.ci = (repo_root() / ".gitlab-ci.yml").read_text(encoding="utf-8")

    def test_every_image_has_a_sha256_digest(self):
        images = re.findall(r"^\s*image:\s*(\S+)\s*$", self.ci, re.M)
        self.assertGreaterEqual(len(images), 8)
        for image in images:
            with self.subTest(image=image):
                self.assertRegex(image, r"^[a-z0-9./-]+:[A-Za-z0-9._-]+@sha256:[0-9a-f]{64}$")

    def test_the_same_tag_is_pinned_to_the_same_digest_everywhere(self):
        pairs = {}
        for image in re.findall(r"^\s*image:\s*(\S+)\s*$", self.ci, re.M):
            name, digest = image.split("@")
            self.assertEqual(pairs.setdefault(name, digest), digest, name)

    PIN = re.compile(r"^[a-z0-9][a-z0-9+_.-]*(~=|=)\d")

    @classmethod
    def apk_invocations(cls, ci: str) -> list[list[str]]:
        """Every `apk add` in the pipeline as its full token list (shell form or the python list form)."""
        import shlex
        found: list[list[str]] = []
        for line in ci.splitlines():
            code = line.strip()
            if code.startswith("#") or "apk" not in code:
                continue
            if code.startswith("- "):
                code = code[2:]
            literal = re.search(r"\[apk,\s*'add'((?:,\s*'[^']*')*)\]", code)
            if literal:
                found.append(["add", *re.findall(r"'([^']*)'", literal.group(1))])
            elif re.match(r"apk\s+add\b", code):
                found.append(shlex.split(code)[1:])
            else:
                raise AssertionError(f"unrecognised apk use (parse it or remove it): {line!r}")
        return found

    def test_every_apk_add_package_is_version_pinned(self):
        invocations = self.apk_invocations(self.ci)
        self.assertGreaterEqual(len(invocations), 8)
        for tokens in invocations:
            with self.subTest(tokens=tokens):
                self.assertEqual(tokens[0], "add")
                self.assertIn("--no-cache", tokens)
                packages = [t for t in tokens[1:] if not t.startswith("-")]
                self.assertTrue(packages)
                for package in packages:
                    self.assertRegex(package, self.PIN, package)
                self.assertFalse([t for t in tokens[1:] if t.startswith("-") and t != "--no-cache"])

    def test_the_apk_parser_rejects_unpinned_and_unrecognised_forms(self):
        for bad in ("    - apk add --no-cache git", "    - apk add --no-cache 'git~=2.5' curl",
                    "    - apk add git~=2.5"):
            tokens = self.apk_invocations(bad)[0]
            packages = [t for t in tokens[1:] if not t.startswith("-")]
            ok = "--no-cache" in tokens and all(self.PIN.match(t) for t in packages)
            self.assertFalse(ok, bad)
        with self.assertRaises(AssertionError):
            self.apk_invocations("    - sh -c 'apk  add git'")

    def test_the_release_job_bootstrap_runs_python_isolated_and_without_the_token(self):
        self.assertIn('python3 -I -c "import os, shutil, subprocess;', self.ci)
        self.assertNotIn("python3 -c", self.ci)
        job = re.search(r"^release:\n(?:[ \t].*\n|\n)+", self.ci, re.M).group(0)
        bootstrap = [ln for ln in job.splitlines() if "subprocess.check_call" in ln][0]
        self.assertIn("!= 'WIKI_TOKEN'", bootstrap)
        self.assertIn("env=env", bootstrap)

    def test_the_unit_test_job_installs_ripgrep_and_the_pinned_mcp_sdk(self):
        job = re.search(r"^unit-tests:\n(?:[ \t].*\n|\n)+", self.ci, re.M).group(0)
        self.assertIn("'ripgrep~=", job)
        pin = re.search(r"^mcp==(\S+)$", (repo_root() / "implementation/runtime/security/requirements-mcp-server.txt")
                        .read_text(encoding="utf-8"), re.M).group(1)
        self.assertIn(f'"mcp=={pin}"', job)

    def test_the_release_job_pins_the_host_and_never_puts_the_token_in_argv(self):
        job = re.search(r"^release:\n(?:[ \t].*\n|\n)+", self.ci, re.M).group(0)
        self.assertIn('--expected-host "${CI_SERVER_HOST}"', job)
        self.assertNotRegex(job, r"--token(?!-env)")


if __name__ == "__main__":
    unittest.main()
