# Artifact: tracked-debt-register-v36.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v35.md` (780 ids; v35 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there; its § 5 and § 6 are carried by reference where this register says "as v35"); `docs/plans/plan-204-tracked-debt-register-v36.md` (§ User decision, § Facts since v35, § The orchestrator's expected delta, § Task Decomposition) and `docs/tasks/task-T916.md` (the user's "v36 go"); `docs/plans/plan-203-batch-x-apk-allowlist.md` (§ User decision "X with apk-allowlist", § Outcome); `docs/artifacts/security-review-t914-batch-x-v1.md` (T915 review: per-id table, new findings SEC-T915-01 to -04, the verdict's LOW table and the orchestrator's addendum); the precedents `tracked-debt-register-v32.md`, `-v33.md` (a fixed id whose residue is a new id) and `-v26.md` (a restatement counts once), and v35 § 1 (the same ruling for SEC-T909-01). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T916 (plan-204; the user's answer of 2026-11-28, verbatim: "v36 go"). **Date**: 2026-11-28.
- **Tree read**: branch `agent/tech-lead/T916` (develop `72cba2dd` plus the plan-204 and T916 commit `a019dc37`). The range for "lines added since v35" is `7f44fd35..72cba2dd`: 6 files, 289 lines added and 53 removed (read here: `git diff --shortstat`). The files are `tests/functional/test_ci_hash_pins.py` (plan-203, T914), the T914 security review, plan-203, the completed-tasks ledger and the task briefs of T914 and T915. No change to `.gitlab-ci.yml`, `scripts/`, `docs/releases/`, `docs/wiki/`, `tests/golden/`, `.mcp.json` or `.vscode/` (read here: `git diff --name-only`).
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on this tree. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **X** drops SEC-T912-01 to -04 (fixed) and gains SEC-T915-01 to -04, so X keeps **6** members (two unchanged, four new). No other batch changes; no new letter, no letter ends.

## 1. Summary

v36 holds **784 ids**: the 780 of v35 and **4 new** (SEC-T915-01 to -04, found by T915 in the review of MR !731). After v36: **629 fixed**, **46 accepted**, **14 obsolete**, **1 open**, **94 tracked-LOW**.

