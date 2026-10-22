"""T665 (SEC-T660-01) -- scripts/check-gitlab-token.py.

The script reads the GitLab token, asks GitLab two read-only questions and prints findings. These tests
never use a real token and never reach GitLab: the HTTP layer is exercised against a LOOPBACK fake server
(plain http, through `run_check`, which sits below the https/host validation), and the full `main()` runs
against an in-process fake opener. Every main guard has a mutation proof: the guard is removed from a copy
of the source, the copy is loaded, and the matching test condition must then FAIL.

Guards under mutation proof: https-only, host pin, redirect refusal, token redaction in output, the
over-broad scope warning, the expiry boundary.
"""
from __future__ import annotations

import ast
import contextlib
import datetime as dt
import http.server
import importlib.util
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import threading
import types
import unittest
import urllib.error
from pathlib import Path

from tests._helpers.repo import repo_root

SCRIPT = repo_root() / "scripts" / "check-gitlab-token.py"
FAKE_TOKEN = "FAKE-test-token-value-0123456789"  # synthetic: not shaped like a GitLab token
TODAY = dt.date(2026, 10, 16)


def load_module(source: str | None = None, name: str = "check_gitlab_token") -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8") if source is None else source
    module = types.ModuleType(name)
    module.__file__ = str(SCRIPT)
    sys.modules[name] = module  # dataclasses looks the defining module up by name
    exec(compile(text, str(SCRIPT), "exec"), module.__dict__)  # noqa: S102 -- our own script / a mutation of it
    return module


def mutated(old: str, new: str) -> types.ModuleType:
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"mutation anchor must occur exactly once: {old!r}"
    return load_module(text.replace(old, new), "check_gitlab_token_mutant")


M = load_module()


def good_self(**over) -> dict:
    data = {"id": 1, "name": "harness", "revoked": False, "active": True, "scopes": ["api"],
            "expires_at": (TODAY + dt.timedelta(days=30)).isoformat()}
    data.update(over)
    return data


def good_user(**over) -> dict:
    data = {"id": 7, "username": "harness-bot", "state": "active", "bot": False, "is_admin": False}
    data.update(over)
    return data


# ------------------------------------------------------------------ fake servers ----

class _Handler(http.server.BaseHTTPRequestHandler):
    routes: dict = {}
    seen: list = []

    def do_GET(self):  # noqa: N802
        type(self).seen.append((self.path, self.headers.get("PRIVATE-TOKEN")))
        status, body, headers = type(self).routes.get(self.path, (404, b"{}", {}))
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silence
        pass


def serve(routes: dict):
    handler = type("H", (_Handler,), {"routes": routes, "seen": []})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, handler, f"http://127.0.0.1:{server.server_address[1]}"


def json_body(data) -> bytes:
    return json.dumps(data).encode("utf-8")


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self, n: int = -1) -> bytes:
        return self._body if n < 0 else self._body[:n]


class FakeOpener:
    """An in-process opener: maps a URL path suffix to a body (bytes) or an exception to raise."""

    def __init__(self, replies: dict) -> None:
        self.replies = replies
        self.calls: list = []

    def open(self, request, timeout=None):
        self.calls.append((request.full_url, request.get_header("Private-token")))
        for suffix, reply in self.replies.items():
            if request.full_url.endswith(suffix):
                if isinstance(reply, Exception):
                    raise reply
                return FakeResponse(reply)
        raise AssertionError("unexpected URL " + request.full_url)


def run_main(argv, environ, opener=None):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = M.main(argv, environ=environ, opener=opener)
    return code, out.getvalue(), err.getvalue()


def http_error(code: int, url: str = "https://gitlab.com/api/v4/user") -> urllib.error.HTTPError:
    return urllib.error.HTTPError(url, code, "x", {}, io.BytesIO(b'{"message":"%s"}' % FAKE_TOKEN.encode()))


# ---------------------------------------------------------------------- target ----

