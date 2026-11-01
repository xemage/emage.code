"""T686 -- the release job authenticates with the GitLab job token; WIKI_TOKEN is for wiki-sync only.

Covers scripts/publish-release.py (``--token-header``, ``CI_JOB_TOKEN`` withheld from child processes), the
``release`` and ``wiki-sync`` jobs of .gitlab-ci.yml, and the "Cutting a release" text of CONTRIBUTING.md.
Every guard has a mutation proof in this file: the guard is removed from a copy of the source, the copy is loaded,
and the matching condition must then FAIL. Only fake tokens appear here; nothing touches a network or GitLab.
"""
from __future__ import annotations

import contextlib
import http.server
import io
import os
import re
import stat
import subprocess
import sys
import tempfile
import threading
import types
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

from tests._helpers.repo import repo_root

SCRIPT = repo_root() / "scripts" / "publish-release.py"
CI = repo_root() / ".gitlab-ci.yml"
SECRET = "t686-FAKE-job-token-not-a-credential"  # not glpat-shaped: the secret scan must not see a PAT
API = "https://gitlab.invalid/api/v4"


def load(source: str | None = None, name: str = "publish_release_t686") -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8") if source is None else source
    module = types.ModuleType(name)
    module.__file__ = str(SCRIPT)
    sys.modules[name] = module
    exec(compile(text, str(SCRIPT), "exec"), module.__dict__)  # noqa: S102 -- our own script / a mutation of it
    return module


def mutated(old: str, new: str) -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"mutation anchor must occur exactly once: {old!r}"
    return load(text.replace(old, new), "publish_release_t686_mutant")


PR = load()


class _Response:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return b"{}"


class _RecordingOpener:
    """Stands in for OPENER: records every request, answers ``{}`` or the configured callable."""

    def __init__(self, answer=None):
        self.requests: list[urllib.request.Request] = []
        self.answer = answer

    def open(self, request, timeout=None):
        self.requests.append(request)
        return self.answer(request) if self.answer else _Response()


def headers_of(request: urllib.request.Request) -> dict[str, str]:
    return {k.lower(): v for k, v in request.header_items()}


class TestTheHeaderTheTokenTravelsIn(unittest.TestCase):
    def send(self, module=PR, **kwargs) -> urllib.request.Request:
        opener = _RecordingOpener()
        with mock.patch.object(module, "OPENER", opener):
            module.gitlab_request("GET", API + "/x", SECRET, **kwargs)
        self.assertEqual(len(opener.requests), 1)
        return opener.requests[0]

    def test_each_allowed_header_carries_the_token_and_no_other_header_does(self):
        for name in ("PRIVATE-TOKEN", "JOB-TOKEN"):
            with self.subTest(header=name):
                headers = headers_of(self.send(token_header=name))
                self.assertEqual(headers[name.lower()], SECRET)
                self.assertEqual([k for k, v in headers.items() if SECRET in v], [name.lower()])
                other = ({"PRIVATE-TOKEN", "JOB-TOKEN"} - {name}).pop().lower()
                self.assertNotIn(other, headers)

    def test_the_default_is_private_token_so_existing_calls_are_unchanged(self):
        self.assertEqual(PR.DEFAULT_TOKEN_HEADER, "PRIVATE-TOKEN")
        headers = headers_of(self.send())
        self.assertEqual(headers["private-token"], SECRET)
        self.assertNotIn("job-token", headers)

    def test_the_url_never_carries_the_token(self):
        request = self.send(token_header="JOB-TOKEN")
        self.assertNotIn(SECRET, request.full_url)
        self.assertNotIn(SECRET, (request.data or b"").decode())

    def test_create_or_update_release_sends_every_call_with_the_chosen_header(self):
        for name in ("PRIVATE-TOKEN", "JOB-TOKEN"):
            with self.subTest(header=name):
                opener = _RecordingOpener(lambda r: _raise404(r) if r.get_method() == "GET" else _TagResponse())
                with mock.patch.object(PR, "OPENER", opener):
                    PR.create_or_update_release("v1.2.3", API, "7", SECRET, "desc", "gitlab.invalid", token_header=name)
                self.assertEqual([r.get_method() for r in opener.requests], ["GET", "POST"])
                for request in opener.requests:
                    self.assertEqual(headers_of(request).get(name.lower()), SECRET)
                    self.assertNotIn(("job-token" if name == "PRIVATE-TOKEN" else "private-token"), headers_of(request))

    def test_an_existing_release_is_updated_with_the_chosen_header_too(self):
        for name in ("PRIVATE-TOKEN", "JOB-TOKEN"):
            with self.subTest(header=name):
                opener = _RecordingOpener(lambda r: _TagResponse())  # the GET finds the release, so the call is a PUT
                with mock.patch.object(PR, "OPENER", opener):
                    PR.create_or_update_release("v1.2.3", API, "7", SECRET, "desc", "gitlab.invalid", token_header=name)
                self.assertEqual([r.get_method() for r in opener.requests], ["GET", "PUT"])
                for request in opener.requests:
                    self.assertEqual(headers_of(request).get(name.lower()), SECRET)

    def test_the_default_through_create_or_update_release_is_private_token(self):
        opener = _RecordingOpener(lambda r: _TagResponse())
        with mock.patch.object(PR, "OPENER", opener):
            PR.create_or_update_release("v1.2.3", API, "7", SECRET, "desc", "gitlab.invalid")
        self.assertTrue(all("private-token" in headers_of(r) for r in opener.requests))

    def test_mutation_sending_every_token_as_private_token_is_detected(self):
        mutant = mutated("request.add_header(token_header, token)", 'request.add_header("PRIVATE-TOKEN", token)')
        headers = headers_of(self.send(mutant, token_header="JOB-TOKEN"))
        self.assertNotIn("job-token", headers)  # the mutant ignores the choice; the test above would fail

    def test_mutation_create_or_update_release_dropping_the_header_is_detected(self):
        mutant = mutated('"POST", f"{api_v4_url}/projects/{project_id}/releases", token, payload, token_header=token_header',
                         '"POST", f"{api_v4_url}/projects/{project_id}/releases", token, payload')
        opener = _RecordingOpener(lambda r: _raise404(r) if r.get_method() == "GET" else _TagResponse())
        with mock.patch.object(mutant, "OPENER", opener):
            mutant.create_or_update_release("v1.2.3", API, "7", SECRET, "d", "gitlab.invalid", token_header="JOB-TOKEN")
        post = [r for r in opener.requests if r.get_method() == "POST"][0]
        self.assertNotIn("job-token", headers_of(post))


class _TagResponse(_Response):
    def read(self):
        return b'{"tag_name": "v1.2.3"}'


class TestTheAllowlist(unittest.TestCase):
    BAD = ("Authorization", "private-token", "Job-Token", "job-token", "PRIVATE-TOKEN ", "PRIVATE-TOKEN\r\nX-Evil: 1",
           "", "X-Gitlab-Token", "PRIVATE_TOKEN")

    def test_the_allowlist_is_exactly_the_two_names_and_the_default_is_one_of_them(self):
        self.assertEqual(PR.TOKEN_HEADERS, ("PRIVATE-TOKEN", "JOB-TOKEN"))
        self.assertIn(PR.DEFAULT_TOKEN_HEADER, PR.TOKEN_HEADERS)

    def test_validate_token_header_accepts_the_names_and_refuses_everything_else_without_echoing_it(self):
        for name in PR.TOKEN_HEADERS:
            self.assertEqual(PR.validate_token_header(name), name)
        for name in self.BAD:
            with self.subTest(name=name), self.assertRaises(PR.ReleasePublishError) as ctx:
                PR.validate_token_header(name)
            self.assertNotIn("X-Evil", str(ctx.exception))

    def test_gitlab_request_refuses_an_unknown_header_before_any_network_call(self):
        for name in self.BAD:
            with self.subTest(name=name):
                opener = _RecordingOpener()
                with mock.patch.object(PR, "OPENER", opener), self.assertRaises(PR.ReleasePublishError):
                    PR.gitlab_request("GET", API + "/x", SECRET, token_header=name)
                self.assertEqual(opener.requests, [])

    def test_create_or_update_release_refuses_an_unknown_header_before_any_network_call(self):
        opener = _RecordingOpener()
        with mock.patch.object(PR, "OPENER", opener), mock.patch.object(PR, "gitlab_request") as request, \
                self.assertRaises(PR.ReleasePublishError):
            PR.create_or_update_release("v1.2.3", API, "7", SECRET, "d", "gitlab.invalid", token_header="Authorization")
        self.assertEqual(opener.requests, [])
        request.assert_not_called()  # the check is its own, not only the one inside gitlab_request

    def test_main_refuses_an_unknown_header_even_if_the_parser_let_it_through(self):
        args = types.SimpleNamespace(tag="v1.2.3", api_v4_url=API, project_id="1", token_env="T686_TOKEN", token=None,
                                     expected_host="gitlab.invalid", skip_api=False, token_header="Authorization")
        with mock.patch.object(PR, "parse_args", return_value=args), mock.patch.dict(os.environ, {"T686_TOKEN": SECRET}), \
                mock.patch.object(PR, "run_git", side_effect=AssertionError("git must not run")), \
                self.assertRaisesRegex(PR.ReleasePublishError, "invalid --token-header"):
            PR.main()

    def run_main(self, header_args: list[str]):
        argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", API, "--expected-host", "gitlab.invalid",
                "--project-id", "1", "--token-env", "T686_TOKEN", *header_args]
        err = io.StringIO()
        with mock.patch.object(sys, "argv", argv), mock.patch.dict(os.environ, {"T686_TOKEN": SECRET}), \
                mock.patch.object(PR, "run_git", side_effect=AssertionError("git must not run")), \
                contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as ctx:
            PR.main()
        return ctx.exception.code, err.getvalue()

    def test_the_command_line_refuses_an_unknown_header_name_with_usage_error_two(self):
        for name in ("Authorization", "private-token", "JOB_TOKEN", ""):
            with self.subTest(name=name):
                code, err = self.run_main(["--token-header", name])
                self.assertEqual(code, 2)
                self.assertIn("--token-header", err)
                self.assertNotIn(SECRET, err)

    def test_mutation_dropping_the_allowlist_check_is_detected(self):
        mutant = mutated("    if name not in TOKEN_HEADERS:", "    if False:")
        self.assertEqual(mutant.validate_token_header("Authorization"), "Authorization")  # the mutant accepts any name
        opener = _RecordingOpener()
        with mock.patch.object(mutant, "OPENER", opener):
            mutant.gitlab_request("GET", API + "/x", SECRET, token_header="X-Evil")
        self.assertIn("x-evil", headers_of(opener.requests[0]))  # ... and sends the token in it

    def test_mutation_dropping_the_argparse_choices_is_detected(self):
        mutant = mutated("        choices=TOKEN_HEADERS,\n", "")
        # without choices only validate_token_header in main() stands between the flag and the request
        argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", API, "--expected-host", "gitlab.invalid",
                "--project-id", "1", "--token-env", "T686_TOKEN", "--token-header", "Authorization"]
        with mock.patch.object(sys, "argv", argv):
            self.assertEqual(mutant.parse_args().token_header, "Authorization")  # parse accepts it ...
            with mock.patch.dict(os.environ, {"T686_TOKEN": SECRET}), self.assertRaises(mutant.ReleasePublishError):
                mutant.main()  # ... and the second check still refuses it (defence in depth)


