"""Regression tests for scripts/check-main-develop-drift.py drift-detection logic."""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

SCRIPT = repo_root() / "scripts" / "check-main-develop-drift.py"
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@example.invalid", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
       "GIT_TERMINAL_PROMPT": "0"}


def _load_module():
    module_path = repo_root() / "scripts" / "check-main-develop-drift.py"
    spec = importlib.util.spec_from_file_location("check_main_develop_drift", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load check-main-develop-drift module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TAGS = ["v6.3.0", "v6.4.0", "v6.4.1", "v6.4.2", "v6.4.3", "v6.5.0"]


class TestParseMarker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_parses_standard_marker(self):
        text = "Some text\nLatest release: v6.5.0\nMore text\n"
        self.assertEqual(self.mod.parse_marker(text), "v6.5.0")

    def test_returns_none_when_marker_absent(self):
        self.assertIsNone(self.mod.parse_marker("no marker here"))


class TestSemverKeyAndSort(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_rejects_non_semver_tags(self):
        self.assertIsNone(self.mod.semver_key("not-a-tag"))
        self.assertIsNone(
            self.mod.semver_key("backup/release-v6.0.3-pre-rewrite-20260617-065656")
        )

    def test_sorts_ascending_numerically_not_lexically(self):
        shuffled = ["v6.5.0", "v6.4.0", "v6.4.10", "v6.4.2"]
        self.assertEqual(
            self.mod.sorted_valid_tags(shuffled),
            ["v6.4.0", "v6.4.2", "v6.4.10", "v6.5.0"],
        )

    def test_drops_invalid_tags_from_sort(self):
        mixed = ["v1.0.0", "not-a-release", "v1.0.1"]
        self.assertEqual(self.mod.sorted_valid_tags(mixed), ["v1.0.0", "v1.0.1"])


class TestReleasesBehind(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_zero_when_versions_match(self):
        self.assertEqual(self.mod.releases_behind("v6.5.0", "v6.5.0", TAGS), 0)

    def test_counts_gap_correctly_matching_real_incident_shape(self):
        # main=v6.4.2, develop=v6.5.0 -> v6.4.3 and v6.5.0 both missing from main -> 2
        self.assertEqual(self.mod.releases_behind("v6.4.2", "v6.5.0", TAGS), 2)

    def test_raises_on_unknown_main_version(self):
        with self.assertRaises(ValueError):
            self.mod.releases_behind("v9.9.9", "v6.5.0", TAGS)

    def test_raises_on_unknown_develop_version(self):
        with self.assertRaises(ValueError):
            self.mod.releases_behind("v6.4.2", "v9.9.9", TAGS)

    def test_raises_when_main_ahead_of_develop(self):
        with self.assertRaises(ValueError):
            self.mod.releases_behind("v6.5.0", "v6.4.2", TAGS)


class TestEvaluate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_pass_when_in_sync(self):
        code, lines = self.mod.evaluate("v6.5.0", "v6.5.0", TAGS)
        self.assertEqual(code, 0)
        self.assertTrue(any("PASS" in line for line in lines))

    def test_pass_within_one_release_grace(self):
        code, _lines = self.mod.evaluate("v6.4.3", "v6.5.0", TAGS)
        self.assertEqual(code, 0)

    def test_fail_when_more_than_one_release_behind(self):
        code, lines = self.mod.evaluate("v6.4.2", "v6.5.0", TAGS)
        self.assertEqual(code, 1)
        self.assertTrue(any("FAIL" in line for line in lines))
        self.assertTrue(any("v6.4.3" in line and "v6.5.0" in line for line in lines))

    def test_one_release_behind_passes_but_states_the_merge_before_tag_duty(self):
        """TL-T649-13: GRACE_RELEASES stays 1 (unchanged); the PASS carries a NOTE."""
        self.assertEqual(self.mod.GRACE_RELEASES, 1)
        code, lines = self.mod.evaluate("v6.4.3", "v6.5.0", TAGS)
        self.assertEqual(code, 0)
        notes = [line for line in lines if "NOTE" in line]
        self.assertEqual(len(notes), 1)
        self.assertIn("BEFORE pushing the tag", notes[0])
        self.assertIn("tolerance", notes[0])

    def test_in_sync_has_no_note(self):
        _code, lines = self.mod.evaluate("v6.5.0", "v6.5.0", TAGS)
        self.assertFalse(any("NOTE" in line for line in lines))

    def test_the_offline_limit_is_documented_in_the_script(self):
        self.assertIn("proves nothing", self.mod.__doc__)

    def test_fail_when_main_marker_missing(self):
        code, _lines = self.mod.evaluate(None, "v6.5.0", TAGS)
        self.assertEqual(code, 1)

    def test_fail_when_develop_marker_missing(self):
        code, _lines = self.mod.evaluate("v6.5.0", None, TAGS)
        self.assertEqual(code, 1)

    def test_fail_when_main_ahead_of_develop(self):
        code, _lines = self.mod.evaluate("v6.5.0", "v6.4.2", TAGS)
        self.assertEqual(code, 1)


def git(cwd: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=cwd, env={**os.environ, **ENV}, check=True, capture_output=True)
    return done.stdout.decode("utf-8", "replace").strip()


def mutated(old: str, new: str) -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"mutation anchor must occur exactly once: {old!r}"
    module = types.ModuleType("check_main_develop_drift_mutant")
    exec(compile(text.replace(old, new), str(SCRIPT), "exec"), module.__dict__)  # noqa: S102 -- our own script
    return module


@unittest.skipUnless(shutil.which("git"), "git is needed")
class TestExactRefNames(unittest.TestCase):
    """T730 (SEC-T716-01): a TAG named ``origin/main`` or ``origin/develop`` (the jobs fetch every tag) must not
    stand in for the remote-tracking branch. main holds v1.0.0, develop v1.2.0: two releases behind, a real FAIL."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.work, self.origin, self.clone = base / "work", base / "origin.git", base / "clone"
        self.work.mkdir()
        git(self.work, "init", "-q", "-b", "main")
        for version in ("v1.0.0", "v1.1.0", "v1.2.0"):
            (self.work / "README.md").write_text(f"Latest release: {version}\n", encoding="utf-8")
            git(self.work, "add", "-A")
            git(self.work, "commit", "-q", "-m", f"chore: release {version}")
            git(self.work, "tag", "-a", version, "-m", version)
        git(self.work, "branch", "develop")
        git(self.work, "reset", "-q", "--hard", "v1.0.0")
        git(base, "init", "-q", "--bare", str(self.origin))
        git(self.work, "remote", "add", "origin", f"file://{self.origin}")
        git(self.work, "push", "-q", "origin", "main", "develop", "--tags")

    def make_clone(self, shadow: dict[str, str], fetch: str = "main develop") -> Path:
        """What the drift jobs have: the branches fetched, then every tag, here with tags named like the refs."""
        for name, target in shadow.items():
            git(self.work, "tag", name, f"{target}^{{commit}}")
            git(self.work, "push", "-q", "--force", "origin", f"refs/tags/{name}")
        git(self.clone.parent, "init", "-q", str(self.clone))
        git(self.clone, "remote", "add", "origin", f"file://{self.origin}")
        if fetch:
            git(self.clone, "fetch", "-q", "origin", *fetch.split())
        git(self.clone, "fetch", "-q", "--force", "origin", "refs/tags/*:refs/tags/*")
        return self.clone

    def run_script(self, cwd: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], cwd=cwd, env={**os.environ, **ENV},
                              capture_output=True, text=True, check=False)

    def read_in(self, module: types.ModuleType, clone: Path, ref: str) -> str:
        cwd = os.getcwd()
        os.chdir(clone)
        try:
            return module.parse_marker(module.read_file_at_ref(ref, "README.md"))
        finally:
            os.chdir(cwd)

    def test_without_a_shadow_tag_the_real_drift_fails(self):
        done = self.run_script(self.make_clone({}))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("main=v1.0.0 develop=v1.2.0 releases_behind=2", done.stdout)

    def test_a_tag_named_origin_main_does_not_shadow_the_branch_false_pass(self):
        clone = self.make_clone({"origin/main": "v1.2.0"})
        self.assertIn("v1.2.0", git(clone, "show", "origin/main:README.md"))  # git's search does pick the tag
        done = self.run_script(clone)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("main=v1.0.0 develop=v1.2.0", done.stdout)

    def test_a_tag_named_origin_develop_does_not_shadow_the_branch_false_fail(self):
        git(self.work, "push", "-q", "--force", "origin", "v1.2.0^{commit}:refs/heads/main")
        clone = self.make_clone({"origin/develop": "v1.0.0"})
        done = self.run_script(clone)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("main=v1.2.0 develop=v1.2.0 releases_behind=0", done.stdout)

    def test_mutation_the_short_name_search_is_detected(self):
        mutant = mutated('    return run_git(["show", "--end-of-options", f"{oid}:{path}"])',
                         '    return run_git(["show", f"{ref}:{path}"])')
        clone = self.make_clone({"origin/main": "v1.2.0"})
        self.assertEqual(self.read_in(_load_module(), clone, "origin/main"), "v1.0.0")
        self.assertEqual(self.read_in(mutant, clone, "origin/main"), "v1.2.0")  # the tag wins: a false PASS

    def test_a_tag_named_like_the_full_ref_does_not_fill_in_for_an_unfetched_branch(self):
        clone = self.make_clone({"refs/remotes/origin/main": "v1.2.0"}, fetch="develop")
        done = self.run_script(clone)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("refs/remotes/origin/main does not exist", done.stdout)
        self.assertNotIn("Traceback", done.stderr)
        done = self.run_script(clone, "--main-ref", "refs/remotes/origin/main")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)

    def test_only_plain_ref_names_are_accepted(self):
        clone = self.make_clone({})
        for ref in ("--output=x", "-x", "origin/main~1", "origin/main^{tree}", "a b", "x:y", ".hidden", "a/../b", ""):
            with self.subTest(ref=ref):
                done = self.run_script(clone, f"--main-ref={ref}")
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertIn("not a plain ref name", done.stdout)


if __name__ == "__main__":
    unittest.main()
