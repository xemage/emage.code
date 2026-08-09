# Task T364 — Update platform docs and release notes for MCP transport fix (P030-05)

**ID:** T364
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** T362
**Created:** 2026-08-09
**Completed:** 2026-08-09
**Based on:** docs/plans/plan-030-mcp-remote-transport-alignment.md

## Objective
Remove or correct any repo documentation that currently teaches the stale remote MCP transport
shape for the platforms T360 confirmed stale (expected: Cline, VS Code/GitHub Copilot, Gemini CLI),
and explicitly document that these platforms' remote transport encoding differs from Claude
Code/Cursor/Opencode's, since this plan's own premise (assuming one fix generalizes) turned out to
be wrong on inspection.

## Context
- Phase: Documentation
- Run only after T362 (regeneration) has settled, per the parent brief's explicit ordering
  requirement — do not write docs before the audited/regenerated shapes are final.
- Search likely locations: `README.md`, `docs/wiki/*.md` (especially any MCP setup or
  platform-specific setup pages, e.g. `docs/wiki/cline-setup.md` if it shows example MCP JSON),
  `implementation/knowledge/mcp/servers.yaml` header comments, `CONTRIBUTING.md` ("Adding a new
  platform" section already flags that MCP `format` may need a new branch — check if it needs an
  update noting the per-platform transport-field lesson from this plan).

## Inputs
- `docs/tasks/task-T360.md` (audit table)
- Regenerated artifacts from T362

## Constraints
- Docs-only change.
- If a platform differs from others (e.g. Gemini's `httpUrl` vs. everyone else's `url`/`type`),
  state that difference explicitly rather than implying one universal shape.
- Token budget: see T361.

## Expected Outputs
- Updated documentation removing/correcting stale transport examples.
- Draft content for the `docs/releases/v6.9.0.md` release notes' relevant bullet (classify as
  Bug Fixes given this is a fix-in-nature correction, unless T360's findings are judged
  release-note-worthy as a feature-level change by the orchestrator) — hand this draft bullet to
  the orchestrator/release-manager for T366, do not create the release file yourself.

## Acceptance Criteria
1. No repo doc still shows the pre-fix stale MCP JSON shape for Cline/VS Code/Gemini as a correct
   example.
2. Any doc that shows platform-specific MCP JSON examples for the affected platforms matches the
   regenerated, doc-confirmed shape.
3. Cross-platform divergence (e.g. Gemini's `httpUrl`) is stated explicitly somewhere discoverable,
   not left implicit.

## Blocker Protocol
Report blockers as: type + severity + proposed mitigation. Max 2 retries.

## Execution notes

**Executed by:** technical-writer, 2026-08-09. Updated `docs/wiki/mcp-servers.md` (new "Remote-server
transport encoding differs per platform" section with the full per-platform shape table, plus fixed
a pre-existing doc bug in the platform-output table and added missing Pi/Claude Code/Cline rows) and
`CONTRIBUTING.md` ("Adding a new platform" section gained a lesson paragraph pointing at
`docs/tasks/task-T360.md` and the new wiki table). No pre-existing docs were found teaching the
stale shape as correct after checking README.md, CONTRIBUTING.md, implementation/README.md,
implementation/knowledge/README.md, servers.yaml, and all `docs/wiki/*.md` pages (including
`cline-setup.md`, whose only MCP example uses the unaffected stdio `gitlab` server).

**Tooling gap (same as T356):** the Technical Writer role has no Bash/git tool access in this
session. It made both edits directly via the Edit tool on the already-checked-out branch but could
not `git add`/commit or report a SHA — reported this plainly rather than fabricating completion.
Orchestrator independently reviewed both diffs in full (`git diff CONTRIBUTING.md`,
`git diff docs/wiki/mcp-servers.md`) before committing on the delegate's behalf: content accurate,
consistent with T360's audit table, links point at real files (`docs/tasks/task-T360.md`,
`cline-setup.md` wiki page), no scope creep beyond docs. Committed as `21b60e0`.

**Draft release-note bullet (for T366):**
> **Fixed** — Corrected remote MCP server (`context7`, `hf-mcp-server`) transport encoding for
> Cline, VS Code/GitHub Copilot, and Gemini CLI. Cline previously emitted `"type": "http"`, which
> Cline does not recognize and silently falls back to a deprecated transport — corrected to
> `"type": "streamableHttp"`. VS Code was missing the required `"type"` field entirely — added.
> Gemini CLI was using the `"url"` key, which Gemini reserves for legacy SSE — corrected to
> `"httpUrl"`. Cursor, Opencode, and Claude Code were audited and confirmed already correct; no
> change. Regenerate your local platform configs (`make sync`, or reinstall via `install.sh
> --update`) to pick up the fix.
