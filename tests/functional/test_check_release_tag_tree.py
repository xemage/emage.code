"""T685 (TL-T649-13, QA-T648-03) -- scripts/check-release-tag-tree.py.

A release tag must carry exactly the content of origin/main. The check compares git TREE ids, not commit ancestry:
GitLab's merge through the API can create a new commit with the same tree, so the tag commit is not an ancestor of
main for a correct release. The tests build real temporary repositories (an origin, a depth-1 clone of the tag as the
CI job makes it, a fetch of main at depth 1) and run the script as a program. Every guard has a mutation proof: the
guard is removed from a copy of the source, the copy is loaded, and the matching condition must then FAIL.

What these tests cannot show: that GitLab's tag pipeline checks the tag out and fetches `main` this way. That is
the first real tag pipeline (the job lines are the same as the existing drift gate's).
"""
from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

ROOT = repo_root()
SCRIPT = ROOT / "scripts" / "check-release-tag-tree.py"
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@example.invalid", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
       "GIT_TERMINAL_PROMPT": "0"}


def load(source: str | None = None, name: str = "check_release_tag_tree") -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8") if source is None else source
    module = types.ModuleType(name)
    module.__file__ = str(SCRIPT)
    sys.modules[name] = module
    exec(compile(text, str(SCRIPT), "exec"), module.__dict__)  # noqa: S102 -- our own script / a mutation of it
    return module


def mutated(old: str, new: str) -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"mutation anchor must occur exactly once: {old!r}"
    return load(text.replace(old, new), "check_release_tag_tree_mutant")


M = load()


def git(cwd: str | Path, *args: str, data: bytes | None = None) -> str:
    done = subprocess.run(["git", *args], cwd=cwd, env={**os.environ, **ENV}, check=True, capture_output=True, input=data)
    return done.stdout.decode("utf-8", "replace").strip()


