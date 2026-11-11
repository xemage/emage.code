# Artifact: security-review-t780-gemini-removal-v1.md

# Security Review T780 (security half): Gemini CLI removal (ADR-014 S1 + S2)

**Based on:** branch `agent/technical-writer/T779` at `21922dcd` (MR !662) against develop `522b1bd0`; `docs/decisions/ADR-014-drop-gemini-platform-support.md` (accepted 2026-11-07); `docs/artifacts/gemini-removal-inventory-v1.md` (`58efdc5f`); precedent `security-review-t773-pi-removal-v1.md`.
**Reviewer:** security-engineer (read-only; no shell). Recorded by the orchestrator from the reviewer's final message, 2026-11-11, condensed; wording is the reviewer's. The `grep_content` tool reaches only the main checkout, so worktree files were read directly; the full D1 grep is the tech-lead half's.

## Summary
- **Risk level:** LOW
- **Findings:** 0 CRITICAL, 0 HIGH, 0 MEDIUM, 7 LOW (two outside the change or user actions)
- **Gate:** PASS; each LOW tracked as debt (register v12).
- **SEC-T657-01 / SEC-T658-01:** close by removal at v11.0.0.

## Findings

| ID | Grade | OWASP | Location | Description | Fix | Blocks? |
|---|---|---|---|---|---|---|
| SEC-T780-01 | SECURITY:LOW | A05 (doc accuracy) | `implementation/PREREQUISITES.md:172`, posture table, Opencode row | Cell still reads "No (K-15); the server-side limits below are the only enforced control"; K-15 ends with ADR-014 and since T663 generated Opencode agents are restricted per agent; contradicts line 184 and the closure. Pre-existing; S2 left it. | Cell: "Partly: generated agents yes, by per-agent `false` entries (T663; documented and read from vendor source, not observed in a live tool call); built-in agents and your own agent files no (K-23), and for them the server-side limits below are the only enforced control"; align any test pinning "No (K-15)". Recommended before merge. | No |
| SEC-T780-02 | SECURITY:LOW | A08 | `tests/functional/test_mcp_package_pins.py:873` | The no-Gemini-clause check skips `agents-root` unconditionally, while the relaxation at 870-871 is drift-gated; after S3 nothing in this test guards the root file (parity gate and D1 grep compensate). | At T781: `if label != "agents-root" or not _root_agents_md_is_declared_drift():` | No |
| SEC-T780-03 | SECURITY:LOW | A04 | `tests/functional/test_install_removed_platform_v11.py:570-592` | Source scans would not catch a write/delete through `$dir` inside `notice_previous_gemini_install` (first scan needs literal `.gemini`; second checks reads only); snapshot tests catch it at run time. | Also `assertNotRegex(code_line, r"\b(rm\|mv\|cp\|rsync\|mkdir\|tee\|touch\|chmod\|ln\|sed)\b\|>")` per body line; same for the Pi notice. | No |
| SEC-T780-04 | SECURITY:LOW | A05 | `scripts/install.sh:1340-1341` (also 1288-1289 Cursor, 1317-1318 Pi) | Check-then-grep gap: a FIFO swapped in after `[[ -f … && ! -L … ]]` makes `grep -Eq` block (hang only; `-q` exposes no content). | `grep -D skip -Eq …` (portability unverified) or read via `timeout`; all three notices. | No |
| SEC-T780-05 | SECURITY:LOW | A05/A08 (SEC-T773-02 class) | adopter `.gemini/settings.json` (frozen) | Adopters who keep Gemini CLI keep frozen GitLab entry, pins and Playwright `excludeTools`; Gemini agents reach every GitLab tool — no wider than v10.x, now outside the harness. The harness hook is a fixed `echo` (develop `sync.mjs:719-734`), so removal breaks nothing in it; older releases unverified. | D4 notice (in place) and the Appendix A migration item in `docs/releases/v11.0.0.md`; register v12. | No |
| SEC-T780-06 | SECURITY:LOW | A01 | user-owned `.vscode/settings.json:13` (`"gemini": true`); one hit in `.claude/settings.json` | Terminal auto-approval for `gemini`; user action (Q4); content not read. | User removes the entry and reviews the `.claude/settings.json` hit. | No |
| SEC-T780-07 | SECURITY:LOW | A03 | `scripts/install.sh:169`, `:242` | Pre-existing: raw argv echoed to stderr without `ascii_printable`. | Wrap both in `$(ascii_printable "…")` as line 200 does. | No |

