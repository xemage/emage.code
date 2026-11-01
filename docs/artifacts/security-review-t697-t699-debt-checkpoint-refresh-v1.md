# Artifact: security-review-t697-t699-debt-checkpoint-refresh-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. Read-only: no shell and no git; the refresh diff was read from a file the orchestrator exported (`git show ff4684c9`). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-31.
- **Target**: branch `chore/T697-T699-debt-checkpoint-refresh`, tip `7e1bdd96`, base develop `e779b9a6`: T699 (root refresh 21, `ff4684c9`), T697 (`docs/artifacts/tracked-debt-register-v3.md`), T698 (`docs/checkpoints/checkpoint-039-post-v8-follow-ups-complete.md`).
- **Based on**: `docs/tasks/task-T697.md`, `task-T698.md`, `task-T699.md`; `security-review-t686-*`, `-t688-*`, `-t689-*`, `-t690-*`, `-t693-*` to `-t696-*`; `implementation/PREREQUISITES.md` (139-186); `docs/wiki/mcp-servers.md` (44, 67, 160).
- **Orchestrator checks relied on**: the refresh changed exactly the 23 declared paths and `--print-drift` prints `[]`; no file under `docs/` or `implementation/` changed by the refresh; the register holds no JWT, token, LAN address or secret-store path (pattern scan, counts only).

## Verdict: CONDITIONAL_PASS

0 critical, 0 high. No Immutable Security Constraint is breached by the change and no security control is removed or weakened.

- **T699**: every hunk is body text from the reviewed knowledge changes of T690 (two server entries), T692 (the `TECHNICAL-DEBT.md` sentence) and T693 (Release Gate Policy item 5, the Gate Inputs row, the orchestrator Release-gate bullet). No `tools:` or `permission:` line changed. The root `security-audit` and `poc-security-audit` entries of `.vscode/mcp.json` are byte-identical to `implementation/.vscode/mcp.json` and match the T690 review (no `env`, no secret, no absolute path).
- **T697**: the MEDIUM findings since v2 (SEC-T686-01, SEC-T688-01, SEC-T693-01, SEC-T694-01, SEC-T694-02, SEC-T695-01) are closed in their reviews, as the register says; no MEDIUM or higher is wrongly shown as closed or accepted; SEC-T662-01 is correctly carried to the v9.0.0 gate. If the SEC-T676-02 acceptance (two HIGH Brave audit findings) lapses on 2026-11-21, those findings block the v9.0.0 tag under Release Gate Policy item 2; the release plan must say so.
- **T698**: no secret, token value or internal IP address; the security statements match the register except as noted in SEC-T699-02 and SEC-T699-03.

## Findings

| Id | Grade | Location | Finding | Recommendation | Status |
|---|---|---|---|---|---|
| SEC-T699-01 | LOW | `tracked-debt-register-v3.md:295,350,429` | TD-T697-08 (D-11) is shown as an open decision, but its option (a) is mostly in place: `implementation/PREREQUISITES.md:160,186` and `docs/wiki/mcp-servers.md:67` already say an exported token in a shell profile is acceptable only on an encrypted disk. Left: the env-var table at `docs/wiki/mcp-servers.md:44` lacks that qualifier, and "the setup instructions export the token" remains in `AGENTS.md:116`, `implementation/AGENTS.md:116` and `docs/wiki/mcp-servers.md:160` (overlaps SEC-T689-03). | Regrade TD-T697-08 LOW, tracked in the SEC-T689-03 token-docs batch; fix the four places before the v9.0.0 tag; the open count becomes 3 in the next register version. | tracked-LOW; devops-engineer with technical-writer; before the v9.0.0 tag |
| SEC-T699-02 | LOW (A09) | `checkpoint-039…md` § 9 | User-side plaintext secrets at rest had no id. | Ids below (UA-T699-1 to -3), presented as user actions, never as accepted risks. | fixed in this branch (ids assigned here; the checkpoint points to them) |
| SEC-T699-03 | LOW | `checkpoint-039…md` § 3, § 9 | The checkpoint gave exact token expiry dates where the register's A-13 marks them unverified, and said the transcripts "should be deleted" where A-15 says optional. | Name the source of the dates or mark them unverified; make the two agree. | fixed in this branch (the checkpoint names the sources: the user's token check and the 90-day mint of 2026-10-31; the transcript deletion is marked as the orchestrator's recommendation against A-15's "optional") |
| SEC-T699-04 | LOW | `tracked-debt-register-v3.md:294,450` | The TD-T697-07 acceptance has no review date and does not say what the orchestrator-role bearer token can do on CWSO, which decides whether MEDIUM is the right grade. | Re-decide at the bearer-token renewal at the latest; record the conditions below. | tracked-LOW; orchestrator, the user decides; by the bearer-token renewal (2027-01-29) |

**User actions with an id (SEC-T699-02).** Plaintext secrets at rest fall under Immutable Security Constraint 6, which admits no risk acceptance; these are actions for the user:

- **UA-T699-1**: the plaintext `.env` files of the user's other projects (database credentials).
- **UA-T699-2**: the plaintext JWT secret file on the CWSO server (the staging source of the `cwso-jwt-secret` volume).
- **UA-T699-3**: the stored Context7 CLI key (rejected as invalid; remove or replace it).

## Grading of register ids

- **TD-T697-07** (CWSO over plain HTTP on the LAN): **MEDIUM confirmed**; the acceptance is valid with conditions. The exposure is that of SEC-T695-01 (a 90-day orchestrator-role bearer JWT in cleartext; exploiting it needs LAN sniffing). "HTTPS everywhere" is a guideline, not an Immutable Security Constraint, so a user acceptance is allowed and decision "C" records it; the repository control (SEC-T695-01, tunnel or TLS required) is fixed. Conditions: re-decide at the token renewal, or earlier if the LAN gains untrusted devices or the token's role widens; **regrade to HIGH** if the orchestrator role can make the CWSO server run code or read secrets (for example by dispatching work to `sia-executor`) (unverified); the SSH tunnel (option A) stays the preferred fix.
- **TD-T697-08 / D-11** (environment mode and Constraint 6): **LOW**. Constraint 6 admits no acceptance by anyone, and no user decision recorded one: the phrase "the user's own accepted Constraint-6 exposure" in `security-review-t689-token-placement-v1.md:28` (residual (3)) is **withdrawn** by this review. Supporting environment mode does not breach Constraint 6: a variable filled at login from an in-memory or encrypted store is not data at rest; only a literal token in a profile file on an unencrypted disk is, and the documents already restrict that to an encrypted disk. Option (b) (rule a shell profile outside Constraint 6) is rejected; option (c) (remove environment mode) is not needed. The remaining wording gaps are SEC-T699-01. No user decision is needed.

## Counts

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 (TD-T697-07, graded here) | 0 | 1 (accepted by the user, with the conditions above) |
| LOW | 5 (SEC-T699-01 to -04, TD-T697-08) | 2 (SEC-T699-02, -03) | 3 (tracked) |

## Unverified

- The reviewer did not compare the 21 refreshed agent and instruction files byte for byte with `implementation/` (the orchestrator's `--print-drift` check, which compares them, prints `[]`).
- What the CWSO orchestrator-role token can do on the CWSO server.
- The user's own token placement (`PREREQUISITES.md:157`).
- `task-T695.md` section 6, the T677 and T696 reviews and the CWSO repository were not read for this review.
