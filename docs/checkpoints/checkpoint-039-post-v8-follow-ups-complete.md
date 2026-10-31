# checkpoint-039 — Post-v8.0.0 follow-ups complete (plan-123)

**Phase:** post-release follow-up (`plan-123` and its addenda of 2026-10-16 to 2026-10-31), closed with the debt register v3, this checkpoint and the twenty-first root refresh
**Written:** 2026-10-31
**Author:** orchestrator
**Based on:** `checkpoint-038`; `docs/plans/plan-123-post-release-follow-ups.md` (all addenda); `docs/artifacts/tracked-debt-register-v2.md`, `tracked-debt-register-v3.md`; `docs/tasks/completed-tasks.md` (rows T661 to T699); MRs !591 to !627 (emage.code) and !216, !217 (CWSO)
**Ledger at this checkpoint:** **0 active, 497 completed** (checkpoint-038: 0 active, 458 completed)

## 1. Phase summary

All of `plan-123` is merged on `develop`. The follow-ups that v8.0.0 deferred are done: Cursor support is removed in three steps under ADR-010 (T661, T662, T678, T679), which makes the next release **v9.0.0 (MAJOR)**; no agent holds the whole GitLab server any more (T660 carried, T666, T667, T688); Opencode agents get per-agent denies (T663); the GitLab token handling is implemented (T664, T665, T681, T683) and, after the user rejected the full-disk-encryption assumption (D-3, 2026-10-24), the documented token file lives in memory (T689); the release job runs on `CI_JOB_TOKEN` (T686); the installer, generator, CI and supply-chain debt themes are closed or tracked (T672 to T677, T680, T682, T684, T685); `orchestrator` is promoted to `stable` on evaluator baseline v22 (T668 to T670); the release self-review ruling is applied (T691, T693).

The last week added an unplanned security track. On 2026-10-30 and 2026-10-31 the user moved every devcontainer secret off the disk (a gpg-encrypted store with a copy in RAM, one new GitLab token, all older tokens revoked). A scan for the current secret values found the CWSO JWT secret committed in the public repositories emage.code and CWSO. The secret was rotated the same day (the committed copies are dead), removed from both repositories (T694, T695), and the CWSO server, down for four weeks for want of a restart policy and a complete Origin list, was repaired; its vulnerable Rust crates and Go toolchain were updated (T696).

## 2. Completed tasks (this phase)

Generated from `docs/tasks/completed-tasks.md` (the ledger is the source of truth). Since checkpoint-038, 39 tasks closed (T661 to T699; T653 to T660 closed before checkpoint-038). By theme:

- **Cursor removal (ADR-010).** T661 (decision and inventory), T662 (S1, code and trees), T678 (S2, live docs), T679 (S3, the root refresh after S2).
- **MCP grants and denials.** T663 (Opencode per-agent denies), T666, T667 (named GitLab tool sets for the remaining five holders), T688 (qa-engineer no longer reads raw job traces), T690 (`security-audit` and `poc-security-audit` generated for GitHub Copilot).
- **GitLab token handling.** T664 (design), T665 (file mode and the checker), T681 and T683 (per-role token decision, Reporter profile), T689 (token file in memory by default; SEC-T665-03 closed).
- **Tracked debt.** T671 (register v1, 204 ids), T672 to T677 (installer robustness, test quality, documentation, CI and release hardening, supply chain, function sizes), T680 (Pi placeholders), T682, T684, T685 (review residuals), T686 (release job on `CI_JOB_TOKEN`), T687 (register v2, 323 ids), T697 (register v3).
- **Golden suite and maturity.** T668 (realignment B under grant G-2), T669 (baseline v22), T670 (`orchestrator` promoted).
- **Rulings.** T691 (release self-review, option A+), T692 (`TECHNICAL-DEBT.md` lives in the PoC root), T693 (A+ applied).
- **CWSO secret and server.** T694 (emage.code scripts read `CWSO_JWT_SECRET` only; the dead value removed), T695 (CWSO CI per-job secret, restart policy, configurable Origin list, `--locked` builds), T696 (16 Rust advisories, Go 1.26.10, govulncheck v1.9.0).
- **Housekeeping.** T698 (this checkpoint), T699 (root refresh 21).

## 3. Open / carried over

No ledger row is open. The full list is `docs/artifacts/tracked-debt-register-v3.md` (T697): **398 ids**, 273 fixed, 39 accepted, 5 obsolete, **4 open**, 77 tracked-LOW. No open item is `SECURITY:HIGH` or `SECURITY:CRITICAL`; every MEDIUM raised since v2 is closed; the only open MEDIUM is SEC-T662-01. The items that need a decision, an action or a release are:

| Item | Source | Owner |
|---|---|---|
| SEC-T662-01 (MEDIUM): `docs/releases/v9.0.0.md` must carry the Cursor migration item of ADR-010 Appendix A, and the release gate must check that the document exists; the other v9.0.0 migration items are listed in `docs/tasks/task-T679.md` section 3a | T662 review, register D-9 | release-manager with technical-writer, before the v9.0.0 tag |
| v9.0.0 release plan | ADR-010 | orchestrator (needs the user's approval) |
| Tracked LOW debt of the reviews T665 v2, T677, T686, T688 to T690, T693 to T696 | register v3 | per item, as recorded there |
| Brave audit acceptance expires 2026-11-21 | T685, register v2 | user |
| First real tag pipeline with `CI_JOB_TOKEN` (SEC-T686-06: runner clone method) | T686 review | user, at the v9.0.0 tag |
| D-11 (TD-T697-08): environment mode on an unencrypted disk is a plaintext secret at rest; the T689 review calls it the user's accepted exposure, but no user decision records that and Constraint 6 admits no acceptance | register v3 | user, with security-engineer |
| D-12 (when to run the batches of tracked-LOW items) and D-13 (add T688, T689, T690 and T693 to the v9.0.0 migration list) | register v3 | user; orchestrator for the v9.0.0 plan |
| The devcontainer GitLab token (expires 2027-01-28) and the CWSO bearer token (expires 2027-01-29) were issued for 90 days (A-13) | the user's secrets setup of 2026-10-31 | user |
| `paste` advisory acceptance in CWSO, review due 2027-01-31 (SEC-T696-06) | T696 review | devops-engineer |

## 4. Key decisions (the user's, recorded verbatim in the plan-123 addenda)

- 2026-10-16: ADR-010 accepted (drop Cursor, v9.0.0, no deprecation release); baseline v22 approved; the token design option D.
- 2026-10-22: the GitHub MCP server removed ("Remove GitHub MCP server"); the Brave audit risk accepted with conditions until 2026-11-21; T681 option A with the Reporter profile documented.
- 2026-10-23: LOW policy, "Track LOW items as debt, stop chasing (Recommended)"; the release job on `CI_JOB_TOKEN`; D-1 (no raw job traces for qa-engineer); root refresh approved for T679.
- 2026-10-24: the answers to the register's decision list ("D2 b", "D-3 reject (disk encryption: no)", "D-4-b", D-5, "D-6 a", "D-7 b", "D-8 accept", "D-10 yes").
- 2026-10-31: "T693 go" and "fix 01"; "T694 go"; decision "C" (CWSO over plain HTTP on the LAN accepted as a risk; SSH tunnel and TLS proxy declined); "T696 go"; "T689 go"; "1 2 go, refresh yes" (T697 to T699).

## 5. Maturity distribution

From `implementation/registry/summary.md` (registry up to date): 80 components.

| Category | Stable | Experimental | Deprecated | Total |
|----------|-------:|-------------:|-----------:|------:|
| Agents | 28 | 0 | 0 | 28 |
| Commands | 14 | 5 | 0 | 19 |
| Instructions | 4 | 2 | 0 | 6 |
| Skills | 7 | 20 | 0 | 27 |
| **Total** | 53 | 27 | 0 | 80 |

Change since checkpoint-038: `orchestrator` moved from `experimental` to `stable` (T670, evaluator baseline v22).

## 6. Artifacts produced (selection)

ADR-010; `cursor-removal-inventory-v1.md`; `gitlab-token-handling-design-v1.md`, `gitlab-per-role-token-design-v1.md`; `tracked-debt-register-v1.md`, `-v2.md`, `-v3.md`; `ruling-p112-p41-o1-release-self-review-v1.md`; `mcp-agent-denials-v1.md`, `mcp-agent-denials-evidence-v1.md`; `brave-audit-acceptance-v1.md`, `-v2.md`; the security reviews `security-review-t662-*` to `-t696-*` and `security-review-t665-token-handling-v2.md`; `evaluator-hash-known-good-v22.json`; plan `plan-123` with thirteen addenda.

## 7. Blockers (active)

None.

## 8. Token usage and incidents

Not measured per phase (the session ran across several context compactions). Recorded overruns: the T689 agent used about 250k tokens against a 150k budget (recorded in `docs/tasks/task-T689.md`); the T697 agent used about 176k tokens against a 100k budget (a 477-line register over ten review artifacts). Process incidents, both LOW and recorded in the reviews: two implementing agents printed the dead CWSO secret value in their own tool output (SEC-T695-06, SEC-T694-10); the value had been rotated before, so no new rotation was needed, but the local session transcripts hold it and should be deleted.

## 9. Next steps

- Phase: v9.0.0 release preparation. First step: a release plan for the user's approval, carrying SEC-T662-01 and the migration items of `task-T679.md` section 3a.
- The user's side: restart the VS Code server on the devcontainer so the session environment picks up the rotated values (the CWSO MCP connection depends on it); delete the local session transcripts that hold the dead secret; decide on the plaintext `.env` files of the user's other projects and on the plaintext JWT secret file on the CWSO server; fix the stored Context7 CLI key.

## Compression note

This checkpoint is the canonical handoff for the v9.0.0 release phase. Subsequent agents receive only this checkpoint, their task brief and the referenced artifact versions.
