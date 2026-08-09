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
Run the sync engine for Cline, **generate and commit its canonical output**
(`implementation/.cline/` and `implementation/.clinerules/`, matching how the 6 existing platforms'
generated trees are committed — e.g. `implementation/.cursor/`, `implementation/.claude/`), and
verify the output structurally matches the corrected format. Not pure verification this time — this
task's output is the actual tracked generated tree, not just a report. No `sync.mjs`/manifest source
edits; route bugs back to T352/T353.

## Context
- Phase: Implementation (plan-028-v2, step 3 of 6).
- **This supersedes v1's brief entirely** — v1 checked for `.cline/rules/`, `alwaysApply`,
  `cline_mcp_settings.json`, `.cline/agents/`, and a root `.clinerules` single-file fallback. None of
  that applies anymore. Use only the criteria below.
- **Important, confirmed by the orchestrator via direct testing before this task was dispatched**:
  this repo has two separate output layers. `implementation/.cursor/`, `implementation/.claude/`,
  etc. are the **canonical generated source**, committed to the repo, and CI-gated by
  `node implementation/scripts/sync.mjs --root implementation --check` (this is what `make verify`
  and the `sync-no-diff`/`verify-knowledge-drift` CI jobs actually check). Separately, this repo also
  has root-level `.cursor/`, `.claude/`, etc. — its own dogfooded self-install, **not** continuously
  CI-checked against `implementation/`. **Your job is the first layer only**:
  `implementation/.cline/` and `implementation/.clinerules/`. Do not create or touch bare
  repo-root `.cline/` or `.clinerules/` — that's a separate, out-of-scope concern (this repo's own
  self-install refresh, not part of this plan).
- Run from the repo root exactly as CI does: `node implementation/scripts/sync.mjs --root
  implementation --platform=cline` (the `--root implementation` is what makes `ROOT` resolve
  correctly — it happens to equal `sync.mjs`'s own default when omitted, since `ROOT` defaults to
  `path.resolve(__dirname, '..')`, but pass it explicitly anyway to match CI's actual invocation
  precisely and avoid ambiguity).

## Inputs
- `implementation/platforms/cline.json` (T352 v2)
- `implementation/scripts/sync.mjs` (T353 v2)
- `implementation/knowledge/mcp/servers.yaml` — cross-reference for the MCP criterion

## Constraints
- Read-only with respect to `implementation/scripts/sync.mjs` and `implementation/platforms/cline.json`
  (the source files) — but you ARE expected to write, `git add`, and commit the generated
  `implementation/.cline/` and `implementation/.clinerules/` output itself; that's this task's actual
  deliverable, not a side effect to discard.
- Do not touch bare repo-root `.cline/` or `.clinerules/` (see Context) or any other platform's
  generated tree under `implementation/`.
- Token budget: ≤ 15k.

## Expected Outputs
- `implementation/.cline/` (skills + `mcp.json` + `.generated-manifest.json`) and
  `implementation/.clinerules/` (`*.md` rules) — generated, `git add`-ed, and committed, the same way
  `implementation/.cursor/` etc. are tracked.
- A validation note (`## Outcome`) with exact command output quoted for every criterion.

## Acceptance Criteria
- [ ] `node implementation/scripts/sync.mjs --root implementation --platform=cline` exits 0
- [ ] `implementation/.clinerules/` exists (sibling of `implementation/.cline/`,
      `implementation/.cursor/`, etc. — NOT bare repo-root `.clinerules/`, NOT nested under
      `implementation/.cline/`) and contains `*.md` files
- [ ] Spot-check at least 3 `implementation/.clinerules/*.md` files: frontmatter (if present)
      contains **only** `description` and/or `paths` — no `globs`, no `alwaysApply`. Quote one full
      frontmatter block from a file that has `paths` set and one from a file that has none
      (always-active rule)
- [ ] `implementation/.cline/skills/*/SKILL.md` files preserve the source directory tree structure
      under `implementation/knowledge/skills/` and have `name` + `description` frontmatter
- [ ] There is **no** `implementation/.cline/rules/`, **no** `implementation/.cline/agents/`, **no**
      `implementation/.cline/commands/`, and **no** bare repo-root `.clinerules` (singular file) —
      confirm all four are absent (v1 leftovers must not linger; if any exist, that's a T353 bug to
      route back)
- [ ] `implementation/.cline/mcp.json` exists, is valid JSON
      (`python3 -m json.tool < implementation/.cline/mcp.json`), and its `mcpServers` object contains
      one entry per server in `implementation/knowledge/mcp/servers.yaml` tagged `core` or
      `extended` — count and compare exactly
- [ ] `implementation/.cline/.generated-manifest.json` exists; its `files` list includes entries like
      `../.clinerules/<name>.md` (relative-outside-outRoot paths) — **this is expected**, not a bug,
      per T353's brief. Confirm every file actually on disk under `implementation/.clinerules/` and
      `implementation/.cline/` appears somewhere in this manifest.
- [ ] `node implementation/scripts/sync.mjs --root implementation --check --platform=cline` passes
      with no drift (run a second time after the first generation and commit — proves the generated
      output is stable/deterministic, not just "generated once")
- [ ] `node implementation/scripts/sync.mjs --root implementation --check` (all platforms, no
      `--platform` filter) passes with no drift for the 6 pre-existing platforms — independently
      re-confirm T353's own claim about this, don't just trust its Outcome section
- [ ] `implementation/.cline/` and `implementation/.clinerules/` are `git add`-ed and committed in
      this task's own commit (verify with `git show --stat HEAD` before opening the MR — both
      directories' files must appear)
- [ ] Task brief updated with an `## Outcome` section quoting actual command output for every
      criterion above

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. Any criterion
failure due to a genuine `cline.json`/`sync.mjs` bug is a `dependency` blocker of `major` severity —
report exactly which criterion failed and route back to T352 or T353, don't patch around it here.
