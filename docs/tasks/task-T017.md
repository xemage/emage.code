# Task T017 — Knowledge registry generation

## Objective
Create a machine-readable and human-readable registry for v3 agents, skills, commands, instructions, and compatibility metadata.

## Inputs
- docs/artifacts/v3-schema-contract-v1.md
- v3 knowledge source directories

## Expected outputs
- v3/implementation/registry/schema.json
- v3/implementation/registry/index.json
- Generated registry markdown summary

## Acceptance criteria
- Registry is generated from source metadata without manual edits.
- Each artifact entry includes id, category, maturity, and platform compatibility.
- Validation enforces schema compliance.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
