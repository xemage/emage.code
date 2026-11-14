# Artifact: tracked-debt-register-v17.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v16.md` (690 ids; v16 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-162-tracked-debt-register-v17.md` (§ User decision, § Facts since v16, § Task Decomposition item 1) and `docs/tasks/task-T827.md` (the user's "v17 go"); `docs/plans/plan-159-release-gate-runner-tag.md`, `docs/plans/plan-160-v11-confirmation-sec-t660-t665.md`, `docs/plans/plan-161-release-v11.md` (each § Outcome and Addenda); `docs/checkpoints/checkpoint-043-release-v11.0.0.md`; `docs/releases/v11.0.0.md` (Known Issues, RELEASE VERDICT Conditions); `docs/artifacts/security-review-t811-release-gate-runner-v1.md`, `security-review-t812-v11-no-harness-fix-v1.md`, `release-v11-audit-v1.md`, `mcp-pin-audit-v11-v1.md`, `security-review-t825-v11-prep-v1.md`, `qa-gate-release-v11-v1.md`, `tech-lead-release-v11-v1.md`, `security-review-t820-release-v11-v1.md`, `security-review-t820-release-v11-addendum-v1.md`, `independent-check-t821-v1.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-013, ADR-014, ADR-015, ADR-016; no ADR is amended here.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T827 (plan-162; the user's answer of 2026-11-14, verbatim: "v17 go"). **Date**: 2026-11-14.
- **Tree read**: branch `agent/tech-lead/T827` at `4ea04df6` (develop `42e30d02` plus the plan-162 commit). The range for "lines added since v16" is `bbe3b8af..42e30d02` (plan-162 § Facts): 44 files, 3130 lines added and 27 removed (read here). Outside the plans, briefs, reviews, gate artifacts, the release document, the checkpoint and the ledger, the changed files are `.gitlab-ci.yml` (the three `tags: ["release-gate"]` lines and their comments, T810), `tests/functional/test_ci_hash_pins.py` (T810), `docs/wiki/mcp-pin-bump-checklist.md` (T810, T824, `a4902de2`), `implementation/PREREQUISITES.md` (T823, SEC-T825-02), the two `implementation/runtime/*/requirements-mcp-server.lock.txt` (T824), `README.md`, `implementation/README.md` and three `docs/wiki/` pages (version strings, T815; not opened here). `implementation/knowledge/`, `scripts/` and `CONTRIBUTING.md` are not in the diff stat (read here). The CWSO repository was not read: every CWSO status carries over from v16.
- **Review mode**: read-only. "Unchanged" means no task, review, plan outcome, checkpoint, release document or ledger row in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). A status taken from a review is the latest source's. "Read here" means a grep, line read or `git` query on `4ea04df6`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v11 to v15 only by grep (the rows of the batch Q, S and X ids, the batch tables). The sources in Based on were read by section or grep, not in full (section 8). No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v16.
- **Batch letters**: S ends (its one id is fixed). No new letter. The batch of each new id is my suggestion (section 5).

## 1. Summary

