# Artifact: security-review-t712-brave-stdio-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. Read-only: no shell; the diffs were read from files the orchestrator exported, the published 2.1.4 `dist/index.js` and `dist/config.js` through unpkg. Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-11-01.
- **Target**: T712 on `chore/plan-124-wave-1` at `f131590d` (`6555dfc9` brave launch with `--transport stdio`; `0fff68ad` audit gate follows reverse `via` links; `3185d89a` acceptance v3 and checklist).
- **Based on**: `docs/tasks/task-T712.md`; `docs/artifacts/security-review-t702-brave-reachability-v1.md`; `scripts/audit-mcp-pins.py`, `tests/functional/test_audit_mcp_pins_hardening.py`, `test_mcp_package_pins.py`, `test_pin_bump_checklist.py`; `docs/artifacts/brave-audit-acceptance-v3.md`; `docs/wiki/mcp-pin-bump-checklist.md`; the six generated MCP configs under `implementation/`.
- **Orchestrator checks relied on**: the v3 gate command with the seven entries exits 0 and without GHSA-f897-62hf-6gxq exits 1; the root drift was the six generated configs, cleared by the twenty-second root refresh on this branch (only the brave arguments changed).

## Verdict: CONDITIONAL_PASS

0 critical, 0 high; no Immutable Security Constraint breached; no control weakened. The condition is the carried MEDIUM SEC-T702-09 (the pin ships seven known advisories), whose remediation plan is acceptance v3 (owner devops-engineer; by 2027-01-30 or the first Brave release above 2.1.4).

- **Gate change** (`scripts/audit-mcp-pins.py:268-292`): more roots can only require more acceptances (`fully_accepted` needs `(advisory, root)` for every root); an entry that reaches no pinned package is still refused (fail-closed). It is stricter than before: a second pin that names the shared library only in its own `via` now keeps the library a finding (a latent wrong acceptance before T712). Cycles end (`seen` per path) and are refused; string/dict `via` entries are handled; the traversal is not memoised (no security effect at this pin-set size).
- **`--transport stdio`**: the published `dist/index.js` starts HTTP only for `options.transport === 'http'`; `dist/config.js` uses the environment only as the commander default. SEC-T702-07 is closed in the source and the six generated configs, and in the root install after the twenty-second refresh.
- **Acceptance v3**: the user's words match `task-T712.md` verbatim; all seven ids, expiry 2027-01-30 (exactly 90 days from 2026-11-01), the stdio condition, the re-audit triggers and "only the user can renew" are present.

## Findings

| Id | Grade | Location | Finding | Status |
|---|---|---|---|---|
| SEC-T712-01 | LOW | `brave-audit-acceptance-v3.md:10` | The grading was cited as "relayed in the T712 brief"; the grading artifact was not cited. | fixed in this branch (cites `security-review-t702-brave-reachability-v1.md`) |
| SEC-T712-02 | LOW | `brave-audit-acceptance-v3.md` Reasoning §1 | "stdio whatever the environment says" stated as fact; it is read, not run. Recommended a live check: dummy key, `BRAVE_MCP_TRANSPORT=http`, launch with `--transport stdio`, no listener. | wording fixed in this branch ("read, not run; L-3"); the live check is a user action (**UA-T712-1**, before the v9.0.0 tag): the orchestrator's attempt to run the package was refused by the session's permission check |
| SEC-T712-03 | LOW | `brave-audit-acceptance-v3.md` (mrhx row, Reasoning §3) | The zod input was called "trusted local client" input; the prompt-injection caveat was missing. | fixed in this branch |
| SEC-T712-04 | LOW | `brave-audit-acceptance-v3.md` Reasoning §4 | "Fixed versions not published" contradicted the other pins resolving sdk 1.32.2 and zod 4.6.7; the point is that no Brave release carries them. | fixed in this branch |
| SEC-T712-05 | LOW | `tests/functional/test_audit_mcp_pins_hardening.py` | No test for a `via` cycle, a `via`-dependent reaching no pinned package, mixed dict/string `via` lists, a non-list `via`. | tracked-LOW; devops-engineer; next change to `audit-mcp-pins.py` |
| SEC-T712-06 | LOW | the root install | The fix reaches installed configs only after the root refresh. | met: the twenty-second refresh on this branch (`21045301`) |

Carried: SEC-T702-09 (MEDIUM, remediation plan acceptance v3), SEC-T702-08 (LOW, tracked).

## Unverified

- That the CLI flag overrides the environment and `.env` (read from the published `dist` through unpkg, not run; UA-T712-1).
- That `npx -y <pkg> --transport stdio` passes the flag to the binary (the same form as other shipped entries).
- The npm 11.17.0 `effects` asymmetry (the implementer's observation).
- The checklist §4 command with `--signatures` and the seven acceptances has not been observed passing.
