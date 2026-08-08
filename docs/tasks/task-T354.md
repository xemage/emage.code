# Task T354 — Generate & Validate Cline Platform Output

**ID:** T354
**Owner:** qa-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T353
**Created:** 2026-08-08
**Based on:** `docs/plans/plan-028-cline-platform-integration.md`; `implementation/platforms/cline.json`
(T352); `implementation/scripts/sync.mjs` (T353)

## Objective
Run the sync engine for Cline and verify the generated `.cline/` output structurally matches what
`cline.json` declares. **Verification only** — this task must not modify `sync.mjs` or the manifest.
If either needs a fix to pass these checks, that fix belongs back in T352/T353 and this task is
re-run afterward — do not patch around a bug here.

## Context
- Phase: Implementation (plan-028, step 3 of 6).
- Run from the repo root: `node implementation/scripts/sync.mjs --platform=cline`. This generates
  `.cline/` at the repo root (sibling to `.cursor/`, `.github/`, etc. — confirmed by reading
  `sync.mjs`'s output-path logic, which joins `outputDir` from the manifest against the repo root).

## Inputs
- `implementation/platforms/cline.json` (T352's output)
- `implementation/scripts/sync.mjs` (T353's output)
- `implementation/knowledge/mcp/servers.yaml` — cross-reference for the MCP acceptance criterion
  below

## Constraints
- Read-only with respect to `sync.mjs` and `implementation/platforms/cline.json`. You may run
  commands and inspect generated output; you may not edit either of those two files.
- Token budget: ≤ 15k.

## Expected Outputs
A validation note (append to this brief's `## Outcome` section) covering every acceptance criterion
below, with exact command output quoted, not paraphrased.

## Acceptance Criteria
- [ ] `node implementation/scripts/sync.mjs --platform=cline` exits 0
- [ ] `.cline/rules/*.md` files each have YAML frontmatter containing `description`, `globs`, and
      `alwaysApply` — spot-check at least 3 files, quote one full frontmatter block
- [ ] `.cline/skills/*/SKILL.md` files preserve the source directory tree structure under
      `implementation/knowledge/skills/` (compare directory names, not just file count) and have
      frontmatter containing `name` and `description`
- [ ] `.cline/agents/*.md` files have `tools` rendered as a **plain comma-separated string** on a
      single YAML line, e.g. `tools: read_file, search_files, apply_diff` — not a YAML list
      (`tools: [read_file, ...]`) and not a boolean map. Quote one full agent frontmatter block.
- [ ] `.cline/cline_mcp_settings.json` exists, is valid JSON
      (`python3 -m json.tool < .cline/cline_mcp_settings.json`), and its `mcpServers` object contains
      one entry for every server in `implementation/knowledge/mcp/servers.yaml` tagged `core` or
      `extended` — count servers in `servers.yaml` with those tags and confirm the count matches
      `mcpServers` key count exactly
- [ ] `.cline/.generated-manifest.json` exists and lists the emitted files (compare against
      `find .cline -type f` output — every file under `.cline/` should appear in the manifest list)
- [ ] Root `.clinerules` file exists (emitted from `_extras/cline/dot-clinerules` per the `extras`
      entry) and contains an `@AGENTS.md` line plus a note mentioning `.cline/rules/`
- [ ] `node implementation/scripts/sync.mjs --check --platform=cline` passes with no drift (run it a
      second time after the first generation — it must report no changes)
- [ ] Task brief updated with an `## Outcome` section quoting the actual command output for each
      criterion above

## Blocker Protocol
Report blockers per `AGENTS.md`: type + severity. Max 2 retries before escalation. If any criterion
fails because of a genuine bug in `cline.json` or `sync.mjs` (not a mistake in this task's own
commands), that is a `dependency` blocker of `major` severity — report exactly which criterion failed,
the actual vs. expected output, and route back to T352 or T353 rather than attempting a fix here.