v17 holds **708 ids**: the 690 of v16 and **18 new**. After v17: **531 fixed**, **47 accepted**, **10 obsolete**, **1 open**, **119 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 have no reviewer's grade (the orchestrator's ids, called LOW). TD-T774-01 now has one: `SECURITY:LOW`, with a regrade trigger (section 2.2). The two new ids that carried a grade above LOW, SEC-T811-01 (MEDIUM) and QA-T818-02 (QA `Medium`), are fixed (section 3).
- **The three MEDIUMs accepted for v11.0.0 only shipped and are not open, but each needs a fix or a new acceptance before the next release that ships it** (section 2.3, § 6.2 item 43): SEC-T660-01 and SEC-T665-01 (the user's "Accept for v11.0.0 (Recommended)" of 2026-11-13, after T812; their plan's review on **2027-01-28** is due, ADR-015 O3, W1) and SEC-T702-09 (ends **2027-01-30** or at the first Brave release above 2.1.4). TD-T697-07 (MEDIUM, not shipped) ends **2027-01-29**.
- **v11.0.0 shipped** (plan-161 § Outcome; checkpoint-043): tag `v11.0.0` (`e5645616`) on `3118924a`; tag pipeline 3067005699 ran all three jobs on runner #59129270; the Release body equals the document. With it SEC-T741-17 (both halves), SEC-T784-01, SEC-T814-01, SEC-T825-02, SEC-T820-01 / TL-T819-01, TL-T819-02 and QA-T818-02 are fixed; K-15 / SEC-T657-01 / SEC-T658-01 close by removal, with a reopen condition.
- **New and tracked-LOW (9)**: SEC-T811-03, SEC-T811-05, SEC-T825-01 (part a), QA-T818-03, QA-T818-04 (the `resolve_previous_tag` change), TL-T819-03 to -05, TL-T821-01.
- **My rulings, for the orchestrator to confirm or overrule** (section 4.2): batch Q's one-time v11.0.0 duties SEC-T773-02, SEC-T780-05 and SEC-T791-01 are fixed by the release document; TD-T808-02 is obsolete; QA-T818-01 is counted with TD-T774-01, and TL-T819-01 with SEC-T820-01.
- **SEC-T786-01 is fixed**: its trigger, Alpine `nodejs` 24.22.3 in a `unit-tests` log, is observed before the tag (the orchestrator's observation, reported 2026-11-14: `Installing nodejs (24.22.3-r0)` in the `unit-tests` logs of pipeline 3066902202 (MR !684 at the release tip `3118924a`, 2026-11-13T22:46:46Z, before the tag) and of develop pipeline 3067048242 (job 18024831240, 2026-11-13T23:50:34Z); I did not read the logs). **A-21 stayed open at the tag**, although the verdict listed it "before the tag"; checkpoint-043 carries it (section 4.3).
- **Next-release checklist** (section 6.2): reset for the release after v11.0.0. 26 items stand as rules for every release, 14 are done at v11.0.0 and leave, 2 stay open (8, 34), and items 43 to 48 are new.

Arithmetic, from the v16 totals:

| Status | v16 | leaves | enters | v17 |
|---|---:|---|---|---:|
| fixed | 514 | | + 6 tracked-LOW (SEC-T741-17, SEC-T784-01, SEC-T786-01, SEC-T773-02, SEC-T780-05, SEC-T791-01) + 2 accepted (SEC-T657-01/SEC-T658-01, K-15) + 9 new | **531** |
| accepted | 49 | - 2 fixed by removal | | **47** |
| obsolete | 9 | | + 1 tracked-LOW (TD-T808-02) | **10** |
| open | 1 | | | **1** |
| tracked-LOW | 117 | - 6 fixed, - 1 obsolete | + 9 new | **119** |
| **all** | **690** | | + 18 new ids | **708** |

Check: 531 + 47 + 10 + 1 + 119 = 708. Open or tracked: 119 + 1 = 120, the size of section 5.

### 1.1 Ids by v16 status and status now

| v16 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 117 | 6 | 0 | 1 | 0 | 110 |
| accepted | 49 | 2 | 47 | 0 | 0 | 0 |
| fixed | 514 | 514 | 0 | 0 | 0 | 0 |
| obsolete | 9 | 0 | 0 | 9 | 0 | 0 |
| **all v16 ids** | **690** | **522** | **47** | **10** | **1** | **110** |
| new in v17 | 18 | 9 | 0 | 0 | 0 | 9 |
| **all v17 ids** | **708** | **531** | **47** | **10** | **1** | **119** |

### 1.2 New ids by source and final status

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t811-release-gate-runner-v1.md`: SEC-T811-01 to -05 (statuses per plan-159 § Outcome) | 5 | 3 (-01, -02, -04) | 2 (-03, -05) |
| plan-161 § Addendum 1 (the orchestrator, from T814): SEC-T814-01 (graded and confirmed fixed by T825) | 1 | 1 | 0 |
| `security-review-t825-v11-prep-v1.md`: SEC-T825-01, -02 | 2 | 1 (-02) | 1 (-01 a) |
| `qa-gate-release-v11-v1.md`: QA-T818-02 to -04 (QA-T818-01 is TD-T774-01, not counted again) | 3 | 1 (-02) | 2 (-03, -04) |
| `tech-lead-release-v11-v1.md` and `security-review-t820-release-v11-v1.md`: TL-T819-01 / SEC-T820-01 (one finding, counted once), TL-T819-02 to -05 | 5 | 2 (-01/SEC-T820-01, -02) | 3 (-03 to -05) |
| `security-review-t820-release-v11-addendum-v1.md`: SEC-T820-02 | 1 | 1 | 0 |
| `independent-check-t821-v1.md`: TL-T821-01 | 1 | 0 | 1 |
| **All new** | **18** | **9** | **9** |

**Ids minted in the range beyond the plan's list: none.** A search of the 3130 added lines, outside `tests/golden/` and `.vscode/`, for `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>` and `A-<n>` tokens, set against registers v1 to v16, finds as not in any register exactly SEC-T811-01 to -05, SEC-T814-01, SEC-T820-01, -02, SEC-T825-01, -02, QA-T818-01 to -04, TL-T819-01 to -05 and TL-T821-01: the plan's list. Beside them:
- **Labels that are not debt ids**: K-26 to K-39 and A-01 to A-06 (the release document's Known Issues and breaking-change labels; K-36 to K-39 are new there, `docs/releases/v11.0.0.md:215`); M-1 to M-9 and MI-1 to MI-8 (migration items); B-1 to B-13 and X-04 (changelog labels); C-1 to C-4, C1 to C3 (gate conditions); O-1 (a T820 observation).
- **v16 ids named with no change of status**: among others SEC-T702-08, SEC-T735-06, SEC-T756-01, SEC-T756-02, SEC-T658-02, TD-T697-07, TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, SEC-T806-01, K-20 and the earlier fixed ids that the release document cites (section 2).
- This register mints no id.

## 2. v16 ids re-checked

Every v16 `open`, `tracked-LOW` and `accepted` id (167) has a row or a list entry here: 1 + 117 + 49. The v16 `fixed` and `obsolete` ids stay as v16 records them.

### 2.1 v16 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). The release document names it only as K-15's reopen condition.

### 2.2 v16 `tracked-LOW` (117)

**Changed (8).**

| Id | v16 | now | Evidence |
|---|---|---|---|
| SEC-T741-17 | tracked-LOW, batch S; the runner half waits on the user (A-20) | **fixed, both halves** | Repository half: T810 (`ab8d02db`, `1c19caab`), T811 § 3 (plan-159 § Outcome). Runner half: the user's report ("Already done", "Yes, both"; plan-159) and tag pipeline 3067005699, where all three jobs ran on runner #59129270, which meets T820 C-3 (checkpoint-043 step 4). That system ID `s_7371c6d24bcc` is `gitlab-runner-16028` rests on the user's report **(unverified)**. **Reopens** if any of the three jobs runs on another runner or manager in a `v*` tag pipeline (plan-159 § Outcome; item 44) |
| SEC-T784-01 | tracked-LOW, batch Q; item 38 | **fixed** | T823 (`ca1cdfa8`), SEC-T825-02's wording, and M-6 and line 31 of the release document; T820 § Status: "Closed (fixed)" (`security-review-t820-release-v11-v1.md:125`, read here) |
| TD-T774-01 | tracked-LOW, batch I; no grade | **tracked-LOW, `SECURITY:LOW` (A08), with a regrade trigger** | QA-T818-01 reproduced it on a user `--update` (`qa-gate-release-v11-v1.md:96`). T820 addendum § 1: LOW; **regrade trigger**: at any later release whose fix for a `SECURITY:MEDIUM` or higher finding changes a file without changing its size, it takes at least that fix's grade, and the code fix (`--checksum`, or a compare after the copy) lands before that release or the release carries a verified check for that file; owner backend-developer, through the orchestrator (item 45). Release document K-39 and M-6 carry the mitigation |
| SEC-T773-02 | tracked-LOW, batch Q; "the v11.0.0 document must carry the Appendix A item and the frozen-state warning (item 31)" | **fixed** (my ruling) | The release document carries M-1, A-01 and K-37; T819 checked M-1 against ADR-013 Appendix A and found SEC-T773-02's "no notice without a marker" added (`tech-lead-release-v11-v1.md:66-68`, read here); TL-T819-02 fixed the Highlights line (`independent-check-t821-v1.md:60`). The frozen state itself is accepted in ADR-013 D11 and stays a Known Issue (K-37) |
| SEC-T780-05 | tracked-LOW, batch Q; "the v11.0.0 document must carry the Appendix A item (item 31)" | **fixed** (my ruling) | M-2, A-02 and K-37 in the release document; T819 checked M-2 against ADR-014 Appendix A (as above) |
| SEC-T791-01 | tracked-LOW, batch Q; the platform-identity migration note (item 39) | **fixed** (my ruling) | M-4 and A-03 of the release document (`docs/releases/v11.0.0.md:50`, `:108`, read here); routed as MI-4 (`release-v11-audit-v1.md:40`) |
| SEC-T786-01 | tracked-LOW, `SECURITY:LOW` (A06), batch X; closes when a `unit-tests` log shows Alpine `nodejs` 24.22.3 (item 37) | **fixed** | Release document K-38: Alpine `v3.24/main` ships `nodejs` 24.22.3-r0 for x86_64 and `unit-tests` installs `nodejs~=24` unpinned (T814 § 8). The log is now observed: the orchestrator's observation, reported 2026-11-14: `Installing nodejs (24.22.3-r0)` in the `unit-tests` logs of pipeline 3066902202 (MR !684 at the release tip `3118924a`, 2026-11-13T22:46:46Z, before the tag) and of develop pipeline 3067048242 (job 18024831240, 2026-11-13T23:50:34Z); I did not read the logs. So the verdict's condition ("read a `unit-tests` log … deadline before the tag") was met in fact before the tag, though checkpoint-043 still carried it as open |
| TD-T808-02 | tracked-LOW, batch Q; a v11.0.0 tag after 2027-01-30 or after a Brave release above 2.1.4 fails the gate | **obsolete** (my ruling) | The condition was checked at the tag: the UTC date was 2026-11-13, npm's newest Brave release was 2.1.4, and the audit with v4's seven `--accept` entries exited 0 (checkpoint-043 step 3). At the next release SEC-T702-09 needs a fix or a new acceptance anyway (item 43) |

**Unchanged (109 tracked-LOW; v16 and earlier stay the record of their text)**: the ids of v16 § 2.2's "Unchanged" list and v16's five new tracked ids, other than the eight above (TD-T774-01 is changed in grade only and counted in the 111 that stay tracked), by batch: I 22 (plus TD-T774-01 = 23), J 1, K 7, L 5, M 12, N 9, P 1, Q 4, R 7, V 15, X 9, Y 9, F 2, U 6. 23 + 1 + 7 + 5 + 12 + 9 + 1 + 4 + 7 + 15 + 9 + 9 + 2 + 6 = 110, of which 109 are unchanged and TD-T774-01 changed in grade; with the 7 that leave, 117. Notes:
- **TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09 (batch Q)** stay tracked: each is a duty that recurs at every release. For v11.0.0 they were met: TD-T723-01 (`tech-lead-release-v11-v1.md:85`), SEC-T735-09 (`:89`; the template keeps the sentence), SEC-T735-08 (the questions of plan-158 and plan-160 named the release, the plan and a deadline ahead; `release-v11-audit-v1.md` § 4 left "whether that closes the id" to this register: **my ruling, it stays tracked**, as no rule text pins how the question is asked), TL-T780-09 (M-1, M-2 checked by hand, `tech-lead-release-v11-v1.md:66`; no check added).
- **SEC-T756-01, SEC-T756-02, SEC-T702-08, SEC-T658-02, SEC-T806-01**: named in the range with no change (K-34, K-29, K-28, K-15 of the release document; plan-161).

### 2.3 v16 `accepted` (49)

**Changed (2), qualifier changed (3), unchanged (44).**

| Id | v16 | now | What the sources record |
|---|---|---|---|
| SEC-T657-01 / SEC-T658-01 (counted as one) | accepted; close by removal at v11.0.0 unless the Opencode live check fails | **fixed, closed by removal at v11.0.0** | Release document K-15: "end with those platforms in v11.0.0, with no acceptance (T780…). **It reopens** if the open Opencode live check (K-20, A-7, SEC-T658-02) shows that the per-agent denies are not honoured" (read here). Item 48 |
| K-15 | as above | **fixed, closed by removal** | As above |
| SEC-T660-01 | accepted MEDIUM, for v10.0.0 only; the v11.0.0 question to be asked again under ADR-016 | **accepted MEDIUM, for v11.0.0 only (shipped)** | T812 (Security Engineer, 2026-11-13, a new review for v11.0.0) confirms no harness fix exists; then the question citing T812 was put on 2026-11-13; the user: **"Accept for v11.0.0 (Recommended)"**, which supersedes "Accept for v11.0.0" of 2026-11-12 (plan-160 § Outcome). All four ADR-016 conditions met (plan-160; checkpoint-043). Plan: owner the user (isolation) and devops-engineer (documentation); fix: none possible in the harness; deadline: the review on **2027-01-28**. The release document records the v8.0.0 plan's passed deadline ("the sprint after v8.0.0", at the latest 2026-11-01). The verdict's Conditions carry it (T820 C-1). **Left**: the review on 2027-01-28 (ADR-015 O3, W1: the owner records in the register whether a harness fix now exists and whether the outside closer is still right), and a fix or a new acceptance before the next release that ships it (item 43) |
| SEC-T665-01 | as SEC-T660-01 | **accepted MEDIUM, for v11.0.0 only (shipped)** | As SEC-T660-01; no earlier deadline, so no passed-deadline statement (T812). TL-T821-01 concerns its Conditions line |
| SEC-T702-09 | accepted MEDIUM, for v11.0.0 only (record v4) | **accepted MEDIUM, for v11.0.0 only (shipped)** | Unchanged in substance. T814 found the same seven advisories and none new; npm's newest Brave release was 2.1.4 on 2026-11-13 (`mcp-pin-audit-v11-v1.md` § 1, release document K-28); the tag-day audit passed (checkpoint-043 step 3). **Left**: ends **2027-01-30** or at the first Brave release above 2.1.4; a fix (the bump) or a new acceptance with a new record before the next release that ships the pin (item 43) |

**v16 § 2.3's open question is settled**: v16 ruled nothing on whether the 2026-11-12 answer held under ADR-016. The sources now record T812, the question again, and the new answer, so the question needs no ruling.

**Unchanged (44)**, with their v16 qualifiers: TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29; the release document says it "neither accepts nor renews it"); the 40 LOW or INFO ids listed in v13 § 2.3; the orchestrator-accepted residues TL-T773-01, TL-T780-01, TL-T780-07. 1 + 40 + 3 = 44; with the 3 rows of changed qualifier, 47 accepted; with the 2 fixed, 49.

## 3. New ids

Grades are the reviewers' own, except where the row says otherwise.

| Id | Grade | Short description | Status | Evidence | Batch |
|---|---|---|---|---|---|
| SEC-T811-01 | SECURITY:MEDIUM (A05/A08) | A second manager on the release-gate runner; the token first registered on a host where branch jobs bind the Docker socket | **fixed** (by the user's action, as reported) | T811 § 6; the user, 2026-11-13: "Already done" (plan-159 § Outcome). Nobody in the session read GitLab (API 401) **(unverified)** | — |
| SEC-T811-02 | SECURITY:LOW (A05) | Runner "Protected" and "Run untagged jobs" unconfirmed | **fixed** (by the user's confirmation) | The user: "Yes, both" (plan-159 § Outcome) **(unverified)** | — |
| SEC-T811-03 | SECURITY:LOW (A08) | Three routes the tag pin does not cover: `trigger:` child pipelines, `inherit: default: false`, `tags: []` (GitLab behaviour from the reviewer's memory, unverified) | **tracked-LOW** | T811 § 6: owner devops-engineer (proposed), next register batch; plan-159 § Outcome | V |
| SEC-T811-04 | SECURITY:LOW (wording) | The checklist paragraph claimed "run only on the user's dedicated project runner" | **fixed** | The orchestrator in `a4902de2`, following T811's proposed fix; **not re-reviewed: the orchestrator's ruling** (plan-159 § Outcome) | — |
| SEC-T811-05 | SECURITY:LOW (A05) | Runner hardening residuals: `allowed_services` unset; container-escape surface (runner behaviour from memory, unverified) | **tracked-LOW** | T811 § 6: owner the user, next runner maintenance | X |
| SEC-T814-01 | SECURITY:LOW (T825) | `opentelemetry-api` 1.45.1 in both runtime locks: CVE-2026-126360 / GHSA-mf5v-w3w3-f6cg, a ReDoS in `traceparent` parsing | **fixed** (minted and fixed in v11.0.0) | Minted by the orchestrator from T814 (plan-161 § Addendum 1); T824 (`6f45ef45`) bumped to 1.45.2; T825 graded LOW and confirmed; T820 § Status | — |
| SEC-T825-01 | SECURITY:LOW (A06) | No `opentelemetry-api>=1.45.2` floor in the unhashed `requirements-mcp-server.txt` inputs, so an existing environment keeps 1.45.1 | **tracked-LOW**, part (a) | (a) the floor and regeneration: tracked under the LOW policy; (b) the upgrade line: done in the release document M-6 (plan-161 § Addendum 2; read here). T820: "SEC-T825-01 (a), tracked" (`security-review-t820-release-v11-v1.md:167`) | K |
| SEC-T825-02 | SECURITY:LOW (A06) | The Node floor "22.23.5+, 24.22.3+ or 26.13.1+" read literally as one floor | **fixed** | Fixed by the orchestrator (one-line wording after T825's example; plan-161 § Addendum 2); T820 reviewed the fix: "Fixed; reviewed now, PASS" (`security-review-t820-release-v11-v1.md:124`) | — |
| TL-T819-01 / SEC-T820-01 (counted as one) | Important (T819); SECURITY:LOW (T820) | K-36 and K-32 stale after the probe tag | **fixed** | T826; T820 addendum: "Fixes SEC-T820-01" (§ 4, K-36 and K-32 rows); verdict Conditions: "C-1 of T819 (TL-T819-01) … met". The pairing is plan-161 § Addendum 4's ("TL-T819-01 (= SEC-T820-01)") | — |
| TL-T819-02 | Minor | Highlights: the notice comes only for a tree with the generator's marker | **fixed** | `independent-check-t821-v1.md:60`: "TL-T819-02 met" | — |
| TL-T819-03 | LOW | `CONTRIBUTING.md` § Cutting a release (`:280-293`) does not name the `release-gate` runner or the digest and `allowed_images` coupling | **tracked-LOW** | T819: "Track for register v17" | Y |
| TL-T819-04 | LOW | `sync.mjs:231-238` `validateArgPlaceholders` covers `args` only | **tracked-LOW** | T819: "Track" | I |
| TL-T819-05 | LOW | `.gitlab-ci.yml:267-271` comment names Runner 19.5.2; the dedicated runner is 19.5.3; whether the clone credential still sits in `.gitlab-runner.ext.conf` there is **(unverified)** | **tracked-LOW** | T819: "re-read the runner source for 19.5.3 at the next run". Whether T820 weighed it: not found by grep here **(unverified)** | V |
| SEC-T820-02 | SECURITY:LOW | Accuracy of K-39 and M-6 (scope of the skipped files, grade clause, automation) | **fixed** (the document part; my ruling on what is left) | T820 addendum § 1 remediation; K-39 and M-6 carry all three lines (`docs/releases/v11.0.0.md`, M-6 last paragraph and `:257`, read here; applied in T826 and T821 per the verdict's C2 line). **Left**: the three files skipped in QA's 30-file case are still not identified **(unverified which)**; that belongs to TD-T774-01's code fix, not to this id | — |
| QA-T818-02 | Medium (QA) | The M-1/M-2 cleanup order fails as written (step 1 deletes the provenance file that step 2 needs) | **fixed** (document) | T826; verdict Conditions: "C1 of T818 (QA-T818-02) … met"; T820 addendum: no security grade, fix safe (§ 4); `independent-check-t821-v1.md:61` | — |
| QA-T818-03 | SECURITY:LOW (A04; T820 addendum § 2) | `build.py` checks only the form of `--project-id`, not equality with the remote; the note at `scripts/install.sh:1746` overstates it | **tracked-LOW** | M-5 corrected in the document; code fix (equality check and note) owner backend-developer, next release (T820 addendum § 2; verdict C2 line) | I |
| QA-T818-04 | Low (QA) | While a probe tag of the same core version exists, `resolve_previous_tag` takes it as the previous release (CHANGELOG artifact, drift script) | **tracked-LOW** (the code change) | The v11.0.0 condition was met: probe deleted, no `gate` ref before or after the push, CHANGELOG artifact "_Commits since v10.0.0._" (checkpoint-043 step 3 and 4). Left: "the `resolve_previous_tag` change of QA-T818-04" is listed "LOW for register v17" in the verdict's Conditions (read here). Item 46 | N |
| TL-T821-01 | LOW | SEC-T665-01's Conditions line attributes the swap and hibernation clause to the plan as shown, though the question named only isolation | **tracked-LOW** | `independent-check-t821-v1.md:78`: "Track for register v17. At the next acceptance line for this finding, attribute the clause to T812" (item 43) | Q |

## 4. Decisions since v16

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-13 | "start plan-159" | The runner-tag plan (T810, T811); no tag or probe | plan-159 § User decision |
| 2026-11-13 | "Already done" | SEC-T811-01: every manager except `gitlab-runner-16028` deleted, token reset, one manager | plan-159 § Outcome |
| 2026-11-13 | "Yes, both" | SEC-T811-02: "Protected" ticked, "Run untagged jobs" off | plan-159 § Outcome |
| 2026-11-13 | "Continue with the next best step" | Read by the orchestrator as the word for T812 and the question again only | plan-160 § User decision |
| 2026-11-13 | "Accept for v11.0.0 (Recommended)" | SEC-T660-01 and SEC-T665-01, for v11.0.0 only, after T812, to the question quoted in plan-160 § Outcome; supersedes the answer of 2026-11-12 | plan-160 § Outcome |
| 2026-11-13 | "release plan go" | The word to write plan-161 (recorded there with a leading quote mark: `"release plan go`) | plan-161 § User decision |
| 2026-11-13 | "Approve (Recommended)", "v11.0.0, MAJOR (Recommended)", "Yes, probe first (Recommended)" | Plan-161's approval, version and probe | checkpoint-043 § Key decisions |
| 2026-11-13 | "Yes, push the probe tag" | The probe tag `v11.0.0-gate.1` on `01fe29e4` | plan-161 § Addendum 3 |
| 2026-11-13 | "Yes, merge to develop", "Yes, then merge to main", "Probe deleted, push the tag" | MR !684, MR !685, the tag | checkpoint-043 steps 1 to 3 |
| 2026-11-14 | "v17 go" | This register | plan-162 § User decision |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T811-04 | Fixed in `a4902de2` after T811's proposal, not re-reviewed | the orchestrator | plan-159 § Outcome |
| SEC-T814-01 | Minted from T814's finding; fixed rather than accepted, "because it is small and available" | the orchestrator | plan-161 § Addendum 1 |
| SEC-T825-02 | Fixed by the orchestrator's one-line wording (T820 then reviewed it: PASS) | the orchestrator | plan-161 § Addendum 2; plan-162 § Facts |
| QA-T818-01, -03 code fixes | Tracked under the LOW policy unless graded MEDIUM or higher | the orchestrator | plan-161 § Addendum 4 |
| Merges, pipelines, ledger, tag | As plan-162 § Facts and checkpoint-043 | the orchestrator's record | section 8 |
| SEC-T786-01 fixed | `Installing nodejs (24.22.3-r0)` observed in two `unit-tests` logs, the first before the tag | the orchestrator's observation (2026-11-14, after plan-162) | section 2.2 |
| QA-T818-01 counted with TD-T774-01; TL-T819-01 with SEC-T820-01 | One finding, one id in the counts (as SEC-T657-01 / SEC-T658-01) | **mine** | sections 1.2, 3 |
| SEC-T773-02, SEC-T780-05, SEC-T791-01 fixed | Their only remaining duty was the v11.0.0 document, which carries it | **mine** | section 2.2 |
| TD-T808-02 obsolete | Its condition was v11.0.0's tag date, checked at the tag | **mine** | section 2.2 |
| SEC-T735-08 stays tracked | Recurs at every acceptance question | **mine** (T813 left it to v17) | section 2.2 |
| SEC-T657-01 / SEC-T658-01 and K-15 as `fixed` | "Closed by removal", with the reopen condition | **mine** (status word) | section 2.3 |
| SEC-T820-02 fixed; QA-T818-04 tracked | See section 4.3 | **mine** | section 3 |
| Batches of the new tracked ids | | **mine** | section 5 |

### 4.3 Differences on the record

These stay as the sources state them.
- **QA-T818-04.** Plan-162 § Task Decomposition says "settled at the tag"; the verdict's Conditions list "the `resolve_previous_tag` change of QA-T818-04" as LOW for register v17. Both hold: the v11.0.0 condition was met, the code change is tracked.
- **SEC-T820-02.** The T820 addendum (its counts table, `security-review-t820-release-v11-addendum-v1.md:122`) and the verdict list it as tracked LOW; checkpoint-043 lists it among new tracked LOWs with "(done in T821)"; plan-162 says the document part is done. I record it fixed, with its unidentified-files residue under TD-T774-01.
- **Publishing approvals.** Checkpoint-043 § Key decisions says "The four publishing approvals above"; its steps quote three (step 4, the tag pipeline, quotes none).
- **K-36 of the release document** says the `release` job on the runner is "Not proven", written before the tag; checkpoint-043 step 4 records it ran there.
- **A-21 at the tag.** The verdict's Conditions list A-21 with the deadline "before the tag"; it remained open when v11.0.0 was tagged. The orchestrator did not get it confirmed before publishing (the orchestrator's disclosure, 2026-11-14; not a ruling on its effect, and none is made here).
- **SEC-T786-01.** Checkpoint-043 carries the log check as open; the orchestrator's later observation shows the log line in pipeline 3066902202, before the tag. The later observation governs the status.
- **Plan-161's approval line** reads "pending"; the orchestrator left it as written and quotes the approval in the briefs and checkpoint (plan-161 § Outcome).

