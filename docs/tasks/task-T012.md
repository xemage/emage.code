# Task T012 — Add validation super-gate

## Objective
Implement a comprehensive validation gate for v3 that checks schemas, references, required artifacts, and drift.

## Inputs
- docs/artifacts/v3-schema-contract-v1.md
- v3 sync/verify tooling
- existing tests/functional patterns

## Expected outputs
- v3/implementation/scripts/check-v3.py
- CI job wiring for validation super-gate

## Acceptance criteria
- Gate fails on schema violations, unresolved references, missing required files, or drift.
- Output is concise and points to specific remediation paths.
- CI integration is documented in README.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
