"""`security-audit` MCP server -- the sole subprocess choke point.

This is the ONLY module in this package that ever calls `subprocess.run`. `commands.py`
only builds Python list literals and validated path strings; it performs no subprocess
I/O. `audit_server.py`'s four tool handlers do nothing but call one
`commands.build_*_argv()` function, then call `run_fixed_argv()` below, then return the
result. This means an adversarial parameter value can only ever influence the *value* of
one pre-determined `argv` element -- it can never influence `argv`'s length, order, the
command name at `argv[0]`, or whether `shell=True` is used, because `shell=False` is set
in exactly one place, right here, and nowhere else in this package.

Implements `security-engineer-audit-server-design-v1.md` §4.2's code sketch, with two
disclosed additions beyond that sketch (both required by `task-T497.md`'s own
Constraints, not style preferences):

1. **`FileNotFoundError` handling.** The design's own §4.2 sketch only catches
   `subprocess.TimeoutExpired`; it does not handle the case where the target executable
   (`npm`, `pip-audit`, `dotnet`, `rg`) is not installed at all. §6 item 4 of the design
   explicitly flags binary availability as "not verified... assumed, not verified", and
   `task-T497.md`'s Constraints section requires this to "surface a clear, structured
   error ... not an unhandled crash." `pip-audit` is confirmed absent in this session's
   own environment, so this path is exercised for real by this package's own test suite
   (see `tests/functional/test_audit_server.py`), not merely theorized.
2. **Output truncation.** §6 item 3 names truncation policy as "recommended: cap and flag
   `truncated: true`, never silently drop" but explicitly leaves it unspecified. This
   module adopts a 200,000-character cap per stream (`MAX_OUTPUT_CHARS`) -- large enough
   to hold any of the four tools' realistic JSON audit output, small enough to bound
   worst-case memory/response size -- and reports `stdout_truncated`/`stderr_truncated`
   booleans rather than silently dropping data. This is exactly the kind of "starting
   point, not a specification to build byte-for-byte" adjustment §6 item 3 anticipates;
   disclosed here rather than silently invented.

T714 (SEV-T690-04 (a)): the child tools no longer inherit the server's whole environment.
`child_env()` builds an allowlisted one, in the pattern of `git_executor.git_env()`: only
`CHILD_ENV_NAMES` that are set are passed (search path, home and temporary directory, locale,
proxy and CA-certificate variables, and the few Windows and .NET variables those tools need to
start). A token or key exported to the client (for example `GITLAB_PERSONAL_ACCESS_TOKEN`) no
longer reaches `npm`, `pip-audit`, `dotnet` or `rg`. `HOME` is kept because `npm` and `pip-audit`
keep their caches and their own configuration there; a registry credential in `~/.npmrc` is
therefore still read by `npm` (that file is the user's, not the server's). A proxy URL can carry
a password; it is passed because the audits need the network through it.

SEC-T714-01: the allowlist also passes the non-secret pointers to the tools' own configuration
(`PIP_CONFIG_FILE`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `NPM_CONFIG_USERCONFIG`,
`NPM_CONFIG_GLOBALCONFIG` and their lowercase npm forms, `NUGET_PACKAGES`) and always sets
`DOTNET_CLI_TELEMETRY_OPTOUT=1` and `DOTNET_NOLOGO=1`. A package-index setting made only in the
environment is NOT passed, because it can carry a credential, and it is not silently dropped
either: dropping `PIP_INDEX_URL` would make `pip-audit -r` (which resolves like `pip install -r`)
fall back to public PyPI, a dependency-confusion path, and dropping `npm_config_registry` would send
the dependency list to the public registry. `index_override_error()` therefore refuses to run
`pip-audit` while `PIP_INDEX_URL`, `PIP_EXTRA_INDEX_URL` or `PIP_FIND_LINKS` (or a `PIP_AUDIT_`
form of them) is set, and `npm` while any `npm_config_*registry` variable (any case, scoped
registries included) is set; the error names the variable, never its value, and says to move the
setting into `pip.conf` / `.npmrc`. NuGet needs no such guard: its package sources are defined in
`NuGet.Config` files, not in environment variables, which carry only credentials
(`NuGetPackageSourceCredentials_<source>`) and paths; dropping a credential makes a private feed
fail with an authentication error instead of switching to another source.
"""
from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Mapping

DEFAULT_TIMEOUT_SECONDS = 30  # §6 item 3: a starting-point default, not load-bearing for
                               # the injection defense itself.
