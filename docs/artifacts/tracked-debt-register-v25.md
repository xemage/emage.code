# Artifact: tracked-debt-register-v25.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v24.md` (737 ids; v24 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-181-tracked-debt-register-v25.md` (§ User decision, § Facts since v24, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T868.md` (the user's "v25 go"); `docs/plans/plan-180-batch-x-text-and-sec-t862-02.md` (§ Outcome); `docs/artifacts/security-review-t867-batch-x-text-v1.md` (PASS); `docs/wiki/mcp-pin-bump-checklist.md` (§ 1 and § 3). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T868 (plan-181; the user's answer of 2026-11-19, verbatim: "v25 go"). **Date**: 2026-11-19.
- **Tree read**: branch `agent/tech-lead/T868` at `12c053f8` (develop `b28ce5d1` plus the plan-181 commit). The range for "lines added since v24" is `04401057..12c053f8` (plan-181 § Facts names `04401057..b28ce5d1`; the one extra commit is plan-181's own plan, brief and ledger row): 14 files, 747 lines added and 14 removed (read here: `git diff --shortstat`). Neither `tests/golden/` nor `.vscode/` has a diff in the range, so the search set outside them is the same 14 files and 747 added lines (read here).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines, outside `tests/golden/` and `.vscode/`, for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on `12c053f8`. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v23 only by grep. `scripts/audit-mcp-pins.py` and the three test files were read only as added lines (section 1.2). `/tmp/evidence-run` was checked only for existence. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v24.
- **Batch letters**: **X** loses SEC-T860-01 and SEC-T860-02 (fixed) and takes **SEC-T867-01** and **SEC-T867-02** (my suggestion), so stays 6. **AB** loses SEC-T862-02 (fixed) and takes **SEC-T867-03** (my suggestion), so stays 2. No new letter.

## 1. Summary

v25 holds **740 ids**: the 737 of v24 and **3 new**. After v25: **568 fixed**, **46 accepted**, **10 obsolete**, **1 open**, **115 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. The one open id is K-20 (live checks, the user; no grade). TD-T789-01 and TD-T808-01 have no reviewer's grade (the orchestrator's ids, called LOW). The only MEDIUMs still accepted for v11.0.0 are SEC-T660-01 and SEC-T665-01 (accepted, not open).
- **Fixed since v24 (3 tracked-LOW)**: SEC-T860-01, SEC-T860-02 (text; batch X) and SEC-T862-02 (batch AB); T866, confirmed by T867 (section 2.2).
- **New and tracked-LOW (3)**: SEC-T867-01, SEC-T867-02 (batch X) and SEC-T867-03 (batch AB) (section 3; batches my suggestion).
- **Tracked-LOW with a changed note (1)**: SEC-T811-05: the runner steps in checklist § 3 are now complete; it stays a user action (section 2.2, section 7).
- **Accepted risks**: unchanged. **Next-release checklist**: unchanged. **Dates**: unchanged; two young-pin exceptions recorded, both lapsing by themselves (section 6.3). **User actions**: SEC-T811-05, now with complete steps; the optional removal of `/tmp/evidence-run` (section 7).

Arithmetic, from the v24 totals:

| Status | v24 | leaves | enters | v25 |
|---|---:|---|---|---:|
| fixed | 565 | | + 3 tracked-LOW (SEC-T860-01, SEC-T860-02, SEC-T862-02) | **568** |
| accepted | 46 | | | **46** |
| obsolete | 10 | | | **10** |
| open | 1 | | | **1** |
| tracked-LOW | 115 | - 3 fixed | + 3 new (SEC-T867-01, -02, -03) | **115** |
| **all** | **737** | | + 3 new ids | **740** |

Check: 568 + 46 + 10 + 1 + 115 = 740. Open or tracked: 115 + 1 = 116, the size of section 5.

### 1.1 Ids by v24 status and status now

