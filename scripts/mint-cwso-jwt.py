#!/usr/bin/env python3
"""Mint an HS256 JWT for CWSO MCP authentication.

Usage examples:
  python3 scripts/mint-cwso-jwt.py
  python3 scripts/mint-cwso-jwt.py --role worker --ttl 1800 --sub vscode-mcp
  python3 scripts/mint-cwso-jwt.py --secret-file /path/you/name/explicitly

Secret source (T694):
  1) --secret-file, only when given explicitly on the command line
  2) otherwise the CWSO_JWT_SECRET environment variable
There is no default secret file and no command-line secret value. When
neither source is set the script exits non-zero and names CWSO_JWT_SECRET;
it never prints the secret.

Secret file rule (SEC-T694-07, shared with scripts/cwso-deploy-helper.sh,
implementation/scripts/sia-executor.py and runtime/cwso/mcp_client.py): the
secret is the first line that is not empty and does not start with `#`,
with surrounding whitespace removed; later lines are ignored.

Error messages name options and variables only, never a value or a path
(SEC-T694-05).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time
from pathlib import Path


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class SecretSourceError(Exception):
    """A secret source problem; the message names the source, never a value or path."""


def secret_from_text(text: str) -> str:
    """Return the first non-empty line not starting with `#`, stripped ("" if none)."""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            return line
    return ""


def _load_secret_from_file(secret_file: Path) -> str:
    if not secret_file.is_file():
        raise SecretSourceError("the file given to --secret-file is not a regular file")
    try:
        text = secret_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise SecretSourceError(
            f"the file given to --secret-file cannot be read ({type(exc).__name__})"
        ) from None
    secret = secret_from_text(text)
    if not secret:
        raise SecretSourceError("the file given to --secret-file has no secret line")
    return secret


SECRET_ENV_VAR = "CWSO_JWT_SECRET"


def _resolve_secret(secret_file_arg: str | None) -> str:
    if secret_file_arg:
        return _load_secret_from_file(Path(secret_file_arg))

    secret_env = os.getenv(SECRET_ENV_VAR, "").strip()
    if secret_env:
        return secret_env

    raise SecretSourceError(
        f"{SECRET_ENV_VAR} is not set; export {SECRET_ENV_VAR} "
        "or pass --secret-file explicitly"
    )


def _mint_token(secret: str, role: str, subject: str, ttl_seconds: int) -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "role": role,
        "iss": "cwso",
        "aud": ["cwso-mcp"],
        "iat": now,
        "nbf": now,
        "exp": now + ttl_seconds,
    }

    encoded_header = _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    message = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
    encoded_signature = _b64url(signature)
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


class QuietArgumentParser(argparse.ArgumentParser):
    """An ArgumentParser whose errors name the option but never echo a value (SEC-T694-05)."""

    def error(self, message: str):  # type: ignore[override]
        match = re.match(r"argument (\S+?)(?:/\S+)?: ", message)
        if match:
            detail = f"invalid or missing value for {match.group(1)} (value not shown)"
        else:
            detail = "invalid arguments (values not shown)"
        self.exit(2, f"{self.prog}: error: {detail}; see --help\n")


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    # allow_abbrev=False: otherwise the removed "--secret VALUE" would be read
    # as "--secret-file VALUE"; QuietArgumentParser never echoes a value.
    parser = QuietArgumentParser(
        description="Mint a JWT for CWSO MCP authentication", allow_abbrev=False
    )
    parser.add_argument(
        "--role",
        default="orchestrator",
        choices=["orchestrator", "worker"],
        help="JWT role claim (default: orchestrator)",
    )
    parser.add_argument(
        "--sub",
        default="vscode-mcp",
        help="JWT sub claim (default: vscode-mcp)",
    )
    parser.add_argument(
        "--ttl",
        type=int,
        default=3600,
        help="token lifetime in seconds (default: 3600)",
    )
    parser.add_argument(
        "--secret-file",
        default=None,
        help=(
            "explicit path to a file holding the JWT secret on the first "
            "non-comment line (no default; otherwise CWSO_JWT_SECRET is used)"
        ),
    )
    return parser.parse_known_args()


def main() -> int:
    args, unknown = parse_args()
    if unknown:
        # Never echo unknown arguments: one of them may be a secret value.
        print(
            f"error: {len(unknown)} unrecognized argument(s), not shown; "
            f"--secret was removed (T694), export {SECRET_ENV_VAR} "
            "or pass --secret-file explicitly",
            file=sys.stderr,
        )
        return 2

    if args.ttl <= 0:
        print("error: --ttl must be > 0", file=sys.stderr)
        return 2

    try:
        secret = _resolve_secret(args.secret_file)
    except SecretSourceError as exc:
        print(f"error: could not resolve JWT secret ({exc})", file=sys.stderr)
        return 1

    token = _mint_token(secret, args.role, args.sub, args.ttl)
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