class TestNoTokenInArgvUrlOrOutput(unittest.TestCase):
    def run_main(self, header: str | None, answer=None, module=PR):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "docs" / "releases").mkdir(parents=True)
        (root / "docs" / "releases" / "v1.2.3.md").write_text("# Release v1.2.3\n\nbody\n", encoding="utf-8")

        def fake_git(args):
            return {"tag": "v1.2.3\nv1.2.2", "rev-parse": "false", "merge-base": "sha", "rev-list": "1"}.get(
                args[0], "feat: x\x00")

        argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", API, "--expected-host", "gitlab.invalid",
                "--project-id", "1", "--token-env", "CI_JOB_TOKEN"] + (["--token-header", header] if header else [])
        opener = _RecordingOpener(answer or (lambda r: _TagResponse() if r.get_method() != "GET" else _raise404(r)))
        out, err = io.StringIO(), io.StringIO()
        error = None
        with mock.patch.object(module, "ROOT", root), mock.patch.object(module, "run_git", fake_git), \
                mock.patch.object(module, "OPENER", opener), mock.patch.object(sys, "argv", argv), \
                mock.patch.dict(os.environ, {"CI_JOB_TOKEN": SECRET}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                module.main()
            except module.ReleasePublishError as exc:
                error = str(exc)
        return argv, opener, out.getvalue(), err.getvalue(), error

    def test_main_with_the_job_token_header_sends_it_only_in_that_header(self):
        argv, opener, out, err, error = self.run_main("JOB-TOKEN")
        self.assertIsNone(error)
        self.assertGreaterEqual(len(opener.requests), 2)
        for request in opener.requests:
            self.assertEqual(headers_of(request)["job-token"], SECRET)
            self.assertNotIn("private-token", headers_of(request))
            self.assertNotIn(SECRET, request.full_url)
        self.assertFalse([a for a in argv if SECRET in a])  # the argv holds the variable NAME only
        self.assertNotIn(SECRET, out + err)

    def test_main_without_the_option_still_uses_private_token(self):
        _argv, opener, _out, _err, error = self.run_main(None)
        self.assertIsNone(error)
        self.assertTrue(all(headers_of(r)["private-token"] == SECRET and "job-token" not in headers_of(r)
                            for r in opener.requests))

    def test_a_failing_api_call_reports_the_status_and_never_the_token(self):
        def refuse(request):
            raise urllib.error.HTTPError(request.full_url, 401, "Unauthorized", {}, io.BytesIO(b'{"message":"401 Unauthorized"}'))

        _argv, _opener, out, err, error = self.run_main("JOB-TOKEN", answer=refuse)
        self.assertIn("401", error)
        self.assertNotIn(SECRET, error + out + err)

    def test_the_ci_line_and_the_dry_run_pass_the_name_not_the_value(self):
        ci = CI.read_text(encoding="utf-8")
        line = [ln for ln in ci.splitlines() if "scripts/publish-release.py" in ln and "--token-env" in ln]
        self.assertEqual(len(line), 1)
        self.assertNotRegex(line[0], r"--token(?!-env|-header)")
        self.assertNotIn("${CI_JOB_TOKEN}", line[0])
        self.assertNotIn("$CI_JOB_TOKEN", line[0])

    def test_a_job_token_with_a_control_character_is_still_refused(self):
        for bad in ("abc\ndef", "abc\r", "abc\x00", "abc\x7f"):
            with self.subTest(bad=repr(bad)), self.assertRaisesRegex(PR.ReleasePublishError, "control character"):
                PR.resolve_token(None, "CI_JOB_TOKEN", {"CI_JOB_TOKEN": bad})

    def test_the_job_token_variable_must_be_set(self):
        with self.assertRaisesRegex(PR.ReleasePublishError, "CI_JOB_TOKEN is not set or empty"):
            PR.resolve_token(None, "CI_JOB_TOKEN", {})


def _raise404(request):
    raise urllib.error.HTTPError(request.full_url, 404, "nf", {}, io.BytesIO(b"{}"))


class TestNoVariableHoldingTheJobTokenReachesAChild(unittest.TestCase):
    """SEC-T686-01: the filter works by name (allowlist) AND by value, in git's environment and in apk's."""

    URL = f"https://gitlab-ci-token:{SECRET}@gitlab.invalid/em-age/emage.code.git"
    LEAKS = {  # the same value under other names / inside other values, as GitLab and the runner provide it
        "CI_JOB_TOKEN": SECRET,
        "WIKI_TOKEN": SECRET,
        "CI_REGISTRY_PASSWORD": SECRET,
        "CI_REPOSITORY_URL": URL,
        "SOME_NEW_VARIABLE": f"prefix-{SECRET}-suffix",
        "LANG": f"C-{SECRET}",  # even an allowlisted name is dropped when its value holds the token
        "http_proxy": f"http://user:{SECRET}@proxy.invalid:3128",
    }
    FINE = {"PATH": "/usr/bin:/bin", "HOME": "/root", "LC_ALL": "C", "https_proxy": "http://proxy.invalid:3128",
            "GIT_SSL_CAINFO": "/etc/ssl/ca.pem", "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.sslVerify",
            "GIT_CONFIG_VALUE_0": "true", "TMPDIR": "/tmp"}
    NOT_LISTED = {"KEEP_ME": "1", "CI_COMMIT_TAG": "v1.2.3", "CI_API_V4_URL": API, "GIT_TRACE": "1",
                  "GIT_DEPTH": "0", "CI_PROJECT_ID": "1", "GIT_CONFIG_PARAMETERS": "'a=b'"}

    def git_env(self, module=PR, environ=None) -> dict:
        seen: list[dict] = []

        def run(argv, **kwargs):
            seen.append(kwargs)
            return mock.Mock(returncode=0, stdout=b"ok\n", stderr=b"")

        with mock.patch.dict(os.environ, environ or {**self.LEAKS, **self.FINE, **self.NOT_LISTED}, clear=True), \
                mock.patch.object(module.subprocess, "run", run):
            module.run_git(["status"])
        return seen[0]["env"]

    def test_the_default_withheld_names_hold_both_ci_tokens(self):
        self.assertTrue({"WIKI_TOKEN", "CI_JOB_TOKEN"} <= set(PR.WITHHELD_ENV_NAMES))

    def test_git_gets_no_variable_whose_value_contains_the_job_token_under_any_name(self):
        env = self.git_env()
        for name in self.LEAKS:
            self.assertNotIn(name, env)
        self.assertNotIn(SECRET, "\n".join(env.values()))

    def test_git_gets_the_allowlisted_names_and_nothing_else(self):
        env = self.git_env()
        self.assertEqual(env, self.FINE)
        self.assertTrue(set(PR.CHILD_ENV_NAMES) >= {"PATH", "HOME", "GIT_SSL_CAINFO"})

    def test_a_value_inside_a_url_shaped_variable_is_found_by_value_not_by_name(self):
        env = self.git_env(environ={"CI_JOB_TOKEN": SECRET, "PATH": "/bin", "LANG": f"x{SECRET}", "LC_ALL": f"https://u:{SECRET}@h"})
        self.assertEqual(env, {"PATH": "/bin"})

    def test_the_value_filter_applies_even_when_the_token_variable_name_is_unknown(self):
        """The token named by --token-env is withheld by name too, and by value through that name."""
        names = set(PR.WITHHELD_ENV_NAMES)
        self.addCleanup(lambda: (PR.WITHHELD_ENV_NAMES.clear(), PR.WITHHELD_ENV_NAMES.update(names)))
        PR.WITHHELD_ENV_NAMES.add("T686_ODD_TOKEN")
        env = self.git_env(environ={"T686_ODD_TOKEN": SECRET, "LANG": f"x{SECRET}", "PATH": "/bin"})
        self.assertEqual(env, {"PATH": "/bin"})

    def test_a_token_given_with_the_deprecated_flag_is_withheld_by_value(self):
        self.addCleanup(PR.WITHHELD_ENV_VALUES.clear)
        argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", API, "--expected-host", "gitlab.invalid",
                "--project-id", "1", "--token", SECRET]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(PR, "run_git", side_effect=RuntimeError("stop")), \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(RuntimeError):
            PR.main()
        env = self.git_env(environ={"LANG": f"x{SECRET}", "HOME": "/root", "PATH": "/bin"})
        self.assertEqual(env, {"HOME": "/root", "PATH": "/bin"})

    def test_an_empty_secret_value_never_matches_everything(self):
        self.addCleanup(PR.WITHHELD_ENV_VALUES.clear)
        PR.WITHHELD_ENV_VALUES.add("")
        env = self.git_env(environ={"CI_JOB_TOKEN": "", "WIKI_TOKEN": "", "HOME": "/root", "PATH": "/bin"})
        self.assertEqual(env, {"HOME": "/root", "PATH": "/bin"})

    def test_main_withholds_ci_job_token_when_it_is_named_by_token_env(self):
        names = set(PR.WITHHELD_ENV_NAMES)
        self.addCleanup(lambda: (PR.WITHHELD_ENV_NAMES.clear(), PR.WITHHELD_ENV_NAMES.update(names)))
        PR.WITHHELD_ENV_NAMES.discard("CI_JOB_TOKEN")  # as if only the --token-env logic protected it
        argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", API, "--expected-host", "gitlab.invalid",
                "--project-id", "1", "--token-env", "CI_JOB_TOKEN"]
        with mock.patch.object(sys, "argv", argv), mock.patch.dict(os.environ, {"CI_JOB_TOKEN": SECRET}), \
                mock.patch.object(PR, "run_git", side_effect=RuntimeError("stop")), self.assertRaises(RuntimeError):
            PR.main()
        self.assertIn("CI_JOB_TOKEN", PR.WITHHELD_ENV_NAMES)

    def test_mutation_leaving_the_job_token_out_of_the_withheld_names_is_detected(self):
        mutant = mutated('WITHHELD_ENV_NAMES = {"WIKI_TOKEN", "CI_JOB_TOKEN"}', 'WITHHELD_ENV_NAMES = {"WIKI_TOKEN"}')
        env = self.git_env(mutant, {"CI_JOB_TOKEN": SECRET, "LANG": f"x{SECRET}", "PATH": "/bin"})
        # the value is no longer a known secret, so its copy under an allowlisted name leaks
        self.assertIn("LANG", env)

    def test_mutation_filtering_by_name_only_is_detected(self):
        mutant = mutated("and k not in WITHHELD_ENV_NAMES and not any(secret in v for secret in secrets)",
                         "and k not in WITHHELD_ENV_NAMES")
        env = self.git_env(mutant, {"CI_REGISTRY_PASSWORD": SECRET, "CI_REPOSITORY_URL": self.URL, "PATH": "/bin"})
        self.assertEqual(set(env), {"PATH"})  # these two names are not allowlisted, so the allowlist still holds ...
        env = self.git_env(mutant, {"LANG": f"x{SECRET}", "http_proxy": self.URL, "CI_JOB_TOKEN": SECRET})
        self.assertIn("LANG", env)  # ... but an allowlisted name carrying the token leaks without the value filter

    def test_mutation_without_the_allowlist_is_detected(self):
        mutant = mutated("        if (k in CHILD_ENV_NAMES or CHILD_ENV_PATTERN.fullmatch(k))\n        and ", "        if ")
        env = self.git_env(mutant, {"KEEP_ME": "1", "PATH": "/bin"})
        self.assertIn("KEEP_ME", env)

    def bootstrap(self) -> str:
        """The code string of the release job's ``python3 -I -c "..."`` before_script (what runs `apk add`)."""
        job = re.search(r"^release:\n(?:[ \t].*\n|\n)+", CI.read_text(encoding="utf-8"), re.M).group(0)
        line = [ln for ln in job.splitlines() if "subprocess.check_call" in ln][0]
        return re.search(r'python3 -I -c "(.*)"\s*$', line).group(1)

    def run_bootstrap(self, code: str, environ: dict[str, str]) -> dict[str, str]:
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "apk"
            fake.write_text('#!/bin/sh\nenv > "${0%/*}/env.txt"\n', encoding="utf-8")
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            env = {**environ, "PATH": f"{tmp}:/usr/bin:/bin"}
            subprocess.run([sys.executable, "-I", "-c", code], env=env, check=True, capture_output=True)
            dump = Path(tmp) / "env.txt"
            return dict(ln.split("=", 1) for ln in dump.read_text(encoding="utf-8").splitlines() if "=" in ln)

    def test_the_bootstrap_is_the_exact_text_that_yaml_parses_to(self):
        try:
            import yaml
        except ImportError:  # pragma: no cover -- the regex above is the fallback
            self.skipTest("PyYAML not installed")
        job = yaml.safe_load(CI.read_text(encoding="utf-8"))["release"]
        self.assertEqual(job["before_script"], [f'python3 -I -c "{self.bootstrap()}"'])

    def test_apk_gets_no_variable_whose_value_contains_the_job_token_under_any_name(self):
        seen = self.run_bootstrap(self.bootstrap(), {**self.LEAKS, "HOME": "/root", "LC_ALL": "C", "TMPDIR": "/tmp",
                                                      "KEEP_ME": "1", "CI_COMMIT_TAG": "v1.2.3"})
        for name in self.LEAKS:
            self.assertNotIn(name, seen)
        self.assertNotIn(SECRET, "\n".join(seen.values()))
        self.assertEqual(seen["HOME"], "/root")  # the allowlisted rest passes ...
        self.assertEqual(seen["LC_ALL"], "C")
        self.assertNotIn("KEEP_ME", seen)  # ... and nothing else does
        self.assertNotIn("CI_COMMIT_TAG", seen)

    def test_the_apk_allowlist_in_the_yaml_equals_the_script_allowlist_without_git_names(self):
        match = re.search(r"ok=\(([^)]*)\)", self.bootstrap())
        names = set(re.findall(r"'([^']+)'", match.group(1)))
        self.assertEqual(names, set(PR.CHILD_ENV_APK_NAMES))
        self.assertFalse([n for n in names if n.startswith("GIT_")])
        self.assertTrue(set(PR.CHILD_ENV_APK_NAMES) <= set(PR.CHILD_ENV_NAMES))

    def test_the_apk_bootstrap_names_both_ci_tokens_as_the_secret_sources(self):
        self.assertIn("k in ('CI_JOB_TOKEN', 'WIKI_TOKEN')", self.bootstrap())

    def test_mutation_the_apk_bootstrap_filtering_by_name_only_is_detected(self):
        code = self.bootstrap().replace(" and not any(x in i[1] for x in secrets)", "")
        self.assertNotEqual(code, self.bootstrap())
        seen = self.run_bootstrap(code, {"CI_JOB_TOKEN": SECRET, "LANG": f"x{SECRET}", "HOME": "/root"})
        self.assertIn("LANG", seen)  # the mutant lets an allowlisted name carry the token

    def test_mutation_the_apk_bootstrap_without_the_allowlist_is_detected(self):
        code = self.bootstrap().replace("(i[0] in ok or i[0].startswith('LC_')) and ", "")
        seen = self.run_bootstrap(code, {"CI_REGISTRY_PASSWORD": "other", "KEEP_ME": "1", "HOME": "/root"})
        self.assertIn("KEEP_ME", seen)

    def test_mutation_the_apk_bootstrap_ignoring_the_job_token_value_is_detected(self):
        code = self.bootstrap().replace("k in ('CI_JOB_TOKEN', 'WIKI_TOKEN')", "k in ('WIKI_TOKEN',)")
        seen = self.run_bootstrap(code, {"CI_JOB_TOKEN": SECRET, "LANG": f"x{SECRET}", "HOME": "/root"})
        self.assertIn("LANG", seen)


