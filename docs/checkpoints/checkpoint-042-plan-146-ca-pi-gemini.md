# checkpoint-042 — plan-146: CA-chain control, Pi removal, Gemini CLI removal

**Phase:** post-release work (`plan-146`): SEC-T756-02 fixed, Pi and Gemini CLI platform support removed
**Written:** 2026-11-11
**Author:** orchestrator
**Based on:** `checkpoint-041`; `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md` (with its Addendum of 2026-11-07); ADR-013; ADR-014; MRs !657 to !663
**Ledger at this checkpoint:** **0 active, 579 completed** (checkpoint-041: 0 active, 562 completed)

## Phase summary

The user asked on 2026-11-07, verbatim: "Plan for: Fix of SEC-T756-02, Remove PI support completely, then review and work on SEC-T657-01/SEC-T658-01". They approved plan-146 ("Approve (Recommended)"). All three parts are merged into `develop`, which is now at `d9b20951` with root drift 0. Every merge followed the same rule: the MR pipeline was green, the full suite passed in a clean worktree, and the merge was pinned to the verified sha.

- **Part A: SEC-T756-02 is LOW (MR !658).**
  - **What was built:** a CI control, `scripts/check-ca-chains.sh` with vendored public fixtures, in the jobs `ca-chain-check-python` and `ca-chain-check-node`. They run on merge-request and branch rules only, and the three tag jobs are unchanged.
  - **What it proves:** inside each pinned image, none of the eMudhra disclosure's 16 chains, nor the 3 extra crt.sh certificates, validates against that image's own CA store. It compares by key (SPKI) and requires `ca-certificates` 20261020 or later. A gitlab.com control chain must still validate.
  - **Evidence:** T767 settled T765's open points, and T768's review gives CONDITIONAL_PASS with its condition met by pipeline 3040148068. The user chose "No pin (Recommended)" for a CA pin on the job's own `git`.
- **Part B: Pi removed under ADR-013 (MRs !659, !660).**
  - **Inventory and decision:** T769 wrote the inventory and T770 wrote ADR-013, which the user accepted with every recommended option.
  - **Code (S1, T771):** the vscode-only emitter keeps every non-Pi output byte-identical. Removed: `pi.json`, both `.pi/` trees, `skipFormats` and `MCP_FORMATS`. `--platform pi` errors, and an existing `.pi/` gets a read-only notice; nothing is ever deleted.
  - **Docs (S2, T772)** followed, then the reviews (T773): security PASS, Tech Lead CONDITIONAL_PASS with its condition recorded.
  - **Root refresh (S3, T774):** done with the user's approval, "Yes, refresh now (Recommended)".
- **Part C: Gemini CLI removed under ADR-014 (MRs !661 to !663).**
  - **Why it changed:** T775 found that Gemini CLI v0.67.0 enforces per-agent MCP tool lists. This harness drops those lists, and its 28 Gemini agent files probably fail the loader. The user chose "Drop Gemini instead of fixing (Recommended)".
  - **Inventory and decision:** T776 wrote the inventory and T777 wrote ADR-014, accepted with every recommended option, plus Q4 "I'll remove it myself (Recommended)".
  - **Code (S1, T778):** fixtures were re-hosted on Opencode first. Then Gemini was removed, with every non-Gemini output and Opencode's `permission` denials byte-identical. `--platform gemini` errors. The read-only notice for an existing `.gemini/` never reads `settings.json` or `.env`, and nothing is ever deleted.
  - **Docs and reviews:** S2 (T779) changed the docs, including the Opencode posture cell (SEC-T780-01). The reviews (T780): security PASS, Tech Lead CONDITIONAL_PASS with its conditions recorded or applied.
  - **Root refresh (S3, T781):** done with the user's approval, "Yes, refresh now (Recommended)". It also removed the test's temporary root `AGENTS.md` allowance (TL-T780-02, SEC-T780-02).
  - **Outcome for SEC-T657-01/SEC-T658-01:** T780's security review closes it by removal at v11.0.0, with no ADR-011 acceptance needed. It reopens if the open Opencode live check (K-20, A-7, SEC-T658-02) shows the per-agent denies are not honoured.

Four platforms remain: claude-code, cline, github and opencode.

## Completed tasks (this phase)

- **Part A:** T766 (CA-chain control), T767 (open points), T768 (security review).
- **Part B:** T769 (Pi inventory), T770 (ADR-013), T771 (Pi S1), T772 (Pi S2), T773 (reviews), T774 (Pi S3).
- **Part C:** T775 (Gemini scoping review), T776 (Gemini inventory), T777 (ADR-014), T778 (Gemini S1), T779 (Gemini S2), T780 (reviews), T781 (Gemini S3), T782 (this checkpoint).

## Open / carried over