class TargetTests(unittest.TestCase):
    def test_a_clean_https_api_url_on_the_pinned_host_is_accepted(self):
        for url in ("https://gitlab.com/api/v4", "https://GitLab.com/api/v4", "https://gitlab.com:8443/api/v4",
                    "https://gitlab.com/sub/api/v4"):
            self.assertIsNone(M.api_url_problem(url, "gitlab.com"), url)

    def test_everything_else_is_refused(self):
        bad = {
            "http://gitlab.com/api/v4": "https",
            "ftp://gitlab.com/api/v4": "https",
            "https://user:pw@gitlab.com/api/v4": "user information",
            "https://gitlab.com@evil.example/api/v4": "user information",
            "https://gitlab.com/api/v4?x=1": "query",
            "https://gitlab.com/api/v4#frag": "query",
            "https://gitlab.com/api/v4/": "api/v4",
            "https://gitlab.com/api/v3": "api/v4",
            "https://gitlab.com/../api/v4": "api/v4",
            "https://gitlab.com/api/v4 ": "whitespace",
            "https://gitlab.com\\@evil.example/api/v4": "backslash",
            "https://gitlab.com.evil.example/api/v4": "expected GitLab host",
            "https://evilgitlab.com/api/v4": "expected GitLab host",
            "https://gitlab.example.org/api/v4": "expected GitLab host",
            "https://gitlab.com:99999/api/v4": "valid URL",
            "https:///api/v4": "host",
        }
        for url, why in bad.items():
            with self.subTest(url=url):
                problem = M.api_url_problem(url, "gitlab.com")
                self.assertIsNotNone(problem, url)
                self.assertIn(why, problem)

    def test_host_resolution_flag_then_ci_then_gitlab_com(self):
        self.assertEqual(M.resolve_expected_host("a.example", {"CI_SERVER_HOST": "b.example"}), "a.example")
        self.assertEqual(M.resolve_expected_host(None, {"CI_SERVER_HOST": "b.example"}), "b.example")
        self.assertEqual(M.resolve_expected_host(None, {}), "gitlab.com")
        for bad in ("", "  ", "a b", "x/y", "a@b"):
            with self.assertRaises(M.CheckError, msg=repr(bad)):
                M.resolve_expected_host(bad, {})

    def test_api_url_resolution(self):
        self.assertEqual(M.resolve_api_url("https://h.example/api/v4/", {}), "https://h.example/api/v4")
        self.assertEqual(M.resolve_api_url(None, {"GITLAB_API_URL": "https://h.example/api/v4"}), "https://h.example/api/v4")
        self.assertEqual(M.resolve_api_url(None, {}), "https://gitlab.com/api/v4")
        self.assertEqual(M.resolve_api_url(None, {"GITLAB_API_URL": ""}), "https://gitlab.com/api/v4")


# ----------------------------------------------------------------------- token ----

class TokenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def token_file(self, content: str = FAKE_TOKEN + "\n", mode: int = 0o600) -> str:
        path = Path(self.tmp.name) / "token"
        path.write_text(content, encoding="utf-8")
        path.chmod(mode)
        return str(path)

    def test_a_non_empty_variable_wins_over_the_file_and_a_warning_names_the_stale_export(self):
        src = M.load_token(M.DEFAULT_TOKEN_ENV, M.DEFAULT_FILE_ENV,
                           {M.DEFAULT_TOKEN_ENV: FAKE_TOKEN, M.DEFAULT_FILE_ENV: self.token_file("other-value")})
        self.assertEqual(src.token, FAKE_TOKEN)
        self.assertIn(M.DEFAULT_TOKEN_ENV, src.description)
        self.assertEqual(len(src.warnings), 1)
        self.assertIn("remove the export", src.warnings[0])
        self.assertNotIn(FAKE_TOKEN, src.warnings[0])

    def test_an_empty_variable_falls_through_to_the_file_like_the_server(self):
        src = M.load_token(M.DEFAULT_TOKEN_ENV, M.DEFAULT_FILE_ENV,
                           {M.DEFAULT_TOKEN_ENV: "", M.DEFAULT_FILE_ENV: self.token_file()})
        self.assertEqual(src.token, FAKE_TOKEN)
        self.assertEqual(src.warnings, [])

    def test_a_group_or_world_readable_file_warns(self):
        src = M.load_token("T", "F", {"F": self.token_file(mode=0o644)})
        self.assertEqual(src.token, FAKE_TOKEN)
        self.assertTrue(any("chmod 600" in w and "0644" in w for w in src.warnings))

    def test_the_variable_names_are_flags_and_must_be_names(self):
        src = M.load_token("MY_TOKEN", "MY_FILE", {"MY_TOKEN": FAKE_TOKEN})
        self.assertIn("MY_TOKEN", src.description)
        for bad in ("a-b", "1X", "", "X Y", "$(id)"):
            with self.assertRaises(M.CheckError, msg=bad):
                M.load_token(bad, "F", {})

    def test_failures_stop_with_a_message_that_never_holds_the_value(self):
        d = Path(self.tmp.name)
        cases = {
            "no token": {},
            "missing file": {"F": str(d / "nope")},
            "directory": {"F": str(d)},
            "empty file": {"F": self.token_file("  \n")},
            "oversized": {"F": self.token_file("x" * 5000)},
            "control char": {"T": FAKE_TOKEN + "\nX-Evil: 1"},
            "control char in file": {"F": self.token_file(FAKE_TOKEN + "\x00y")},
        }
        for label, environ in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(M.CheckError) as ctx:
                    M.load_token("T", "F", environ)
                self.assertNotIn(FAKE_TOKEN, str(ctx.exception))

    # --- SEC-T665-04 / -05: one descriptor, no symlink, no FIFO, owner, printable ASCII, BOM ---

    def test_a_symbolic_link_is_refused(self):
        real = self.token_file()
        link = Path(self.tmp.name) / "link"
        link.symlink_to(real)
        with self.assertRaises(M.CheckError) as ctx:
            M.load_token("T", "F", {"F": str(link)})
        self.assertIn("symbolic link", str(ctx.exception))

    def test_a_fifo_is_refused_without_blocking(self):
        fifo = Path(self.tmp.name) / "fifo"
        os.mkfifo(fifo)
        result: list = []
        thread = threading.Thread(target=lambda: result.append(self._try(str(fifo))), daemon=True)
        thread.start()
        thread.join(5)
        self.assertFalse(thread.is_alive(), "reading a FIFO blocked")
        self.assertIn("not a regular file", result[0])

    def _try(self, path: str) -> str:
        try:
            M.load_token("T", "F", {"F": path})
        except M.CheckError as exc:
            return str(exc)
        return "accepted"

    def test_a_file_owned_by_another_user_is_refused(self):
        from unittest import mock
        path = self.token_file()
        with mock.patch.object(M.os, "geteuid", return_value=os.geteuid() + 1):
            with self.assertRaises(M.CheckError) as ctx:
                M.load_token("T", "F", {"F": path})
        self.assertIn("not owned", str(ctx.exception))

    def test_a_bom_is_stripped_from_the_file_and_the_variable(self):
        self.assertEqual(M.load_token("T", "F", {"F": self.token_file("\ufeff" + FAKE_TOKEN + "\n")}).token, FAKE_TOKEN)
        self.assertEqual(M.load_token("T", "F", {"T": "\ufeff" + FAKE_TOKEN}).token, FAKE_TOKEN)

    def test_non_ascii_spaces_and_bad_bytes_are_refused(self):
        for label, environ in {
            "non-latin-1": {"T": "val\u20acue"},
            "latin-1 only": {"T": "val\u00e9ue"},
            "inner space": {"T": "val ue"},
            "inner tab": {"T": "val\tue"},
            "invalid utf-8 file": {"F": self._bytes_file(b"abc\xff\xfe")},
        }.items():
            with self.subTest(case=label):
                with self.assertRaises(M.CheckError) as ctx:
                    M.load_token("T", "F", environ)
                self.assertNotIn("val", str(ctx.exception))

    def _bytes_file(self, data: bytes) -> str:
        path = Path(self.tmp.name) / "bytes"
        path.write_bytes(data)
        path.chmod(0o600)
        return str(path)

    def test_mutation_proof_symlink_refusal(self):
        mutant = mutated('    for name in ("O_NOFOLLOW", "O_NONBLOCK", "O_CLOEXEC"):', '    for name in ("O_NONBLOCK", "O_CLOEXEC"):')
        real = self.token_file()
        link = Path(self.tmp.name) / "link2"
        link.symlink_to(real)
        self.assertEqual(mutant.load_token("T", "F", {"F": str(link)}).token, FAKE_TOKEN)

    def test_mutation_proof_size_cap(self):
        big = self.token_file("x" * 5000)
        with self.assertRaises(M.CheckError):
            M.load_token("T", "F", {"F": big})
        mutant = mutated("    if len(data) > MAX_TOKEN_FILE_BYTES:", "    if False:")
        self.assertEqual(len(mutant.load_token("T", "F", {"F": big}).token), M.MAX_TOKEN_FILE_BYTES + 1)

    def test_mutation_proof_file_mode_warning(self):
        path = self.token_file(mode=0o644)
        self.assertTrue(M.load_token("T", "F", {"F": path}).warnings)
        mutant = mutated("        if info.st_mode & 0o077:", "        if False:")
        self.assertEqual(mutant.load_token("T", "F", {"F": path}).warnings, [])

    def test_mutation_proof_control_character_refusal(self):
        with self.assertRaises(M.CheckError):
            M.load_token("T", "F", {"T": FAKE_TOKEN + "\nX-Evil: 1"})
        mutant = mutated("    if not TOKEN_TEXT_RE.fullmatch(token):", "    if False:")
        self.assertIn("X-Evil", mutant.load_token("T", "F", {"T": FAKE_TOKEN + "\nX-Evil: 1"}).token)

    def test_the_token_source_repr_does_not_show_the_value(self):
        src = M.TokenSource(token=FAKE_TOKEN, description="x")
        self.assertNotIn(FAKE_TOKEN, repr(src))
        self.assertNotIn(FAKE_TOKEN, f"{src}")


# -------------------------------------------------------------------- analysis ----

