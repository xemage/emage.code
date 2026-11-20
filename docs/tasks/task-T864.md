# T864 — Root refresh after the server-filesystem bump (T859)

**ID:** T864
**Owner:** orchestrator
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T860
**Affects:** —
**Created:** 2026-11-19
**Completed:** 2026-11-19
**Based on:**
- `docs/plans/plan-177-batch-x-ci-images-ca-runner.md` (§ Constraints: "A root refresh, if (d) bumps a pin, needs the user's approval at that moment")
- The user's approval of 2026-11-19 (question dialog, option label verbatim): "Refresh, keep python pin (Recommended)"

## 1. What and why

Refresh the three root MCP configs after T859's `server-filesystem` 2.4.0 pin.

## 2. Output

`.mcp.json`, `.cline/mcp.json` and `.opencode/opencode.json`, plus the emptied drift baseline, on `agent/devops-engineer/T859`.

## 3. Constraints

- Every commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No `.vscode` or `.claude` file is touched.

## 4. Acceptance criteria

- Exactly the 3 declared paths change.
- `--print-drift` gives `[]`.

## 5. Blocker protocol

Report each blocker with its type and severity.
