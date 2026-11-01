# Artifact: security-review-t678-cursor-docs-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test or generator run; the changed files were read at the worktree and compared with the base checkout). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-22.
- **Target**: T678, commit `0d1dd838` on `agent/technical-writer/T678` (from develop `5dfd12fa`): ADR-010 step S2, Cursor removed from live docs, knowledge text and templates.
- **Based on**: `docs/tasks/task-T678.md`, `docs/decisions/ADR-010-drop-cursor-platform-support.md` (S2 row, documentation-assertions paragraph), `docs/plans/plan-123-post-release-follow-ups.md`.
- **Orchestrator checks**: full suite 1475 tests OK (skipped 23), all gates pass (sync, registry, maturity, scorecard 34/30/0, ledger, held-out isolation, version consistency), the Cursor grep over `implementation/` returns only the `ux-designer` false positives.

## Verdict: PASS

0 critical, 0 high, 0 medium, 3 LOW. The GitLab-grants, six-tool Playwright denial and Opencode per-agent denial paragraphs are textually unchanged apart from the Cursor sentences; every caveat is kept (Gemini gap, "not observed in a live run", "a policy, not an enforcement", the token and `execute` exposure, built-in agents, `playwright-local`). The `SECURITY.md` `${env:VAR}` platform list matches `sync.mjs`. No secret was added. The platform counts checked are consistent.

## Findings

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T678-01 | LOW | `tests/functional/test_mcp_server_denials.py:654` guard regex still names Cursor, so it can no longer match the current wording; make the Cursor part optional | handed to T673 (same file, SEC-T658-06 anchoring work) |
| SEC-T678-02 | LOW | Two live citations of `mcp-server-denials-v1.md` (`docs/wiki/mcp-servers.md:78`, `implementation/PREREQUISITES.md:33`) lacked the "recorded before Cursor was removed" clause | fixed in the T678 branch |
| SEC-T678-03 | LOW | No live doc says that a leftover `.cursor/` in an adopter project is no longer updated and that its agents are not tool-restricted | goes into the v9.0.0 migration item (ADR-010 Appendix A, release document); recorded in `task-T679.md` and the release checklist |

## Not read by the reviewer (unverified)

Root `AGENTS.md` lines 1-79, `implementation/README.md`, wiki pages quick-start, cline-setup, architecture, instructions-overview and contributing-workflow, the `.gitlab` templates, README beyond line 175, the generated mirrors and the registry (the orchestrator's gates cover the last two).
