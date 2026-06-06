# emage.code — Key Differences & Migration Summary

## What's New in emage.code vs. DEV-Team-Recruiter

### New Capabilities

| Capability | Description | Inspired By |
|-----------|-------------|-------------|
| **Plan-Approve-Execute** | All non-trivial workflows require user approval of a plan before execution begins | Claude Code `EnterPlanMode`/`ExitPlanMode` |
| **DAG-Based Task Management** | Structured task list with dependencies, ownership, and status tracking in `docs/tasks/` | Claude Code `TaskUpdate` with `blocks`/`blockedBy` |
| **Checkpoint Compression** | Phase-boundary summaries that replace full history for context-efficient delegation | Claude Code checkpoint system |
| **Validation Gates** | Structured PASS/CONDITIONAL_PASS/FAIL verdicts at quality checkpoints | Claude Code verification agent |
| **Blocker Escalation Protocol** | Typed blocker reports with deterministic routing and 2-retry limit before user escalation | Claude Code blocker handling |
| **Immutable Artifact Versioning** | `<type>-v<N>.md` naming with explicit dependency references | Claude Code immutable handoffs |
| **Structured Delegation Briefs** | Self-contained briefs with objective, context, inputs, constraints, outputs, criteria | Claude Code "brief like a smart colleague" |
| **Batch Processing** | Decompose sweeping changes into isolated units for parallel execution | Claude Code `/batch` skill |
| **Skillify** | Capture successful workflows as reusable skill files via structured interview | Claude Code `/skillify` skill |
| **Memory Consolidation** | Review and organize persistent memory (MCP Memory) with promote/prune workflow | Claude Code `/remember` + dream consolidation |
| **Token Governance** | Per-phase token budgets with tracking, warnings, and compression triggers | Claude Code cost governance |

### Carried Forward (Enhanced)

| Component | Count | Enhancement |
|-----------|-------|-------------|
| Production agents | 14 | Protocol-awareness (task completion, blocker reporting, artifact versioning) |
| PoC agents | 13 | Same protocol-awareness, lighter weight |
| Skills | 12 → 22 | 10 new skills for protocols + existing skills enhanced |
| Commands | 12 → 16 | 4 new commands (/plan, /batch, /skillify, /consolidate-memory) |
| Instructions | 4 | Enhanced with protocol rules |
| MCP servers | 7 | Configuration verified |
| Hooks | 1 | Carried forward |

### Removed / Changed

| Item | Change | Reason |
|------|--------|--------|
| Multi-platform support | Deferred to future | Focus on VS Code + Copilot first for quality |
| Implicit parallel delegation | Replaced by DAG | Explicit dependencies prevent conflicts |
| Unstructured agent output | Replaced by protocols | Standardized completion reports, VERDICTs, blocker reports |
| Feature flags | Removed for v1 | All features enabled; no gradual rollout needed initially |

## Architecture Comparison

```
DEV-Team-Recruiter:                    emage.code:
                                       
User → /command → Orchestrator         User → /command → Orchestrator
         ↓                                      ↓
    Delegate to agents                     Plan Phase (propose plan)
    (implicit coordination)                     ↓
         ↓                                 User Approval
    Agents work                                 ↓
    (hope for coherence)                   Execute Phase (DAG-ordered)
         ↓                                     ↓
    Result                                 Task T1 → Agent → Checkpoint
                                           Task T2 → Agent → Checkpoint
                                               ↓
                                           Review Phase (validation gates)
                                               ↓
                                           VERDICT → Proceed or Fix
                                               ↓
                                           Result (with audit trail)
```

## File Structure Comparison

```
DEV-Team-Recruiter:                    emage.code:

.github/                               .github/
  agents/ (27)                            agents/ (27, enhanced)
  skills/ (12)                            skills/ (22, 10 new)
  prompts/ (12)                           prompts/ (16, 4 new)
  instructions/ (4)                       instructions/ (4, enhanced)
  hooks/ (1)                              hooks/ (1)
  AGENTS.md                             AGENTS.md (rewritten)
.vscode/mcp.json                        .vscode/mcp.json
                                        docs/              ← NEW
                                          tasks/           ← task DAG state
                                          plans/           ← plan documents
                                          decisions/       ← ADRs
                                          checkpoints/     ← phase summaries
                                          artifacts/       ← versioned deliverables
```

## Migration Path

For existing DEV-Team-Recruiter users:

1. **Copy new `.github/` directory** — Replaces all agents, skills, prompts, instructions
2. **Copy new `AGENTS.md`** — New workspace conventions
3. **Create `docs/` directory** — New runtime state location
4. **Keep `.vscode/mcp.json`** — Compatible (may need minor update)
5. **No configuration changes needed** — Same environment variables, same MCP servers

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Orchestrator instructions too long for context | Medium | High | Compress instructions, externalize to skills, test token usage |
| Plan-approve-execute slows down simple tasks | Low | Medium | Orchestrator instructions skip plan for trivial tasks |
| File-based task state is fragile | Medium | Medium | Strict format enforcement in orchestrator; agents don't modify task list directly |
| Users unfamiliar with new protocol | Medium | Low | Clear docs, /plan command for visibility, gradual adoption |
| Copilot agent delegation limits | Low | High | Test with real Copilot; adjust delegation depth if needed |
