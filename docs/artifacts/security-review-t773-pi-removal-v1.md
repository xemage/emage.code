# Artifact: security-review-t773-pi-removal-v1.md

# Security Review T773 (security half): Pi platform removal, ADR-013 S1 and S2

**Based on:** branch `agent/technical-writer/T772` at `dc8042bc` (MR !659) against `docs/decisions/ADR-013-drop-pi-platform-support.md` (accepted 2026-11-07); base develop `04676e5f`.
**Reviewer:** security-engineer (read-only; no shell). Recorded by the orchestrator from the reviewer's final message, 2026-11-07; wording is the reviewer's, condensed.
**Method:** worktree files read directly; no git, test or generator run; the `security-audit` grep tool searches only the main checkout and failed on worktree paths.

## Summary
- **Risk level:** LOW
- **Findings:** 0 CRITICAL, 0 HIGH, 0 MEDIUM, 2 LOW
- **Status:** PASS; the two LOW findings are tracked as technical debt.

No security control removed or weakened; no Immutable Security Constraint breached. The installer has no path that writes to, deletes in or follows a link into an adopter's `.pi/`. The vscode-only emitter equals the old shared emitter's vscode branch for every input. The generic SEC-T680 guards are kept. CI tag jobs unchanged. In the docs only Pi text was removed; nothing about the remaining platforms was broadened.

## Findings

| id | grade | OWASP | location | description | fix | blocks? |
|---|---|---|---|---|---|---|
| SEC-T773-01 | SECURITY:LOW | A08 | `tests/functional/test_verify_release_docs.py:1925-1942` | The UTF-8 test now skips any release document named by `install.sh` that is missing and newer than the newest `docs/releases/v*.md`. The gate (`scripts/verify-release-docs.py:940-951`, unchanged) still rejects such a pointer at an older tag ("a version newer than {tag}") and at its own tag ("does not exist; write it before the tag is cut"), so the real tag stays protected. Gap: on develop the test cannot tell the intended pointer (`v11.0.0.md`) from a stray one (`v12.0.0.md`, `v11.1.0.md`); such a pointer is caught only at tag time. | Keep the skip, tighten it: at most one skipped pointer, and it must be the next release after `newest`; add a negative subtest. | No (debt) |
| SEC-T773-02 | SECURITY:LOW | A05 / A06 | `scripts/install.sh:1306-1326` (notice), ADR-013 D11 | Residual already accepted in ADR-013 D11: an adopter's `.pi/mcp.json` and `.pi/agents/*.md` stay frozen (pins, Playwright hardening, GitLab grants, pre-T680 forms). A `.pi/` with neither marker gets no notice; the notice appears only on `--update`/`--projections-only`. | The v11.0.0 release document carries the ADR-013 Appendix A migration item with cleanup steps and the frozen-state warning; release-manager confirms; register v12 records it. | No (debt) |

## Answers

**1. Installer.** The early refusal (`install.sh:184-201`) runs before `TARGET_ABS` is resolved and before any `mkdir`, in every mode; `[Pp][Ii]` covers all letter cases; the message is fixed text. `SUPPORTED_PLATFORMS` (line 20) has no `pi`; no `install_pi`; an unknown platform exits 70. The notice (1311-1326) only reads: early return if `.pi` is not a directory or is a symlink; manifest read with `grep -Eq` only when a regular non-symlink file; the sidecar only tested for existence. Only `$dir` (= `$TARGET/.pi`, through `printable`) reaches the terminal: no injection. `validate_before_update` iterates only `.github .gemini .opencode .claude .cline .clinerules`; no `install_*` names `.pi`, so `--update`, `--projections-only`, `--dry-run` cannot write there. A symlink race would only affect a read in the user's own directory. The tests in `test_install_removed_platform_v11.py` match ADR-013 D5.5 (a)–(e) (run by the orchestrator, not the reviewer).

