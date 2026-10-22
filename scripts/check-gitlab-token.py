#!/usr/bin/env python3
"""Check that the GitLab token the MCP server uses is as weak as the harness needs (T665, SEC-T660-01).

``docs/artifacts/gitlab-token-handling-design-v1.md`` (R1) turns "use a least-privilege token" from
advice into a check. The script reads the token the way the pinned ``@zereight/mcp-gitlab@2.2.5`` does
(a non-empty ``GITLAB_PERSONAL_ACCESS_TOKEN`` wins, else the file named by
``GITLAB_PERSONAL_ACCESS_TOKEN_FILE``), asks GitLab two questions and prints findings. It is
standard-library only and read-only: two ``GET`` requests, nothing is created, changed or revoked.

  GET <api>/personal_access_tokens/self   scopes (or granular_scopes), expiry, revoked/active
  GET <api>/user                          owner: bot, administrator, state

Findings (exit code 1 when any warning is printed):
  - a scope outside ``api``, ``read_api`` (``read_user``, ``write_repository``, ``ai_features``,
    ``sudo``, ``admin_mode``, ``create_runner`` ...): the roles need ``api`` and nothing else;
  - no expiry, or an expiry more than 90 days away;
  - the owner is an instance administrator, or is not active;
  - a role above Developer, when a response carries one (``access_level`` or ``role``);
  - a token file that group or others can read; both the variable and the file set (the server then
    uses the variable and only warns).
The role is NOT checked in the usual case: the two endpoints above are not documented to report it.
The script then always prints "role: NOT checked ..." (verify Planner, Reporter or Developer in the
project's Members page) and ends with "result: ok (scope, expiry and owner only; the role was not
verified)": a clean result never claims the role. That line is information, not a warning, so the
exit code stays 0; only a role that was seen and is too high produces a warning.
Exit codes: 0 ok, 1 warnings, 2 error (no token, bad target, unreachable, rejected, revoked, reply
that is not JSON, any unexpected failure; the message names the exception type only).
The token file is opened once without following a symbolic link or blocking on a FIFO, must be a
regular file owned by the current user and at most 4096 bytes; a mode wider than 0600 is a warning.
The token must be printable ASCII without spaces (a leading BOM is stripped like the server's trim).

Safety properties (each has a test with a mutation proof):
  - the token is never printed or logged: only fixed fields are printed, any server-provided text is
    stripped of control characters and the token value is replaced by ``[redacted]``; no argv value
    holds the token (the variable NAME is a flag, the value is not);
  - the target is parsed, not prefix-matched (the idea of ``validate_api_target`` of
    ``scripts/publish-release.py``): https only, a host name, no user information, no query or
    fragment, a clean ``.../api/v4`` path, and the host pinned (``--expected-host``, else
    ``CI_SERVER_HOST``, else ``gitlab.com``), so a wrong ``GITLAB_API_URL`` never receives the token;
  - the HTTP opener refuses every redirect, so ``PRIVATE-TOKEN`` is never re-sent to a second location;
  - the reply is size-limited and parsed as JSON; an error body is never printed.

This script is NOT run against GitLab by the harness's agents (an agent holds no token). The user runs
it with the token the MCP server will use; the live checks of the design (section 8.4) stay the
user's.
"""

from __future__ import annotations

import argparse
import datetime as dt
import http.client
import json
import os
import re
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Mapping, Sequence

EXIT_OK = 0
EXIT_WARNINGS = 1
EXIT_ERROR = 2

DEFAULT_TOKEN_ENV = "GITLAB_PERSONAL_ACCESS_TOKEN"
DEFAULT_FILE_ENV = "GITLAB_PERSONAL_ACCESS_TOKEN_FILE"
DEFAULT_API_URL = "https://gitlab.com/api/v4"
DEFAULT_HOST = "gitlab.com"
MAX_EXPIRY_DAYS = 90
MAX_ROLE_LEVEL = 30  # Developer; 40 is Maintainer, 50 is Owner
ACCEPTED_SCOPES = frozenset({"api", "read_api"})
ROLE_LEVELS = {"guest": 10, "planner": 15, "reporter": 20, "developer": 30, "maintainer": 40, "owner": 50}
HTTP_TIMEOUT_SECONDS = 15
MAX_REPLY_BYTES = 1_000_000
MAX_TOKEN_FILE_BYTES = 4096
PREFIX = "gitlab-token-check"
ROLE_NOT_CHECKED = (
    "role: NOT checked (the endpoints do not report it); verify Planner, Reporter or Developer "
    "in the project's Members page"
)

