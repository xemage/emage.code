#!/usr/bin/env python3
"""Handoff payload and route validator for emage.code v3.

Fail-closed behavior:
- reject unknown routes,
- reject malformed payloads,
- reject payloads that contain likely secrets,
- reject oversize payloads.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SECRET_KEY_RE = re.compile(r"(token|password|api[_-]?key|authorization|secret)", re.IGNORECASE)
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
AGENT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
TASK_RE = re.compile(r"^T[0-9]{3,}$")
UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")
MAX_PAYLOAD_BYTES = 64 * 1024


class ValidationResult:
    def __init__(self, ok: bool, errors: list[str]) -> None:
        self.ok = ok
        self.errors = errors


REQUIRED_TOP_KEYS = {
    "schema",
    "schemaVersion",
    "handoffId",
    "timestamp",
    "fromAgent",
    "toAgent",
    "taskId",
    "intent",
    "payload",
    "constraints",
    "trace",
}
REQUIRED_CONSTRAINT_KEYS = {"maxToolCalls", "writablePaths", "forbiddenActions", "deadlineUtc"}
REQUIRED_TRACE_KEYS = {"correlationId", "parentStepId", "checkpointRef"}
ALLOWED_INTENTS = {"delegate", "request-review", "request-data", "escalate"}


def _deep_contains_secret_keys(value: Any) -> bool:
    if isinstance(value, dict):
        for k, v in value.items():
            if SECRET_KEY_RE.search(str(k)):
                return True
            if _deep_contains_secret_keys(v):
                return True
    elif isinstance(value, list):
        return any(_deep_contains_secret_keys(item) for item in value)
    return False


def validate_handoff_payload(payload: dict[str, Any], *, max_bytes: int = MAX_PAYLOAD_BYTES) -> ValidationResult:
    errors: list[str] = []

    if not isinstance(payload, dict):
        return ValidationResult(False, ["payload root must be an object"])

    if set(payload) != REQUIRED_TOP_KEYS:
        unknown = sorted(set(payload) - REQUIRED_TOP_KEYS)
        missing = sorted(REQUIRED_TOP_KEYS - set(payload))
        if missing:
            errors.append(f"missing keys: {missing}")
        if unknown:
            errors.append(f"unknown keys: {unknown}")

    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    if len(raw.encode("utf-8")) > max_bytes:
        errors.append("payload exceeds max size")

    if "schemaVersion" in payload and not SEMVER_RE.match(str(payload["schemaVersion"])):
        errors.append("schemaVersion must be semver")

    for key in ("handoffId",):
        value = payload.get(key)
        if value is not None and not UUID_RE.match(str(value)):
            errors.append(f"{key} must be uuid-like")

    for key in ("fromAgent", "toAgent"):
        value = payload.get(key)
        if value is not None and not AGENT_RE.match(str(value)):
            errors.append(f"{key} has invalid format")

    task = payload.get("taskId")
    if task is not None and not TASK_RE.match(str(task)):
        errors.append("taskId has invalid format")

    intent = payload.get("intent")
    if intent is not None and intent not in ALLOWED_INTENTS:
        errors.append("intent must be one of allowed values")

    constraints = payload.get("constraints")
    if not isinstance(constraints, dict):
        errors.append("constraints must be object")
    else:
        if set(constraints) != REQUIRED_CONSTRAINT_KEYS:
            unknown = sorted(set(constraints) - REQUIRED_CONSTRAINT_KEYS)
            missing = sorted(REQUIRED_CONSTRAINT_KEYS - set(constraints))
            if missing:
                errors.append(f"constraints missing keys: {missing}")
            if unknown:
                errors.append(f"constraints unknown keys: {unknown}")
        if not isinstance(constraints.get("maxToolCalls"), int) or constraints.get("maxToolCalls", -1) < 0:
            errors.append("constraints.maxToolCalls must be int >= 0")

    trace = payload.get("trace")
    if not isinstance(trace, dict):
        errors.append("trace must be object")
    else:
        if set(trace) != REQUIRED_TRACE_KEYS:
            unknown = sorted(set(trace) - REQUIRED_TRACE_KEYS)
            missing = sorted(REQUIRED_TRACE_KEYS - set(trace))
            if missing:
                errors.append(f"trace missing keys: {missing}")
            if unknown:
                errors.append(f"trace unknown keys: {unknown}")
        corr = trace.get("correlationId")
        if corr is not None and not UUID_RE.match(str(corr)):
            errors.append("trace.correlationId must be uuid-like")

    if _deep_contains_secret_keys(payload.get("payload")):
        errors.append("payload contains prohibited secret-like keys")

    return ValidationResult(ok=not errors, errors=errors)


def route_allowed(from_agent: str, to_agent: str, allow_routes: list[dict[str, str]]) -> bool:
    for route in allow_routes:
        if route.get("from") == from_agent and route.get("to") == to_agent:
            return True
    return False


def load_allow_routes_from_cookbook(cookbook_path: Path) -> list[dict[str, str]]:
    import yaml

    data = yaml.safe_load(cookbook_path.read_text(encoding="utf-8")) or {}
    handoff = data.get("handoffPolicy") or {}
    routes = handoff.get("allowRoutes") or []
    if not isinstance(routes, list):
        return []
    out: list[dict[str, str]] = []
    for route in routes:
        if isinstance(route, dict) and "from" in route and "to" in route:
            out.append({"from": str(route["from"]), "to": str(route["to"])})
    return out