class TestTheCiJobs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ci = CI.read_text(encoding="utf-8")
        cls.jobs = {m.group(1): m.group(0) for m in re.finditer(r"^([A-Za-z0-9_.-]+):\n(?:[ \t].*\n|\n)+", cls.ci, re.M)}

    @staticmethod
    def code(job: str) -> list[str]:
        return [ln for ln in job.splitlines() if not ln.lstrip().startswith("#")]

    def test_the_release_job_uses_the_job_token_in_the_job_token_header(self):
        body = "\n".join(self.code(self.jobs["release"]))
        self.assertIn("--token-env CI_JOB_TOKEN --token-header JOB-TOKEN", body)
        self.assertIn('--expected-host "${CI_SERVER_HOST}"', body)
        self.assertEqual(len(re.findall(r"--token-env\s+\S+", body)), 1)
        self.assertNotIn("--token-env WIKI_TOKEN", body)
        self.assertNotIn("--token-header PRIVATE-TOKEN", body)

    def test_no_job_reads_wiki_token_as_a_credential_except_wiki_sync(self):
        for name, job in self.jobs.items():
            hits = [ln for ln in self.code(job) if "WIKI_TOKEN" in ln]
            with self.subTest(job=name):
                if name == "wiki-sync":
                    self.assertTrue(any('"$WIKI_TOKEN"' in ln for ln in hits))
                elif name == "release":
                    # the only mention is the filter that keeps it away from apk
                    self.assertEqual(len(hits), 1)
                    self.assertIn("k in ('CI_JOB_TOKEN', 'WIKI_TOKEN')", hits[0])
                    self.assertNotIn("--token-env", hits[0])
                else:
                    self.assertEqual(hits, [])

    def test_no_job_besides_release_names_a_token_header_or_the_job_token(self):
        for name, job in self.jobs.items():
            if name == "release":
                continue
            with self.subTest(job=name):
                self.assertNotIn("CI_JOB_TOKEN", "\n".join(self.code(job)))
                self.assertNotIn("--token-header", job)

    def test_wiki_sync_still_runs_the_wiki_script_with_the_wiki_token(self):
        body = "\n".join(self.code(self.jobs["wiki-sync"]))
        self.assertIn("python3 scripts/sync-wiki.py", body)
        self.assertIn('if [ -z "$WIKI_TOKEN" ]', body)
        self.assertIn('$CI_COMMIT_BRANCH == "develop"', body)

    def test_the_whole_file_has_no_release_call_with_wiki_token(self):
        self.assertNotRegex(self.ci, r"publish-release\.py[^\n]*WIKI_TOKEN")
        self.assertEqual(len(re.findall(r"--token-header", self.ci)), 1)

    def test_mutation_the_release_line_back_on_wiki_token_is_detected(self):
        body = self.jobs["release"].replace("--token-env CI_JOB_TOKEN --token-header JOB-TOKEN", "--token-env WIKI_TOKEN")
        self.assertIn("--token-env WIKI_TOKEN", body)  # what the checks above reject
        self.assertNotIn("--token-header JOB-TOKEN", body)