class AnalysisTests(unittest.TestCase):
    def analyse(self, self_info=None, user_info=None):
        return M.analyse(self_info or good_self(), user_info or good_user(), TODAY)

    def test_a_narrow_short_lived_token_has_no_findings(self):
        f = self.analyse()
        self.assertEqual((f.warnings, f.errors), ([], []))
        self.assertIn("scopes: api", f.infos)

    def test_each_over_broad_scope_warns(self):
        for scope in ("read_user", "write_repository", "read_repository", "ai_features", "sudo", "admin_mode", "create_runner", "k8s_proxy"):
            with self.subTest(scope=scope):
                f = self.analyse(good_self(scopes=["api", scope]))
                self.assertEqual(len(f.warnings), 1)
                self.assertIn(scope, f.warnings[0])

    def test_api_and_read_api_alone_are_accepted_and_read_user_is_not(self):
        self.assertTrue(self.analyse(good_self(scopes=["api", "read_user"])).warnings)
        self.assertIn("read_user", self.analyse(good_self(scopes=["read_user"])).warnings[0])
        for scopes in (["api"], ["read_api"], ["api", "read_api"]):
            self.assertEqual(self.analyse(good_self(scopes=scopes)).warnings, [], scopes)

    def test_expiry_none_beyond_90_days_and_the_boundary(self):
        self.assertTrue(any("no expiry" in w for w in self.analyse(good_self(expires_at=None)).warnings))
        self.assertEqual(self.analyse(good_self(expires_at=(TODAY + dt.timedelta(days=90)).isoformat())).warnings, [])
        f = self.analyse(good_self(expires_at=(TODAY + dt.timedelta(days=91)).isoformat()))
        self.assertEqual(len(f.warnings), 1)
        self.assertIn("91 days", f.warnings[0])
        self.assertTrue(any("could not be read" in w for w in self.analyse(good_self(expires_at="soon")).warnings))
        self.assertTrue(self.analyse(good_self(expires_at=(TODAY - dt.timedelta(days=1)).isoformat())).errors)

    def test_revoked_or_inactive_is_an_error(self):
        self.assertTrue(self.analyse(good_self(revoked=True)).errors)
        self.assertTrue(self.analyse(good_self(active=False)).errors)

    def test_administrator_owner_and_non_active_owner_warn(self):
        self.assertTrue(any("administrator" in w for w in self.analyse(None, good_user(is_admin=True)).warnings))
        self.assertTrue(any("'blocked'" in w for w in self.analyse(None, good_user(state="blocked")).warnings))
        self.assertTrue(any("bot user" in i for i in self.analyse(None, good_user(bot=True)).infos))

    def test_a_role_above_developer_warns_when_a_response_carries_one(self):
        for key, value in (("access_level", 40), ("access_level", 50), ("role", "maintainer"), ("role", "Owner")):
            with self.subTest(key=key, value=value):
                self.assertTrue(any("above Developer" in w for w in self.analyse(good_self(**{key: value})).warnings))
                self.assertTrue(any("above Developer" in w for w in self.analyse(None, good_user(**{key: value})).warnings))
        for key, value in (("access_level", 30), ("access_level", 15), ("role", "reporter"), ("access_level", True)):
            self.assertEqual(self.analyse(good_self(**{key: value})).warnings, [], (key, value))

    def test_fine_grained_tokens_are_noted_not_evaluated(self):
        f = self.analyse(good_self(scopes=None, granular_scopes=[{"permission": "x"}]))
        self.assertEqual(f.warnings, [])
        self.assertTrue(any("fine-grained" in i for i in f.infos))
        self.assertTrue(any("scope list was not reported" in w for w in self.analyse(good_self(scopes=None)).warnings))


# ------------------------------------------------------------------------ HTTP ----

