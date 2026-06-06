# 05 — Migration from v1 to v2

> **Scope.** This guide is for repository maintainers moving the *project source* from v1 layout to v2 layout. **End-user projects already deployed with v1** (i.e. those that copied `.github/`, `.gemini/`, or `.opencode/` into their workspace) do not need to migrate — they keep working. This file is intentionally short because the user explicitly opted out of an end-user migration tool.

## Side-by-side

| Concern | v1 (`emage.code/implementation/`) | v2 (`emage.code/v2/implementation/`) |
|--------|-----------------------------------|---------------------------------------|
| Source of truth | distributed across `.github/`, `.gemini/`, `.opencode/` | `knowledge/` |
| Platforms | GitHub, Gemini, Opencode | GitHub, Gemini, Opencode, **Cursor** |
| MCP config | three independent JSON/JSONC files | `knowledge/mcp/servers.yaml` (single) |
| Adding a platform | manually duplicate every file | drop a `platforms/<name>.json` |
| Drift control | none (manual) | `scripts/verify.mjs` in CI |
| docs/ templates | empty `.gitkeep` only | `_template.md` per type |
| Security docs | none | `SECURITY.md` |
| Toolradar API key | leaked live key in three files | env-var reference only |
| Extension format | `.agent.md`, `.prompt.md`, `.instructions.md` (GitHub); `.md` (others) | unchanged in generated output; `.md` in `knowledge/` |

## What stays identical

- Every agent, skill, command, instruction body — content is byte-equal between v1 `.github/` and v2 `knowledge/`.
- The 6-layer architecture (commands → orchestration → agents → skills → memory → MCP).
- The Plan-Approve-Execute, DAG task, validation gate, checkpoint, and token-budget protocols.
- The 16 commands, 27 agents, 22 skills, 4 instructions.

## What's gone / changed

- v1's `MIGRATION.md` (v0→v1 mapping) is dropped.
- The Toolradar API key in v1 MCP configs is **rotated and replaced** with `${env:TOOLRADAR_API_KEY}`. **Anyone who used v1 must rotate that key with the issuing party.** See `SECURITY.md` § 2.
- `.opencode/` no longer commits `node_modules/` or `package-lock.json`. (The Opencode plugin layer was unused in v1.)
- `phase 2–7` detail docs that v1's `plan/05-implementation-phases.md` referenced but never delivered are present in `plan/v2/06..11-phase{2..7}-detail.md`.

## How to maintain v1 alongside v2

`emage.code/implementation/` is **not modified**. Maintainers can:
- accept critical fixes there (security-only) and cherry-pick into `knowledge/`, or
- declare v1 frozen and direct all new work to v2.

The recommended posture: declare v1 frozen on the day v2 ships. CI is wired only to `v2/implementation/`.

## How to switch a project from v1 to v2 (manual)

1. Pick a platform.
2. Delete the existing `.github/` (or `.gemini/`, `.opencode/`) from the project.
3. Copy the matching v2 generated folder + `AGENTS.md` + `docs/`.
4. Update `.vscode/mcp.json` from v2's emitted file.
5. Rotate any leaked credentials.
6. Run a smoke test: `/new-feature "..."`. Orchestrator should still propose a plan.