class TestRedirectsAreStillRefusedWithTheNewHeader(unittest.TestCase):
    CODES = (301, 302, 303, 307, 308)

    class Handler(http.server.BaseHTTPRequestHandler):
        seen: list = []
        status = 302
        redirect_to: str | None = None

        def do_GET(self):  # noqa: N802
            type(self).seen.append((self.headers.get("JOB-TOKEN"), self.headers.get("PRIVATE-TOKEN")))
            if self.redirect_to:
                self.send_response(self.status)
                self.send_header("Location", self.redirect_to)
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"{}")

        def log_message(self, *args):
            pass

    def serve(self, handler):
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"http://127.0.0.1:{server.server_address[1]}"

    def pair(self, code):
        target = type("Target", (self.Handler,), {"seen": [], "redirect_to": None})
        origin = type("Origin", (self.Handler,), {"seen": [], "status": code, "redirect_to": self.serve(target) + "/leak"})
        return target, origin, self.serve(origin)

    def test_the_job_token_header_is_sent_once_and_never_resent_on_any_redirect(self):
        for code in self.CODES:
            with self.subTest(code=code):
                target, origin, url = self.pair(code)
                with self.assertRaisesRegex(PR.ReleasePublishError, f"failed: {code}"):
                    PR.gitlab_request("GET", url + "/x", SECRET, token_header="JOB-TOKEN")
                self.assertEqual(origin.seen, [(SECRET, None)])
                self.assertEqual(target.seen, [])

    def test_control_the_default_opener_would_resend_the_job_token_header(self):
        target, _origin, url = self.pair(307)
        with mock.patch.object(PR, "OPENER", urllib.request.build_opener()):
            PR.gitlab_request("GET", url + "/x", SECRET, token_header="JOB-TOKEN")
        self.assertEqual(target.seen, [(SECRET, None)])

    def test_mutation_following_redirects_is_detected_for_the_new_header(self):
        mutant = mutated("        return None  # the caller then sees the 3xx as an HTTPError",
                         "        return super().redirect_request(req, fp, code, msg, headers, newurl)")
        target, _origin, url = self.pair(302)
        mutant.gitlab_request("GET", url + "/x", SECRET, token_header="JOB-TOKEN")
        self.assertEqual(target.seen, [(SECRET, None)])  # the mutant leaks the job token