class HttpLayerTests(unittest.TestCase):
    """The request layer against a loopback server (plain http: below the https validation, by design)."""

    def start(self, routes):
        server, handler, base = serve(routes)
        self.addCleanup(server.shutdown)
        self.addCleanup(server.server_close)
        return handler, base

    def ok_routes(self):
        return {
            "/personal_access_tokens/self": (200, json_body(good_self()), {}),
            "/user": (200, json_body(good_user()), {}),
        }

    def test_two_get_requests_with_the_token_header_and_nothing_else(self):
        handler, base = self.start(self.ok_routes())
        findings, user = M.run_check(base, FAKE_TOKEN, M.make_opener(), TODAY)
        self.assertEqual(handler.seen, [("/personal_access_tokens/self", FAKE_TOKEN), ("/user", FAKE_TOKEN)])
        self.assertEqual(findings.warnings, [])
        self.assertEqual(user["username"], "harness-bot")

    def test_a_redirect_is_refused_and_the_token_is_not_resent(self):
        target_handler, target_url = self.start({})
        origin_handler, origin_url = self.start(
            {"/personal_access_tokens/self": (302, b"", {"Location": target_url + "/leak"})})
        with self.assertRaises(M.CheckError) as ctx:
            M.run_check(origin_url, FAKE_TOKEN, M.make_opener(), TODAY)
        self.assertIn("redirect", str(ctx.exception))
        self.assertEqual(target_handler.seen, [], "the token was re-sent to the redirect target")
        self.assertEqual(len(origin_handler.seen), 1)

    def test_mutation_proof_the_default_opener_would_have_followed_the_redirect(self):
        import urllib.request
        target_handler, target_url = self.start({"/leak": (200, b"{}", {})})
        origin_handler, origin_url = self.start({"/personal_access_tokens/self": (302, b"", {"Location": target_url + "/leak"})})
        try:
            M.api_get(urllib.request.build_opener(), origin_url + "/personal_access_tokens/self", FAKE_TOKEN, "x")
        except M.CheckError:
            pass
        self.assertEqual(target_handler.seen, [("/leak", FAKE_TOKEN)], "the test setup no longer proves anything")

    def test_mutation_proof_removing_the_refusal_lets_the_token_follow_the_redirect(self):
        mutant = mutated("        return None  # the caller then sees the 3xx as an HTTPError",
                         "        return super().redirect_request(req, fp, code, msg, headers, newurl)")
        target_handler, target_url = self.start({"/leak": (200, b"{}", {})})
        origin_handler, origin_url = self.start({"/personal_access_tokens/self": (302, b"", {"Location": target_url + "/leak"})})
        try:
            mutant.run_check(origin_url, FAKE_TOKEN, mutant.make_opener(), TODAY)
        except mutant.CheckError:
            pass
        self.assertEqual(target_handler.seen, [("/leak", FAKE_TOKEN)])

    def test_http_errors_report_the_status_and_never_the_body(self):
        for status in (401, 403, 404, 500):
            with self.subTest(status=status):
                _, base = self.start({"/personal_access_tokens/self": (status, json_body({"message": FAKE_TOKEN}), {})})
                with self.assertRaises(M.CheckError) as ctx:
                    M.run_check(base, FAKE_TOKEN, M.make_opener(), TODAY)
                self.assertIn(f"HTTP {status}", str(ctx.exception))
                self.assertNotIn(FAKE_TOKEN, str(ctx.exception))

    def test_a_reply_that_is_not_a_json_object_is_an_error(self):
        for body in (b"<html>", b"[1,2]", b"\xff\xfe", b"", b'"x"'):
            with self.subTest(body=body):
                _, base = self.start({"/personal_access_tokens/self": (200, body, {})})
                with self.assertRaises(M.CheckError):
                    M.run_check(base, FAKE_TOKEN, M.make_opener(), TODAY)

    def test_an_oversized_reply_is_refused(self):
        _, base = self.start({"/personal_access_tokens/self": (200, b" " * (M.MAX_REPLY_BYTES + 10), {})})
        with self.assertRaises(M.CheckError) as ctx:
            M.run_check(base, FAKE_TOKEN, M.make_opener(), TODAY)
        self.assertIn("more than", str(ctx.exception))

    def test_a_deeply_nested_reply_is_an_error_not_a_crash(self):
        _, base = self.start({"/personal_access_tokens/self": (200, b"[" * 200000, {})})
        with self.assertRaises(M.CheckError) as ctx:
            M.run_check(base, FAKE_TOKEN, M.make_opener(), TODAY)
        self.assertIn("JSON", str(ctx.exception))

    def test_mutation_proof_an_error_body_that_was_read_would_reach_the_message(self):
        route = {"/personal_access_tokens/self": (401, json_body({"message": FAKE_TOKEN}), {})}
        text = SCRIPT.read_text(encoding="utf-8")
        for old, new in (("        exc.close()  # the body is never read or printed\n", ""),
                         ('        raise CheckError(f"GET {label} failed: HTTP {exc.code}") from exc',
                          '        raise CheckError(f"GET {label} failed: HTTP {exc.code} " + exc.read().decode()) from exc')):
            self.assertEqual(text.count(old), 1)
            text = text.replace(old, new)
        mutant = load_module(text, "check_gitlab_token_mutant")
        _, base = self.start(route)
        with self.assertRaises(mutant.CheckError) as ctx:
            mutant.run_check(base, FAKE_TOKEN, mutant.make_opener(), TODAY)
        self.assertIn(FAKE_TOKEN, str(ctx.exception))

    def test_an_unreachable_server_is_an_error_without_the_token(self):
        server, _, base = serve({})
        server.shutdown()
        server.server_close()
        with self.assertRaises(M.CheckError) as ctx:
            M.run_check(base, FAKE_TOKEN, M.make_opener(), TODAY)
        self.assertNotIn(FAKE_TOKEN, str(ctx.exception))


# ------------------------------------------------------------------------ main ----

