#!/usr/bin/env python3
"""Run one command under an allowlisted environment (T750, plan-143; SEC-T745-04, SEC-T745-05).

Usage: python3 -I scripts/run-allowlisted.py [--keep NAME]... -- COMMAND [ARGUMENT]...

The process replaces itself with COMMAND through os.execvpe, so COMMAND keeps its pid, its signals and its exit code.
COMMAND sees only these variables:

  - the names in ALLOWED_NAMES and the names matching ALLOWED_PATTERN, the allowlist of the before_script of the
    `release` job (tests/functional/test_run_allowlisted.py compares the two);
  - each NAME given with --keep, whatever its value holds.

An allowlisted name whose value contains the value of a name in SECRET_NAMES is dropped, as `release` does: a proxy URL
can carry the job token. --keep passes a name past that filter, so CI_JOB_TOKEN can be kept by its own name.

What it does not do: it filters the environment and nothing else. COMMAND can still read any file the job can read, so a
credential in a file is a matter for the job (.gitlab-ci.yml), and the shell that started this keeps its own variables.

Run it with `python3 -I`, so nothing from PYTHONPATH, the current directory or the user's site directory is imported.
Only the standard library is used.

Exit codes: COMMAND's own once it runs; 2 usage error; 126 COMMAND cannot be executed; 127 COMMAND was not found.
"""
from __future__ import annotations

import os
import re
import sys
from collections.abc import Mapping

ALLOWED_NAMES = frozenset({
    "PATH", "HOME", "LANG", "LANGUAGE", "TMPDIR", "TZ", "SSL_CERT_FILE", "SSL_CERT_DIR", "CURL_CA_BUNDLE",
    "http_proxy", "https_proxy", "no_proxy", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "ALL_PROXY",
})
ALLOWED_PATTERN = re.compile(r"LC_[A-Z_]+")
SECRET_NAMES = ("CI_JOB_TOKEN", "WIKI_TOKEN")
KEEP_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
USAGE = "usage: run-allowlisted.py [--keep NAME]... -- COMMAND [ARGUMENT]..."


def usage_error(message: str) -> SystemExit:
    print(f"run-allowlisted: {message}\n{USAGE}", file=sys.stderr)
    return SystemExit(2)


def parse_args(argv: list[str]) -> tuple[set[str], list[str]]:
    """(the names to keep, the command). By hand: everything after `--` is the command's, untouched."""
    keep: set[str] = set()
    index = 0
    while index < len(argv) and argv[index] != "--":
        if argv[index] != "--keep":
            raise usage_error(f"unexpected argument {ascii(argv[index])}")
        if index + 1 >= len(argv) or not KEEP_NAME.fullmatch(argv[index + 1]):
            raise usage_error("--keep needs a variable name")
        keep.add(argv[index + 1])
        index += 2
    command = argv[index + 1:]
    if index >= len(argv) or not command:
        raise usage_error("a command is required after --")
    return keep, command


def allowlisted_env(environ: Mapping[str, str], keep: set[str]) -> dict[str, str]:
    """The child's environment: a kept name as it is, an allowlisted name unless its value holds a secret's value."""
    secrets = [value for name, value in environ.items() if name in SECRET_NAMES and value]

    def allowed(name: str, value: str) -> bool:
        listed = name in ALLOWED_NAMES or ALLOWED_PATTERN.fullmatch(name) is not None
        return listed and not any(secret in value for secret in secrets)

    return {name: value for name, value in environ.items() if name in keep or allowed(name, value)}


def main(argv: list[str]) -> int:
    if argv[:1] in (["-h"], ["--help"]):
        print(__doc__)
        return 0
    keep, command = parse_args(argv)
    try:
        os.execvpe(command[0], command, allowlisted_env(os.environ, keep))
    except OSError as failure:  # the name only: the environment and the arguments stay out of the message
        print(f"run-allowlisted: cannot run {ascii(command[0])}: {failure.strerror}", file=sys.stderr)
        return 127 if isinstance(failure, (FileNotFoundError, NotADirectoryError)) else 126
    return 126  # not reached: execvpe either replaces this process or raises


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