ENV_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
HOST_RE = re.compile(r"[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")
TOKEN_TEXT_RE = re.compile(r"[\x21-\x7e]+")
# The only API base shape: .../api/v4. A segment is never "." or "..".
API_PATH_RE = re.compile(r"(/(?!\.{1,2}(?:/|$))[A-Za-z0-9._~-]+)*/api/v4")


class CheckError(RuntimeError):
    """A condition that stops the check (exit code 2). The message never holds the token."""


@dataclass
class TokenSource:
    """Where the token came from and what was noticed while reading it (never the value in a message)."""

    token: str
    description: str
    warnings: list[str] = field(default_factory=list)

    def __repr__(self) -> str:  # a stray print() or traceback must not show the value
        return f"TokenSource(description={self.description!r}, token=<redacted>)"


@dataclass
class Findings:
    role_checked: bool = True  # False when no response carried a role (the usual case)
    infos: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------- target ----

def api_url_problem(api_url: str, expected_host: str) -> str | None:
    """Return why ``api_url`` is not an acceptable API base for the token, or None when it is."""
    if not api_url.startswith("https://"):
        return "must start with https://"
    if any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 or ch == "\\" for ch in api_url):
        return "must not contain whitespace, control characters or backslashes"
    try:
        parts = urllib.parse.urlsplit(api_url)
        parts.port  # noqa: B018 -- raises ValueError on a malformed or out-of-range port
    except ValueError:
        return "is not a valid URL"
    if parts.scheme != "https" or not parts.hostname:
        return "must be an https URL with a host name"
    if "@" in parts.netloc or parts.username is not None or parts.password is not None:
        return "must not contain user information"
    if parts.query or parts.fragment or "?" in api_url or "#" in api_url:
        return "must not contain a query or a fragment"
    if not API_PATH_RE.fullmatch(parts.path):
        return "must end with /api/v4"
    if parts.hostname.lower() != expected_host.lower():
        return (f"host {parts.hostname.lower()!r} is not the expected GitLab host {expected_host.lower()!r}; "
                "pass --expected-host if this is the instance the token belongs to")
    return None


def resolve_expected_host(flag: str | None, environ: Mapping[str, str]) -> str:
    """``--expected-host``, else ``$CI_SERVER_HOST``, else ``gitlab.com``; an empty value is an error."""
    host = flag if flag is not None else environ.get("CI_SERVER_HOST", DEFAULT_HOST)
    host = host.strip()
    if not host or not HOST_RE.fullmatch(host):
        raise CheckError("invalid --expected-host: must be a host name")
    return host


def resolve_api_url(flag: str | None, environ: Mapping[str, str]) -> str:
    """``--api-url``, else ``$GITLAB_API_URL``, else the gitlab.com API; one trailing slash is dropped."""
    url = flag if flag is not None else (environ.get("GITLAB_API_URL") or DEFAULT_API_URL)
    return url.strip().removesuffix("/")


def validate_target(api_url: str, expected_host: str) -> None:
    problem = api_url_problem(api_url, expected_host)
    if problem:
        raise CheckError(f"invalid API URL: {problem}")


# ----------------------------------------------------------------- token ----

def _env_name(value: str, flag: str) -> str:
    if not ENV_NAME_RE.fullmatch(value):
        raise CheckError(f"invalid {flag}: must be an environment variable name")
    return value


def _open_token_file(path: str, file_env: str) -> int:
    """Open once, without following a symbolic link and without blocking on a FIFO or device."""
    flags = os.O_RDONLY
    for name in ("O_NOFOLLOW", "O_NONBLOCK", "O_CLOEXEC"):
        flags |= getattr(os, name, 0)
    try:
        return os.open(path, flags)
    except OSError as exc:
        raise CheckError(
            f"cannot open the token file named by {file_env} (a symbolic link is refused): {type(exc).__name__}"
        ) from exc