@unittest.skipUnless(shutil.which("git"), "git is needed")
class RepoCase(unittest.TestCase):
    """A work repository, a bare origin and the helpers to make the clone the tag pipeline would have."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.work, self.origin, self.clone = base / "work", base / "origin.git", base / "clone"
        self.work.mkdir()
        git(self.work, "init", "-q", "-b", "main")
        self.write("README.md", "base\n")
        self.commit("chore: base")
        git(base, "init", "-q", "--bare", str(self.origin))
        git(self.work, "remote", "add", "origin", f"file://{self.origin}")

    def write(self, name: str, text: str) -> None:
        (self.work / name).write_text(text, encoding="utf-8")

    def commit(self, message: str) -> str:
        git(self.work, "add", "-A")
        git(self.work, "commit", "-q", "-m", message)
        return git(self.work, "rev-parse", "HEAD")

    def push(self, *refs: str) -> None:
        git(self.work, "push", "-q", "--force", "origin", *refs)

    def make_clone(self, tag: str, fetch_main: bool = True) -> Path:
        """What the tag job has: a depth-1 clone holding the tag, then `git fetch origin main --depth=1` and the tags."""
        git(self.clone.parent, "init", "-q", str(self.clone))
        git(self.clone, "remote", "add", "origin", f"file://{self.origin}")
        git(self.clone, "fetch", "-q", "--depth=1", "origin", f"+refs/tags/{tag}:refs/tags/{tag}")
        git(self.clone, "checkout", "-q", "--detach", f"refs/tags/{tag}")
        if fetch_main:
            git(self.clone, "fetch", "-q", "origin", "main", "--depth=1")
        return self.clone

    def run_script(self, cwd: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], cwd=cwd, env={**os.environ, **ENV},
                              capture_output=True, text=True, check=False)


class TestTreeComparison(RepoCase):
    def release(self) -> str:
        """main holds a release; the tag is on the release commit."""
        self.write("docs.md", "release content\n")
        sha = self.commit("feat: release content")
        git(self.work, "tag", "-a", "v1.2.3", "-m", "Release v1.2.3")
        self.push("main", "v1.2.3")
        return sha

    def test_a_tag_whose_tree_equals_main_passes_in_a_depth_one_clone(self):
        self.release()
        clone = self.make_clone("v1.2.3")
        self.assertEqual(git(clone, "rev-parse", "--is-shallow-repository"), "true")
        done = self.run_script(clone, "--tag", "v1.2.3")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("RELEASE TAG TREE: PASS", done.stdout)

    def test_a_squash_style_merge_commit_with_the_same_tree_passes_where_ancestry_fails(self):
        """The GitLab API merge: main gets a NEW commit with the tag commit's tree; the tag commit is no ancestor."""
        sha = self.release()
        tree = git(self.work, "rev-parse", f"{sha}^{{tree}}")
        base = git(self.work, "rev-parse", f"{sha}~1")
        api_merge = git(self.work, "commit-tree", tree, "-p", base, "-m", "Merge branch 'release/v1.2.3' into 'main'")
        git(self.work, "update-ref", "refs/heads/main", api_merge)
        self.push("main")
        clone = self.make_clone("v1.2.3")
        tag_commit = git(clone, "rev-parse", "refs/tags/v1.2.3^{commit}")
        main_commit = git(clone, "rev-parse", "origin/main")
        self.assertNotEqual(tag_commit, main_commit)
        # ancestry is the wrong signal: in a depth-1 clone it cannot even be evaluated, and in a full history it is false
        full = subprocess.run(["git", "merge-base", "--is-ancestor", sha, api_merge], cwd=self.work, check=False,
                              env={**os.environ, **ENV})
        self.assertNotEqual(full.returncode, 0)
        done = self.run_script(clone, "--tag", "v1.2.3")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_main_ahead_of_the_tag_with_other_content_fails_and_names_the_path(self):
        self.release()
        self.write("hotfix.md", "later\n")
        self.commit("fix: after the tag")
        self.push("main")
        done = self.run_script(self.make_clone("v1.2.3"), "--tag", "v1.2.3")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("differs from the tree of origin/main", done.stdout)
        self.assertIn("  hotfix.md", done.stdout)
        self.assertIn("RELEASE TAG TREE: FAIL", done.stdout)

    def test_a_tag_pushed_before_the_release_reached_main_fails(self):
        """The case the one-release grace window of the drift gate lets through."""
        self.push("main")  # main is still the base
        self.write("docs.md", "release content, not on main\n")
        self.commit("feat: release content")
        git(self.work, "tag", "-a", "v1.2.3", "-m", "Release v1.2.3")
        self.push("v1.2.3")
        done = self.run_script(self.make_clone("v1.2.3"), "--tag", "v1.2.3")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("  docs.md", done.stdout)

    def test_a_lightweight_tag_is_compared_like_an_annotated_one(self):
        self.write("docs.md", "release content\n")
        self.commit("feat: release content")
        git(self.work, "tag", "v1.2.3")
        self.push("main", "v1.2.3")
        self.assertEqual(self.run_script(self.make_clone("v1.2.3"), "--tag", "v1.2.3").returncode, 0)

    def test_main_that_was_not_fetched_fails_closed(self):
        self.release()
        done = self.run_script(self.make_clone("v1.2.3", fetch_main=False), "--tag", "v1.2.3")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("origin/main does not resolve to a commit", done.stdout)
        self.assertIn("an offline run proves nothing", done.stdout)

    def test_a_tag_that_was_not_fetched_fails_closed(self):
        self.release()
        clone = self.make_clone("v1.2.3")
        done = self.run_script(clone, "--tag", "v1.2.4")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("tag v1.2.4 does not resolve to a commit", done.stdout)

    def test_a_tag_that_points_at_a_tree_is_refused(self):
        sha = self.release()
        git(self.work, "tag", "v1.2.4", f"{sha}^{{tree}}")
        self.push("v1.2.4")
        git(self.work, "fetch", "-q", "origin")
        clone = self.make_clone("v1.2.3")
        git(clone, "fetch", "-q", "--depth=1", "origin", "+refs/tags/v1.2.4:refs/tags/v1.2.4")
        done = self.run_script(clone, "--tag", "v1.2.4")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("does not resolve to a commit", done.stdout)

    def test_only_release_tag_names_and_plain_refs_are_accepted(self):
        self.release()
        clone = self.make_clone("v1.2.3")
        for tag in ("main", "v1.2", "--output=x", "v1.2.3;id", "v1.2.3\n", "../v1.2.3", "refs/tags/v1.2.3", "V1.2.3", ""):
            with self.subTest(tag=tag):
                self.assertEqual(M.check(tag, "origin/main")[0], 1)
                self.assertEqual(self.run_script(clone, f"--tag={tag}").returncode, 1)
        for ref in ("--exclude=x", "-x", "origin/main~1", "origin/main^{tree}", "a b", "x:y", ".hidden", ""):
            with self.subTest(ref=ref):
                self.assertIn("not a plain ref name", "\n".join(M.check("v1.2.3", ref)[1]))

    def test_many_differing_paths_are_capped_and_control_characters_are_removed(self):
        self.push("main")
        self.write("docs.md", "release\n")
        for n in range(25):
            self.write(f"f{n:02d}.txt", "x\n")
        self.write("evil\x1b[2Jname.txt", "x\n")
        self.commit("feat: many files")
        git(self.work, "tag", "v1.2.3")
        self.push("v1.2.3")
        done = self.run_script(self.make_clone("v1.2.3"), "--tag", "v1.2.3")
        self.assertEqual(done.returncode, 1)
        self.assertIn("... and 7 more", done.stdout)
        self.assertNotIn("\x1b", done.stdout)
        listed = [line for line in done.stdout.splitlines() if line.startswith("  ")]
        self.assertEqual((len(listed), listed[-1].strip()), (21, "... and 7 more"))  # 20 paths and the rest counted

    def test_the_script_only_reads_the_repository(self):
        self.release()
        clone = self.make_clone("v1.2.3")
        before = git(clone, "for-each-ref") + git(clone, "status", "--porcelain")
        self.run_script(clone, "--tag", "v1.2.3")
        self.assertEqual(before, git(clone, "for-each-ref") + git(clone, "status", "--porcelain"))

    def test_a_missing_git_is_a_usage_error(self):
        done = subprocess.run([sys.executable, "-I", str(SCRIPT), "--tag", "v1.2.3"], cwd=self._tmp.name, capture_output=True,
                              text=True, check=False, env={"PATH": "/nonexistent"})
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertNotIn("Traceback", done.stderr)


