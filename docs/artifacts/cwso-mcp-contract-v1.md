# Artifact: cwso-mcp-contract-v1.md

- Producer agent: backend-developer
- Task: T201
- Created: 2026-06-19
- Based on: docs/tasks/task-T201.md, docs/plans/plan-009-cwso-emagecode-sia-integration.md

## Scope

Verifiable snapshot of the live CWSO v0.4.1 MCP contract at http://127.0.0.1:8080/mcp, including tool surface, role behavior, permission boundaries, and transport constraints required by downstream integration tasks.

## Probe Method

- Endpoint: POST /mcp
- Protocol: JSON-RPC 2.0
- Auth: Authorization: Bearer <HS256 JWT>
- JWT claims: role, iss:"cwso", aud:["cwso-mcp"], exp (+600s)
- Secret source (dev): /home/emage/Code/emage/CWSO/.env.jwt.dev
- Roles tested: orchestrator, worker, planner
- Captured via local Python probe and validated by reusable helper plus live snapshot test.

## Snapshot Summary

- tools/list returned 11 tools for role=orchestrator
- tools/list returned 11 tools for role=worker
- tools/list for role=planner returned HTTP 403 with body: forbidden: unrecognised role
- tools/call commit_shadow with role=orchestrator returned JSON-RPC error code -32002

## Tool Inventory (11 tools)

1. read_file_sync
2. write_file_sync
3. list_dir
4. create_shadow_workspace
5. write_shadow_file
6. read_shadow_file
7. commit_shadow
8. drop_shadow_workspace
9. query_ast
10. dispatch_concurrent_jobs
11. merge_concurrent_results

## Input Schemas (Live)

### read_file_sync
- required: path:string

### write_file_sync
- required: path:string, content:string

### list_dir
- optional: path:string

### create_shadow_workspace
- optional: base_commit_sha:string

### write_shadow_file
- required: workspace_uuid:string, path:string, content:string

### read_shadow_file
- required: workspace_uuid:string, path:string

### commit_shadow
- required: workspace_uuid:string, message:string

### drop_shadow_workspace
- required: workspace_uuid:string

### query_ast
- required: workspace_uuid:string, path:string, query_type:enum
- query_type enum: find_definition, find_references, extract_signature, list_exports, detect_entrypoints
- optional: target_symbol:string

### dispatch_concurrent_jobs
- required: jobs:array(minItems=1)
- job required fields: agent_role:string, objective_prompt:string(minLength=1), target_workspace_uuid:string(format=uuid)
- job optional: sandbox_profile enum [docker-trusted, gvisor-fast-ephemeral, firecracker-secure-isolation]
- optional top-level: execution_timeout_seconds:integer(min=1, default=300)

### merge_concurrent_results
- required: source_workspace_uuids:array(minItems=2, uuid), merge_inputs:array(minItems=1)
- merge_inputs item required: path:string(minLength=1), language:enum, base_content:string, ours_content:string, theirs_content:string
- language enum: go, rust, python, typescript
- optional: auto_resolve_heuristic enum [ast_semantic_only, prefer_theirs, prefer_ours, fail_rapidly_on_conflict] (default ast_semantic_only)
- optional: target_branch_ref:string (default main)
- optional: rollout_session_id:string (reward attachment hook)

## Roles and Tier Expectations

Observed from live behavior and tool descriptions:

- Read-tier tools:
  - read_file_sync
  - list_dir
  - read_shadow_file
  - query_ast

- Planning-tier tools:
  - create_shadow_workspace
  - drop_shadow_workspace
  - dispatch_concurrent_jobs

- Worker-tier tools:
  - write_file_sync
  - write_shadow_file
  - commit_shadow
  - merge_concurrent_results

Acceptance evidence:
- commit_shadow called as orchestrator -> JSON-RPC -32002 role may not invoke tool.
- planner role rejected before tool dispatch -> HTTP 403 unrecognised role.

## Error Surface

- HTTP 403 + body "forbidden: unrecognised role" for unknown role (planner).
- JSON-RPC error code -32002 for role/tool permission violations (example: orchestrator -> commit_shadow).

## Rate Limit / Pacing Contract

Plan and CWSO integration recipe indicate 60 req/min with burst=1 for POST /mcp.
Integration helper enforces >= 1.05s inter-request pacing to avoid 429 under normal operation.

## Reusable Helper and Test Assets Produced in T201

- Helper: implementation/runtime/cwso/mcp_client.py
  - HS256 JWT minting with role-aware claims
  - tools/list and tools/call wrappers
  - transport error mapping (HTTP and JSON-RPC)
  - >=1.05s pacing between requests
  - env-based config for endpoint and JWT secret

- Snapshot fixture: tests/fixtures/cwso/tools_list_snapshot_v1.json

- Live snapshot test: tests/functional/test_cwso_mcp_contract_snapshot.py
  - validates exact 11-tool list for orchestrator and worker
  - validates planner rejection (403)
  - validates worker-tier gate via orchestrator commit_shadow (-32002)

## Consumers

- T210 (CwsoClient typed wrappers)
- T202 (ADR with grounded contract references)
- T220 (real harness adapter against pinned tool surface)