MAX_OUTPUT_CHARS = 200_000     # disclosed addition -- see module docstring, item 2.
_DEFAULT_PATH = "/usr/local/bin:/usr/bin:/bin"

# T714 (SEV-T690-04 (a)): the only variables a child tool receives, each only when it is set.
CHILD_ENV_NAMES = (
    "PATH", "HOME", "TMPDIR", "TEMP", "TMP",
    "LANG", "LANGUAGE", "LC_ALL", "LC_CTYPE", "LC_MESSAGES",
    "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "no_proxy", "all_proxy",
    "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "NODE_EXTRA_CA_CERTS",
    "SYSTEMROOT", "COMSPEC", "PATHEXT", "USERPROFILE", "APPDATA", "LOCALAPPDATA",
    "DOTNET_ROOT", "DOTNET_CLI_HOME",
    # SEC-T714-01: non-secret pointers to the tools' own configuration and caches
    "PIP_CONFIG_FILE", "XDG_CONFIG_HOME", "XDG_CACHE_HOME",
    "NPM_CONFIG_USERCONFIG", "NPM_CONFIG_GLOBALCONFIG", "npm_config_userconfig", "npm_config_globalconfig",
    "NUGET_PACKAGES",
)
CHILD_ENV_FIXED = {"DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"}  # always set (SEC-T714-01)

# SEC-T714-01: variables that redirect the package index (and can carry a credential). While one is
# set in the server's environment, the matching tool is refused instead of run without it.
_PIP_INDEX_RE = re.compile(r"PIP_(AUDIT_)?(INDEX_URL|EXTRA_INDEX_URL|FIND_LINKS)", re.IGNORECASE)
_NPM_REGISTRY_RE = re.compile(r"npm_config_.*registry", re.IGNORECASE)
_INDEX_GUARDS = {
    "pip-audit": (_PIP_INDEX_RE, "pip.conf (PIP_CONFIG_FILE)"),
    "npm": (_NPM_REGISTRY_RE, ".npmrc"),
}


def child_env(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """The complete environment of a child tool: the set `CHILD_ENV_NAMES`, nothing else."""
    source = os.environ if environ is None else environ
    env = {name: source[name] for name in CHILD_ENV_NAMES if source.get(name)}
    env.setdefault("PATH", _DEFAULT_PATH)
    env.update(CHILD_ENV_FIXED)
    return env


def index_override_error(argv: list[str], environ: Mapping[str, str] | None = None) -> str | None:
    """Why `argv` must not run while the server's environment redirects its package index, or None.

    The message names the variables, never their values (SEC-T714-01)."""
    guard = _INDEX_GUARDS.get(os.path.basename(argv[0])) if argv else None
    if guard is None:
        return None
    pattern, home = guard
    source = os.environ if environ is None else environ
    names = sorted(name for name in source if pattern.fullmatch(name))
    if not names:
        return None
    return (f"refused: {', '.join(names)} is set in the server's environment; the audit runs with an "
            "allowlisted environment that does not pass package-index settings, so it could resolve "
            f"against the public index instead. Move the setting into {home}, unset the variable and restart "
            "the server")


def run_fixed_argv(
    argv: list[str],
    cwd: str | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict:
    """The only call to `subprocess.run` anywhere in this package. `shell` is never a
    parameter here -- it is hardcoded `False`, permanently, so no caller (even a future
    maintainer editing this file) can accidentally flip it per-call. `check=False` is
    required, not optional: `npm audit`, `pip-audit`, and `dotnet list ... --vulnerable`
    all use a non-zero exit code to signal "vulnerabilities were found," the expected,
    successful-audit outcome, not an execution error.
    """
    refused = index_override_error(argv)
    if refused:
        return {"timed_out": False, "error": refused, "argv": argv}
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            env=child_env(),
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"timed_out": True, "error": None, "argv": argv}
    except FileNotFoundError as exc:
        return {
            "timed_out": False,
            "error": f"executable not found: {exc.filename or argv[0]!r}",
            "argv": argv,
        }
    stdout, stdout_truncated = _truncate(result.stdout)
    stderr, stderr_truncated = _truncate(result.stderr)
    return {
        "exit_code": result.returncode,
        "stdout": stdout,
        "stdout_truncated": stdout_truncated,
        "stderr": stderr,
        "stderr_truncated": stderr_truncated,
        "timed_out": False,
        "error": None,
    }


def _truncate(text: str) -> tuple[str, bool]:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text, False
    return text[:MAX_OUTPUT_CHARS], True
