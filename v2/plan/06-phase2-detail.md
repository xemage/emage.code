# 06 — Phase 2 detail: Agent enhancement

> Backfill of the v1 Phase-2 placeholder in [`../05-implementation-phases.md`](../05-implementation-phases.md).

## Goal
Every agent in `knowledge/agents/` carries a **Protocol Awareness** section that anchors it in the v2 protocols (Plan-Approve-Execute, task-management, blocker-escalation, validation-gates, artifact-versioning, token-governance).

## Required section template

Inserted after the agent identity, before role-specific instructions:

```markdown
## Protocol Awareness

You operate inside emage.code v2. Honor these protocols at all times:

- **Plan-Approve-Execute** — never start non-trivial work without an approved plan.
- **Task contract** — read your task brief in `docs/tasks/task-<ID>.md`; report blockers to the orchestrator only; never modify the task list yourself.
- **Artifacts are immutable** — produce `<type>-v<N>.md`; do not overwrite existing versions.
- **Blockers** — typed (`technical` / `dependency` / `unclear_requirements` / `external`), severity-graded, max 2 retries.
- **Validation gates** (review agents only) — verdict ∈ {`PASS`, `CONDITIONAL_PASS`, `FAIL`}; do not modify code during review.
- **Token budget** — your phase has a budget (see `AGENTS.md`); compress and hand off when nearing 80% utilization.
- **MCP** — use only servers listed in your `tools:` frontmatter.
```

## Acceptance criteria
- [ ] All 27 agents in `knowledge/agents/` contain the section verbatim or a justified variant.
- [ ] Reviewer-type agents (Tech Lead, QA Engineer, Security Engineer) include the validation-gate clause prominently.
- [ ] Orchestrators reference the section and require their subagents to honor it.

## Verification
- `grep -L "## Protocol Awareness" knowledge/agents/*.md` returns no files.
- Smoke-test: launch orchestrator on an empty workspace; have it delegate a trivial task; the assigned agent's first response references the protocol.
