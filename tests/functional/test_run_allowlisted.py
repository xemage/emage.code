"""T750 (SEC-T745-04, SEC-T745-05): scripts/run-allowlisted.py, run as the pipeline runs it, with `python3 -I`.

Fake values only. `env` is the child wherever the whole environment matters, because a Python child could add to it.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._helpers.repo import repo_root

ROOT = repo_root()
SCRIPT = ROOT / "scripts" / "run-allowlisted.py"
SECRET = "fake-secret-value-t750"
BASE = {"PATH": "/usr/local/bin:/usr/bin:/bin", "LANG": "C.UTF-8"}  # C.UTF-8: Python adds no LC_CTYPE for its child


def run(*args: str, env: dict[str, str] | None = None, script: Path = SCRIPT) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(script), *args], env=BASE if env is None else env,
                          capture_output=True, text=True, timeout=30, check=False)


def child_env(*keep: str, env: dict[str, str]) -> dict[str, str]:
    flags = [part for name in keep for part in ("--keep", name)]
    done = run(*flags, "--", "env", env=env)
    if done.returncode != 0:
        raise AssertionError(done.stderr)
    return dict(line.split("=", 1) for line in done.stdout.splitlines())


class TestAllowlist(unittest.TestCase):
    def test_a_secret_variable_does_not_reach_the_child(self):
        for name in ("CI_JOB_TOKEN", "WIKI_TOKEN", "CI_REPOSITORY_URL", "CI_REGISTRY_PASSWORD", "A_LATER_PROJECT_VARIABLE",
                     "PYTHONPATH", "PIP_INDEX_URL", "GIT_CONFIG_GLOBAL", "LC_all", "LC_X1", "XLC_ALL", "PATHX"):
            with self.subTest(name):
                self.assertEqual(child_env(env={**BASE, name: SECRET}), BASE)

    def test_an_allowlisted_variable_reaches_the_child(self):
        names = {name: f"value-of-{name}" for name in (
            "HOME", "LANGUAGE", "TMPDIR", "TZ", "SSL_CERT_FILE", "SSL_CERT_DIR", "CURL_CA_BUNDLE", "http_proxy", "https_proxy",
            "no_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "ALL_PROXY", "LC_ALL", "LC_CTYPE", "LC_ALL_")}
        self.assertEqual(child_env(env={**BASE, **names}), {**BASE, **names})

    def test_an_allowlisted_name_holding_a_secret_value_is_dropped(self):
        for secret_name in ("CI_JOB_TOKEN", "WIKI_TOKEN"):
            with self.subTest(secret_name):
                env = {**BASE, secret_name: SECRET, "https_proxy": f"https://u:{SECRET}@proxy.invalid", "TZ": "UTC"}
                self.assertEqual(child_env(env=env), {**BASE, "TZ": "UTC"})

    def test_an_empty_secret_filters_nothing(self):
        """`"" in value` is true for every value: without the guard an empty token would empty the environment."""
        self.assertEqual(child_env(env={**BASE, "CI_JOB_TOKEN": "", "TZ": "UTC"}), {**BASE, "TZ": "UTC"})

    def test_the_allowlist_is_the_one_of_the_release_job(self):
        """The `release` job keeps its own copy (plan-143: moving it is a later change), so this keeps the two equal."""
        code = yaml.safe_load((ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8"))["release"]["before_script"][0]
        module = SCRIPT.read_text(encoding="utf-8")
        ok = re.search(r"ok=\(([^)]*)\)", code)[1]
        secrets = re.search(r"if k in \(([^)]*)\) and v", code)[1]
        allowed = re.search(r"ALLOWED_NAMES = frozenset\(\{(.*?)\}\)", module, re.S)[1]
        self.assertEqual(set(re.findall(r"'([^']+)'", ok)), set(re.findall(r'"([^"]+)"', allowed)))
        self.assertEqual(set(re.findall(r"'([^']+)'", secrets)),
                         set(re.findall(r'"([^"]+)"', re.search(r"SECRET_NAMES = \((.*?)\)", module)[1])))
        self.assertEqual(re.search(r"re\.fullmatch\('([^']+)', i\[0\]\)", code)[1],
                         re.search(r'ALLOWED_PATTERN = re\.compile\(r"([^"]+)"\)', module)[1])


class TestKeep(unittest.TestCase):
    def test_keep_passes_the_named_variable_only(self):
        env = {**BASE, "CI_JOB_TOKEN": SECRET, "WIKI_TOKEN": "other-fake", "OTHER": "x"}
        self.assertEqual(child_env("CI_JOB_TOKEN", env=env), {**BASE, "CI_JOB_TOKEN": SECRET})

    def test_keep_repeats_and_a_name_not_set_is_no_error(self):
        env = {**BASE, "ONE": "1", "TWO": "2", "THREE": "3"}
        self.assertEqual(child_env("ONE", "TWO", "NOT_SET", env=env), {**BASE, "ONE": "1", "TWO": "2"})

    def test_keep_does_not_open_the_value_filter_for_other_names(self):
        env = {**BASE, "CI_JOB_TOKEN": SECRET, "https_proxy": f"https://u:{SECRET}@proxy.invalid"}
        self.assertEqual(child_env("CI_JOB_TOKEN", env=env), {**BASE, "CI_JOB_TOKEN": SECRET})

    def test_the_runner_credential_helper_gets_the_token_only_when_kept(self):
        """The helper of shells/abstract.go (GitLab Runner 19.5.2) with FF_GIT_URLS_WITHOUT_TOKENS on: it reads the
        variable, so git's child must inherit it. `git credential fill`, no network. The real fetch needs a tag pipeline."""
        if shutil.which("git") is None:
            self.fail("git is required")
        helper = 'credential.https://example.invalid.helper=!f(){ if [ "$1" = "get" ] ; then echo "password=${CI_JOB_TOKEN}" ; fi ; } ; f'
        command = ["git", "-c", "credential.interactive=never", "-c", helper, "credential", "fill"]
        request = "protocol=https\nhost=example.invalid\nusername=gitlab-ci-token\n\n"
        outputs = {}
        for flags in ((), ("--keep", "CI_JOB_TOKEN")):
            outputs[flags] = subprocess.run(
                [sys.executable, "-I", str(SCRIPT), *flags, "--", *command], input=request, capture_output=True, text=True,
                timeout=30, check=False, env={**BASE, "CI_JOB_TOKEN": SECRET})
        self.assertNotIn(SECRET, outputs[()].stdout + outputs[()].stderr)
        self.assertEqual(outputs[("--keep", "CI_JOB_TOKEN")].returncode, 0)
        self.assertIn(f"password={SECRET}", outputs[("--keep", "CI_JOB_TOKEN")].stdout)


