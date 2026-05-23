#!/usr/bin/env python3
"""Prototype runner for v3 schedule/event trigger execution with policy guardrails."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TriggerValidationError(ValueError):
    """Raised when trigger payload violates schema contract."""


class TriggerPolicyError(PermissionError):
    """Raised when trigger payload violates policy guardrails."""


class TriggerExecutionError(RuntimeError):
    """Raised when trigger enqueue fails after retries."""


@dataclass
class TriggerRunResult:
    trigger_id: str
    status: str
    attempts: int
    correlation_id: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trigger", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--queue", required=True)
    parser.add_argument("--audit-log", required=True)
    parser.add_argument("--simulate-failures", type=int, default=0)
    return parser.parse_args()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _audit(audit_path: Path, event: dict[str, Any]) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def _validate_common_fields(trigger: dict[str, Any]) -> None:
    required = ("triggerId", "type", "source", "steeringInput", "retryPolicy")
    for key in required:
        if key not in trigger:
            raise TriggerValidationError(f"missing required field: {key}")

    trigger_id = trigger["triggerId"]
    if not isinstance(trigger_id, str) or not trigger_id:
        raise TriggerValidationError("triggerId must be non-empty string")

    trigger_type = trigger["type"]
    if trigger_type not in {"schedule", "event"}:
        raise TriggerValidationError("type must be schedule or event")

    source = trigger["source"]
    if not isinstance(source, str) or not source:
        raise TriggerValidationError("source must be non-empty string")

    steering = trigger["steeringInput"]
    if not isinstance(steering, dict) or not steering:
        raise TriggerValidationError("steeringInput must be non-empty object")

    retry_policy = trigger["retryPolicy"]
    if not isinstance(retry_policy, dict):
        raise TriggerValidationError("retryPolicy must be object")
    max_attempts = retry_policy.get("maxAttempts")
    if not isinstance(max_attempts, int) or max_attempts < 1:
        raise TriggerValidationError("retryPolicy.maxAttempts must be integer >= 1")


def _validate_type_fields(trigger: dict[str, Any]) -> None:
    trigger_type = trigger["type"]
    if trigger_type == "schedule":
        schedule = trigger.get("schedule")
        if not isinstance(schedule, dict):
            raise TriggerValidationError("schedule trigger requires schedule object")
        if not schedule.get("expression"):
            raise TriggerValidationError("schedule.expression is required")
        if not schedule.get("timezone"):
            raise TriggerValidationError("schedule.timezone is required")
        return

    event = trigger.get("event")
    if not isinstance(event, dict):
        raise TriggerValidationError("event trigger requires event object")
    if not event.get("name"):
        raise TriggerValidationError("event.name is required")


def _validate_trigger(trigger: dict[str, Any]) -> None:
    _validate_common_fields(trigger)
    _validate_type_fields(trigger)


def _effective_attempts(trigger: dict[str, Any], policy: dict[str, Any]) -> int:
    requested = int(trigger["retryPolicy"]["maxAttempts"])
    cap = int(policy.get("maxAttemptsCap", 1))
    return min(requested, cap)


def _enforce_policy(trigger: dict[str, Any], policy: dict[str, Any]) -> None:
    allowed_types = policy.get("allowedTypes", [])
    if trigger["type"] not in allowed_types:
        raise TriggerPolicyError(f"type not allowed: {trigger['type']}")

    allowed_sources = policy.get("allowedSources", [])
    if trigger["source"] not in allowed_sources:
        raise TriggerPolicyError(f"source not allowed: {trigger['source']}")

    if policy.get("requireSteeringTaskId", False):
        task_id = trigger["steeringInput"].get("taskId")
        if not isinstance(task_id, str) or not task_id:
            raise TriggerPolicyError("steeringInput.taskId is required by policy")


def _append_queue_event(queue_path: Path, trigger: dict[str, Any], correlation_id: str) -> None:
    payload = {
        "triggerId": trigger["triggerId"],
        "type": trigger["type"],
        "source": trigger["source"],
        "steeringInput": trigger["steeringInput"],
        "correlationId": correlation_id,
        "queuedAt": _now_iso(),
    }

    if queue_path.is_file():
        queue = _load_json(queue_path)
    else:
        queue = {"events": []}
    if not isinstance(queue.get("events"), list):
        raise TriggerExecutionError("queue file must contain events array")

    queue["events"].append(payload)
    _write_json(queue_path, queue)


def _audit_event(
    trigger: dict[str, Any],
    correlation_id: str,
    stage: str,
    status: str,
    reason: str,
    attempt: int | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "ts": _now_iso(),
        "triggerId": trigger.get("triggerId", "<unknown>"),
        "correlationId": correlation_id,
        "stage": stage,
        "status": status,
        "reason": reason,
    }
    if attempt is not None:
        event["attempt"] = attempt
    return event


def run_trigger(
    trigger_path: Path,
    policy_path: Path,
    queue_path: Path,
    audit_path: Path,
    simulate_failures: int = 0,
) -> TriggerRunResult:
    trigger = _load_json(trigger_path)
    policy = _load_json(policy_path)
    correlation_id = f"{trigger.get('triggerId', 'unknown')}-{int(datetime.now(timezone.utc).timestamp())}"

    _validate_trigger(trigger)
    _audit(audit_path, _audit_event(trigger, correlation_id, "validation", "pass", "validated"))

    _enforce_policy(trigger, policy)
    _audit(audit_path, _audit_event(trigger, correlation_id, "policy", "pass", "allowed"))

    attempts = _effective_attempts(trigger, policy)
    failures_left = simulate_failures
    for attempt in range(1, attempts + 1):
        if failures_left > 0:
            failures_left -= 1
            _audit(
                audit_path,
                _audit_event(trigger, correlation_id, "attempt", "retry", "enqueue_error", attempt),
            )
            continue

        _append_queue_event(queue_path, trigger, correlation_id)
        _audit(
            audit_path,
            _audit_event(trigger, correlation_id, "attempt", "success", "enqueued", attempt),
        )
        _audit(
            audit_path,
            _audit_event(trigger, correlation_id, "completion", "success", "completed", attempt),
        )
        return TriggerRunResult(trigger["triggerId"], "success", attempt, correlation_id)

    _audit(
        audit_path,
        _audit_event(trigger, correlation_id, "completion", "error", "exhausted_retries", attempts),
    )
    raise TriggerExecutionError("trigger execution failed: exhausted retries")


def main() -> int:
    args = parse_args()
    trigger_path = Path(args.trigger).resolve()
    policy_path = Path(args.policy).resolve()
    queue_path = Path(args.queue).resolve()
    audit_path = Path(args.audit_log).resolve()

    try:
        result = run_trigger(
            trigger_path=trigger_path,
            policy_path=policy_path,
            queue_path=queue_path,
            audit_path=audit_path,
            simulate_failures=args.simulate_failures,
        )
    except TriggerValidationError as exc:
        print(f"validation_error: {exc}")
        return 2
    except TriggerPolicyError as exc:
        print(f"policy_denied: {exc}")
        return 3
    except TriggerExecutionError as exc:
        print(f"execution_error: {exc}")
        return 4

    print(f"trigger {result.trigger_id} completed in {result.attempts} attempt(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
