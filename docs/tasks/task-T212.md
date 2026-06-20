# Task T212 - Concurrent-merge orchestration (N workers → shadow → merge)

## Objective
Implement the Pattern A orchestration: fan out N emage.code worker agents into N isolated CWSO shadow
workspaces, then deterministically merge their results via `merge_concurrent_results`.

## Inputs
- `CwsoClient` (T210)
- `role-tier-mapping-v1.md` (T211)
- Plan 009 §2.1 (Pattern A), §3.2

## Expected outputs
- Orchestration module: per-agent `create_shadow_workspace` → `write_shadow_file`/`commit_shadow` →
  collect base/ours/theirs → `merge_concurrent_results` (default `ast_semantic_only`) → drop workspaces
- `docs/artifacts/cwso-emagecode-adapter-v1.md` documenting the flow + audit trail (commit/tree OIDs)

## Expected outputs (cont.)
- Returns merged content + per-file conflict report; surfaces unresolved conflicts to the orchestrator

## Acceptance criteria
- A multi-file, multi-agent edit set merges with `ast_semantic_only` and no manual intervention on the happy path.
- Unresolved conflicts return a structured report (not a silent failure).
- Audit trail (workspace UUIDs, commit/tree OIDs) recorded.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
