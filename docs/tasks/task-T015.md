# Task T015 — Trajectory telemetry and replay

## Objective
Implement trajectory telemetry capture and replay tooling for cross-platform regression analysis.

## Inputs
- docs/artifacts/v3-hook-policy-spec-v1.md
- existing benchmark fixtures and outputs

## Expected outputs
- docs/artifacts/v3-telemetry-schema-v1.md
- replay runner scripts and sample trajectory fixtures

## Acceptance criteria
- Telemetry schema captures step, tool, handoff, and verdict events.
- Replay tool compares runs and reports structural and quality deltas.
- Output supports CI artifact publishing.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
