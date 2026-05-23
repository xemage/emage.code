"""Opencode SDK automation adapter prototype for safe scripted orchestration."""
from __future__ import annotations

from .base import AdapterEnvelope, AdapterResponse


FEATURE_FLAG = "V3_ADAPTER_OPENCODE"


def _safe_command(intent: str) -> str:
    allowed = {
        "triage-new-issue": "opencode run --workflow issue-triage",
        "run-daily-health-check": "opencode run --workflow health-check",
    }
    return allowed.get(intent, "opencode run --workflow generic")


def transform(envelope: AdapterEnvelope) -> AdapterResponse:
    warnings: list[str] = []
    if "shell" in envelope.payload:
        warnings.append("payload key 'shell' ignored by safety policy")

    command = _safe_command(envelope.intent)
    script = {
        "automation": {
            "runId": envelope.run_id,
            "taskRef": envelope.trigger_id,
            "command": command,
            "args": {
                "intent": envelope.intent,
                "taskId": envelope.payload.get("taskId", ""),
            },
        },
        "guardrails": {
            "allowArbitraryShell": False,
            "requirePolicyHooks": True,
        },
    }
    return AdapterResponse(adapter="opencode", accepted=True, output=script, warnings=warnings)
