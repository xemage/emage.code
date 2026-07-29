**Status:** done
**Completed:** 2026-05-22
# Task T011 — Build managed-agent cookbooks

## Objective
Create managed-agent cookbook manifests and examples for orchestrator-worker deployment in v3.

## Inputs
- docs/artifacts/v3-schema-contract-v1.md
- docs/plans/plan-002-emage-code-v3-roadmap.md
- managed-agent-cookbooks patterns from external research

## Expected outputs
- v3/implementation/cookbooks/README.md
- v3/implementation/cookbooks/<agent-slug>/agent.yaml
- v3/implementation/cookbooks/<agent-slug>/steering-examples.json

## Acceptance criteria
- Cookbook manifest fields map cleanly to runtime deployment fields.
- At least one orchestrator and two worker examples are included.
- Per-agent security notes and handoff rules are documented.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
