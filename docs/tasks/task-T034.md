**Status:** done
**Completed:** 2026-05-23
# Task T034 — Fix v3 command accuracy

## Objective
Correct any inaccurate v3 runbook commands and make the v3 scripts easier to invoke correctly from the documented entry points.

## Inputs
- `docs/tasks/task-T031.md`
- `v3/implementation/README.md`
- `v3/implementation/scripts/verify-v3.mjs`
- `v3/implementation/scripts/sync-v3.mjs`

## Expected outputs
- corrected command examples and/or script path handling
- v3 README commands that work as documented

## Acceptance criteria
- Documented v3 commands execute successfully from their stated working directory.
- Any root-path handling ambiguity is removed or explicitly documented.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
