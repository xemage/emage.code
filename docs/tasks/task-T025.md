# Task T025 — Audit documentation and usage flow

## Objective
Audit current user-facing and contributor-facing documentation for alignment with the current emage.code v2 workflow, repository structure, and release process.

## Inputs
- `README.md`
- `CONTRIBUTING.md`
- `docs/wiki/*.md`
- `.gitlab-ci.yml`
- `v2/implementation/README.md`

## Expected outputs
- audit artifact documenting mismatches and required updates
- task-level recommendation list that unblocks T026, T027, and T028

## Acceptance criteria
- Every core user path (install/copy, configure MCP, invoke orchestrator, validate workflow, release workflow) is mapped to at least one current doc section.
- Gaps are documented with specific file-level remediation actions.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