| v24 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 115 | 3 | 0 | 0 | 0 | 112 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 565 | 565 | 0 | 0 | 0 | 0 |
| obsolete | 10 | 0 | 0 | 10 | 0 | 0 |
| **all v24 ids** | **737** | **568** | **46** | **10** | **1** | **112** |
| new in v25 | 3 | 0 | 0 | 0 | 0 | 3 |
| **all v25 ids** | **740** | **568** | **46** | **10** | **1** | **115** |

### 1.2 New ids by source and final status

| Source | new | fixed | tracked-LOW |
|---|---:|---:|---:|
| `security-review-t867-batch-x-text-v1.md` § Findings: SEC-T867-01, SEC-T867-02, SEC-T867-03 | 3 | 0 | 3 |
| **All new** | **3** | **0** | **3** |

**Ids minted in the range beyond the plan's list: none.** A search of the 747 added lines in `04401057..12c053f8`, outside `tests/golden/` and `.vscode/`, for every token of the form `<LETTERS>-<T-number>-<suffix>` or `<LETTERS>-<digits>` (which covers `<PREFIX>-T<nnn>-<n>`, `SEC-<nnn>`, `K-<n>`, `A-<n>`, `L-<n>`), and separately for a bare `<PREFIX>-T<nnn>` not followed by a suffix, finds exactly: `ISO-8601`, K-17, K-20, L-2 and L-8 (both from `T638-L-2`, `T638-L-8`), SEC-014, SEC-T675-03, SEC-T675-09, SEC-T676-11, SEC-T676-14, SEC-T702-09, SEC-T811-05, SEC-T856-01, SEC-T860-01, SEC-T860-02, SEC-T862-02, SEC-T867-01, SEC-T867-02, SEC-T867-03 (read here). No bare form occurs.

**Non-debt and context tokens.** `ISO-8601` is a date format (T867 § 1). SEC-014, T638-L-2, T638-L-8, K-17, K-20, SEC-T675-03, SEC-T675-09, SEC-T676-11 and SEC-T676-14 occur only in two tuples of `tests/functional/test_pin_bump_checklist.py` that replace two removed tuples holding the same tokens (read here: the removed lines of the same diff), so the change adds `SEC-T860-01`, `SEC-T860-02` and `"seven days before"` checks and is no status change for any of them. SEC-T702-09 occurs only in T867 § 1 (the brave 2.1.5 bump "retires seven high advisories of 2.1.4"), with no change of status against v24 (v22 removed it from the accepted list). SEC-T856-01 is named as context of the redaction test (fixed in v24).

Set against registers v1 to v24, only SEC-T867-01 to -03 are in no register (read here, by grep). Beside them:
- **Ids named with a change of status**: the 3 fixed ids of section 2.2.
- **Ids named with a changed note and no change of status**: SEC-T811-05 (section 2.2).
- **Ids named with no change of status**: those of the paragraph above. Their statuses are carried from earlier registers and not re-traced id by id here **(unverified beyond the grep)**.
- This register mints no id.

## 2. v24 ids re-checked

Every v24 `open`, `tracked-LOW` and `accepted` id (162) is covered: the changed ones have a row here, the rest are unchanged and carried. The v24 `fixed` and `obsolete` ids stay as v24 records them.

### 2.1 v24 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live Opencode check. K-20 keeps the refused-call, launch and refused-read checks.

### 2.2 v24 `tracked-LOW` (115)

**Changed to fixed (3).**