## 5. Open items by LOW batch

"Do first" as in v5; the flag's source stays **(unverified)** as v5 § 5 says. Batches not named as changed are carried from v16. O, Z and now S are ended and dropped.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v16 § 5; **new:** QA-T818-03, TL-T819-04 | 25 | as v16; backend-developer for QA-T818-03 and TD-T774-01 (T820 addendum) | as v16; **TD-T774-01 graded LOW, regrade trigger (item 45)**; QA-T818-03 next release |
| J | Opencode `tools` to `permission` | SEC-T663-02 | 1 | as v16 | as v16 |
| K | Security runtime | as v16 § 5; **new:** SEC-T825-01 | 8 | as v16; devops-engineer for SEC-T825-01 (my suggestion) | as v16; SEC-T825-01 at the next lock regeneration |
| L | CWSO helper scripts in emage.code | as v16 § 5 | 5 | as v16 | as v16 |
| M | CWSO repository | as v16 § 5 | 12 | as v16 | as v16 |
| N | Release tooling, second round | as v16 § 5; **new:** QA-T818-04 | 10 | as v16 | as v16; QA-T818-04 before the next probe tag (item 46) |
| P | Upstream report to the Brave project | SEC-T702-08 | 1 | the user files or declines | as v16 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09; **new:** TL-T821-01; **left:** SEC-T784-01, SEC-T773-02, SEC-T780-05, SEC-T791-01 (fixed), TD-T808-02 (obsolete) | 5 | as v16 | **the next release** (items 4, 10, 43) |
| R | Release-gate text, second round | as v16 § 5 | 7 | as v16 | as v16; the route of SEC-T735-06 and -07 still to be settled |
| V | Release gate after plans 142, 143 and 146 | as v16 § 5; **new:** SEC-T811-03, TL-T819-05 | 17 | devops-engineer | as v16; TL-T819-05 at the next runner run or tag-job edit |
| X | CI images, the CA control and runner settings | as v16 § 5; **new:** SEC-T811-05; **left:** SEC-T786-01 (fixed) | 10 | as v16; the user for SEC-T811-05 | as v16 (A-21; item 35); SEC-T811-05 at the next runner maintenance |
| Y | Shipped text and records | as v16 § 5; **new:** TL-T819-03 | 10 | as v16 | as v16; TL-T819-03 before the next release |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v16 | as v16 |
| U | Live checks and user | as v16 § 5 | 7 | the user or an authorised live session | A-2, A-7, A-11, A-15, A-22 |