**2. Generator.** `emitMcpVscode` (`sync.mjs:704-717`) equals develop's `emitMcpVscodePi` (`734-753`) on its vscode branch for all inputs (`${env:VAR}`, `mapEnv`, `{type:'http', url}` plus headers, `cwd` only for `workspace`, `env` written when set, `{servers}` wrapper). Other emitters unchanged; `mapEnvOmitOptional` deleted (Pi-only). `optional` validation kept, optional headers still refused (`316-320`). A leftover `skipFormats` key fails as an unknown key; `MCP_EMITTERS` rejects `pi`. No new secret handling.

**3. Deleted tests.** SEC-T680-01/-05/-07/-08/-09 generic guards moved to `test_merge_mcp_json_guards.py` (method count 22 → 22 is the orchestrator's, (unverified) by the reviewer). SEV-T690-06 grant drop still covered (`test_mcp_tool_name_mapping.py:313-347`). The removed `skipFormats` subcase tested an impossible path. No lost guard found; `test_gitlab_token_handling.py` and the deleted `test_github_security_servers.py` method not opened (unverified).

**4. Release-gate narrowing.** SEC-T773-01. The skip cannot hide a missing or invalid document at a real tag. Keep and tighten; do not replace.

**5. CI.** `unit-tests` gains only `git fetch --depth=1 origin tag v10.0.0` plus a comment, like the v8.0.0 fetch; no job-token reference. `main-develop-drift-gate` and `release` identical (offset +2); `release-docs-gate` compared by offset only (partly unverified). The test runs the project's own v10.0.0 installer in a job that binds the host Docker socket: same trust as the v8.0.0 precedent; tag protection of `v10.*` (unverified).

**6. Docs (S2).** `implementation/AGENTS.md:102, 116, 118`: only Pi clauses removed; no claim broadened; "not observed in a live run" qualifiers kept. `PREREQUISITES.md:165-175`: legend names only the Claude Code row as observed; 5 rows; other rows and "What this does not protect" intact. `docs/wiki/mcp-servers.md` not read (unverified). Pre-existing mismatch, not caused here: `PREREQUISITES.md:186` and the Opencode row say tool lists are not enforced on Opencode (K-15), while `AGENTS.md:116` says generated Opencode agents get per-agent denies (T663); tracked under K-23; worth aligning in Part C.

**7. Bookkeeping.** ADR-013 D11 correct: the Pi part of K-15/SEC-T657-01/SEC-T658-01 ends (remainder Gemini CLI, plan-146 Part C); Opencode stays K-23; K-20 and A-7 lose the Pi item; SEC-T680-02..-04 moot (the "headers cannot be optional" rule stays enforced generically); SEC-T680-01's Pi half moot. New for register v12: SEC-T773-01, -02.

## Compliance checklist
- [x] OWASP Top 10 reviewed (A01, A05, A08 in depth)
- [x] Authentication secure (no token-handling change)
- [x] Authorization enforced (tool-list and deny statements unchanged for remaining platforms)
- [x] Input validation complete (`--platform` refused early; unknown keys and formats fail closed)
- [x] Secrets management verified
- [x] Dependencies audited (no dependency change)
- [x] Security headers configured (not applicable)
- [x] Logging appropriate (stderr sanitised; no file content echoed)

## VERDICT: PASS

| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 2 | 0 | 2 |

### Conditions (LOW tracked as debt)
- SEC-T773-01: owner devops-engineer; tighten the skip to the single next-release pointer with a negative subtest; next sprint (register v12).
- SEC-T773-02: owner release-manager; the v11.0.0 release document carries the ADR-013 Appendix A Pi migration item and frozen-state warning; before the v11.0.0 tag.

### Blockers
None.

## Not verified
No test, generator or git command run by the reviewer; worktree `install.sh:360` checked on develop only; `release-docs-gate` by line offset; not opened: `docs/wiki/mcp-servers.md`, `test_gitlab_token_handling.py`, `test_mcp_optional_env.py`, full bodies of `test_merge_mcp_json_guards.py`, the inventory; tag protection of `v10.0.0`/`v8.0.0`; what Pi stores in `.pi/`; pre-T680 adopter files.
