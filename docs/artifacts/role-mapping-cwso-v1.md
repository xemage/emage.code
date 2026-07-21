# Artifact: role-mapping-cwso-v1

## Metadata
- Producer agent: solution-architect
- Task: T211
- Created: 2026-06-20
- Based on: docs/plans/plan-009-cwso-emagecode-sia-integration.md, docs/decisions/ADR-001-cwso-sia-integration.md, docs/artifacts/cwso-mcp-contract-v1.md

## Objective
Define a deterministic mapping between emage.code agent roles and CWSO permission tiers to enforce least privilege while enabling Pattern A orchestration.

## Why Mapping Is Required
emage.code coordinates multi-agent execution while CWSO enforces role-gated tool permissions at the MCP boundary. A stable mapping ensures:
- permission-safe orchestration,
- predictable failure modes for unauthorized tool calls,
- complete role-aware audit trails for task execution.

## CWSO Permission Tiers
Based on the live MCP contract snapshot (11 tools):

### `orchestrator` tier (planning-focused)
Primary responsibility: allocate workspaces, coordinate fan-out, and orchestrate workflows.

Typical tools:
- `create_shadow_workspace`
- `dispatch_concurrent_jobs`
- `drop_shadow_workspace`

### `worker` tier (write/merge execution)
Primary responsibility: produce code changes and perform merge operations.

Typical tools:
- `write_file_sync`
- `write_shadow_file`
- `commit_shadow`
- `merge_concurrent_results`

### `read` tier (inspection-only)
Primary responsibility: inspect workspace state and code structure without writes.

Typical tools:
- `read_file_sync`
- `list_dir`
- `read_shadow_file`
- `query_ast`

## emage.code Agent -> CWSO Tier Mapping

| emage.code agent | CWSO tier | Rationale |
|---|---|---|
| `orchestrator` | `orchestrator` | Coordinates decomposition, dispatch, and lifecycle management; should not directly mutate task outputs. |
| `poc-orchestrator` | `orchestrator` | Same orchestration duties for PoC workflows; planning-scoped permissions only. |
| `backend-developer` | `worker` | Produces and commits code in shadow workspaces. |
| `frontend-developer` | `worker` | Produces and commits UI code changes in isolated workspaces. |
| `database-engineer` | `worker` | Writes schema/query changes and commits merge inputs. |
| `devops-engineer` | `worker` | Writes CI/CD and infra artifacts requiring workspace mutation. |
| `technical-writer` | `worker` | Updates documentation artifacts that require write capability. |
| `qa-engineer` | `worker` | Can author/update tests and helper fixtures as part of execution tasks. |
| `release-manager` | `worker` | May write release notes/metadata and merge release-oriented changes. |
| `tech-lead` | `read` | Review role; should inspect and validate without implementation writes during gates. |
| `security-engineer` | `read` | Audit role; requires read/query-only access to enforce separation of duties. |
| `product-owner` | `read` | Requirement and prioritization role; no code mutation required. |
| `solution-architect` | `read` | Architecture review/decision role; read-only for implementation boundaries. |
| `scrum-master` | `read` | Process coordination role; no direct code mutation. |
| `ux-designer` | `read` | Design feedback role; no direct code mutation in runtime execution. |

## Implementation Notes
- JWT role claim is minted by the emage.code CWSO adapter per effective agent role.
- Default JWT TTL: 600 seconds.
- Request pacing must enforce approximately 1.05 seconds minimum interval to match observed server policy (about 60 req/min with burst 1).
- Orchestrator-stage operations use `orchestrator` tokens; implementation-stage operations use `worker` tokens.
- Validation and audit gates should run with `read` tokens for non-mutating reviewers.

## Security Implications
- Server-side role gate remains the source of truth; client mapping is advisory and should never bypass server checks.
- Any permission rejection is logged as a task-level security event and treated as a blocker until role assignment is corrected.
- Tool-call logs should include task ID, agent role, CWSO tier, timestamp, and outcome (without secrets).
- Secrets (JWT secret, provider keys) stay in environment or mounted files only.

## Ready-for-Use Contract (for T212)
For concurrent merge orchestration:
1. `orchestrator` creates target shadow workspace(s) and dispatches jobs.
2. `worker` roles write and commit per assigned workspace.
3. `worker` executes `merge_concurrent_results`.
4. `read` roles run post-merge inspection (`query_ast`, `read_shadow_file`) for validation gates.

This mapping is approved for Pattern A implementation and is the reference contract for T212.
