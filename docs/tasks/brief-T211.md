# Delegation Brief — T211: Map emage.code Agent Roles → CWSO Permission Tiers

## Objective
Document a clear mapping from emage.code agent roles (backend-developer, frontend-developer, qa-engineer, etc.) to CWSO permission tiers (orchestrator, worker) based on the ADR decision and MCP contract.

## Context
- **Plan**: docs/plans/plan-009-cwso-emagecode-sia-integration.md (§4 target architecture, §8 agent assignments)
- **ADR**: docs/decisions/ADR-001-cwso-sia-integration.md (ownership boundaries, tier definitions)
- **Evidence**: docs/artifacts/cwso-mcp-contract-v1.md (JWT role-gating rules)
- **Task Dependencies**: T202 (ADR, done) — defines tier semantics
- **Next Task**: T212 (concurrent-merge orchestration) — will use this mapping

## Expected Outputs

**File**: `docs/artifacts/role-mapping-cwso-v1.md`

**Content Structure**:
1. **Introduction**: Why mapping is needed (isolation, permission enforcement, audit trail)
2. **CWSO Tier Definitions** (from MCP contract):
   - `orchestrator`: Can call planning-tier tools (create_shadow_workspace, dispatch_concurrent_jobs, drop_shadow_workspace, merge_concurrent_results)
   - `worker`: Can call worker-tier tools (write_file_sync, write_shadow_file, commit_shadow, merge_concurrent_results)
   - `read`: Can call read-tier tools (read_file_sync, list_dir, read_shadow_file, query_ast)
3. **emage.code Agent → CWSO Role Mapping**:
   ```
   Orchestrator (emage.code)           → orchestrator (CWSO planning tier)
   backend-developer, frontend-dev...  → worker (CWSO worker tier)
   tech-lead, security-engineer...     → read (CWSO read tier, for review-phase audits)
   ```
4. **Rationale**: Each mapping row explains why (e.g., "backend-developer is a worker because it writes code into shadow workspaces", "tech-lead is read because it reviews, does not modify during gate")
5. **Implementation Notes**:
   - JWT generation: Orchestrator mints tokens with role based on emage.code agent name
   - Token lifetime: 600 sec (matches CWSO default)
   - Rate limiting: Orchestrator job dispatch respects 60 req/min pacing
6. **Security Implications**:
   - Permission failures are logged and escalate as task blockers
   - Cross-tier calls are rejected server-side (already enforced by CWSO)
   - Audit trail: every tool call includes role, timestamp, task ID

## Acceptance Criteria
- [ ] Mapping covers all emage.code agents (orchestrator, developer roles, reviewer roles, infrastructure roles)
- [ ] Each mapping row includes: emage.code agent → CWSO tier + one-sentence rationale
- [ ] CWSO tier definitions match the MCP contract exactly (11 tools, 3 tiers)
- [ ] Implementation notes clarify how JWT tokens are minted per agent
- [ ] Security implications section explains server-side enforcement and audit
- [ ] Artifact references Plan 009 §4 and ADR-001
- [ ] Ready for T212 (concurrent-merge orchestration can import and use this mapping)

## Constraints
- Stay grounded in the MCP contract (cwso-mcp-contract-v1.md)
- Do not invent new tiers or tool access patterns (consume the 11 tools + 3 tiers as-is)
- Do not design role-revocation or dynamic tier changes (out of scope; fixed per agent type)
- No secrets or API keys in the artifact

## Blocker Protocol
If blocked, report type, severity, and mitigation.

## References
- CWSO MCP tool surface: docs/artifacts/cwso-mcp-contract-v1.md
- ADR on integration: docs/decisions/ADR-001-cwso-sia-integration.md (Ownership Boundaries)
- Agent definitions: AGENTS.md (emage.code orchestrator, worker roles)
