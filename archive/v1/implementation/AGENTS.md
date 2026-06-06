# emage.code — Workspace Conventions

## Team Model
- Two orchestration tracks: Production (`@orchestrator`) and PoC (`@poc-orchestrator`)
- Only orchestrators are user-invocable. All other agents are subagents.
- Orchestrators delegate via structured briefs. Agents do not self-activate.

## Lifecycle States
```
pending → in_progress → blocked → in_review → done | cancelled
```

## Task Protocol
- Task list: `docs/tasks/active-tasks.md` (structured table with ID, status, owner, dependencies)
- Task briefs: `docs/tasks/task-<ID>.md` (objective, inputs, outputs, acceptance criteria)
- Only orchestrators create/transition tasks. Agents report completion and blockers.
- Tasks use sequential IDs: T001, T002, ...
- Priority levels: P0 (critical path), P1 (important), P2 (nice-to-have)

## Artifact Versioning
- Immutable artifacts: `<type>-v<N>.md` (e.g., `requirements-v1.md`, `architecture-v1.md`)
- Every artifact references its input versions: `Based on: requirements-v1.md`
- Revisions create new versions, never overwrite
- Agents MUST reference the specific version they consumed

## Checkpoint Protocol
- Checkpoints: `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`
- Written at every phase boundary by the orchestrator
- Include: completed tasks, key decisions, blockers, token metrics, next steps
- Agents receive latest checkpoint + task brief (not full history)

## Decision Log
- ADRs: `docs/decisions/ADR-<NNN>-<slug>.md`
- Each decision references requirements and task IDs
- Immutable once accepted. Superseded decisions link to replacement.

## Delegation Brief Format
Every delegation from orchestrator to agent includes:
1. **Objective** — clear, one-paragraph description
2. **Context** — current phase + latest checkpoint reference
3. **Inputs** — specific artifact versions to reference
4. **Constraints** — token budget, file ownership boundaries, technology constraints
5. **Expected Outputs** — artifact names and format
6. **Acceptance Criteria** — specific, testable conditions
7. **Blocker Protocol** — reminder to report blockers with type and severity

## Blocker Protocol
- Agents report blockers with: type, severity, description, suggested resolution
- Types: `technical` | `dependency` | `unclear_requirements` | `external`
- Severities: `critical` | `major` | `minor`
- Orchestrator routes to resolver. Max 2 retries before user escalation.
- Agents MUST NOT silently fail.

## Validation Gates
- VERDICT format: `PASS` | `CONDITIONAL_PASS` | `FAIL`
- Review agents (Tech Lead, QA, Security) must not modify code during review
- `FAIL` blocks progression. Orchestrator creates fix tasks and re-routes.
- `CONDITIONAL_PASS` proceeds with tracked conditions (added to task list).

## Code Standards
- See `.github/instructions/coding-standards.instructions.md`
- Max 50-line functions, max 4 parameters, early returns
- Conventional Commits with issue references (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)
- GitFlow branching: `main`, `develop`, `feature/*`, `bugfix/*`, `release/*`, `hotfix/*`

## Security
- See `.github/instructions/security-guidelines.instructions.md`
- OWASP Top 10 compliance required
- No secrets in code — use environment variables or vault
- Parameterized queries only — no string concatenation for SQL
- Input validation at all system boundaries

## MCP Servers
| Server | Purpose | Used By |
|--------|---------|---------|
| `gitlab` | Repository, issues, MRs, pipelines | Orchestrator, Scrum Master, DevOps, Release Manager |
| `playwright` | Browser automation, E2E testing | QA, Frontend, Demo Agent |
| `memory` | Persistent knowledge graph | Orchestrator (team memory) |
| `sequential-thinking` | Complex problem decomposition | Architect, Orchestrator |
| `fetch` | Web content fetching | Architect, Tech Lead, Developers |
| `brave` | Technology discovery | Technology Scout, Feasibility |
| `context7` | Framework/API documentation | Technology Scout, Integration |

## Token Governance
| Phase | Budget |
|-------|--------|
| Planning | ≤80k tokens |
| Architecture | ≤80k tokens |
| Implementation | ≤120k tokens |
| QA/Security/Release | ≤60k tokens |

Track usage in checkpoints. Compress context and start fresh delegation when approaching budget.