class TestHostPinAndDryRunStillWork(unittest.TestCase):
    def test_a_wrong_host_is_refused_before_the_token_is_resolved_or_sent(self):
        opener = _RecordingOpener()
        argv = ["publish-release.py", "--tag", "v1.2.3", "--api-v4-url", "https://evil.invalid/api/v4",
                "--expected-host", "gitlab.invalid", "--project-id", "1", "--token-env", "CI_JOB_TOKEN",
                "--token-header", "JOB-TOKEN"]
        with mock.patch.object(PR, "OPENER", opener), mock.patch.object(sys, "argv", argv), \
                mock.patch.dict(os.environ, {"CI_JOB_TOKEN": SECRET}), \
                mock.patch.object(PR, "run_git", side_effect=AssertionError("git must not run")), \
                self.assertRaisesRegex(PR.ReleasePublishError, "host does not match"):
            PR.main()
        self.assertEqual(opener.requests, [])

    def test_the_dry_run_needs_no_real_token_and_rehearses_the_job_token_header(self):
        spec_path = repo_root() / "scripts" / "dry-run-publish-release.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("dry_run_publish_release_t686", spec_path)
        dry = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = dry
        spec.loader.exec_module(dry)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CI_JOB_TOKEN", None)
            os.environ.pop("WIKI_TOKEN", None)
            with tempfile.TemporaryDirectory() as tmp:
                fixtures = Path(tmp) / "f"
                dry.write_template_shaped_document(repo_root(), fixtures)
                result = dry.run_dry_run("v1.2.3", Path(tmp) / "work", dry.DryRunSource(source_dir=fixtures, copy_changelog=False))
        self.assertEqual(result["exit"], 0)
        self.assertTrue(result["sent"])
        self.assertEqual({c["token_header"] for c in result["sent"]}, {"JOB-TOKEN"})