- **Open above LOW: nothing.** T915 found 0 CRITICAL, HIGH or MEDIUM. The one open id is K-20 (live checks, the user; no grade). TD-T808-01 and TD-T888-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v35, from tracked-LOW (4)**: SEC-T912-01, SEC-T912-02 and SEC-T912-04 closed by T914 (T915 PASS; section 2.2); and SEC-T912-03 **counted fixed by my ruling** (section 1.3), its residue carried once by SEC-T915-01 and -02.
- **New, tracked-LOW (4)**: SEC-T915-01 to -04 (batch X; section 3).
- **Nothing is minted and closed in the same MR, and nothing is obsolete, in this range.**
- **Unchanged in batch X**: SEC-T881-02 (the user chose "Keep the lock") and SEC-T756-02 (the user's runner and variable side, A-21).
- **The apk allowlist is decided, not open**: the user's word of 2026-11-23, "X with apk-allowlist" (plan-203), implemented by T914 (section 4.1). v35 § 7 recorded it as a question; it is closed here.
- **Next-release checklist**: 36 numbers carried, none new; no item changes (section 6.2). **Dates**: as v35; the three dates of v35 § 6.3 that fell in late November have passed (section 6.3). **User actions**: v35's, plus the two questions in section 7.

Arithmetic, from the v35 totals:

| Status | v35 | leaves | enters | v36 |
|---|---:|---|---|---:|
| fixed | 625 | | + 4 from tracked-LOW (SEC-T912-01, -02, -03 by ruling, -04) | **629** |
| accepted | 46 | | | **46** |
| obsolete | 14 | | | **14** |
| open | 1 | | | **1** |
| tracked-LOW | 94 | - 4 fixed | + 4 new (SEC-T915-01 to -04) | **94** |
| **all** | **780** | | + 4 new ids | **784** |

Check: 629 + 46 + 14 + 1 + 94 = 784. Open or tracked: 94 + 1 = 95, the size of section 5.

### 1.1 Ids by v35 status and status now

| v35 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 94 | 4 | 0 | 0 | 0 | 90 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 625 | 625 | 0 | 0 | 0 | 0 |
| obsolete | 14 | 0 | 0 | 14 | 0 | 0 |
| **all v35 ids** | **780** | **629** | **46** | **14** | **1** | **90** |
| new in v36 | 4 | 0 | 0 | 0 | 0 | 4 |
| **all v36 ids** | **784** | **629** | **46** | **14** | **1** | **94** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t914-batch-x-v1.md` § New findings: SEC-T915-01, -02, -03, -04 | 4 | 0 | 0 | 4 |
| **All new** | **4** | **0** | **0** | **4** |

**Ids minted in the range beyond T915's list: none.** A search of the 289 lines added in `7f44fd35..72cba2dd` (`git diff -U0`) for every token of the form `<LETTERS>-T<number>-<suffix>`, `<LETTERS>-<digits>` or `ADR-<digits>` finds 12 distinct tokens, set against the text of registers v1 to v35. Exactly four appear in no register: **SEC-T915-01, SEC-T915-02, SEC-T915-03, SEC-T915-04**. The other eight are in earlier registers: SEC-T912-01 to -04 (fixed here, section 2.2), SEC-T909-02, SEC-T891-01, SEC-T881-02 and SEC-T756-02 (named as unchanged). Most of the occurrences come from the T915 review and plan-203, which name the v35 ids.

**Duplicates: none.** SEC-T915-01 and -02 are the residue of SEC-T912-03 (section 1.3), counted once, as new ids. SEC-T915-03 and -04 are defects of the T914 code and its tests and restate no earlier id.

### 1.3 My ruling on SEC-T912-03

**Counted fixed, its residue carried once by SEC-T915-01 and -02.** T915 grades it "Partly closed" and names the remainder in its own table: "Residue (see SEC-T915-01 and -02)". I checked the T912-03 forms against the T915 text, not against the status word alone:

- `env $PM`, `X=1 $PM`, `then $PM`, `eval $X`, a later line of a block: closed, since every `$`, backtick or `eval` at any position in the three fields of the two jobs is refused unless its line is pinned (T915, reasoned, not run).
- `extends:` and `default:` that could add lines: closed, since `extends` on either job is refused and the top-level `default:` may not carry the three fields (T915).
- A program with no trigger token, and a job-level key outside the three fields, in the python job: **not closed**. T915 names these as SEC-T915-01 and -02 and calls them "the residue of SEC-T912-03" (addendum).

So the remainder of SEC-T912-03 is exactly -01 and -02, and T915 itself says "the register counts the residue once, as in the precedents". This is the v35 ruling for SEC-T909-01 (T912 said "Partly fixed"; counted fixed; residue as new ids). Keeping SEC-T912-03 tracked as well would count the same remainder twice, which v26 forbids. Every remainder is tracked once in batch X. The word "partly" in T915 describes the state of the finding, and this register's states are fixed, accepted, obsolete, open and tracked-LOW; the T915 text supports counting it fixed with its residue on the two new ids. This agrees with the orchestrator's expected delta.

## 2. v35 ids re-checked

Every v35 `open`, `tracked-LOW` and `accepted` id (141) is covered: the changed ones have a row here, the rest are unchanged and carried. The v35 `fixed` and `obsolete` ids stay as v35 records them.

### 2.1 v35 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v35 `tracked-LOW` (94)

Basis: plan-203 Outcome, T915's per-id table (reasoned; T915 had no shell) and the orchestrator's addendum. Plan-203: MR !731, develop `72cba2dd`, pinned `82631d40`; the suite was 2873 OK, skipped=38 in the MR pipeline and 2871 on develop (the difference is the two tests T914 added). **Verified here in `git diff --name-only 7f44fd35..72cba2dd`**: only `tests/functional/test_ci_hash_pins.py` changes among code and CI files; no job, digest, pin, `.gitlab-ci.yml` line, published `docs/releases/v*.md` or `tests/golden/` file is touched. The range's `.mcp.json` is not in the diff.

**Changed to fixed (4).**

| Id | v35 batch | now | Evidence and remainder |
|---|---|---|---|
| SEC-T912-01 | X | **fixed** (T914, plan-203; T915 closed) | `apk_allowlist_problems` refuses any of `before_script`, `script`, `after_script` that is not a list of strings, for both jobs, with no silent skip. Mutations cover a string, a nested list, an int item, `after_script: null` and `after_script: "apk add x"` (T915, reasoned, not run) |
| SEC-T912-02 | X | **fixed** (T914, plan-203; T915 closed) | The decision is equality with a pinned line, not a scan, so the stray apostrophe cannot hide a redirect. `apk add x ' > /tmp/y` is refused (T915, reasoned, not run) |
| SEC-T912-03 | X | **fixed by my ruling** (section 1.3; T915 "partly closed") | Closed: `extends`, `default:`, `$`, backtick and `eval` in any position of the three fields of both jobs. **Residue, tracked once as SEC-T915-01 and -02** |
| SEC-T912-04 | X | **fixed** (T914, plan-203; T915 closed) | The judged set is now only lines with `apk`, `$`, a backtick or `eval`. The test `test_the_real_ci_has_no_other_line_with_a_trigger_token_in_the_two_jobs` asserts by sorted equality which real lines are judged (T915 read the real file, reasoned, not run) |

**Unchanged (90 tracked-LOW)**: by batch: I 25, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 3, X 2 (SEC-T756-02, SEC-T881-02), Y 2 (SEC-T904-01, SEC-T904-03), F 2, U 5 (U's sixth id is K-20, open), AB 3: 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 2 + 2 + 2 + 5 + 3 = 90 = the 94 of v35 less 4 fixed. The sizes of unchanged batches are carried from v35 and not recounted id by id.

### 2.3 v35 `accepted` (46)

**Unchanged (46)**, with their v35 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. No source in the range changes any of them. SEC-T702-09 is not in this list: v22 records it fixed (section 4.3).

## 3. New ids

The grade is the reviewer's own (T915 § New findings). Owner: devops-engineer (my suggestion; no source names one). All four are tracked-LOW (new); nothing is minted and closed in the same MR. Line numbers are T915's and were not re-read.

| Id | Grade | Short description | Status | Remediation | Batch |
|---|---|---|---|---|---|
| SEC-T915-01 | SECURITY:LOW (A08) | `ca-chain-check-python` is not in `PINNED_JOBS`, so its lines are judged only for the trigger tokens `apk`, `$`, a backtick and `eval`. An install or command without those tokens passes (a glob such as `/sbin/a?k`, a `python3 -c` program, `base64 -d \| sh`, `sh other.sh`). The job is the reference the drift gate's CA lines are paired with, so an extra install there makes the check prove a different store. No current exposure: the real file has none of these, and the job runs only in branch and merge request pipelines | **tracked-LOW** (new) | Pin the python job's lines exactly, as the drift gate's are (a constant list and an `assertEqual` on `script` and `before_script`, in a separate pin). SEC-T915-01 and -02 are one fix | X |
| SEC-T915-02 | SECURITY:LOW (A08) | The python job's key set is not pinned: `hooks:` (`pre_get_sources_script`), `run:` or any other job-level key is not judged (only `default:hooks` is refused). No current exposure | **tracked-LOW** (new) | Check the job's key set exactly and add a mutation with `hooks` on that job; the same fix as SEC-T915-01 | X |
| SEC-T915-03 | SECURITY:LOW (A08) | The python job's permitted apk line is counted across the three fields but not placed. Moved to `after_script`, or before the copy of the shipped store, it passes, although the check relies on the order. Not a regression: the old code had the same gap | **tracked-LOW** (new) | Assert the apk line's index in `before_script`: after the cp line and the release floor, before the live-store checks (as the gate's test does); or fold it into the exact list of SEC-T915-01 | X |
| SEC-T915-04 | SECURITY:LOW (A08, test quality) | The mutation "drift gate permitted line moved to after_script" appends a trailing space, so it proves refusal of an altered line, not of a verbatim move or repeat. Inside `apk_allowlist_problems` a verbatim move or a duplicate is accepted; only `PINNED_JOBS` refuses it | **tracked-LOW** (new) | Add verbatim move and duplicate cases for the pinned job, asserting that the refusal comes from `pinned_job_problems`; or document that this function relies on the pin | X |

**Why batch X.** All four concern the CI-lock and pin checks in `tests/functional/test_ci_hash_pins.py`, the surface of SEC-T909-01 and -02 and of SEC-T912-01 to -04. Trigger (my suggestion, from T915): the next edit of the `ca-chain-check-python` job or its pins (SEC-T915-01 and -02 are one fix), and at the latest the next image bump that changes that job's `script` shape. SEC-T915-03 and -04 are in the same test file, and T915 places their remediation there too.

## 4. Decisions since v35

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-22 | "X go" | Batch X round 2, plan-201 (SEC-T909-01, -02) | plan-201 § User decision |
| 2026-11-22 | "v35go" | Register v35 | plan-202 § User decision; T913 brief |
| 2026-11-23 | "X with apk-allowlist" | The exact-line allowlist of the apk check (plan-203); closes the question of v35 § 7 | plan-203 § User decision |
| 2026-11-28 | "v36 go" | This register | plan-204 § User decision; T916 brief |

I did not verify the words beyond those records. No risk was accepted by the user in the range.

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T912-01 to -04 tracked, fixed by T914 | Closed by an exact-line allowlist, the user's word of 2026-11-23 | the user; T914 | plan-203 |
| SEC-T912-03 counted fixed, residue SEC-T915-01 and -02 | v26, v32 and v33 precedents; the v35 ruling for SEC-T909-01; T915's own "the register counts the residue once" | the orchestrator proposed; **I confirm** | section 1.3 |
| SEC-T915-01 and -02 are one fix | An exact pin of the python job's lines and key set | the orchestrator's addendum (T915) | security review addendum |
| SEC-T915-01 to -04 in batch X | The same surface as SEC-T909-01 and -02 and SEC-T912-01 to -04 | **mine** | section 3 |
| Merges, pipelines, ledger | As plan-204 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in any count.** Ids 784, fixed 629, accepted 46, obsolete 14, open 1, tracked-LOW 94, section 5 of 95, and batch X of 6 (SEC-T756-02, SEC-T881-02, SEC-T915-01 to -04) all agree. I derived each from v35 and the delta (sections 1 and 5). The ruling on SEC-T912-03 is mine, reached against the review text (section 1.3), and it matches the expected delta.
- **T915's status word.** T915 says "partly closed" for SEC-T912-03; I count it fixed, as section 1.3 explains. The register's states are fixed, accepted, obsolete, open and tracked-LOW.
- **SEC-T702-09 (the plan's § 7 question).** Plan-204 § Task Decomposition asks that SEC-T702-09 be put to the user as open. This register's record does not show it open: v22 records SEC-T702-09 **fixed** by the Brave pin bump to 2.1.5 (T851, T852 PASS), and v22 § 6.1 ends its acceptance. The tracked tree agrees: `.mcp.json` line 62 pins `@brave/brave-search-mcp-server@2.1.5` (read here). The v11.0.0 release document (`docs/releases/v11.0.0.md`, K-28 and its RELEASE VERDICT) and plan-204's "npm newest still 2.1.4 on 2026-11-12" describe it as the open MEDIUM of the release, with its acceptance for v11.0.0 only. **I did not decide which record is right.** The reconciliation is the orchestrator's (section 7, question 2). No count in this register depends on it.
- **Ledger.** Plan-204 § Facts: "0 active, 710 completed". Not re-counted row by row; the T916 row is the one active row, and it leaves when the orchestrator closes it.

## 5. Open items by LOW batch

Carried from v35 § 5; **X keeps its size and changes members**; all other rows unchanged.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v35 § 5 (includes TD-T888-01) | 25 | as v35 | as v35 |
| K | Security runtime | as v35 § 5 | 8 | as v35 | as v35 |
| L | CWSO helper scripts in emage.code | as v35 § 5 | 5 | as v35 | as v35 |
| M | CWSO repository | as v35 § 5 | 12 | as v35 | as v35 |
| N | Release tooling, second round | as v35 § 5 | 10 | as v35 | as v35 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v35 | as v35 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v35 | each release's preparation |
| R | Release-gate text, second round | as v35 § 5 | 7 | as v35 | as v35 |
| V | Release gate, fourth round | SEC-T900-02, SEC-T900-04, SEC-T900-06 | 3 | devops-engineer | the next change to `scripts/verify-release-docs.py`; at the latest before the tag's release document is gated (item 52) |
| **X** | CI images, the CA control, the CI locks and the pin-age check | **stay:** SEC-T756-02, SEC-T881-02. **new:** SEC-T915-01, SEC-T915-02, SEC-T915-03, SEC-T915-04. **Left (fixed):** SEC-T912-01, SEC-T912-02, SEC-T912-03, SEC-T912-04 (and SEC-T909-01, SEC-T909-02 as v35) | 6 | devops-engineer (SEC-T915-01 to -04: my suggestion; no source names one) | SEC-T756-02, SEC-T881-02: as v35; SEC-T915-01 to -04: the next edit of the `ca-chain-check-python` job or its pins, and at the latest the next image bump that changes that job's `script` shape |
| Y | Shipped text and records | SEC-T904-01, SEC-T904-03 | 2 | technical-writer (SEC-T904-01); devops-engineer (SEC-T904-03) (as v35) | as v35 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v35 | as v35 |
| U | Live checks and user | as v35 § 5 | 6 | as v35 | as v35 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v35 | as v35 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 6 + 2 + 2 + 6 + 3 = **95** = 94 tracked-LOW + 1 open (K-20). Against v35's 95: minus 4 (the fixed T912 ids) and plus 4 (the new T915 ids) in X, so unchanged at 95 (tracked-LOW 94 - 4 + 4 = 94). **No open item carries a grade above LOW** on any scale; K-20, TD-T808-01 and TD-T888-01 have no reviewer's grade.

**Rows changed against v35: X only (members).**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v35 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range.

### 6.2 Next release checklist (the release after v12.0.0)

v35 § 6.2 stands with its numbers and text (36 numbers; item 8 open; item 17 as amended in v29 and v31; item 52 with 16 points). **No change from this range.** Checked against the range:

- **plan-203 (T914).** A test file only (`tests/functional/test_ci_hash_pins.py`); no job, digest, pin, checklist page or release-gate script changed (`.gitlab-ci.yml`, `scripts/` and `docs/wiki/` not in the range). The wiki pin-bump checklist is not in the range; a grep of it for the old denylist wording found none (not read in full).
- **SEC-T915-01 to -04** are batch X debt, not a release condition.
- **Item 8** stays open: no tag pipeline ran in the range. Items 43, 44, 46 to 51 and points 1 to 16 of item 52: as v35.

Count: 36 numbers carried, 0 new; item 52 has 16 points.

### 6.3 Dates

Unchanged from v35 § 6.3 except for what has now passed (today is 2026-11-28):

- **Passed**: the young-pin exceptions lapsed about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0, 7 days old about **2026-11-26** **(derived, unverified)**. Whether any check now behaves differently was not run here. **No bump is decided by this register**: the pinned Brave version is in section 4.3 and section 7.
- **Future**: **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19` at `.gitlab-ci.yml` line 25, read here; the range changes no `.gitlab-ci.yml` line), 2027-03-19 the last passing day.

## 7. User actions

v35 § 7 stands unchanged, except that the allowlist question is closed (section 4.1):

- **The CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists. Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).
- The SEC-T881-02 choice stays decided ("Keep the lock (Recommended)", 2026-11-21). SEC-T756-02 stays with the user's runner and variable side (A-21).

**Questions the user may rule on (not decided here):**

1. **The Brave bump.** The pin is 2.1.5 (`.mcp.json` line 62, read here). The register records no decision on a 2.2.0 bump; its 7-day age passed on about 2026-11-26 (section 6.3, unverified whether 2.2.0 exists or what it changes). Bump, or keep 2.1.5 and say so. A one-word answer is enough.
2. **SEC-T702-09's record.** The register records it fixed at v22 (Brave 2.1.5); plan-204 and the v11.0.0 release document record it as the open shipped MEDIUM. The user's ruling, or the orchestrator's reconciliation with the release document, is needed before the next release verdict. This register does not decide it (section 4.3).

## 8. Method, limits and validation

- **Carried statuses**: v35's rows and lists, plus the sources in Based on. Plan-204 § Facts and the plan-203 Outcome are the only sources for the merge (!731), the pinned shas, the suite counts and the pipelines. The ledger figure "0 active, 710 completed" is the plan's. No network call was made.
- **The search for changes**: every id-like token was extracted from the 289 lines added in `7f44fd35..72cba2dd` and set against the text of registers v1 to v35; the result is section 1.2 (12 distinct tokens, 4 in no register).
- **Counting**: 4 ids named new by T915; 4 counted (no duplicate), all tracked-LOW; 4 status changes into `fixed` from tracked-LOW (3 by closure, 1 by my ruling). Section 5 stays at 95 ids; the sizes of unchanged batches are v35's, not recounted id by id.
- **Still unverified**:
  - Carried from v35 § 8.
  - T915's reading (no shell; the orchestrator's and the engineer's test runs, the clean suite and the pipeline are taken as given; "reasoned, not run" throughout).
  - The line numbers in SEC-T915-01 to -04 (T915's).
  - The Brave 2.2.0 release and its contents (no network call).
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - The batch membership behind "as v35 § 5".
- **Not run here**: the suite, the pipelines, the mutations.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'` (exit codes in the T916 report).

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v35.md`; registers v1 to v35 (the token search, by grep); `-v26.md`, `-v32.md`, `-v33.md` (precedents); `plan-204-tracked-debt-register-v36.md`; `plan-203-batch-x-apk-allowlist.md` (User decision, Outcome); `security-review-t914-batch-x-v1.md` (all sections, addendum);
  - `git diff --shortstat`, `--name-only` and `-U0` of `7f44fd35..72cba2dd`; `.gitlab-ci.yml` line 25 and `.mcp.json` line 62 (read here);
  - `docs/releases/v11.0.0.md` and `docs/artifacts/tracked-debt-register-v22.md` (section 4.3 only, for the SEC-T702-09 record).
- Decision IDs: ADR-011, ADR-015, ADR-016.