class TestCommand(unittest.TestCase):
    def test_the_exit_code_passes_through_under_the_variables_of_a_tag_pipeline(self):
        """SEC-T751-02: every gate command runs through this file, so a wrong exit here would skip a gate."""
        tag_job = {**BASE, "CI": "true", "GITLAB_CI": "true", "CI_COMMIT_TAG": "v1.2.3", "CI_COMMIT_REF_NAME": "v1.2.3",
                   "CI_PIPELINE_SOURCE": "push", "CI_COMMIT_REF_PROTECTED": "true", "CI_JOB_TOKEN": SECRET,
                   "WIKI_TOKEN": SECRET}
        for keep in ((), ("--keep", "CI_JOB_TOKEN")):
            for command, expected in ((("sh", "-c", "exit 7"), 7), (("false",), 1), (("true",), 0)):
                with self.subTest(keep=keep, command=command):
                    self.assertEqual(run(*keep, "--", *command, env=tag_job).returncode, expected)
        gate_shape = ("sh", "-c", "exit 7", "--tag", "v1.2.3")
        self.assertEqual(run("--", *gate_shape, env=tag_job).returncode, 7, "a command that looks like the gate's")

    def test_a_missing_command_fails_and_names_only_the_command(self):
        done = run("--", "no-such-command-t750", "argument-text", env={**BASE, "CI_JOB_TOKEN": SECRET})
        self.assertEqual(done.returncode, 127)
        self.assertIn("no-such-command-t750", done.stderr)
        self.assertNotIn(SECRET, done.stdout + done.stderr)
        self.assertNotIn("argument-text", done.stderr)

    def test_a_command_that_cannot_be_executed_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "not-executable"
            path.write_text("#!/bin/sh\n", encoding="utf-8")
            self.assertEqual(run("--", str(path)).returncode, 126)

    def test_the_command_is_found_on_the_allowlisted_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "only-here-t750"
            path.write_text("#!/bin/sh\necho found\n", encoding="utf-8")
            path.chmod(0o755)
            self.assertEqual(run("--", "only-here-t750", env={**BASE, "PATH": f"{tmp}:{BASE['PATH']}"}).stdout, "found\n")
            self.assertEqual(run("--", "only-here-t750").returncode, 127)

    def test_the_exit_code_and_the_arguments_are_the_commands_own(self):
        self.assertEqual(run("--", "sh", "-c", "exit 7").returncode, 7)
        done = run("--", "printf", "%s|", "--keep", "--", "a b", "$HOME")
        self.assertEqual(done.stdout, "--keep|--|a b|$HOME|")

    def test_usage_errors(self):
        for args in ((), ("--",), ("--keep",), ("--keep", "NAME"), ("--keep", "NAME", "--"), ("env",), ("--keep", "--", "env"),
                     ("--keep", "A=B", "--", "env"), ("--keep=NAME", "--", "env"), ("-x", "--", "env")):
            with self.subTest(args):
                done = run(*args)
                self.assertEqual(done.returncode, 2)
                self.assertIn("usage:", done.stderr)
                self.assertEqual(done.stdout, "")

    def test_help(self):
        done = run("--help")
        self.assertEqual(done.returncode, 0)
        self.assertIn("os.execvpe", done.stdout)

    def test_dash_big_i_runs_it_and_ignores_a_planted_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / SCRIPT.name
            shutil.copy(SCRIPT, copy)
            (Path(tmp) / "re.py").write_text("raise SystemExit('planted')\n", encoding="utf-8")
            done = run("--", "env", env={**BASE, "PYTHONPATH": tmp}, script=copy)
            self.assertEqual((done.returncode, dict(line.split("=", 1) for line in done.stdout.splitlines())), (0, BASE))


if __name__ == "__main__":
    unittest.main()