Total 25 + 1 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 10 + 10 + 2 + 7 = **120** = 119 tracked-LOW + 1 open. Against v16's 118: I + 2, K + 1, N + 1, Q - 5 + 1, S - 1, V + 2, X + 1 - 1, Y + 1. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Order, my suggestion only.**
1. Before 2027-01-28: the SEC-T660-01 and SEC-T665-01 review (item 43); decide early whether the next release comes before 2027-01-30 (Brave) or needs a new Brave record.
2. With the next tag-job image bump: `allowed_images` (item 44) and TL-T819-05.
3. I's TD-T774-01 code fix before any release whose MEDIUM-or-higher fix is a same-size change (item 45); QA-T818-04 before the next probe tag.
4. A-21 (item 34), owed to the v11.0.0 verdict's condition and still open.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v16 § 6.1 stand and stay the record. Since v16: SEC-T660-01 and SEC-T665-01 are accepted by the user for v11.0.0 only (plan-160), after T812; SEC-T702-09's acceptance for v11.0.0 only shipped unchanged. No agent accepted a risk. **Each acceptance covered v11.0.0 only**: each id returns at the next release that ships it, to be fixed or accepted again (release document § Known Issues). End dates: TD-T697-07 **2027-01-29**; SEC-T702-09 **2027-01-30 or the first Brave release above 2.1.4**; SEC-T660-01 and SEC-T665-01 review **2027-01-28**.

