# Using CWSO from emage.code

CWSO (Concurrent Workspace Orchestration) is a **separate, separately-deployed** MCP
server. This page explains what it is and how emage.code talks to it. It does not cover
installing, deploying, or operating CWSO itself — for that, go to the CWSO repository:

> **CWSO repository:** <https://gitlab.com/em-age/emage.code.cwso>

## What CWSO is

CWSO is a deterministic MCP orchestration backend that lets multiple agents edit the same
or related files at the same time, safely. Each agent gets its own isolated, in-memory
"shadow workspace" branched from a shared base commit, writes and commits independently,
and an orchestrator-role client runs an AST-aware (semantic, not line-based) conflict
pre-check before a structured `merge_concurrent_results` call produces one integrated
commit. Inside emage.code, this workflow is called **Pattern A**.

## When an emage.code user would reach for it

Reach for CWSO/Pattern A when a task genuinely calls for **N agents editing overlapping
files concurrently** rather than the default sequential, one-agent-at-a-time delegation
model. It is not needed for ordinary single-agent task execution.

## How emage.code talks to it

- **Connection:** a hand-added `cwso` entry in this repo's `.vscode/mcp.json`, pointed at
  a locally running CWSO instance (Streamable HTTP, JWT bearer auth). It is not part of
  the generated `implementation/knowledge/mcp/servers.yaml` registry — it is preserved
  verbatim across `sync`/`--update` runs the same way any hand-added MCP entry is (see
  [MCP Servers](../wiki/mcp-servers.md)).
- **Runtime client:** agent code calls CWSO through `implementation/runtime/cwso/`
  (`CwsoClient`, `AstConflictChecker`, `ConcurrentMergeOrchestrator`) — see that
  directory's `README.md` for the current, accurate usage patterns and a worked example.
- **Permission tiers:** the live CWSO server enforces role-gated tool permissions
  (`orchestrator` / `worker` / `read`). The approved emage.code-agent-to-tier mapping is
  `docs/artifacts/role-mapping-cwso-v1.md`. Before writing or dispatching any CWSO-related
  work, read the `cwso-awareness` skill
  (`implementation/knowledge/skills/cwso-awareness/SKILL.md`) — it explains the mandatory
  worker/orchestrator role split and the tier mapping in full; this page does not
  duplicate it.

## Deploying or configuring CWSO itself

Not covered here. See the CWSO repository linked above for installation, deployment
environments, and configuration.