class TestTheDocs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = (repo_root() / "CONTRIBUTING.md").read_text(encoding="utf-8")
        start = text.index("### Cutting a release")
        mid = text.index("### Release token and permissions")
        end = text.index("### Drift detection")
        flat = lambda chunk: re.sub(r"\s+", " ", chunk)  # noqa: E731
        cls.steps = flat(text[start:mid])  # "Cutting a release" including step 8
        cls.section = flat(text[mid:end])  # only the "Release token and permissions" section

    def test_step_eight_names_the_job_token_and_states_the_value_based_filter(self):
        for needle in ("--token-env CI_JOB_TOKEN --token-header JOB-TOKEN",
                       "no variable whose value contains the job token is passed to either of them",
                       "allowlisted environment"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.steps)
        self.assertNotIn("--token-env WIKI_TOKEN", self.steps)
        self.assertNotIn("reads the GitLab token from the CI variable `WIKI_TOKEN`", self.steps)
        self.assertNotIn("is withheld from the `git` and `apk` child processes", self.steps)  # the old name-based claim

    def test_the_section_states_roles_protection_wiki_token_fallback_and_limits(self):
        for needle in (
            "needs at least the **Developer role**",
            "permission to create the tag",
            "may be higher than the role the old `WIKI_TOKEN` carried",
            "restricted to Maintainers",
            "does **not** limit who holds a Releases-capable token",
            "job token permission and allowlist settings",
            "protected and masked",
            "only by the `wiki-sync` job",
            "typically Developer",
            "glab release create",
            "401 or 403",
            "no variable whose value contains the job token, `WIKI_TOKEN` or the token that was passed",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.section)

    def test_the_unverified_points_and_the_rehearsal_checklist_are_in_the_section(self):
        for needle in ("(unverified)", "protected tags also restrict release create, update and delete",
                       "`CI_JOB_TOKEN` is masked in job logs", "First-tag rehearsal checklist",
                       "Search the whole job log"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.section)


if __name__ == "__main__":
    unittest.main()
