#!/usr/bin/env python3
"""Role-aware JWT + HTTP client for the CWSO MCP endpoint."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any
from urllib import error, request


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


class CwsoMcpError(RuntimeError):
    """Base error for CWSO MCP transport failures."""


class CwsoHttpError(CwsoMcpError):
    """Raised when HTTP transport rejects a request."""

    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body}")


class CwsoRpcError(CwsoMcpError):
    """Raised when the JSON-RPC response contains an error object."""

    def __init__(self, code: int, message: str, data: Any = None) -> None:
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"RPC error {code}: {message}")


class CwsoMcpClient:
    """Minimal MCP JSON-RPC client with role-aware JWT minting and pacing."""

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8080",
        jwt_secret: str | None = None,
        jwt_secret_file: Path | None = None,
        issuer: str = "cwso",
        audience: tuple[str, ...] = ("cwso-mcp",),
        subject: str = "emage-code",
        token_ttl_seconds: int = 600,
        min_interval_seconds: float = 1.05,
        timeout_seconds: float = 30.0,
    ) -> None:
        secret = jwt_secret or self._load_secret_from_file(jwt_secret_file)
        if not secret:
            raise ValueError("jwt secret missing: set jwt_secret or jwt_secret_file")
        self._secret = secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.issuer = issuer
        self.audience = audience
        self.subject = subject
        self.token_ttl_seconds = token_ttl_seconds
        self.min_interval_seconds = min_interval_seconds
        self.timeout_seconds = timeout_seconds
        self._last_rpc_at = 0.0

    @classmethod
    def from_env(cls) -> "CwsoMcpClient":
        base_url = os.getenv("CWSO_BASE_URL", "http://127.0.0.1:8080")
        jwt_secret = os.getenv("CWSO_JWT_SECRET")
        jwt_secret_file = os.getenv("CWSO_JWT_SECRET_FILE")
        if not jwt_secret and not jwt_secret_file:
            workspace_root = Path(__file__).resolve().parents[3]
            fallback_candidates = [
                workspace_root.parent / "CWSO" / ".env.jwt.dev",
                workspace_root / "CWSO" / ".env.jwt.dev",
            ]
            for candidate in fallback_candidates:
                if candidate.is_file():
                    jwt_secret_file = str(candidate)
                    break

        return cls(
            base_url=base_url,
            jwt_secret=jwt_secret,
            jwt_secret_file=Path(jwt_secret_file) if jwt_secret_file else None,
            min_interval_seconds=float(os.getenv("CWSO_MIN_INTERVAL_SECONDS", "1.05")),
            timeout_seconds=float(os.getenv("CWSO_TIMEOUT_SECONDS", "30")),
        )

    @staticmethod
    def _load_secret_from_file(secret_file: Path | None) -> str | None:
        if not secret_file or not secret_file.is_file():
            return None
        for raw_line in secret_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#"):
                return line
        return None

    @staticmethod
    def _b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    def mint_jwt(self, role: str) -> str:
        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        claims = {
            "sub": self.subject,
            "role": role,
            "iss": self.issuer,
            "aud": list(self.audience),
            "iat": now,
            "exp": now + self.token_ttl_seconds,
        }
        encoded_header = self._b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        encoded_claims = self._b64url(json.dumps(claims, separators=(",", ":")).encode("utf-8"))
        signature = hmac.new(
            self._secret,
            f"{encoded_header}.{encoded_claims}".encode("utf-8"),
            hashlib.sha256,
        ).digest()
        encoded_sig = self._b64url(signature)
        return f"{encoded_header}.{encoded_claims}.{encoded_sig}"

    def _pace(self) -> None:
        now = time.monotonic()
        wait_seconds = self.min_interval_seconds - (now - self._last_rpc_at)
        if wait_seconds > 0:
            time.sleep(wait_seconds)

    def rpc(self, *, role: str, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self._pace()
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        req = request.Request(
            f"{self.base_url}/mcp",
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": "Bearer " + self.mint_jwt(role),
                "Content-Type": "application/json",
                "Origin": "http://localhost",
            },
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                self._last_rpc_at = time.monotonic()
                parsed = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            self._last_rpc_at = time.monotonic()
            body = exc.read().decode("utf-8", errors="replace")
            raise CwsoHttpError(exc.code, body) from exc

        if "error" in parsed:
            err = parsed["error"]
            raise CwsoRpcError(err.get("code", -1), err.get("message", "unknown error"), err.get("data"))
        result = parsed.get("result")
        if not isinstance(result, dict):
            raise CwsoMcpError("missing JSON-RPC result object")
        return result

    def list_tools(self, *, role: str) -> list[dict[str, Any]]:
        result = self.rpc(role=role, method="tools/list", params={})
        tools = result.get("tools", [])
        if not isinstance(tools, list):
            raise CwsoMcpError("tools/list returned non-list 'tools' field")
        return tools

    def call_tool(self, *, role: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return self.rpc(
            role=role,
            method="tools/call",
            params={"name": name, "arguments": arguments},
        )

    @staticmethod
    def normalized_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize tool listing so snapshots are stable across order changes."""
        return sorted(tools, key=lambda tool: str(tool.get("name", "")))


def live_contract_tests_enabled() -> bool:
    """Guard network tests so regular CI/local runs stay deterministic."""
    return _is_truthy(os.getenv("CWSO_LIVE_CONTRACT_TEST"))
