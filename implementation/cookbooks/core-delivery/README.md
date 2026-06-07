# core-delivery cookbook

## Summary

Baseline software delivery workflow with one orchestrator and two worker roles.
It is intended as the first reference cookbook for v3 managed deployment.

## Security tier

Tier: `standard-controlled`

Controls:
- route allowlist enforced from orchestrator to workers only
- fail-closed schema validation for all handoff payloads
- log redaction for sensitive field names
- no secrets allowed in payloads

## Agent topology

- orchestrator: `orchestrator`
- workers:
  - `solution-architect`
  - `backend-engineer`

## Handoff policy

Allowed routes:
- orchestrator -> solution-architect
- orchestrator -> backend-engineer

Default policy: deny.

## Notes

This cookbook is deployment-oriented and does not replace canonical knowledge
authoring under `implementation/knowledge`.