### 6.2 Next release checklist (the release after v11.0.0)

Reset from v16 § 6.2, with its numbers. Where an item keeps its text, the text is in the register that last changed it (v11 to v16, as `release-v11-audit-v1.md` § 3 column "Source" lists). Status at v11.0.0 from `release-v11-audit-v1.md` § 3 and the gates.

**Stand as rules for every release (26), text carried**: 3, 4 (TD-T723-01: re-cite current `install.sh` lines), 6, 7, 9, 10 (SEC-T735-09: drop the template's pointer sentence), 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28 (now with the plan-159 runner checks; TL-T819-03), 29, 30, 35. Line citations into `.gitlab-ci.yml` moved with plan-159 as `release-v11-audit-v1.md` § 3 rows 14, 21 and 23 record; re-read them at the next release.

**Done at v11.0.0, dropped (14)**:
- 1 (done at v10.0.0); 13 (settled, T753);
- 2 (the three acceptances recorded in the Conditions; T820 C-1; replaced by item 43);
- 5 and 42 (the Brave dates and v4's gate command on the tag day: checkpoint-043 step 3);
- 31 (M-1, M-2, A-01, A-02, K-37; T819 by hand; T818 install runs);
- 32 (K-15 closed by removal in the release document; reopen condition now item 48);
- 33 (the release document states the ADR-015 and ADR-016 rules as ruled, `docs/releases/v11.0.0.md:42`);
- 36 (K-35 closed, `docs/releases/v11.0.0.md`, § Closed or regraded);
- 38 (SEC-T784-01 fixed, T820);
- 39 (M-4; SEC-T791-01 fixed);
- 37 (SEC-T786-01 fixed: the `unit-tests` log shows `nodejs` 24.22.3-r0 before the tag, the orchestrator's observation; section 2.2);
- 40 and 41 (Conditions lines per ADR-015 and ADR-016, T812 named with its date, T806 not the confirming review: release document K-16 and Conditions; T820 C-1; T821 PASS).

**Stay open (2)**:
- 8: the npm step in a tag pipeline and the musl lock stay **(unverified)**; tag pipeline 3067005699 ran the `release` job, but no source here says what it showed for the npm step.
- 34: A-21, open for the user; the verdict made it a condition "before the tag", not recorded as met (checkpoint-043).

**New (6)**:

43. **The three MEDIUMs accepted for v11.0.0 only: SEC-T660-01, SEC-T665-01, SEC-T702-09.** Each needs a fix or a new acceptance before the next release that ships it; no agent grants or carries one over.
    - SEC-T660-01 and SEC-T665-01: on **2027-01-28** the owner records in the register whether a harness fix now exists and whether the outside closer is still right (ADR-015 O3, W1). A new acceptance needs, before the user is asked, the Security Engineer's new review or dated statement for that release (ADR-016 D1, D2, O-B, O-C; T812 served v11.0.0 and does not serve unseen). If the v11.0.0 plan's deadline (2027-01-28) has passed when the next release ships, the release document says so, with its date and the release it was given for (ADR-015). The Conditions line attributes the swap and hibernation clause to T812 (TL-T821-01).
    - SEC-T702-09: the fix (the first Brave release above 2.1.4) or a new acceptance with a new Brave record (v5) and gate command before the tag; check npm's newest Brave release at preparation.
    - Ask the way SEC-T735-08 says: name the release, show the plan and a deadline still ahead.
44. **The release-gate runner.** At any bump of the tag jobs' image digest, the runner's `allowed_images` changes with it (`docs/wiki/mcp-pin-bump-checklist.md:34`; the comment beside `tags: ["release-gate"]` in `.gitlab-ci.yml`); the user changes the runner. In every `v*` tag pipeline, all three jobs must show runner #59129270, or SEC-T741-17 reopens (plan-159 § Outcome).
45. **TD-T774-01's regrade trigger** (T820 addendum § 1): if the release's fix for a `SECURITY:MEDIUM` or higher finding changes a file without changing its size, TD-T774-01 takes at least that grade, and the code fix lands first or the release carries a verified check for that file. Until the fix, the release document keeps K-39 and M-6's check and `touch` workaround.
46. **Probe tags** (QA-T818-04): until `resolve_previous_tag` skips pre-releases of the same core version, a probe tag of the next version is deleted on the remote and locally (or only `refs/tags/<tag>` is pushed), and `git ls-remote --tags origin` shows no `gate` ref before and after the tag push (T820 C-4; checkpoint-043 step 3).
47. **Dates**: section 6.3; each acceptance shown to the user must have its deadline still ahead at the tag.
48. **K-15's reopen condition**: if the Opencode live check (K-20, A-7, SEC-T658-02) shows the per-agent denies are not honoured, SEC-T657-01 / SEC-T658-01 reopen (release document K-15).

Count: 26 + 14 + 2 = 42 carried numbers, plus 6 new.

### 6.3 Dates

Carried from v16 § 6.3 (through it, v13 § 6.3), with these rows now:

| Date | What | Ids |
|---|---|---|
| **2027-01-28** | GitLab token renewal; the review of SEC-T660-01 and SEC-T665-01's plan, which is its deadline under ADR-015 (item 43) | A-13; SEC-T660-01, SEC-T665-01 |
| **2027-01-29** | End of TD-T697-07 (CWSO over plain HTTP on a LAN; not shipped, not renewed by v11.0.0) | TD-T697-07 |
| **2027-01-30** | End of the Brave acceptance, or the first Brave release above 2.1.4 if earlier; after it the gate fails without a fix or a new acceptance | SEC-T702-09, SEC-T702-01 to -06 |
| **2027-03-12** | `ci_images_reviewed_on: 2026-11-11` (`.gitlab-ci.yml:21`, read here; unchanged in the range) plus 120 days: `test_ci_hash_pins.py` fails from this day | X; item 19 |

## 7. User actions

Carried from v16 § 7, with these changes:
- **A-20: closed.** The user reported "Already done" and "Yes, both" (plan-159); tag pipeline 3067005699 ran all three jobs on runner #59129270 (checkpoint-043). The system ID's tie to `gitlab-runner-16028` is the user's report **(unverified)**.
- **A-21: open.** It stayed open at the tag although the verdict listed it "before the tag" (section 4.3); checkpoint-043 carries it.
- **A-22: open**, state **(unverified)** (the user's own settings files were not opened).
- **K-20 / A-7: open** (live client checks); K-15's reopen condition depends on it.
- **Optional, not a fix** (T812 point 2; release document K-16): read-deny rules for the token file and the `glab` and git credentials in the user's own `.claude/settings.json`.
- SEC-T811-05: runner hardening at the next maintenance, owner the user.
- The probe tag `v11.0.0-gate.1` was deleted by the user in the web UI (checkpoint-043 step 3; the user's report, with the orchestrator's `ls-remote` check).

## 8. Method, limits and validation

- **Carried statuses**: v16's rows and lists, plus the sources in Based on. Plan-162 § Facts and checkpoint-043 are the only source for the merges (!680 to !686), the tag and tag pipeline, the Release body, the ledger count (0 active, 623 completed after !686) and the orchestrator's ids. `docs/tasks/completed-tasks.md` holds 623 task rows and `active-tasks.md` one (T827) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 3130 lines added in `bbe3b8af..42e30d02` outside `tests/golden/` and `.vscode/`, and set against the text of registers v1 to v16; the result is section 1.2. Each v16 id with a change of status was read in its source's context.
- **Counting**: 18 new ids (QA-T818-01 and SEC-T820-01 not counted separately). Section 5 expands to 120 ids. The sizes of unchanged batches are v16's, not recounted id by id here.
- **What real runs proved** (sources only; I read no job log and ran no pipeline): plan-162 § Facts and checkpoint-043 for the tag pipeline, the tag-day checks and the Release body; plan-161 § Addendum 3 for the probe pipeline 3066689514; T818 for the suite and gates at `67222765`.
- **Still unverified**:
  - Carried from v16 § 8.
  - SEC-T786-01's log lines: the orchestrator's observation; I read no job log.
  - The user's reports: SEC-T811-01, -02 (GitLab not read, API 401), the system ID's host, the probe tag's deletion.
  - SEC-T811-03 and -05 rest on GitLab Runner behaviour from the reviewer's memory; TL-T819-05's 19.5.3 credential file.
  - Which three files QA's 30-file case skipped (SEC-T820-02, TD-T774-01).
  - Item 8's npm step and musl lock.
  - From this register: the user's words beyond the plans' records; the full text of the sources (read by section or grep); the batch membership behind "as v16 § 5"; whether T820 weighed TL-T819-05.
- **Not run here**: the suite, the pipelines, `npm`, the audit script, `install.sh`. No mutation and no full suite.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v16.md`; `plan-162-tracked-debt-register-v17.md`; `docs/tasks/task-T827.md`;
  - by section or grep: plans 159, 160, 161; `checkpoint-043-release-v11.0.0.md`; `docs/releases/v11.0.0.md`; the artifacts of T811, T812, T813, T814, T818, T819, T820 (and addendum), T821, T825; registers v11 to v15; `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`;
  - `git diff --shortstat` and `--stat` of `bbe3b8af..42e30d02`; `git diff -U0` of `.gitlab-ci.yml`.
- Decision IDs: ADR-011, ADR-013, ADR-014, ADR-015, ADR-016.
