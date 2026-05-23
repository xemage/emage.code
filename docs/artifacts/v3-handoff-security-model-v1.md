# v3 Handoff Security Model v1

## Purpose

Define fail-closed security controls for cross-agent handoff payloads in v3.

## Threat model

Primary threats:
- injected handoff payloads from untrusted context
- unauthorized routing to privileged agents
- oversized payload denial-of-service attempts
- secret exfiltration through payload fields
- replay and correlation confusion

## Security controls

1. Route allowlisting
- Every handoff must match an explicit `from -> to` route in cookbook `handoffPolicy.allowRoutes`.
- Unknown routes are denied.

2. Strict payload schema
- Payloads must match required top-level and nested keys.
- Unknown fields are rejected.
- Key constraints include semver, UUID-like IDs, bounded list/object sizes.

3. Fail-closed validation
- Schema mismatch or malformed payload causes immediate rejection.
- No fallback auto-correction of invalid payloads.

4. Secret suppression
- Payload body must not include keys matching secret-like patterns:
  `token`, `password`, `api_key`, `authorization`, `secret`.
- Violations are denied and logged as security events.

5. Payload size limit
- Max serialized payload size is 64 KiB.
- Oversized payloads are rejected.

6. Trace integrity
- `handoffId`, `correlationId`, and `taskId` format checks are enforced.

## Enforcement points

- Runtime validator module:
  `v3/implementation/runtime/handoff/validator.py`
- Runtime schema contract:
  `v3/implementation/runtime/handoff/schema-v1.json`
- Super-gate command:
  `python3 v3/implementation/scripts/check-v3.py --handoff-security --root v3/implementation`

## Cookbook integration

Each cookbook must define:
- `handoffPolicy.allowRoutes`
- `handoffPolicy.defaultAction`
- `security.allowSecretsInPayload: false`
- `security.requireSchemaValidation: true`

## Test coverage

- Positive path: valid handoff payload + allowed route passes.
- Negative path: secret-like keys fail.
- Negative path: unknown route fails.
- Negative path: missing required keys fail.

## Operational guidance

- Treat failed handoff validations as security-relevant events.
- Do not auto-retry malformed payloads without deterministic correction logic.
- Keep route tables minimal and role-aligned.