class TestEvaluate(unittest.TestCase):
    TREE_A, TREE_B = "a" * 40, "b" * 40

    def test_equal_trees_pass_different_fail_and_missing_fail(self):
        self.assertEqual(M.evaluate("v1.0.0", "origin/main", self.TREE_A, self.TREE_A)[0], 0)
        self.assertEqual(M.evaluate("v1.0.0", "origin/main", self.TREE_A, self.TREE_B, ["x"])[0], 1)
        self.assertEqual(M.evaluate("v1.0.0", "origin/main", None, self.TREE_A)[0], 1)
        self.assertEqual(M.evaluate("v1.0.0", "origin/main", self.TREE_A, None)[0], 1)
        self.assertEqual(M.evaluate("v1.0.0", "origin/main", None, None)[0], 1)

    def test_the_tag_name_rule_equals_the_ci_tag_rule(self):
        ci = (ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8")
        rules = set(re.findall(r"\$CI_COMMIT_TAG =~ /(.+)/'", ci))
        self.assertEqual(rules, {M.TAG_RE.pattern})


class TestMutations(RepoCase):
    def setUp(self):
        super().setUp()
        self.write("docs.md", "release content\n")
        self.commit("feat: release content")
        git(self.work, "tag", "-a", "v1.2.3", "-m", "Release v1.2.3")
        self.write("later.md", "later\n")
        self.commit("fix: later")
        self.push("main", "v1.2.3")
        self.clone_dir = self.make_clone("v1.2.3")

    def run_in_clone(self, module, tag: str = "v1.2.3") -> int:
        cwd = os.getcwd()
        os.chdir(self.clone_dir)
        try:
            return module.check(tag, "origin/main")[0]
        finally:
            os.chdir(cwd)

    def test_mutation_comparing_nothing_is_detected(self):
        mutant = mutated("    if tag_tree != main_tree:", "    if False:")
        self.assertEqual(self.run_in_clone(M), 1)
        self.assertEqual(self.run_in_clone(mutant), 0)  # the mutant passes a tag that is not on main

    def test_mutation_unresolved_refs_comparing_equal_is_detected(self):
        """Both refs unresolved gives None == None: without the two explicit checks that would be a PASS."""
        text = SCRIPT.read_text(encoding="utf-8")
        for anchor in ("    if tag_tree is None:", "    if main_tree is None:"):
            self.assertEqual(text.count(anchor), 1)
            text = text.replace(anchor, "    if False:")
        mutant = load(text, "check_release_tag_tree_mutant2")
        self.assertEqual(M.evaluate("v1.2.3", "origin/main", None, None)[0], 1)
        try:
            code = mutant.evaluate("v1.2.3", "origin/main", None, None)[0]
        except TypeError:
            code = None  # the mutant walks into the PASS branch and crashes while printing the tree id
        self.assertNotEqual(code, 1)  # no controlled FAIL: the mutant treats two missing refs as equal

    def test_mutation_accepting_a_tag_that_is_not_a_commit_is_detected(self):
        mutant = mutated('    if run_git(["rev-parse", "--verify", "--quiet", "--end-of-options", f"{rev}^{{commit}}"]).returncode != 0:',
                         "    if False:")
        tree = git(self.work, "rev-parse", "main^{tree}")
        git(self.work, "tag", "v9.9.9", tree)
        self.push("v9.9.9")
        git(self.clone_dir, "fetch", "-q", "--depth=1", "origin", "+refs/tags/v9.9.9:refs/tags/v9.9.9")
        self.assertEqual(self.run_in_clone(M, "v9.9.9"), 1)
        self.assertEqual(self.run_in_clone(mutant, "v9.9.9"), 0)  # the tree tag equals main's tree: the mutant passes it

    def test_mutation_accepting_any_tag_name_is_detected(self):
        mutant = mutated("    if not TAG_RE.fullmatch(tag):", "    if False:")
        self.assertEqual(M.check("--output=x", "origin/main")[0], 1)
        self.assertNotIn("not a release tag name", "\n".join(mutant.check("--output=x", "origin/main")[1]))

    def test_mutation_accepting_any_ref_is_detected(self):
        mutant = mutated("    if not REF_RE.fullmatch(main_ref):", "    if False:")
        self.assertIn("not a plain ref name", "\n".join(M.check("v1.2.3", "--exclude=x")[1]))
        self.assertNotIn("not a plain ref name", "\n".join(mutant.check("v1.2.3", "--exclude=x")[1]))

    def test_mutation_printing_raw_path_names_is_detected(self):
        mutant = mutated('names = [UNSAFE_RE.sub("?", n) for n in', "names = [n for n in")
        self.write("evil\x1bname.txt", "x\n")
        self.commit("feat: evil name")
        self.push("main")
        git(self.clone_dir, "fetch", "-q", "origin", "main", "--depth=1")
        tag_tree = git(self.clone_dir, "rev-parse", "refs/tags/v1.2.3^{tree}")
        main_tree = git(self.clone_dir, "rev-parse", "origin/main^{tree}")
        cwd = os.getcwd()
        os.chdir(self.clone_dir)
        try:
            self.assertNotIn("\x1b", "".join(M.differing_paths(tag_tree, main_tree)))
            self.assertIn("\x1b", "".join(mutant.differing_paths(tag_tree, main_tree)))
        finally:
            os.chdir(cwd)

    def test_mutation_an_uncapped_listing_is_detected(self):
        mutant = mutated("    shown = names[:MAX_LISTED_PATHS]", "    shown = names")
        for n in range(25):
            self.write(f"g{n:02d}.txt", "x\n")
        self.commit("feat: many")
        self.push("main")
        git(self.clone_dir, "fetch", "-q", "origin", "main", "--depth=1")
        tag_tree = git(self.clone_dir, "rev-parse", "refs/tags/v1.2.3^{tree}")
        main_tree = git(self.clone_dir, "rev-parse", "origin/main^{tree}")
        cwd = os.getcwd()
        os.chdir(self.clone_dir)
        try:
            self.assertEqual(len(M.differing_paths(tag_tree, main_tree)), 21)
            self.assertGreater(len(mutant.differing_paths(tag_tree, main_tree)), 21)
        finally:
            os.chdir(cwd)


class TestCiWiring(unittest.TestCase):
    def job(self, name: str) -> str:
        ci = (ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8")
        match = re.search(rf"^{re.escape(name)}:\n(?P<body>(?:[ \t].*\n|\n)+)", ci, re.M)
        self.assertIsNotNone(match, name)
        return match.group("body")

    def test_the_blocking_tag_gate_runs_the_tree_check_after_fetching_main_and_the_tags(self):
        body = self.job("main-develop-drift-gate")
        fetch_main = body.index("git fetch origin main develop --depth=1")
        fetch_tags = body.index("git fetch --force origin 'refs/tags/*:refs/tags/*'")
        drift = body.index("scripts/check-main-develop-drift.py")
        tree = body.index('python3 scripts/check-release-tag-tree.py --tag "${CI_COMMIT_TAG}" --main-ref origin/main')
        self.assertLess(fetch_main, tree)
        self.assertLess(fetch_tags, tree)
        self.assertLess(drift, tree)
        self.assertIn('GIT_DEPTH: "1"', body)  # depth 1 is the case the tree comparison is built for
        self.assertNotIn("allow_failure", body)  # blocking: the release job needs this job
        self.assertNotIn("WIKI_TOKEN", body)  # the job takes no token

    def test_the_release_job_still_needs_the_gate(self):
        self.assertIn('needs: ["release-docs-gate", "main-develop-drift-gate"]', self.job("release"))

    def test_the_informational_develop_job_does_not_run_the_tag_check(self):
        self.assertNotIn("check-release-tag-tree", self.job("main-develop-drift-check"))

    def test_mutation_dropping_the_job_line_is_detected(self):
        body = self.job("main-develop-drift-gate")
        stripped = re.sub(r".*check-release-tag-tree.*\n", "", body)
        self.assertNotEqual(body, stripped)
        self.assertNotIn("check-release-tag-tree", stripped)


class TestDocumented(unittest.TestCase):
    def test_contributing_describes_the_tree_check(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("scripts/check-release-tag-tree.py", text)
        self.assertIn("same tree", text)

    def test_the_drift_script_points_to_the_tree_check(self):
        text = (ROOT / "scripts" / "check-main-develop-drift.py").read_text(encoding="utf-8")
        self.assertIn("check-release-tag-tree.py", text)


if __name__ == "__main__":
    unittest.main()
