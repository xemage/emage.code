# v3 Managed Agent Cookbooks

This folder contains deployment-oriented cookbook manifests for emage.code v3.

## Purpose

Cookbooks package an orchestrator + worker routing contract with explicit
security, handoff, and steering examples for managed deployment surfaces.

## Structure

Each cookbook lives in its own directory and includes:

- `agent.yaml`: primary deployment manifest
- `README.md`: security tier, handoff policy, and operator notes
- `steering-examples.json`: sample steering events for orchestration layers

## Validation expectations

Cookbooks are validated by `check-v3 --cookbooks` (T012) for:

- required fields and schema version
- `orchestrator` and `workers` reference integrity
- handoff route allowlists
- security defaults (`allowSecretsInPayload: false`, schema validation enabled)

## Initial cookbook set

- `core-delivery`: baseline software delivery flow with architecture,
  implementation, and QA-style worker delegation patterns.