def _read_token_file(path: str, file_env: str) -> tuple[str, list[str]]:
    """Read the token file through ONE descriptor: regular file, owned by the current user, size-capped."""
    warnings: list[str] = []
    fd = _open_token_file(path, file_env)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise CheckError(f"the token file named by {file_env} is not a regular file")
        if hasattr(os, "geteuid") and info.st_uid != os.geteuid():
            raise CheckError(f"the token file named by {file_env} is not owned by the current user")
        if info.st_mode & 0o077:
            warnings.append(
                f"the token file is accessible by group or others (mode {stat.S_IMODE(info.st_mode):04o}); "
                "use chmod 600"
            )
        data = os.read(fd, MAX_TOKEN_FILE_BYTES + 1)
    except OSError as exc:
        raise CheckError(f"cannot read the token file named by {file_env}: {type(exc).__name__}") from exc
    finally:
        os.close(fd)
    if len(data) > MAX_TOKEN_FILE_BYTES:
        raise CheckError(f"the token file named by {file_env} is larger than {MAX_TOKEN_FILE_BYTES} bytes")
    try:
        return data.decode("utf-8").lstrip("\ufeff").strip(), warnings
    except UnicodeDecodeError as exc:
        raise CheckError(f"the token file named by {file_env} is not UTF-8 text") from exc


def _check_token_text(token: str, description: str) -> None:
    """The token is non-empty printable ASCII without a space (it goes into an HTTP header)."""
    if not token:
        raise CheckError(f"the token read from {description} is empty")
    if not TOKEN_TEXT_RE.fullmatch(token):
        raise CheckError(
            f"the token read from {description} contains a character outside printable ASCII "
            "(a control character, a space or a non-ASCII character)"
        )


def load_token(token_env: str, file_env: str, environ: Mapping[str, str]) -> TokenSource:
    """Read the token like the pinned server: a non-empty variable first, else the file.

    Messages name the variable or the flag, never the value.
    """
    token_env = _env_name(token_env, "--token-env")
    file_env = _env_name(file_env, "--token-file-env")
    inline = environ.get(token_env, "").lstrip("\ufeff").strip()
    path = environ.get(file_env, "").strip()
    warnings: list[str] = []
    if inline:
        if path:
            warnings.append(
                f"both {token_env} and {file_env} are set: the server uses the variable and ignores the "
                f"file; remove the export of {token_env} to use the file"
            )
        token, description = inline, f"environment variable {token_env}"
    elif path:
        token, file_warnings = _read_token_file(path, file_env)
        warnings.extend(file_warnings)
        description = f"the file named by {file_env}"
    else:
        raise CheckError(f"no token: {token_env} is empty or unset and {file_env} is not set")
    _check_token_text(token, description)
    return TokenSource(token=token, description=description, warnings=warnings)


# ------------------------------------------------------------------ HTTP ----

class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect: urllib would re-send ``PRIVATE-TOKEN`` to the new location."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None  # the caller then sees the 3xx as an HTTPError


def make_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(_RefuseRedirects)


