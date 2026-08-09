# Task T361 — Patch generator transport mapping for confirmed-stale platforms (P030-02)

**ID:** T361
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T360
**Created:** 2026-08-09
**Completed:** 2026-08-09
**Based on:** docs/plans/plan-030-mcp-remote-transport-alignment.md; docs/tasks/task-T360.md

## Objective
Update only the `emitMcp()` format branches in `implementation/scripts/sync.mjs` that T360's audit
table marked "change needed: Y", to the exact doc-confirmed correct value. Leave every branch T360
marked "no change" byte-for-byte untouched — this task's diff must be traceable line-for-line back
to a specific audit table row.

## Context
- Phase: Implementation
- Preliminary orchestrator research (see plan-030's "Plan Review Corrections" section) found three
  likely candidates, subject to T360's final confirmation:
  1. `cline` branch (~line 365-375): `{ type: 'http', url: s.url }` → should become
     `{ type: 'streamableHttp', url: s.url }`
  2. `vscode` branch (shared with `cursor`, ~line 298-309): remote entries currently emit only
     `{ url: s.url }` with no `type` key at all for the `vscode` output path specifically (the
     `cursor` output path sharing this code block is expected to stay `{ url: s.url }` — do NOT
     add a `type` key to the `cursor` output, only to `vscode`'s). VS Code's schema requires
     `type: "http"` as a mandatory field for HTTP/SSE remote servers.
  3. `gemini` branch (~line 311-339): remote entries currently use the `url` key
     (`mcpServers[name] = { url: s.url }`), but Gemini CLI reserves `url` for legacy SSE and
     requires the `httpUrl` key for streamable-HTTP remotes.
- Do not trust the above as final — T360 is the source of truth. If T360's table disagrees with
  this preliminary list (finds fewer, more, or different platforms stale, or a different correct
  value), follow T360, not this brief's preliminary guess, and note the discrepancy in Execution
  notes.
- The `vscode`/`cursor` shared code block (lines ~298-309) will need to branch its remote-entry
  logic per-format if `vscode` needs a field `cursor` does not — do this as a minimal, targeted
  `format === 'vscode'` vs `format === 'cursor'` split inside that block, not a broader refactor.

## Inputs
- `docs/tasks/task-T360.md` — the audit table (authoritative)
- `implementation/scripts/sync.mjs`

## Constraints
- Minimal, targeted diff only — no unrelated refactor of `sync.mjs`.
- Every changed line must map to a T360 table row marked "Y".
- Every unchanged branch must remain byte-identical.
- No new npm/node dependencies.
- Token budget: implementation phase overall ≤120k across T360-T365.

## Expected Outputs
- Modified `implementation/scripts/sync.mjs` (generator only — do not hand-edit any generated
  output file in this task; that is T362's job).

## Acceptance Criteria
1. `git diff implementation/scripts/sync.mjs` touches only the branches T360 marked stale.
2. `node implementation/scripts/sync.mjs --root implementation --check` is expected to now report
   drift for the platforms just changed here (that drift is resolved by T362, not this task) — no
   syntax errors, script still runs.
3. No behavior change to any platform's stdio-server (`command`/`args`/`env`) emission.

## Blocker Protocol
Report blockers as: type + severity + proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
