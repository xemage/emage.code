# Artifact: cwso-emagecode-adapter-v1

## Metadata
- Producer agent: backend-developer
- Task: T212 (in progress)
- Created: 2026-06-20
- Based on: docs/plans/plan-009-cwso-emagecode-sia-integration.md, docs/artifacts/role-mapping-cwso-v1.md, implementation/runtime/cwso/client.py

## Objective
Document the Pattern A orchestration flow used by emage.code to run multi-agent edits in CWSO shadow workspaces and deterministically merge results.

## Implemented Flow
1. `create_shadow_workspace` per worker edit set.
2. `write_shadow_file` for each file authored by the worker.
3. `commit_shadow` to capture commit/tree OIDs.
4. `merge_concurrent_results` with `auto_resolve_heuristic=ast_semantic_only`.
5. `drop_shadow_workspace` cleanup for all allocated workspaces.

Current implementation: `implementation/runtime/cwso/concurrent_merge.py`.

## Runtime Data Captured
Per worker workspace, the orchestrator records:
- `agent_role`
- `workspace_uuid`
- `commit_oid`
- `tree_oid`

These form the audit trail attached to orchestration output.

## Conflict Handling Contract
- Merge response is parsed for `unresolved_conflicts`.
- Conflicts are normalized to structured entries: `{path, reason}`.
- Caller receives both merge payload and structured conflict list.
- Cleanup always runs even on failures.

## Example Result Envelope
```json
{
  "merge_response": {"merge_status": "success"},
  "audit_records": [
    {
      "agent_role": "backend-developer",
      "workspace_uuid": "...",
      "commit_oid": "...",
      "tree_oid": "..."
    }
  ],
  "unresolved_conflicts": []
}
```

## Validation
Unit tests:
- `tests/unit/test_cwso_concurrent_merge.py`
  - happy path
  - structured conflict report
  - minimum worker cardinality validation

## Known Gaps
- Merge input generation is currently path-based and uses the latest worker edit as `theirs_content`.
- Future refinement should add richer base-content recovery from repository snapshots for higher-fidelity multi-way merges.
