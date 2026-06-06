# v3 Trigger Framework Spec v1

Status: Draft for implementation (Execution Wave 2, P2)
Based on: [docs/artifacts/v3-hook-policy-spec-v1.md](../../docs/artifacts/v3-hook-policy-spec-v1.md)

## 1) Purpose

Define schedule and event trigger contracts that can enqueue orchestration steering inputs in a fail-closed, auditable runtime.

## 2) Trigger Types

Supported types:
- schedule: cron-like periodic triggers.
- event: external event triggers (for example webhook, queue, or integration events).

Required fields:
- triggerId: stable identifier.
- type: schedule or event.
- source: source identifier used for policy allowlists.
- steeringInput: object forwarded to orchestrator intake.
- retryPolicy: retry configuration.

Schedule trigger fields:
- schedule.expression: cron expression string.
- schedule.timezone: timezone name.

Event trigger fields:
- event.name: canonical event name.
- event.filter: optional key/value filter object.

## 3) Policy Guardrails

Policy file contains:
- allowedTypes: explicit allowed trigger types.
- allowedSources: explicit source allowlist.
- maxAttemptsCap: hard cap for retry attempts.
- requireSteeringTaskId: steering input must include taskId.

Fail-closed rules:
- Unknown type: deny.
- Unknown source: deny.
- Missing policy file: deny.
- Missing required steering input fields: deny.

## 4) Execution Contract

Runner behavior:
1. Validate trigger schema and type-specific fields.
2. Validate trigger against policy guardrails.
3. Attempt enqueue to queue artifact.
4. Retry with bounded attempts when enqueue fails.
5. Emit append-only audit entries for validation, policy, attempts, and final outcome.

Enqueue artifact:
- JSON file with envelope entries under events[].
- Runner appends a normalized record: triggerId, type, source, steeringInput, correlationId, queuedAt.

## 5) Failure And Retry Semantics

Retry policy fields:
- retryPolicy.maxAttempts: requested max attempts (>= 1).
- retryPolicy.backoffSeconds: base delay metadata for operators.

Retry resolution:
- effectiveMaxAttempts = min(retryPolicy.maxAttempts, policy.maxAttemptsCap)
- attempt 1 runs immediately.
- attempts 2..N are retried after conceptual exponential backoff metadata.

Failure categories:
- validation_error: bad trigger payload.
- policy_denied: source/type/guardrail mismatch.
- enqueue_error: queue write failed.
- exhausted_retries: enqueue kept failing after effective max attempts.

## 6) Audit Logging

Audit entries are JSON lines with:
- ts
- triggerId
- correlationId
- stage (validation, policy, attempt, completion)
- status (pass, deny, error, retry, success)
- reason
- attempt (for attempt stage)

Security constraints:
- Never log secrets from steering payload.
- Log only metadata fields and summary reason codes.

## 7) Prototype Scope

Prototype scope includes:
- local trigger execution from JSON files.
- policy enforcement and deterministic audit trail.
- simulated retry path for deterministic functional testing.

Out of scope:
- distributed scheduler.
- real queue backends.
- dynamic policy loading from remote stores.
