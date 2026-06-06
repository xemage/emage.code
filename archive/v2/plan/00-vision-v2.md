# 00 — Vision v2

## Why v2

v1 demonstrated the value of a multi-agent dev team driven by Plan-Approve-Execute, DAG task lists, validation gates, checkpoints, and per-phase token budgets. It also exposed two structural weaknesses that v2 fixes:

1. **Triple duplication.** The same 27 agents, 22 skills, 16 commands, and 4 instructions live three times: under `.github/`, `.gemini/`, and `.opencode/`. Every authoring change risks divergence; reviews are 3× larger; the only thing keeping platforms in lockstep is human discipline.
2. **Platform lock-in.** v1 supports GitHub Copilot, Gemini CLI, and Opencode. Cursor — a major user base — has no first-class adapter, even though its conventions (`.cursor/rules/*.mdc`, `AGENTS.md`, MCP) overlap heavily.

## v2 in one paragraph

A single canonical `knowledge/` folder holds every agent, skill, command, instruction, and MCP server. Each platform — GitHub, Gemini, Opencode, **and Cursor (new)** — has a JSON manifest declaring extensions, frontmatter transforms, and MCP profile. A Node script (`scripts/sync.mjs`) reads the manifest and projects `knowledge/` into a per-platform folder. CI (`scripts/verify.mjs`) refuses PRs where the generated folders drift from `knowledge/`.

## Design principles (carried from v1, sharpened)

- **One source of truth, many projections.** No platform owns content; all read from `knowledge/`.
- **Manifest > script.** Adding a platform is a JSON file, not a code change.
- **Determinism.** Same `knowledge/` + same manifest ⇒ byte-identical output. CI relies on this.
- **No external runtime deps.** `sync.mjs` uses only Node stdlib (no `npm install` to use the project).
- **Human-readable diffs.** Markdown stays markdown; YAML frontmatter stays text. Generated folders are committed so PRs show the user-visible delta.
- **Security explicit.** Secrets via env vars only; no inline keys; v1's leaked Toolradar token is rotated.

## Non-goals

- Replacing the agent / skill protocol from v1.
- Migration tooling for end-users with deployed v1 projects (manual copy is sufficient given the small footprint).
- A web UI or interactive scaffolder.

## Out-scope but compatible

The architecture is intentionally extensible to:
- New platforms (Claude Code, Aider, Continue.dev, …) — drop a manifest.
- Per-environment MCP profiles (dev / ci / prod) via additional tags.
- Knowledge variants (e.g., `enterprise` vs `oss` skill bundles) via tag filtering.
