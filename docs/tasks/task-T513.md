# T513 — Fix context-retriever / security-audit MCP servers never working outside this repo

**Status:** done
**Owner:** top-level session
**Priority:** P0
**Depends on:** none
**Completed:** 2026-09-19
**Based on:** the user's explicit bug report ("The installed version of the 'context-retriever' MCP server seems not to work. It shows error (Connection closed)... Same problem in CWSO project... The problem also seems to exist for other platforms like Github Copilot. Investigate and debug this issue.")

## Objective

Root-cause and fix a real, user-reported connectivity failure affecting two real MCP servers
(`@context-retriever`, `@security-engineer`'s `security-audit`) across at least two real projects
and multiple platform clients. Mandatory `systematic-debugging` skill followed: no fix proposed
before root cause was confirmed by direct reproduction.

## Inputs

- The user's bug report (repo, symptom, affected projects, affected platforms).
- `implementation/runtime/memory/context_retriever_mcp_server/`, `implementation/runtime/security/`
  (T495/T497's already-shipped server code).
- `scripts/install.sh` (the actual distribution mechanism).

## Outputs

- `scripts/install.sh`: new `install_mcp_server_runtime()` step; `copy_tree_into()`/
  `sync_tree_into()` exclude-path and directory-safety fixes; explicit post-install notices for the
  pip-install and index-build steps; `set -e`-safe conditional fixes (a real bug in this task's own
  first fix attempt, caught by CI).
- Both real environments (this repo, CWSO) fixed live: dependencies installed, per-project search
  indexes built, both servers confirmed starting cleanly and answering real queries.

## Acceptance criteria

- [x] Root cause identified by direct reproduction, not assumption (three independent, compounding
      gaps, each reproduced before being fixed)
- [x] Fix verified end-to-end against a fresh throwaway target directory, both fresh install and
      `--update`
- [x] Previously-skipped live adversarial test suites now pass for real:
      `test_context_retriever_mcp_server.py` (8/8), `test_audit_server.py` (30/31, 1 unrelated skip)
- [x] CI green on the actual merge request, not just local testing (a real gap between the two was
      found and fixed within this same task)
- [x] Full verification bar green: `tests/run.py`, `sync.mjs --check`, `check-maturity.py`,
      `validate-tasks.py`
- [x] Both real, currently-in-use environments (this repo, CWSO) independently confirmed working,
      not just the code merged

## Execution notes

See `docs/tasks/completed-tasks.md`'s T513 row for the full closure record, including a fourth,
distinct, deliberately-unscoped finding (a hardcoded per-project index directory name in
`servers.yaml`) flagged for the user's own future decision rather than silently redesigned.
