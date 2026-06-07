"""Shared contracts and feature-flag helpers for v3 experimental adapters."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


GLOBAL_ADAPTER_FLAG = "V3_EXPERIMENTAL_ADAPTERS"


@dataclass(frozen=True)
class AdapterEnvelope:
    run_id: str
    trigger_id: str
    intent: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class AdapterResponse:
    adapter: str
    accepted: bool
    output: dict[str, Any]
    warnings: list[str]


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def adapters_enabled() -> bool:
    return _env_flag(GLOBAL_ADAPTER_FLAG)


def adapter_enabled(flag_name: str) -> bool:
    return adapters_enabled() and _env_flag(flag_name)