| Item | Source | Owner |
|---|---|---|
| The v11.0.0 release (MAJOR: Pi and Gemini CLI removed); its release document must carry the ADR-013 and ADR-014 Appendix A migration items and the frozen-state warnings (SEC-T773-02, SEC-T780-05, TL-T780-09: the release-doc gate checks migration items only on lines that mention Cursor) | ADR-013, ADR-014 | orchestrator, release-manager; a separate plan |
| The MEDIUMs accepted for v10.0.0 only (ADR-011): SEC-T660-01, SEC-T665-01, SEC-T702-09 still need a fix or a new acceptance before v11.0.0. SEC-T756-02 is now LOW; SEC-T657-01/SEC-T658-01 closes by removal | checkpoint-041, T768, T780 | the user; orchestrator tracks |
| Tracked-debt register v12. New LOW ids: SEC-T768-01 to -06, SEC-T773-01/-02, TL-T773-01 to -04, SEC-T780-01 (fixed), SEC-T780-02 (fixed), SEC-T780-03 to -07, TL-T780-01 to -09, SEC-T775-01 to -03 (closed by removal), the installer's rsync size-and-time skip (T774, T781: an equal-length edit with equal checkout times is not copied; compare checksums), plus the v10.0.0 ids listed in checkpoint-041 | the reviews | orchestrator |
| A-21: the runner owner reports whether `FF_GIT_URLS_WITHOUT_TOKENS` is on, whether any of `SSL_CERT_FILE`, `SSL_CERT_DIR`, `CURL_CA_BUNDLE`, `GIT_SSL_CAINFO`, `GIT_SSL_CAPATH` or `GIT_SSL_NO_VERIFY` is set as a CI variable, and whether `tls-ca-file` or `helper_image` is set (presence only). SEC-T756-02 stays LOW only if none is set; before the next tag or by 2027-02-19 | T767, T768 | user |
| The user's own `.vscode/settings.json:13` auto-approves the `gemini` CLI (ADR-014 Q4, SEC-T780-06), and the one Gemini mention in `.claude/settings.json` (not opened) | T776, T780 | user |
| The Node image bump after the advisory due 2026-11-11: both CA jobs must pass on the new digest | checkpoint-041, T766 | devops-engineer |
| Brave acceptance ends 2027-01-30; GitLab token renewal 2027-01-28; CWSO bearer 2027-01-29; CI image review date 2027-02-19 | checkpoint-041 | user, devops-engineer |

## Key decisions

All are the user's, recorded verbatim in plan-146, the ADRs and the briefs:

- "Approve (Recommended)" (plan-146); "No pin (Recommended)" (CA pin).
- ADR-013: Q1 "v11.0.0, no deprecation (Recommended)"; Q2 "Error + notice, never delete (Recommended)"; Q3 "Delete both in S1 (Recommended)"; Q4/Q5 "Accept all (Recommended)".
- Gemini: "Agent lists + GitLab allowlist (Recommended)", "Yes, I use glab/web/other (Recommended)" and "Drop Gemini support"; the conflict was resolved as "Drop Gemini instead of fixing (Recommended)".
- ADR-014: Q1 "Error + notice, never delete (Recommended)"; Q2 "Delete both in T778 (Recommended)"; Q3/Q5 "Accept all (Recommended)"; Q4 "I'll remove it myself (Recommended)".
- Both root refreshes: "Yes, refresh now (Recommended)", each approved at its moment.
- The orchestrator's own decisions, not the user's:
  - the T767 owner change;
  - accepting T771's narrowed release-gate test skip and the CI tag fetch;
  - accepting T778's deviations;
  - recording TL-T773-01 and TL-T780-01 as accepted residue in the ledger rows of T773 and T780.

## Maturity distribution

Unchanged: `check-maturity.py` checks 80 components, and none fails its claimed level.

| Category | Stable | Experimental | Deprecated | Total |
|----------|-------:|-------------:|-----------:|------:|
| Agents | 28 | 0 | 0 | 28 |
| Commands | 14 | 5 | 0 | 19 |
| Instructions | 4 | 2 | 0 | 6 |
| Skills | 7 | 20 | 0 | 27 |
| **Total** | **53** | **27** | **0** | **80** |

## Artifacts produced

- **Part A:** `ca-check-t767-v1.md`, `security-review-t768-ca-control-v1.md`.
- **Part B:** `pi-removal-inventory-v1.md`, ADR-013, `security-review-t773-pi-removal-v1.md`, `tech-lead-t773-pi-removal-v1.md`.
- **Part C:** `security-review-t775-gemini-scoping-v1.md`, `gemini-removal-inventory-v1.md`, ADR-014, `security-review-t780-gemini-removal-v1.md`, `tech-lead-t780-gemini-removal-v1.md`.
- **Closeout:** this checkpoint.

## Blockers (active)

None.

## Token usage

Not measured per phase. Agent runs above their brief budgets, by the harness's count:

| Task | Used | Budget |
|---|---:|---:|
| T771 | about 323k | 150k |
| T778 | about 293k | 150k |
| T772 writer | about 200k | 120k |
| T779 writer | about 251k | 120k |
| T766 | about 197k | 110k |
| T776 | about 209k | 120k |

The account's 5-hour limit and later its weekly limit interrupted T771 and T778; both resumed from their saved state. The top-level session's context was compacted during plan-145 and resumed from its summary.

## Next steps

- Tracked-debt register v12.
- The v11.0.0 release plan, which carries the Pi and Gemini migration items and resolves the v10.0.0-only acceptances.
- The Node image bump, and the user actions above.

## Compression note

This checkpoint is the canonical handoff after plan-146. Subsequent agents receive only this checkpoint, their task brief and the referenced artifact versions.
