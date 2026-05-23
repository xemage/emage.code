"""Antigravity-style adapter prototype for trigger-driven orchestration inputs."""
from __future__ import annotations

from typing import Any

from .base import AdapterEnvelope, AdapterResponse


FEATURE_FLAG = "V3_ADAPTER_ANTIGRAVITY"
SUPPORTED_PRIORITIES = {"low", "normal", "high"}


def _normalized_priority(payload: dict[str, Any]) -> str:
    priority = str(payload.get("priority", "normal")).lower()
    if priority not in SUPPORTED_PRIORITIES:
        return "normal"
    return priority


def transform(envelope: AdapterEnvelope) -> AdapterResponse:
    payload = envelope.payload
    warnings: list[str] = []
    priority = _normalized_priority(payload)
    if priority != str(payload.get("priority", "normal")).lower():
        warnings.append("priority normalized to 'normal'")

    document = {
        "session": {
            "runId": envelope.run_id,
            "source": "v3-trigger-framework",
        },
        "task": {
            "id": envelope.trigger_id,
            "intent": envelope.intent,
            "priority": priority,
            "inputs": payload,
        },
        "hooks": [
            "inspect.session.start",
            "inspect.handoff.preflight",
            "decide.handoff.route",
        ],
    }
    return AdapterResponse(adapter="antigravity", accepted=True, output=document, warnings=warnings)
