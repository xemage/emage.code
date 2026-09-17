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
"""
from __future__ import annotations

import subprocess

DEFAULT_TIMEOUT_SECONDS = 30  # §6 item 3: a starting-point default, not load-bearing for
                               # the injection defense itself.
MAX_OUTPUT_CHARS = 200_000     # disclosed addition -- see module docstring, item 2.


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
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
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
