---
title: Migration v1 to v2
---
# Migration v1 → v2

The full migration guide lives at [`v2/plan/05-migration-from-v1.md`](https://gitlab.com/em-age/emage.code/-/blob/main/v2/plan/05-migration-from-v1.md). This page is the executive summary.

## What changed

| | v1 | v2 |
|---|----|----|
| Source of truth | per-platform folders, **triple-duplicated** | single `knowledge/` tree |
| Platforms | GitHub Copilot, Gemini CLI, Opencode | + **Cursor** |
| MCP config | three divergent JSON files | one `mcp/servers.yaml` registry |
| Drift detection | none | `verify.mjs` + CI gate |
| `docs/` templates | empty `.gitkeep` placeholders | populated templates |
| Security docs | scattered | `SECURITY.md` + threat model |
| `.gitignore` | missing | present |

## Why migrate?

- **One edit, four platforms** — change a skill in `knowledge/` and all generated mirrors update on next sync.
- **Drift is impossible** — CI fails the pipeline if generated folders deviate from `knowledge/`.
- **Easier to add platforms** — Cursor was added without touching the sync engine.
- **Cleaner reviews** — MRs touch the canonical source, not three copies.

## Steps

1. **Don't migrate in place.** v1 is frozen and stays at [`v1/`](https://gitlab.com/em-age/emage.code/-/tree/main/v1).
2. Adopt v2 in your project by copying the relevant platform folder from [`v2/implementation/`](https://gitlab.com/em-age/emage.code/-/tree/main/v2/implementation) — see [Quick Start](quick-start).
3. Migrate any custom agents/skills you wrote in v1:
   - Place them under `v2/implementation/knowledge/agents/` or `knowledge/skills/`
   - Run `node scripts/sync.mjs`
4. Migrate MCP server overrides into `knowledge/mcp/servers.yaml` (single registry).
5. Re-run your test commands; the agent set is identical, only the wiring changed.

## Compatibility notes

- Slash commands have the same names — `/new-project`, `/checkpoint`, etc.
- Lifecycle states unchanged (`pending → in_progress → blocked → in_review → done | cancelled`)
- Validation gates unchanged
- Workspace conventions in `AGENTS.md` are largely identical (the v2 version adds knowledge-base authoring rules)

## Known v1 limitations preserved (for reference only)

- v1 SKILL `references/` placeholder links remain broken (templates were never authored). v2 fixes these.
- v1 has **no CI** for drift detection. v2 adds the `.gitlab-ci.yml` pipeline.

## Questions

Open an issue tagged `migration` or ask in the wiki discussion thread.
