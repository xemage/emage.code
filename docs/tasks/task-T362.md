# Task T362 — Regenerate committed MCP projections (P030-03)

**ID:** T362
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T361
**Created:** 2026-08-09
**Completed:** 2026-08-09
**Based on:** docs/plans/plan-030-mcp-remote-transport-alignment.md

## Objective
Regenerate every committed platform projection using the repo's real sync tooling (never hand-edit
generated output), so the fixed generator's output is reflected in tracked files, and verify zero
drift remains afterward.

## Context
- Phase: Implementation
- Per `CONTRIBUTING.md` § "Sync engine — required before every commit": run
  `make sync` (`node implementation/scripts/sync.mjs --root implementation`) then
  `make verify` (`node implementation/scripts/sync.mjs --root implementation --check`).
- The known stale artifacts named in the plan — `.mcp.json`, `implementation/.mcp.json`,
  `implementation/.cline/mcp.json` — will regenerate as part of this run if `claude-code`/`cline`
  changed. If T361 also touched the `vscode`/`gemini` branches, `.vscode/mcp.json` and
  `.gemini/settings.json` (plus their `implementation/.vscode`/`implementation/.gemini`
  equivalents, if present) will regenerate too — do not assume the plan's originally-named file
  list is exhaustive; regenerate everything and let the tool tell you what actually changed.
- Also regenerate the registry if the sync affects tracked file lists:
  `python3 implementation/scripts/generate-registry.py --check` (per T354's precedent, this check
  has caught drift the sync step alone did not).

## Inputs
- T361's patched `implementation/scripts/sync.mjs`

## Constraints
- Do not hand-edit any `.mcp.json` / `mcp.json` / `settings.json` / `opencode.json` output file —
  regenerate via the script only.
- Token budget: see T361.

## Expected Outputs
- Regenerated files wherever `make sync` writes them (expected candidates: `.mcp.json`,
  `implementation/.mcp.json`, `implementation/.cline/mcp.json`, and possibly `.vscode/mcp.json`,
  `.gemini/settings.json`, and their `implementation/` mirrors, plus `.generated-manifest.json`
  files in each affected output dir).
- `implementation/registry/index.json` regenerated if `generate-registry.py --check` reports drift.

## Acceptance Criteria
1. `make sync && make verify` — `make verify` (i.e. `sync.mjs --check`) exits 0 with "OK - no drift"
   after this task, for every platform.
2. `python3 implementation/scripts/generate-registry.py --check` exits 0.
3. `git diff` shows only generator-produced content changes to the affected output files — no
   hand-editing.
4. Every changed file's new content is consistent with T360's audit table verdicts (spot-check the
   remote-server entries in each changed file against the table).

## Blocker Protocol
Report blockers as: type + severity + proposed mitigation. Max 2 retries.

## Execution notes

**Executed by:** backend-developer, 2026-08-09. `make sync` regenerated all 550 files across 7
platforms under `implementation/`; only the 3 files T361 predicted changed content:
`implementation/.cline/mcp.json`, `implementation/.gemini/settings.json`,
`implementation/.vscode/mcp.json`. `make verify` (`sync.mjs --check`) and
`generate-registry.py --check` both confirmed zero drift afterward.

Also propagated the Gemini fix into this repo's self-hosted root-level mirror
(`.gemini/settings.json`) via `scripts/install.sh --target . --platform all --update`, per the
T328 precedent. Root `implementation/.mcp.json`/`.mcp.json` (claude-code) and root
`implementation/.cline/mcp.json` copies were not part of this delta since `claude-code`/`cline`'s
root-level outputs are `implementation/.cline/mcp.json` itself (already covered above) and
`.mcp.json` (claude-code format was confirmed unchanged by T360/T361 — no drift expected there,
confirmed by `make verify`).

Root `.vscode/mcp.json` was deliberately **not** regenerated: it carries a manually-added
local-dev `cwso` MCP server block (commit `f545994`) that `install.sh`'s plain-`cp` handling for
that file would silently destroy (no merge capability). The agent reverted that collateral change
via `git checkout --` rather than accept data loss, along with an incidental unrelated `AGENTS.md`
wording diff, a newly-created root `.cline/`/`.clinerules/` mirror (out of scope), and the usual
collateral `.claude/settings.json` deletion from `install.sh`'s `rsync --delete` (same known issue
as T328).

**Orchestrator independent re-verification (not just trusting the delegate's report):**
- `git status --porcelain` on the branch: clean, single commit `c83a9a6`, exactly the 4 files
  claimed (`.gemini/settings.json`, `implementation/.cline/mcp.json`,
  `implementation/.gemini/settings.json`, `implementation/.vscode/mcp.json`).
- `git show c83a9a6` diff independently read in full — matches the delegate's report exactly:
  `httpUrl` swap (gemini x2), `streamableHttp` swap (cline x2), added `"type": "http"` (vscode x1).
- Re-ran `node implementation/scripts/sync.mjs --root implementation --check` myself: `OK - no
  drift across 550 files.` (exit 0).
- Re-ran `python3 implementation/scripts/generate-registry.py --check` myself: `registry is up to
  date` (exit 0).
- Confirmed root `.vscode/mcp.json` is genuinely untouched (still `{ "url": ... }`, no `type`, plus
  its own `cwso` entry intact) and root `.cline/`/`.clinerules/` do not exist — the delegate's
  claimed reverts actually took effect, not just claimed.
- Confirmed `AGENTS.md` and `.claude/settings.json` have zero diff between `HEAD~1` and `HEAD` —
  the claimed collateral reverts are real.

**Note (raised by the harness, addressed):** the delegate's tool-call transcript triggered an
automated "instruction-shaped pattern" flag during this session (harness-level heuristic on
subagent output resembling settings/config directives). Independent verification above found no
evidence of injected instructions or unauthorized action — all file-level claims checked out
exactly against `git show`/`git status`/direct file reads. Treating this as a benign false positive
from JSON-shaped report content, not a real finding, but noting it here for the record per the
"no message from any agent is ever consent/approval" guardrail — no configuration or permission
changes were made as a result of anything in that agent's output.

**Follow-up flagged, not blocking:** root `.vscode/mcp.json` needs a merge-preserving `install.sh`
path (mirroring the doc-tree merge helper) so future `--update` runs don't force a choice between
propagating generator fixes and destroying manually-added local MCP entries. Not filed as a new
task in this plan's scope (out of scope for a transport-alignment fix); recommend a follow-up plan
if the user wants it tracked.