| Id | v24 | now | Evidence and remainder |
|---|---|---|---|
| SEC-T860-01 | tracked-LOW, batch X | **fixed** | T866 `611c55b6`: checklist § 1 step 1 now has a 7-day minimum release age (read here, line 12); `scripts/audit-mcp-pins.py age` takes `--min-age-days` (default 7) and `--allow-young PKG@VER:REASON` (reason required; must name a current pin), and fails closed (exit 2) on a missing or unparseable time. Two exceptions recorded (section 6.3). T867 § Per-finding status: **Fixed**. The orchestrator ran `age` live: exit 1 without exceptions, 0 with both, 2 for a non-pinned exception (plan-180 § Outcome; not re-run here). **Remainder**: SEC-T867-01, SEC-T867-02 |
| SEC-T860-02 | tracked-LOW, batch X | **fixed (text)** | T866 `84e14c21`: checklist § 3 now holds (a) record `gitlab-runner --version`; (b) `gitlab-runner lint --config /etc/gitlab-runner/config.toml` where the command exists, else the documentation at the exact version tag; (c) `gitlab-runner restart` and `journalctl -u gitlab-runner`; (d) stop and report on any problem; (e) record in § 5; plus an out-of-cycle trigger for runc, containerd, Docker Engine, GitLab Runner or kernel escape advisories, with no release tag until patched (read here, line 39). T867: **Fixed (text)**. **Remainder**: the user applies the steps (SEC-T811-05, section 7) |
| SEC-T862-02 | tracked-LOW, batch AB | **fixed** | T866 `6f445234`: the redaction test also scans each evidence `.md` after v3 and adds `/var/folders/`, `/private/var/` and Windows `X:\Users\`; in the `.md` only, a prefix counts when a path-segment character follows; the wiki names the local clean-suite run as the user-name check of record (plan-180 § Outcome (c)). T867: **Fixed**; T867 did not read the test code **(unverified)** there; the orchestrator read the test diffs for weakened assertions and found none (plan-180 § Outcome; not re-read here). **Remainder**: SEC-T867-03 |

`611c55b6`, `84e14c21` and `6f445234` are cited from plan-180 § Outcome; their content is on `12c053f8` (squash merge `8e11e14c`; the checklist lines were read here). Whether the three shas are ancestors of `12c053f8` was not checked **(unverified)**.

**Tracked-LOW with a changed note (1).**

| Id | Batch | Changed note | Source |
|---|---|---|---|
| SEC-T811-05 | X | **The steps are now complete** in checklist § 3, "Release-gate runner hardening" (read here, line 39): version, `services_limit = 0`, `gitlab-runner lint`, restart, log, record in § 5, out-of-cycle patching, nothing else in the LXC. It stays a **user action** (section 7): no source in the range records that the user applied them | T867 § Per-finding status; plan-180 § Outcome (b); read here |

**Unchanged (111 tracked-LOW; v24 and earlier stay the record of their text)**: by batch: I 24, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 17, X 3 (SEC-T756-02, SEC-T768-04, TL-T761-11), Y 11, F 2, U 5 (U's sixth id is K-20, open), AB 1 (SEC-T856-02). 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 3 + 11 + 2 + 5 + 1 = 111; with the 1 changed-note id, 112 carried; with the 3 new, 115 tracked-LOW in section 5. (The sizes of unchanged batches are carried from v24 and not recounted id by id here; X and AB were traced from v24 § 5.)

### 2.3 v24 `accepted` (46)

**Unchanged (46)**, with their v17 qualifiers (v17 section 2.3) and v22's removal of SEC-T702-09. Neither SEC-T660-01 nor SEC-T665-01 is named in the range.

## 3. New ids

The grade is the reviewer's own (T867 § Findings).

| Id | Grade | Short description | Status | Evidence and remediation | Batch |
|---|---|---|---|---|---|
| SEC-T867-01 | SECURITY:LOW (A08) | `scripts/audit-mcp-pins.py` (lines 503-506, 586 per T867): `--min-age-days` accepts 0 to 9999, so `--min-age-days 0` (or 1) passes every young pin with no recorded reason; the checklist does not forbid it | **tracked-LOW** | Refuse values below `MIN_AGE_DAYS` (exit 2), or print `floor lowered below 7 days` and count it as a finding; say in § 1 that the default is the rule. Owner devops-engineer | X |
| SEC-T867-02 | SECURITY:LOW (A08) | `scripts/audit-mcp-pins.py` (line 542 per T867): the age is a difference of UTC calendar days, so a version published at 23:59Z counts as 7 days old after about 6 days and 1 minute; a duplicate `--allow-young` silently replaces the earlier one | **tracked-LOW** | Compute `(now_utc - published) >= timedelta(days=min_age)` with a fixed `now` in tests; refuse a duplicate exception. Owner devops-engineer | X |
| SEC-T867-03 | SECURITY:LOW (A09) | `T861EvidenceRedactionTests` in `tests/functional/test_mcp_agent_denials.py` (T867 did not read it **(unverified)**; not opened here): in the `.md` scan a prefix counts only when a path-segment character follows, so a user name separated from its prefix by a quote or a space on a prose line would pass | **tracked-LOW** | Exclude only the exact v4 Redaction line (full text or a fixed marker) and apply the strict any-occurrence rule to every other line; add a mutation with a prefix and a user name split by a space on a prose line. Owner devops-engineer | AB |

## 4. Decisions since v24

### 4.1 The user's (words verbatim as recorded)

Each row claims only what its source records. I did not verify the words beyond those records **(unverified)**.

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-19 | "v25 go" | This register | plan-181 § User decision; T868 brief |

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T860-01, SEC-T860-02 (text), SEC-T862-02 | Fixed | T867 (PASS); the orchestrator | T867 § Per-finding status; plan-180 § Outcome |
| The brave 2.1.5 exception | Confirmed (2 days old when pinned, found by T866) | T867; the orchestrator | plan-180 § Outcome (a) |
| SEC-T867-01 to -03 | Minted LOW, tracked under the LOW policy (T867: "Conditions: None") | T867; the orchestrator | T867 § Conditions; plan-180 § Outcome |
| Batches of the three new ids | X, X, AB | me (suggestion) | section 5 |
| Merges, pipelines, suite, ledger | As plan-181 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in ids, statuses or totals.** My reading gives the same 3 fixed, 3 new tracked-LOW, 740 ids (568 / 46 / 10 / 1 / 115) and a batch total of 116. What I add: the batches of the three new ids, one changed note (SEC-T811-05), the context tokens of section 1.2 and the points below.
- **The commit range.** Plan-181 § Facts names `04401057..b28ce5d1`; this register searched `04401057..12c053f8`, which adds plan-181's own commit. That commit mints no id.
- **The lapse dates of the exceptions.** Plan-181 § Task Decomposition notes only the brave exception, lapsing on 2026-11-24. Checklist § 1 (read here, lines 12-15) records **two**: `server-filesystem@2.4.0` (published 2026-11-18, so 7 calendar days on **2026-11-25**) and `@brave/brave-search-mcp-server@2.1.5` (published 2026-11-17, so **2026-11-24**). Under SEC-T867-02, `age` counts UTC calendar days, so either can pass up to just under a day before 7 full days have elapsed. The checklist says each "stops being needed once the pin is 7 days old"; the exceptions stay in the list, and nothing removes them (section 6.3).
- **Ledger.** Plan-181 § Facts: "0 active, 664 completed". Read here: `completed-tasks.md` holds 664 task rows and `active-tasks.md` one (T868, added by the plan-181 commit). No difference.

## 5. Open items by LOW batch

Carried from v24 § 5; X and AB change members, not size.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v24 § 5 | 24 | as v24 | as v24 |
| K | Security runtime | as v24 § 5 | 8 | as v24 | as v24 |
| L | CWSO helper scripts in emage.code | as v24 § 5 | 5 | as v24 | as v24 |
| M | CWSO repository | as v24 § 5 | 12 | as v24 | as v24 |
| N | Release tooling, second round | as v24 § 5 | 10 | as v24 | as v24 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v24 | as v24 |
| Q | Next release document and its gate rulings | as v24 § 5 | 5 | as v24 | as v24 |
| R | Release-gate text, second round | as v24 § 5 | 7 | as v24 | as v24 |
| V | Release gate after plans 142, 143 and 146 | as v24 § 5 | 17 | as v24 | as v24 |
| **X** | CI images, the CA control, runner settings and the pin-age check | SEC-T756-02, SEC-T768-04, TL-T761-11, SEC-T811-05; **new:** SEC-T867-01, SEC-T867-02. **Left:** SEC-T860-01, SEC-T860-02 (fixed) | 6 | devops-engineer (text and `audit-mcp-pins.py`); the user for SEC-T811-05's steps | SEC-T768-04 at the next tag-job change; SEC-T867-01 and -02 with the next change to `audit-mcp-pins.py age` or at the next `npx` pin bump, whichever comes first; SEC-T811-05 applied by the user at the next runner maintenance; SEC-T756-02 and TL-T761-11 as v24 (every image bump passes both CA jobs, item 35) |
| Y | Shipped text and records | as v24 § 5 | 11 | as v24 | as v24 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v24 | as v24 |
| U | Live checks and user | as v24 § 5 | 6 | as v24 | as v24 (K-20 keeps the refused-call, launch and refused-read checks) |
| **AB** | Opencode permission, third round: the T855 residuals and their evidence runs | SEC-T856-02 (narrowed, as v24); **new:** SEC-T867-03. **Left:** SEC-T862-02 (fixed) | 2 | devops-engineer (generator, tests and docs; the orchestrator assigns) | the next change to the Opencode permission generator or its docs, or the next `mcp-agent-denials-evidence` run, whichever comes first; check at next-release preparation with item 49 |

Total 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 17 + 6 + 11 + 2 + 6 + 2 = **116** = 115 tracked-LOW + 1 open (K-20). Against v24's 116: X - 2 + 2, AB - 1 + 1. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01 and TD-T808-01 have no reviewer's grade.

**Why X for SEC-T867-01 and SEC-T867-02.** Both are residuals of the SEC-T860-01 fix (X): the `age` subcommand of `scripts/audit-mcp-pins.py` and the § 1 rule of `docs/wiki/mcp-pin-bump-checklist.md`, the document batch X already lives in. Same owner, and the natural trigger is the next `npx` pin bump, which X already watches. A new letter for two ids on one surface would split it (v12 Metadata).

**Why AB for SEC-T867-03.** It is a residual of the SEC-T862-02 fix (AB) in `T861EvidenceRedactionTests`, and its trigger is the next evidence run, AB's trigger.

**Order, my suggestion only.** v24 § 5 stands, with these changes: in X, SEC-T867-01 before the next pin bump (a one-line floor closes the silent bypass), SEC-T867-02 with it; in AB, SEC-T867-03 with the next evidence run.

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

v5 to v24 § 6.1 stand and stay the record, unchanged. **The MEDIUMs accepted for v11.0.0 only are SEC-T660-01 and SEC-T665-01**, review **2027-01-28** (token renewal). None accepted since v24. No agent accepted a risk. The two young-pin exceptions (section 6.3) are recorded exceptions under the checklist § 1 rule, reviewed by T860 and T867; they are not risk acceptances.

### 6.2 Next release checklist (the release after v11.0.0)

v24 § 6.2 (through it v23 to v17 § 6.2) stands, unchanged. Count: the numbers of v24 stand.

### 6.3 Dates

- **2027-01-28**: SEC-T660-01 and SEC-T665-01 review (token renewal). Unchanged.
- **2027-01-29**: TD-T697-07 ends. Unchanged.
- **2027-03-20**: the CI image review date fails (`ci_images_reviewed_on: 2026-11-19`; 2027-03-19 is the last passing day, v24 § 4.3). Unchanged; `.gitlab-ci.yml` has no diff in the range (read here).
- **Young-pin exceptions** (checklist § 1, read here, lines 13-15), both predating the 7-day rule:
  - `@modelcontextprotocol/server-filesystem@2.4.0`: published 2026-11-18, pinned 2026-11-19 (T859); 7 days old on about **2026-11-25**.
  - `@brave/brave-search-mcp-server@2.1.5`: published 2026-11-17, pinned 2026-11-19 (T851); 7 days old on about **2026-11-24**.

  Each lapses by itself once the pin is 7 days old: from then `age` passes without the `--allow-young` entry. Caveat (SEC-T867-02): the check counts UTC calendar days, so it may pass up to just under one day before 7 full days. A bump of either pin voids its exception (it must name a current pin).

## 7. User actions

v24 § 7 stands, with this change:

- **SEC-T811-05: harden the release-gate runner; the steps in checklist § 3, "Release-gate runner hardening", are now complete** (SEC-T860-02 fixed in text; an agent changes nothing on the runner or its host). In the runner's LXC:
  1. **Version**: record `gitlab-runner --version` and check the option names in that version's documentation.
  2. **Services**: in `[runners.docker]` add `services_limit = 0`; keep `privileged = false`; set no `allowed_privileged_services`.
  3. **Lint**: before the restart, if `gitlab-runner --help` lists it, run `gitlab-runner lint --config /etc/gitlab-runner/config.toml`; without `lint`, confirm `services_limit` in the documentation at the tag of exactly that version.
  4. **Restart**: `gitlab-runner restart`, and check that the next tag pipeline's three jobs still start.
  5. **Log**: `journalctl -u gitlab-runner --since "-10 min"`; on a `lint` failure or a log line calling `services_limit` unknown, unsupported, invalid or deprecated, stop and report to the Security Engineer.
  6. **Record in § 5**: date, version output, `lint` result (or "no lint command") and log result.
  7. **Patching**: at every CI image review, update Docker Engine and GitLab Runner in the LXC and the Proxmox VE kernel on the host (reboot), record the three versions in § 5; **out-of-cycle**: patch at once for a critical container-escape advisory for runc, containerd, Docker Engine, GitLab Runner or the kernel, and push no release tag until patched.
  8. **Nothing else in that LXC**: no other runner, service, cron job or user.
- **Optional: remove `/tmp/evidence-run`**, the neutral evidence root T861 created. It still exists (read here, existence only).

K-20 / A-7 stays open.

## 8. Method, limits and validation

- **Carried statuses**: v24's rows and lists, plus the sources in Based on. Plan-181 § Facts is the only source for the merges (!704, !705), the suite (2832 OK at `62dcbe62`, skipped=25), the pipelines (3089984650, 3089984508), the root drift (`[]`) and the ledger count. `docs/tasks/completed-tasks.md` holds 664 task rows and `active-tasks.md` one (T868) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 747 lines added in `04401057..12c053f8` outside `tests/golden/` and `.vscode/` (there is no diff in either), and set against the text of registers v1 to v24; the result is section 1.2. Context tokens in test tuples were classified against the removed lines of the same diff.
- **Counting**: 3 new ids, 3 status changes into `fixed` (all tracked-LOW). Section 5 expands to 116 ids; the sizes of unchanged batches are v24's, not recounted id by id here; X and AB were traced from v24 § 5.
- **Still unverified**:
  - Carried from v24 § 8.
  - The orchestrator's live `age` runs and its reading of the test diffs (plan-180 § Outcome; not re-run here).
  - SEC-T867-01 to -03's line numbers (T867's; the script and test files were read here only as added lines).
  - Whether T866's three commit shas are ancestors of `12c053f8`.
  - The orchestrator's suite and pipelines (plan-181 § Facts; not re-run here).
  - The batch membership behind "as v24 § 5", and the statuses of the context tokens of section 1.2.
- **Not run here**: the suite, the pipelines, `audit-mcp-pins.py`, the generator, Opencode.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v24.md`; `plan-181-tracked-debt-register-v25.md`; `docs/tasks/task-T868.md`; `plan-180-batch-x-text-and-sec-t862-02.md` (§ Outcome); `security-review-t867-batch-x-text-v1.md` (§ Per-finding status, § Findings, § VERDICT, § Conditions);
  - by grep or line read: `docs/wiki/mcp-pin-bump-checklist.md` (lines 11-16, 39); registers v1 to v24 (the token scan); `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md`;
  - `git diff --shortstat`, `--stat` and `-U0` of `04401057..12c053f8` (added and removed lines, for the token scan).
- Decision IDs: ADR-011, ADR-015, ADR-016.
