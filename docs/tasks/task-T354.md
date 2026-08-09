# Task T354 v2 — Generate & Validate Cline Platform Output (corrected format)

**ID:** T354
**Owner:** qa-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T353
**Created:** 2026-08-08 (revised 2026-08-09 for corrected Cline format)
**Based on:** `docs/plans/plan-028-cline-platform-integration-v2.md`; `implementation/platforms/cline.json`
(T352 v2); `implementation/scripts/sync.mjs` (T353 v2)

## Objective
Run the sync engine for Cline and verify the generated output structurally matches the corrected
format: `.clinerules/` at the **repo root**, `.cline/skills/`, `.cline/mcp.json`. Verification only —
no `sync.mjs` or manifest edits; route bugs back to T352/T353.

## Context
- Phase: Implementation (plan-028-v2, step 3 of 6).
- **This supersedes v1's brief entirely** — v1 checked for `.cline/rules/`, `alwaysApply`,
  `cline_mcp_settings.json`, `.cline/agents/`, and a root `.clinerules` single-file fallback. None of
  that applies anymore. Use only the criteria below.
- Run from the repo root: `node implementation/scripts/sync.mjs --platform=cline`.

## Inputs
- `implementation/platforms/cline.json` (T352 v2)
- `implementation/scripts/sync.mjs` (T353 v2)
- `implementation/knowledge/mcp/servers.yaml` — cross-reference for the MCP criterion

## Constraints
- Read-only with respect to `sync.mjs` and `cline.json`.
- Token budget: ≤ 15k.

## Expected Outputs
A validation note (`## Outcome`) with exact command output quoted for every criterion.

## Acceptance Criteria
- [ ] `node implementation/scripts/sync.mjs --platform=cline` exits 0
- [ ] `.clinerules/` exists at the **repository root** (sibling of `implementation/`, `README.md`,
      etc. — NOT nested under `.cline/`) and contains `*.md` files
- [ ] Spot-check at least 3 `.clinerules/*.md` files: frontmatter (if present) contains **only**
      `description` and/or `paths` — no `globs`, no `alwaysApply`. Quote one full frontmatter block
      from a file that has `paths` set and one from a file that has none (always-active rule)
- [ ] `.cline/skills/*/SKILL.md` files preserve the source directory tree structure under
      `implementation/knowledge/skills/` and have `name` + `description` frontmatter
- [ ] There is **no** `.cline/rules/`, **no** `.cline/agents/`, **no** `.cline/commands/`, and **no**
      root-level `.clinerules` (singular file) — confirm all four are absent (v1 leftovers must not
      linger; if any exist, that's a T353 bug to route back)
- [ ] `.cline/mcp.json` exists, is valid JSON (`python3 -m json.tool < .cline/mcp.json`), and its
      `mcpServers` object contains one entry per server in
      `implementation/knowledge/mcp/servers.yaml` tagged `core` or `extended` — count and compare
      exactly
- [ ] `.cline/.generated-manifest.json` exists; its `files` list includes entries like
      `../.clinerules/<name>.md` (relative-outside-outRoot paths) — **this is expected**, not a bug,
      per T353's brief. Confirm every file actually on disk under `.clinerules/` and `.cline/` appears
      somewhere in this manifest.
- [ ] `node implementation/scripts/sync.mjs --check --platform=cline` passes with no drift (run a
      second time after the first generation)
- [ ] `node implementation/scripts/sync.mjs --check` (all platforms, no `--platform` filter) passes
      with no drift for the 6 pre-existing platforms — independently re-confirm T353's own claim
      about this, don't just trust its Outcome section
- [ ] Task brief updated with an `## Outcome` section quoting actual command output for every
      criterion above

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. Any criterion
failure due to a genuine `cline.json`/`sync.mjs` bug is a `dependency` blocker of `major` severity —
report exactly which criterion failed and route back to T352 or T353, don't patch around it here.