class MainTests(unittest.TestCase):
    ENV = {"GITLAB_PERSONAL_ACCESS_TOKEN": FAKE_TOKEN}

    def opener(self, self_info=None, user_info=None):
        return FakeOpener({"/personal_access_tokens/self": json_body(self_info or good_self(
            expires_at=(dt.date.today() + dt.timedelta(days=30)).isoformat())),
            "/user": json_body(user_info or good_user())})

    def test_exit_0_when_the_token_is_narrow_and_short_lived(self):
        opener = self.opener()
        code, out, err = run_main([], self.ENV, opener)
        self.assertEqual((code, err), (0, ""))
        self.assertIn("result: ok", out)
        self.assertEqual([c[0] for c in opener.calls],
                         ["https://gitlab.com/api/v4/personal_access_tokens/self", "https://gitlab.com/api/v4/user"])
        self.assertTrue(all(c[1] == FAKE_TOKEN for c in opener.calls))

    def test_a_clean_result_never_claims_the_role_when_none_was_reported(self):
        code, out, _ = run_main([], self.ENV, self.opener())
        self.assertEqual(code, 0)
        self.assertIn("role: NOT checked", out)
        self.assertIn("Members page", out)
        self.assertIn("result: ok (scope, expiry and owner only; the role was not verified)", out)
        self.assertNotIn("result: ok\n", out)

    def test_a_reported_role_is_shown_and_the_result_is_plain_ok(self):
        code, out, _ = run_main([], self.ENV, self.opener(good_self(
            expires_at=(dt.date.today() + dt.timedelta(days=30)).isoformat(), access_level=30)))
        self.assertEqual(code, 0)
        self.assertNotIn("NOT checked", out)
        self.assertIn("role: level 30 as reported", out)
        self.assertIn("result: ok\n", out)

    def test_a_reported_high_role_is_a_warning_with_exit_1(self):
        code, out, _ = run_main([], self.ENV, self.opener(good_self(
            expires_at=(dt.date.today() + dt.timedelta(days=30)).isoformat(), access_level=40)))
        self.assertEqual(code, 1)
        self.assertIn("warning: the token carries a role above Developer", out)

    def test_the_role_line_is_printed_with_warnings_too(self):
        _, out, _ = run_main([], self.ENV, self.opener(good_self(scopes=["api", "sudo"], expires_at=None)))
        self.assertIn("role: NOT checked", out)
        self.assertIn("2 warning(s)", out)

    def test_mutation_proof_without_the_role_line_or_the_qualified_result_the_role_would_look_checked(self):
        no_line = mutated("        out.infos.append(ROLE_NOT_CHECKED)", "        pass")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            no_line.main([], environ=self.ENV, opener=self.opener())
        self.assertNotIn("role: NOT checked", out.getvalue())
        plain = mutated('    return "ok" if findings.role_checked else "ok (scope, expiry and owner only; the role was not verified)"',
                        '    return "ok"')
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            plain.main([], environ=self.ENV, opener=self.opener())
        self.assertIn("result: ok\n", out.getvalue())

    def test_an_unexpected_exception_exits_2_naming_only_the_type(self):
        from unittest import mock
        boom = TypeError("bad " + FAKE_TOKEN)
        with mock.patch.object(M, "run_check", side_effect=boom):
            code, out, err = run_main([], self.ENV, self.opener())
        self.assertEqual(code, 2)
        self.assertIn("unexpected error: TypeError", err)
        self.assertNotIn(FAKE_TOKEN, out + err)
        with mock.patch.object(M, "run_check", side_effect=RecursionError("x")):
            code, _, err = run_main([], self.ENV, self.opener())
        self.assertEqual((code, "unexpected error: RecursionError" in err), (2, True))

    def test_argument_errors_do_not_echo_the_arguments(self):
        for argv in (["--bogus", FAKE_TOKEN], [FAKE_TOKEN], ["--token-env"], ["--api-url=" + FAKE_TOKEN, "--zzz"]):
            with self.subTest(argv=argv):
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    with self.assertRaises(SystemExit) as ctx:
                        M.main(argv, environ=self.ENV, opener=self.opener())
                self.assertEqual(ctx.exception.code, 2)
                self.assertNotIn(FAKE_TOKEN, out.getvalue() + err.getvalue())

    def test_non_printable_server_text_is_replaced_in_the_output(self):
        nasty = "ev\u0085il\u202e\u2028x\u2029y\x1b[31m\u200bz"
        code, out, err = run_main([], self.ENV, self.opener(None, good_user(username=nasty)))
        self.assertEqual(code, 0)
        for ch in ("\u0085", "\u202e", "\u2028", "\u2029", "\x1b", "\u200b"):
            self.assertNotIn(ch, out + err)
        self.assertIn("token owner: ev?il?", out)
        # a legitimate non-ASCII username stays readable
        _, out, _ = run_main([], self.ENV, self.opener(None, good_user(username="J\u00fcrgen-bot")))
        self.assertIn("token owner: J\u00fcrgen-bot", out)

    def test_redaction_comes_before_the_cut_and_the_fold(self):
        reporter = M.Reporter(FAKE_TOKEN)
        self.assertEqual(reporter.clean("a" * 190 + FAKE_TOKEN), ("a" * 190 + "[redacted]")[:200])
        self.assertNotIn(FAKE_TOKEN[:10], reporter.clean("x" * 195 + FAKE_TOKEN))

    def test_mutation_proof_the_c1_and_bidi_characters_would_survive_a_c0_only_filter(self):
        mutant = mutated('        text = "".join(ch if ch.isprintable() else "?" for ch in text)',
                         '        text = M0.sub("?", text)')
        mutant.M0 = __import__("re").compile(r"[\x00-\x1f\x7f]")
        self.assertIn("\u202e", mutant.Reporter("").clean("a\u202eb"))
        self.assertNotIn("\u202e", M.Reporter("").clean("a\u202eb"))

    def test_a_failure_while_printing_is_exit_2_not_exit_1(self):
        class Broken(io.StringIO):
            def write(self, text):
                raise UnicodeEncodeError("ascii", text, 0, 1, "boom")

        err = io.StringIO()
        with contextlib.redirect_stdout(Broken()), contextlib.redirect_stderr(err):
            code = M.main([], environ=self.ENV, opener=self.opener(good_self(
                scopes=["api", "sudo"], expires_at=None)))
        self.assertEqual(code, 2)
        self.assertIn("unexpected error: UnicodeEncodeError", err.getvalue())
        self.assertNotIn(FAKE_TOKEN, err.getvalue())

    def test_a_broken_stderr_does_not_turn_the_error_into_a_traceback(self):
        class Broken(io.StringIO):
            def write(self, text):
                raise OSError("closed")

        with contextlib.redirect_stdout(Broken()), contextlib.redirect_stderr(Broken()):
            self.assertEqual(M.main([], environ=self.ENV, opener=self.opener()), 2)

    def test_mutation_proof_printing_outside_the_guard_would_exit_1(self):
        # the guard is the `except Exception` of main(); without it the exception propagates
        mutant = mutated("    except Exception as exc:  # noqa: BLE001 -- fail closed with the type only: a message could echo the token\n"
                         "        try:",
                         "    except ZeroDivisionError as exc:\n        try:")

        class Broken(io.StringIO):
            def write(self, text):
                raise UnicodeEncodeError("ascii", text, 0, 1, "boom")

        with contextlib.redirect_stdout(Broken()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(UnicodeEncodeError):
                mutant.main([], environ=self.ENV, opener=self.opener())

    def test_an_invalid_variable_name_flag_does_not_echo_it(self):
        code, out, err = run_main(["--token-env", FAKE_TOKEN + "!"], self.ENV, self.opener())
        self.assertEqual(code, 2)
        self.assertNotIn(FAKE_TOKEN, out + err)

    def test_exit_1_with_warnings(self):
        code, out, err = run_main([], self.ENV, self.opener(good_self(scopes=["api", "write_repository"], expires_at=None)))
        self.assertEqual(code, 1)
        self.assertIn("warning: scope(s) beyond", out)
        self.assertIn("warning: the token has no expiry", out)
        self.assertIn("2 warning(s)", out)

    def test_exit_2_on_errors(self):
        cases = {
            "no token": ({}, self.opener()),
            "http 401": (self.ENV, FakeOpener({"/personal_access_tokens/self": http_error(401)})),
            "unreachable": (self.ENV, FakeOpener({"/personal_access_tokens/self": urllib.error.URLError(ConnectionRefusedError())})),
            "revoked": (self.ENV, self.opener(good_self(revoked=True))),
            "not json": (self.ENV, FakeOpener({"/personal_access_tokens/self": b"nope"})),
        }
        for label, (environ, opener) in cases.items():
            with self.subTest(case=label):
                code, out, err = run_main([], environ, opener)
                self.assertEqual(code, 2)
                self.assertIn("error:", err)

    def test_the_token_never_appears_in_stdout_or_stderr(self):
        # even when GitLab echoes it back in a field that is printed, in an error body, or in a header value
        echoing_user = good_user(username=FAKE_TOKEN)
        for label, environ, opener in (
            ("success echo", self.ENV, self.opener(None, echoing_user)),
            ("warning path", self.ENV, self.opener(good_self(scopes=["write_repository"]), echoing_user)),
            ("http error", self.ENV, FakeOpener({"/personal_access_tokens/self": http_error(401)})),
            ("scope echo", self.ENV, self.opener(good_self(scopes=["api", FAKE_TOKEN]))),
        ):
            with self.subTest(case=label):
                code, out, err = run_main([], environ, opener)
                self.assertNotIn(FAKE_TOKEN, out)
                self.assertNotIn(FAKE_TOKEN, err)

    def test_mutation_proof_without_the_redaction_the_echo_would_be_printed(self):
        mutant = mutated('            text = text.replace(self._token, "[redacted]")', "            pass")
        out = io.StringIO()
        opener = FakeOpener({"/personal_access_tokens/self": json_body(good_self(expires_at=(dt.date.today() + dt.timedelta(days=30)).isoformat())),
                             "/user": json_body(good_user(username=FAKE_TOKEN))})
        with contextlib.redirect_stdout(out):
            mutant.main([], environ=self.ENV, opener=opener)
        self.assertIn(FAKE_TOKEN, out.getvalue())

    def test_the_token_from_a_file_is_not_printed_either(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t"
            path.write_text(FAKE_TOKEN + "\n", encoding="utf-8")
            path.chmod(0o600)
            code, out, err = run_main([], {"GITLAB_PERSONAL_ACCESS_TOKEN_FILE": str(path)}, self.opener())
        self.assertEqual(code, 0)
        self.assertIn("the file named by GITLAB_PERSONAL_ACCESS_TOKEN_FILE", out)
        self.assertNotIn(FAKE_TOKEN, out + err)

    def test_a_bad_target_stops_before_any_request_is_made(self):
        for argv, environ in (
            (["--api-url", "http://gitlab.com/api/v4"], self.ENV),
            (["--api-url", "https://evil.example/api/v4"], self.ENV),
            ([], {**self.ENV, "GITLAB_API_URL": "https://self-hosted.example/api/v4"}),
            (["--api-url", "https://user:x@gitlab.com/api/v4"], self.ENV),
        ):
            with self.subTest(argv=argv):
                opener = self.opener()
                code, out, err = run_main(argv, environ, opener)
                self.assertEqual(code, 2)
                self.assertEqual(opener.calls, [], "the token was sent to an unvalidated target")
                self.assertNotIn(FAKE_TOKEN, out + err)

    def test_a_self_hosted_instance_needs_the_explicit_host_pin(self):
        opener = self.opener()
        code, _, _ = run_main(["--api-url", "https://git.example.org/api/v4", "--expected-host", "git.example.org"],
                              self.ENV, opener)
        self.assertEqual(code, 0)
        self.assertEqual(opener.calls[0][0], "https://git.example.org/api/v4/personal_access_tokens/self")

    def test_mutation_proof_https_only_guard(self):
        # Two independent lines refuse plain http (the prefix test and the parsed scheme); the proof removes both.
        text = SCRIPT.read_text(encoding="utf-8")
        for old, new in (('    if not api_url.startswith("https://"):', "    if False:"),
                         ('    if parts.scheme != "https" or not parts.hostname:', "    if not parts.hostname:")):
            self.assertEqual(text.count(old), 1)
            text = text.replace(old, new)
        mutant = load_module(text, "check_gitlab_token_mutant")
        self.assertIsNone(mutant.api_url_problem("http://gitlab.com/api/v4", "gitlab.com"))
        self.assertIsNotNone(M.api_url_problem("http://gitlab.com/api/v4", "gitlab.com"))

    def test_mutation_proof_host_pin_guard(self):
        mutant = mutated("    if parts.hostname.lower() != expected_host.lower():", "    if False:")
        self.assertIsNone(mutant.api_url_problem("https://evil.example/api/v4", "gitlab.com"))
        self.assertIsNotNone(M.api_url_problem("https://evil.example/api/v4", "gitlab.com"))

    def test_mutation_proof_scope_and_expiry_guards(self):
        scope = mutated('ACCEPTED_SCOPES = frozenset({"api", "read_api"})',
                        'ACCEPTED_SCOPES = frozenset({"api", "read_api", "read_user", "write_repository"})')
        self.assertEqual(scope.analyse(good_self(scopes=["api", "write_repository"]), good_user(), TODAY).warnings, [])
        self.assertTrue(M.analyse(good_self(scopes=["api", "write_repository"]), good_user(), TODAY).warnings)
        expiry = mutated("    elif days > MAX_EXPIRY_DAYS:", "    elif days > MAX_EXPIRY_DAYS + 1000:")
        long_lived = good_self(expires_at=(TODAY + dt.timedelta(days=365)).isoformat())
        self.assertEqual(expiry.analyse(long_lived, good_user(), TODAY).warnings, [])
        self.assertTrue(M.analyse(long_lived, good_user(), TODAY).warnings)


# ------------------------------------------------------------------ static / CLI ----

class ScriptShapeTests(unittest.TestCase):
    def test_standard_library_only(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        self.assertTrue(names <= set(sys.stdlib_module_names) | {"__future__"}, sorted(names - set(sys.stdlib_module_names)))

    def test_the_script_is_executable_and_has_a_shebang(self):
        self.assertTrue(SCRIPT.stat().st_mode & stat.S_IXUSR)
        self.assertEqual(SCRIPT.read_text(encoding="utf-8").splitlines()[0], "#!/usr/bin/env python3")

    def test_no_function_exceeds_the_50_line_standard(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.assertLessEqual(node.end_lineno - node.lineno + 1, 50, node.name)
                if node.name != "redirect_request":  # the signature of urllib's HTTPRedirectHandler override
                    self.assertLessEqual(len(node.args.args) + len(node.args.kwonlyargs), 4, node.name)

    def test_cli_exit_2_on_a_plain_http_api_url(self):
        env = {"PATH": os.environ.get("PATH", ""), "GITLAB_PERSONAL_ACCESS_TOKEN": "", "GITLAB_API_URL": "http://127.0.0.1:9/api/v4"}
        proc = subprocess.run([sys.executable, str(SCRIPT)], env=env, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("invalid API URL", proc.stderr)

    def test_cli_with_a_token_in_the_environment_never_echoes_it(self):
        env = {"PATH": os.environ.get("PATH", ""), "GITLAB_PERSONAL_ACCESS_TOKEN": FAKE_TOKEN,
               "GITLAB_API_URL": "https://git.example.org/api/v4"}
        proc = subprocess.run([sys.executable, str(SCRIPT)], env=env, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 2)  # host is not the pinned gitlab.com: refused before any request
        self.assertNotIn(FAKE_TOKEN, proc.stdout + proc.stderr)
        self.assertIn("not the expected GitLab host", proc.stderr)


if __name__ == "__main__":
    unittest.main()
