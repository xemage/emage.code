"""`poc-security-audit` MCP server -- the sole subprocess choke point (T603).

Implements `docs/artifacts/poc-security-engineer-tool-scoping-v2.md` §3.1 ("Executor",
"Argv", "Environment"). This is the ONLY module of the new server that spawns a process.
It differs from `executor.py` (which the four-tool `security-audit` server keeps unchanged)
in exactly the ways v2 requires:

* explicit, minimal subprocess environment (nothing inherited);
* every git argv starts with the hardening prefix (no fsmonitor, pager or hooks from a
  repository's own config);
* stdout is read through a bounded streaming loop (never `capture_output`);
* one aggregate `Deadline` covers every subprocess of a tool call;
* stderr is sent to /dev/null and never returned; no argv is ever returned.
"""
from __future__ import annotations

import os
import selectors
import signal
import subprocess
import time
from dataclasses import dataclass

# git's empty tree: attributes are read from it, not from the repository's .gitattributes.
# `--attr-source` needs git >= 2.40; an older git exits non-zero and every call then fails
# closed as `git_failed` (never a silent fallback). `.git/info/attributes` is NOT covered by
# it (verified on git 2.43.0), which is why git grep/log also run with `-a` / `--text`.
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
HARDENING = (
    f"--attr-source={EMPTY_TREE}",
    "-c", "core.fsmonitor=false",
    "-c", "core.pager=cat",
    "-c", "core.hooksPath=/dev/null",
    "-c", "color.ui=false",
    "-c", "color.grep=false",
    "-c", "log.showSignature=false",
    "-c", "gpg.program=/bin/false",
)
LOG_FLAGS = ("--no-textconv", "--no-ext-diff", "--no-show-signature", "--text")
_DEFAULT_PATH = "/usr/local/bin:/usr/bin:/bin"
_CHUNK = 65536

ERR_TIMEOUT = "timeout"
ERR_GIT_MISSING = "git_missing"
ERR_GIT_FAILED = "git_failed"


def git_env() -> dict[str, str]:
    """The complete subprocess environment. Nothing else is inherited."""
    return {
        "PATH": os.environ.get("PATH") or _DEFAULT_PATH,
        "HOME": "/nonexistent",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C",
    }


def git_argv(root: str, *args: str) -> list[str]:
    """`git -C <root> <hardening> <args...>` as a fixed argv list."""
    return ["git", "-C", root, *HARDENING, *args]


class Deadline:
    """One wall-clock budget shared by every subprocess of a single tool call."""

    def __init__(self, seconds: float) -> None:
        self._end = time.monotonic() + seconds

    def remaining(self) -> float:
        return self._end - time.monotonic()


@dataclass(frozen=True)
class GitResult:
    stdout: bytes
    truncated: bool
    error: str | None  # coded: timeout | git_missing | git_failed | None


def run_git(
    argv: list[str],
    deadline: Deadline,
    max_bytes: int,
    ok_codes: tuple[int, ...] = (0,),
) -> GitResult:
    """Run one fixed argv. Never raises; never returns stderr or argv."""
    if deadline.remaining() <= 0:
        return GitResult(b"", True, ERR_TIMEOUT)
    try:
        proc = subprocess.Popen(
            argv,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=git_env(),
            close_fds=True,
            start_new_session=True,
        )
    except FileNotFoundError:
        return GitResult(b"", False, ERR_GIT_MISSING)
    except OSError:
        return GitResult(b"", False, ERR_GIT_FAILED)
    try:
        data, truncated, timed_out = _read_bounded(proc, deadline, max_bytes)
        if truncated or timed_out:
            _terminate(proc)
        code = _reap(proc, deadline)
        if code is None:
            timed_out = True
    finally:
        _terminate(proc)  # no-op once the process has been reaped
        if proc.stdout is not None:
            proc.stdout.close()
    if timed_out:
        return GitResult(data, True, ERR_TIMEOUT)
    if not truncated and code not in ok_codes:
        return GitResult(b"", False, ERR_GIT_FAILED)
    return GitResult(data, truncated, None)


def _read_bounded(
    proc: subprocess.Popen, deadline: Deadline, max_bytes: int
) -> tuple[bytes, bool, bool]:
    """Stream stdout until EOF, `max_bytes` or the deadline. -> (data, truncated, timed_out)"""
    assert proc.stdout is not None
    fd = proc.stdout.fileno()
    chunks: list[bytes] = []
    total = 0
    with selectors.DefaultSelector() as sel:
        sel.register(fd, selectors.EVENT_READ)
        while True:
            left = deadline.remaining()
            if left <= 0:
                return b"".join(chunks), True, True
            if not sel.select(timeout=min(left, 0.5)):
                continue
            chunk = os.read(fd, _CHUNK)
            if not chunk:
                return b"".join(chunks), False, False
            total += len(chunk)
            chunks.append(chunk)
            if total > max_bytes:
                return b"".join(chunks)[:max_bytes], True, False


def _reap(proc: subprocess.Popen, deadline: Deadline) -> int | None:
    try:
        return proc.wait(timeout=max(deadline.remaining(), 0.05))
    except subprocess.TimeoutExpired:
        return None


def _terminate(proc: subprocess.Popen) -> None:
    """Kill the process group once, and only while the leader is not yet reaped (so a
    recycled pid can never be signalled). `returncode` is set only by wait()/poll()."""
    if proc.returncode is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass
