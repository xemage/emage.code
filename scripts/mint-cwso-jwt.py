#!/usr/bin/env python3
"""Mint an HS256 JWT for CWSO MCP authentication.

Usage examples:
  python3 scripts/mint-cwso-jwt.py
  python3 scripts/mint-cwso-jwt.py --role worker --ttl 1800 --sub vscode-mcp
  python3 scripts/mint-cwso-jwt.py --secret-file ../CWSO/.env.jwt.dev

Secret resolution order:
  1) --secret
  2) CWSO_JWT_SECRET environment variable
  3) --secret-file
  4) default sibling file ../CWSO/.env.jwt.dev
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
from pathlib import Path


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _load_secret_from_file(secret_file: Path) -> str:
    if not secret_file.is_file():
        raise FileNotFoundError(f"secret file not found: {secret_file}")

    for raw_line in secret_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            return line

    raise ValueError(f"secret file has no usable secret line: {secret_file}")


def _resolve_secret(secret_arg: str | None, secret_file_arg: str | None) -> str:
    if secret_arg:
        return secret_arg

    secret_env = os.getenv("CWSO_JWT_SECRET", "").strip()
    if secret_env:
        return secret_env

    if secret_file_arg:
        return _load_secret_from_file(Path(secret_file_arg))

    default_file = Path(__file__).resolve().parents[1].parent / "CWSO" / ".env.jwt.dev"
    return _load_secret_from_file(default_file)


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mint a JWT for CWSO MCP authentication")
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
        "--secret",
        default=None,
        help="raw JWT secret (avoid shell history for shared machines)",
    )
    parser.add_argument(
        "--secret-file",
        default=None,
        help="path to file containing the JWT secret on the first non-comment line",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.ttl <= 0:
        print("error: --ttl must be > 0", file=sys.stderr)
        return 2

    try:
        secret = _resolve_secret(args.secret, args.secret_file)
    except Exception as exc:
        print(f"error: could not resolve JWT secret ({exc})", file=sys.stderr)
        return 1

    token = _mint_token(secret, args.role, args.sub, args.ttl)
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