def api_get(opener, url: str, token: str, label: str) -> dict:
    """GET ``url`` with the token; return the parsed JSON object. Errors name the endpoint and the status only."""
    request = urllib.request.Request(url=url, method="GET")
    request.add_header("PRIVATE-TOKEN", token)
    request.add_header("Accept", "application/json")
    try:
        with opener.open(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            raw = response.read(MAX_REPLY_BYTES + 1)
    except urllib.error.HTTPError as exc:  # includes a refused redirect (3xx)
        exc.close()  # the body is never read or printed
        if 300 <= exc.code < 400:
            raise CheckError(f"GET {label} answered with a redirect (HTTP {exc.code}); redirects are refused") from exc
        raise CheckError(f"GET {label} failed: HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise CheckError(f"GET {label} is unreachable: {type(exc.reason).__name__}") from exc
    except (OSError, http.client.HTTPException) as exc:
        raise CheckError(f"GET {label} failed: {type(exc).__name__}") from exc
    if len(raw) > MAX_REPLY_BYTES:
        raise CheckError(f"GET {label} answered with more than {MAX_REPLY_BYTES} bytes")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise CheckError(f"GET {label} did not answer with JSON") from exc
    if not isinstance(data, dict):
        raise CheckError(f"GET {label} did not answer with a JSON object")
    return data


# -------------------------------------------------------------- analysis ----

def _parse_date(value: object) -> dt.date | None:
    if not isinstance(value, str) or len(value) < 10:
        return None
    try:
        return dt.date.fromisoformat(value[:10])
    except ValueError:
        return None


def _check_scopes(self_info: Mapping, out: Findings) -> None:
    scopes = self_info.get("scopes")
    granular = self_info.get("granular_scopes")
    if granular:
        out.infos.append("fine-grained token: its permission rows are not evaluated by this script; "
                         "compare them with the table in docs/wiki/mcp-servers.md")
    if not isinstance(scopes, list) or not all(isinstance(s, str) for s in scopes):
        if not granular:
            out.warnings.append("the token's scope list was not reported; its power is unknown")
        return
    out.infos.append("scopes: " + (", ".join(sorted(scopes)) or "(none)"))
    extra = sorted(set(scopes) - ACCEPTED_SCOPES)
    if extra:
        out.warnings.append(
            f"scope(s) beyond api, read_api: {', '.join(extra)}; the roles need 'api' and nothing "
            "more: create a token without them"
        )


def _check_expiry(self_info: Mapping, today: dt.date, out: Findings) -> None:
    raw = self_info.get("expires_at")
    if raw in (None, ""):
        out.warnings.append(f"the token has no expiry; use at most {MAX_EXPIRY_DAYS} days")
        return
    expires = _parse_date(raw)
    if expires is None:
        out.warnings.append("the token's expiry date could not be read")
        return
    days = (expires - today).days
    out.infos.append(f"expires: {expires.isoformat()} (in {days} days)")
    if days < 0:
        out.errors.append("the token has expired")
    elif days > MAX_EXPIRY_DAYS:
        out.warnings.append(f"the token expires in {days} days; use at most {MAX_EXPIRY_DAYS} days")


def _role_level(*sources: Mapping) -> int | None:
    """The highest role a response carries (``access_level`` as a number, ``role`` as a name), or None."""
    levels: list[int] = []
    for info in sources:
        level = info.get("access_level")
        if isinstance(level, int) and not isinstance(level, bool):
            levels.append(level)
        role = info.get("role")
        if isinstance(role, str) and role.lower() in ROLE_LEVELS:
            levels.append(ROLE_LEVELS[role.lower()])
    return max(levels) if levels else None


def _check_owner(self_info: Mapping, user_info: Mapping, out: Findings) -> None:
    if self_info.get("revoked") is True or self_info.get("active") is False:
        out.errors.append("the token is revoked or not active")
    if user_info.get("bot") is True:
        out.infos.append("the owner is a bot user (project or group access token)")
    if user_info.get("is_admin") is True:
        out.warnings.append("the token's owner is an instance administrator; use a dedicated low-role user")
    state = user_info.get("state")
    if isinstance(state, str) and state != "active":
        out.warnings.append(f"the token owner's state is {state!r}, not 'active'")
    level = _role_level(self_info, user_info)
    if level is None:
        out.role_checked = False
        out.infos.append(ROLE_NOT_CHECKED)
    elif level > MAX_ROLE_LEVEL:
        out.warnings.append("the token carries a role above Developer; use Developer at most, Planner or Reporter where enough")
    else:
        out.infos.append(f"role: level {level} as reported (Developer is 30)")


def analyse(self_info: Mapping, user_info: Mapping, today: dt.date) -> Findings:
    """Turn the two replies into findings. Pure: no I/O, no token."""
    out = Findings()
    _check_scopes(self_info, out)
    _check_expiry(self_info, today, out)
    _check_owner(self_info, user_info, out)
    return out


# ---------------------------------------------------------------- output ----

class Reporter:
    """Prints findings; every line is cleaned and the token value can never appear in it."""

    def __init__(self, token: str) -> None:
        self._token = token

    def clean(self, text: str) -> str:
        """Redact the token first, then replace every non-printable character (C0/C1 controls, bidi
        overrides, line and paragraph separators, unassigned code points), then cut."""
        if self._token:
            text = text.replace(self._token, "[redacted]")
        text = "".join(ch if ch.isprintable() else "?" for ch in text)
        return text[:200]

    def line(self, text: str, level: str = "") -> None:
        label = f"{level}: " if level else ""
        stream = sys.stderr if level == "error" else sys.stdout  # looked up per call, so redirects work
        print(f"{PREFIX}: {label}{self.clean(text)}", file=stream)


def _result_text(findings: Findings) -> str:
    """`ok` is only claimed for what was checked: scope, expiry and owner, and the role only if it was seen."""
    if findings.warnings:
        return f"{len(findings.warnings)} warning(s)"
    return "ok" if findings.role_checked else "ok (scope, expiry and owner only; the role was not verified)"


def _server_text(info: Mapping, key: str) -> str:
    value = info.get(key)
    return value if isinstance(value, str) else "(not reported)"


def run_check(api_url: str, token: str, opener, today: dt.date) -> tuple[Findings, Mapping]:
    """Ask GitLab the two questions. The caller has validated ``api_url`` (https, pinned host)."""
    self_info = api_get(opener, f"{api_url}/personal_access_tokens/self", token, "/personal_access_tokens/self")
    user_info = api_get(opener, f"{api_url}/user", token, "/user")
    return analyse(self_info, user_info, today), user_info


class _QuietParser(argparse.ArgumentParser):
    """argparse echoes unknown arguments; a token passed by mistake must not reach the terminal."""

    def error(self, message: str):  # noqa: D401
        print(f"{PREFIX}: error: invalid arguments (the values are not echoed); see --help", file=sys.stderr)
        raise SystemExit(EXIT_ERROR)


def build_parser() -> argparse.ArgumentParser:
    parser = _QuietParser(description="Check the GitLab token of the MCP server (read-only).")
    parser.add_argument("--token-env", default=DEFAULT_TOKEN_ENV,
                        help=f"NAME of the variable that holds the token (default {DEFAULT_TOKEN_ENV}); not the token")
    parser.add_argument("--token-file-env", default=DEFAULT_FILE_ENV,
                        help=f"NAME of the variable that holds the token file path (default {DEFAULT_FILE_ENV})")
    parser.add_argument("--api-url", default=None, help="API base, https://<host>/api/v4 (default $GITLAB_API_URL, else gitlab.com)")
    parser.add_argument("--expected-host", default=None, help="the only host that may receive the token (default $CI_SERVER_HOST, else gitlab.com)")
    return parser


def _prepare(args: argparse.Namespace, environ: Mapping[str, str]) -> tuple[str, TokenSource]:
    host = resolve_expected_host(args.expected_host, environ)
    api_url = resolve_api_url(args.api_url, environ)
    validate_target(api_url, host)
    return api_url, load_token(args.token_env, args.token_file_env, environ)


def _report(reporter: Reporter, source: TokenSource, findings: Findings, user: Mapping) -> int:
    reporter.line(f"token owner: {_server_text(user, 'username')}")
    findings.warnings[:0] = source.warnings
    for text in findings.infos:
        reporter.line(text)
    for text in findings.warnings:
        reporter.line(text, "warning")
    for text in findings.errors:
        reporter.line(text, "error")
    if findings.errors:
        return EXIT_ERROR
    reporter.line("result: " + _result_text(findings))
    return EXIT_WARNINGS if findings.warnings else EXIT_OK


def _run(args: argparse.Namespace, environ: Mapping[str, str], opener) -> int:
    reporter = Reporter("")
    try:
        api_url, source = _prepare(args, environ)
        reporter = Reporter(source.token)
        reporter.line(f"token source: {source.description}")
        reporter.line(f"GitLab API: {api_url}")
        findings, user = run_check(api_url, source.token, opener or make_opener(), dt.date.today())
    except CheckError as exc:
        reporter.line(str(exc), "error")
        return EXIT_ERROR
    return _report(reporter, source, findings, user)


def main(argv: Sequence[str] | None = None, environ: Mapping[str, str] | None = None, opener=None) -> int:
    """Run the check. ANY exception, including one raised while printing, is exit 2, never exit 1."""
    environ = os.environ if environ is None else environ
    args = build_parser().parse_args(argv)
    try:
        return _run(args, environ, opener)
    except Exception as exc:  # noqa: BLE001 -- fail closed with the type only: a message could echo the token
        try:
            print(f"{PREFIX}: error: unexpected error: {type(exc).__name__}", file=sys.stderr)
        except Exception:  # noqa: BLE001 -- stderr itself is broken; the exit code still says error
            pass
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