## Answers
1. **Installer:** no path writes, deletes, follows a link into `.gemini`, or opens `.gemini/settings.json`/`.gemini/.env`. `--platform gemini` refused at 184-205 before `--target` is checked (`[Gg][Ee][Mm][Ii][Nn][Ii]`, all cases; other values via `ascii_printable`); tests cover five modes with rsync and cp and that no target is created. `SUPPORTED_PLATFORMS`, `platform_managed_paths`, `platform_mcp_config` no longer name gemini; `install_gemini` and the warning loop entry gone. The notice runs only from `validate_before_update`, skips a symlinked `.gemini`, greps only a regular non-symlink `.generated-manifest.json` with `-q`, tests the sidecar's existence only, names neither `settings.json` (except the sidecar name) nor `.env`, and prints the path through `printable()`. The FIFO test (548-564) runs the whole installer with both files as FIFOs and a 120 s timeout: meaningful. Residuals -03, -04.
2. **Generator:** `emitMcpOpencode` unchanged (`permission[<server>_<tool>] = 'deny'`), `denyTools` validation and per-agent construction in place (worktree copy of the latter not re-read; the orchestrator's byte proof relied on). `tools: 'drop'` gone from code and schema enum (a bypass falls to keeping `tools`: fail-closed). `MCP_EMITTERS` four entries; unknown format throws.
3. **merge-mcp-json.py:** only `merge_exclude_tools`, its call and the `hooks` note removed; a user's own such key is kept; `merge_permission` and the SEC-T680 guards unchanged. Only change: a hand run on an old `.gemini/settings.json` gets "source wins" for `excludeTools`; the installer never does this.
4. **Tests:** `ARTIFACT_UNSAFE_CONTEXTS` anchor platform-neutral, still tied to its section; no guard lost. The drift-gated root wording is correct and fail-closed; the adjacent unconditional exemption is -02. Not verified: 101/101 count, deleted/renamed list, `merge_rule_findings` needles, `REMOVED_PLATFORM_DIRS`.
5. **Docs:** no statement about Claude Code, Copilot/VS Code or Cline changed meaning; `PREREQUISITES.md:184` accurate (K-23, T775); 44-45, 57 Opencode-only and accurate; posture cell is -01. Wiki 95 drop correct ("elsewhere" meant Gemini); optional "(built-in agents and your own agent files: K-23)". Wiki 109 ("an element the generator stops shipping later stays in your file") still true for `permission` (fail-closed).
6. **SEC-T657-01/SEC-T658-01: close by removal at v11.0.0**; no ADR-011 acceptance needed. Claude Code enforces (observed); Copilot/VS Code (documented); Opencode generated agents per-agent denies plus server-level Playwright deny (documented, bytes unchanged); Cline has no agent files; Opencode built-ins and own agent files are K-23 (user decision 2026-10-16). Limits: takes effect with v11.0.0 after S3; v10.x installs stay under the v10.0.0 acceptance; reopens if the open Opencode live check (K-20/A-7/SEC-T658-02) shows the per-agent denies are not honoured; fix -01 first. SEC-T775-01..-03 closed by removal; K-15 ends; K-20, A-7, SEC-T658-02 lose the Gemini item and stay open for Opencode; SEC-T660-06 moot (record not re-read); K-35 stays, re-run on Opencode or Cline advisable.
7. **Adopter residual:** -05; the `.vscode/settings.json` auto-approval: -06 (user action).

## Compliance checklist
- [x] OWASP reviewed (A01, A03, A04, A05, A08, A09 apply)
- [x] Authorization: Opencode deny paths unchanged
- [x] Input validation: `--platform` refused before any write; unknown values printed safely
- [x] Secrets: `.env` never opened; no secret file read
- [x] Dependencies: no change
- [x] Logging: notices print names and paths only, through `printable()`
- [x] Immutable Security Constraints 1-6: no breach
- [ ] Docs fully consistent: -01 open

## VERDICT: PASS

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 7 | 0 | 7 |

### Conditions
None. Recommended, not blocking: -01 in T779 before merge; -02 at T781; -03, -04, -07 in a later hardening batch; the user acts on -06; the v11.0.0 release plan carries the Appendix A migration item (covers -05).

### Blockers
None (`grep_content` not reaching the worktree: technical, minor, worked around).

## Not verified
Opencode denial test counts; deleted/renamed test list; `merge_rule_findings` needles; `REMOVED_PLATFORM_DIRS`; worktree per-agent deny code; whether a test pins "No (K-15)"; the `--update --dry-run` FIFO variant; `grep -D skip` portability; older hooks; checklist § 6; SEC-T660-06 content; the settings-file hits; the full D1 grep; no test, generator or installer run.
