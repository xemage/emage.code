# Artifact: tracked-debt-register-v34.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v33.md` (774 ids; v33 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there; its § 5 and § 6 are carried by reference where this register says "as v33"); `docs/artifacts/tracked-debt-register-v26.md`, `-v24.md` and `-v15.md` (the precedents for counting an id minted before merge); `docs/artifacts/tracked-debt-register-v31.md` (SEC-T897-01, SEC-T891-02) and `-v12.md` (TL-T753-05); `docs/plans/plan-200-tracked-debt-register-v34.md` (§ User decision, § Facts since v33, § The orchestrator's expected delta, § Task Decomposition) and `docs/tasks/task-T910.md` (the user's "v34 go"); `docs/plans/plan-198-tl-t753-05-root-refresh.md` (Outcome); `docs/plans/plan-199-batch-x-sec-t897-01.md` (Outcome); `docs/artifacts/security-review-t908-batch-x-v1.md` (per-id table, new findings, the orchestrator's addendum). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T910 (plan-200; the user's answer of 2026-11-21, verbatim: "v34 go"). **Date**: 2026-11-21.
- **Tree read**: branch `agent/tech-lead/T910` (develop `229459a2` plus the plan-200 commit `34de4a15`). The range for "lines added since v33" is `1c835d3a..229459a2`: 43 files, 330 lines added and 69 removed (read here: `git diff --shortstat`). No diff under `tests/golden/` or `.vscode/`. The range holds nine edits in six knowledge-source files and their regenerated mirrors and root copies (plan-198), `tests/functional/test_ci_hash_pins.py` and one line of `docs/wiki/mcp-pin-bump-checklist.md` (plan-199), the ledger, two task briefs, two plans and one artifact. No change to `.gitlab-ci.yml`, `scripts/` or `docs/releases/` (read here: `git diff --name-only`). The plan-200 commit is outside the searched range.
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on this tree. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v33 only by grep (the token scan). No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **Y** drops TL-T753-05 (fixed), so Y goes from **3 to 2**. **X** drops SEC-T897-01 (fixed) and gains SEC-T909-01 and SEC-T909-02, so X goes from **3 to 4**. No other batch changes; no new letter, no letter ends.

## 1. Summary

v34 holds **776 ids**: the 774 of v33 and **2 new** (SEC-T909-01, SEC-T909-02, found by T909 in the review of MR !727). After v34: **623 fixed**, **46 accepted**, **14 obsolete**, **1 open**, **92 tracked-LOW**.

- **Open above LOW: nothing.** T909 found 0 CRITICAL, HIGH or MEDIUM. The one open id is K-20 (live checks, the user; no grade). TD-T808-01 and TD-T888-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v33, from tracked-LOW (2)**: TL-T753-05 (plan-198) and SEC-T897-01 (plan-199). Section 2.2.
- **New, tracked-LOW (2)**: SEC-T909-01, SEC-T909-02 (batch X; section 3).
- **Nothing is minted and closed in the same MR, and nothing is obsolete, in this range.**
- **SEC-T891-02 is not re-opened.** T909's status table lists a "SEC-T891-02 checklist wording" row. The orchestrator's addendum says the wording gap belongs to SEC-T897-01 and the register keeps SEC-T897-01 as the id. v31 already records SEC-T891-02 as fixed; I follow the addendum (section 4.3).
- **Unchanged in batch X**: SEC-T881-02 (the user chose "Keep the lock", decided) and SEC-T756-02 (the user's runner and variable side, A-21).
- **Next-release checklist**: 36 numbers carried, none new; no item changes (section 6.2). **Dates**: as v33 (section 6.3). **User actions**: v33's, less the root refresh for TL-T753-05, which is done (section 7).

Arithmetic, from the v33 totals:

| Status | v33 | leaves | enters | v34 |
|---|---:|---|---|---:|
| fixed | 621 | | + 2 tracked-LOW (TL-T753-05, SEC-T897-01) | **623** |
| accepted | 46 | | | **46** |
| obsolete | 14 | | | **14** |
| open | 1 | | | **1** |
| tracked-LOW | 92 | - 2 fixed | + 2 new (SEC-T909-01, -02) | **92** |
| **all** | **774** | | + 2 new ids | **776** |

Check: 623 + 46 + 14 + 1 + 92 = 776. Open or tracked: 92 + 1 = 93, the size of section 5.

### 1.1 Ids by v33 status and status now

| v33 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 92 | 2 | 0 | 0 | 0 | 90 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 621 | 621 | 0 | 0 | 0 | 0 |
| obsolete | 14 | 0 | 0 | 14 | 0 | 0 |
| **all v33 ids** | **774** | **623** | **46** | **14** | **1** | **90** |
| new in v34 | 2 | 0 | 0 | 0 | 0 | 2 |
| **all v34 ids** | **776** | **623** | **46** | **14** | **1** | **92** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t908-batch-x-v1.md` § New findings: SEC-T909-01, SEC-T909-02 | 2 | 0 | 0 | 2 |
| **All new** | **2** | **0** | **0** | **2** |

**Ids minted in the range beyond T909's list: none.** A search of the 330 lines added in `1c835d3a..229459a2` (no diff under `tests/golden/` or `.vscode/`) for every token of the form `<LETTERS>-<T-number>-<suffix>`, `<LETTERS>-<digits>` or `ADR-<digits>` (14 distinct tokens), set against the text of registers v1 to v33, finds as in no register exactly the two ids **SEC-T909-01, SEC-T909-02**. The other 12 tokens are in earlier registers: A-21, K-33, SEC-T756-02, SEC-T860-01, SEC-T867-01, SEC-T867-02, SEC-T881-02, SEC-T891-01, SEC-T891-02, SEC-T897-01, TL-T753-05, TL-T753-06.

**Duplicates: none.** SEC-T909-01 and -02 are residues and a maintainability point of the SEC-T897-01 fix. They restate no earlier id: SEC-T897-01 was "the apk pairing ignored non-`apk add` forms", closed for the listed forms; SEC-T909-01 is a different residue (forms the raw-text gate cannot see), and SEC-T909-02 is a false refusal the fix introduced.

**Ids named with no change of status** (in the range; carried and not re-traced beyond the grep): SEC-T756-02, SEC-T881-02 (named as unchanged), SEC-T860-01, SEC-T867-01, SEC-T867-02, SEC-T891-01, SEC-T891-02 (quoted inside the checklist line), TL-T753-06 (the manifest `files` list, named as not part of plan-198; it is not a v33 debt id of its own to change), K-33 and A-21 (text only).

## 2. v33 ids re-checked

Every v33 `open`, `tracked-LOW` and `accepted` id (139) is covered: the changed ones have a row here, the rest are unchanged and carried. The v33 `fixed` and `obsolete` ids stay as v33 records them.

### 2.1 v33 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v33 `tracked-LOW` (92)

Basis: plan-198 Outcome, plan-199 Outcome, T909's per-id table (reasoned; T909 had no shell) and the orchestrator's addendum. Plan-198: MR !726, develop `93d08065`, squash `a77549f6`, pinned `a58539b2`; pipelines 3098006469 and 3098006356; clean suite 2883 OK, skipped=25. Plan-199: MR !727, develop `229459a2`, squash `bb1036f7`, pinned `f3129407`; pipelines 3098092037 and 3098091973; clean suite 2883 OK, skipped=25 (plan-200 § Facts). **Verified here in `git diff 1c835d3a..229459a2`:** each fix below is in the diff; no published `docs/releases/v*.md`, immutable `-vN` artifact, `tests/golden/` file, job, digest or pin is touched.

**Changed to fixed (2).**

| Id | v33 batch | now | Evidence and remainder |
|---|---|---|---|
| TL-T753-05 | Y | **fixed** (T906, plan-198) | The orchestrator knowledge source now says `scripts/verify-release-docs.py` is the authoring repository's script and a target lacks it (new text "In the authoring repository, run ... (a target lacks the script)"; read here in the diff of `implementation/knowledge/agents/orchestrator.md`). Mirrors and root copies regenerated in the same MR: 43 files in the range include the `.claude`, `.cline`, `.github` and `.opencode` copies of the same five places (orchestrator, `prepare-release`, `release-workflow`, `verification-before-completion`) and `implementation/docs/wiki/README.md` and `home.md`. The Outcome records the root refresh as done with `install.sh --projections-only` (14 derived files) on the user's "Root refresh"; drift prints `.vscode/mcp.json` only, the user's own uncommitted edit (the plan's record; I did not read that file). The nine edits in six files is the plan's figure; I did not count each edit **(unverified)** |
| SEC-T897-01 | X | **fixed** (T908, plan-199; T909 PASS) | `apk_adds` in `tests/functional/test_ci_hash_pins.py` now looks at every `before_script` and `script` line that holds the token `apk`; a line is a normal add only if its words begin `apk add`, contain no later `apk` word and no shell metacharacter. Everything else is a stray and fails the pairing check (fail closed). 8 new mutation cases; the 13 original cases remain; no assertion weakened (T909, read; the orchestrator's addendum records 141 tests OK and 7 of 8 new cases failing on the old code, taken as given). The checklist line 12 gains "`--allow-young` cannot override the refusal of a future time" (read here), true against `scripts/audit-mcp-pins.py` (T909). **Remainder**: SEC-T909-01, SEC-T909-02 (tracked) |

**Unchanged (90 tracked-LOW)**: by batch: I 25, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 3, X 2 (SEC-T756-02, SEC-T881-02), Y 2 (SEC-T904-01, SEC-T904-03), F 2, U 5 (U's sixth id is K-20, open), AB 3: 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 2 + 2 + 2 + 5 + 3 = 90 = the 92 of v33 less 2 fixed. The sizes of unchanged batches are carried from v33 and not recounted id by id.

### 2.3 v33 `accepted` (46)

**Unchanged (46)**, with their v33 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. No source in the range names SEC-T660-01 or SEC-T665-01.

## 3. New ids

The grade is the reviewer's own (T909 § New findings). Owner: devops-engineer (my suggestion; no source names one). Both are tracked-LOW (new); nothing is minted and closed in the same MR.

| Id | Grade | Short description | Status | Remediation | Batch |
|---|---|---|---|---|---|
| SEC-T909-01 | SECURITY:LOW (A08) | `apk_adds` in `tests/functional/test_ci_hash_pins.py` (raw-text gate near line 1485; `before_script` and `script` only): the test `\bapk\b` runs before shlex parsing, so a quote- or escape-split token such as `ap""k add x` is skipped, an install through a variable naming the program is not seen, and `after_script` is not scanned (it was not scanned before). No current exposure: nothing uses these forms and both jobs are equal. An install through `pip` or `npm` is outside the apk-pairing claim | **tracked-LOW** (new) | Test the parsed words as well as the raw text (any word that equals or ends with `/apk`, or contains `apk`), or refuse any quote, backslash or `$` outside the standard add line; scan `after_script` or add a case that the jobs have none; add a mutation case for `ap""k add x` | X |
| SEC-T909-02 | SECURITY:LOW (A08, maintainability of the control) | Same function (character set near line 1493): `<` and `>` in a word refuse a legitimate constraint such as `'git>=2.54'` as a stray, with a message that names only "not exactly an `apk add` line". A maintainer may weaken the check to get a bump through | **tracked-LOW** (new) | Drop `<` and `>` from the character set (inert inside a quoted word), or say in the message and the docstring which characters are refused; add a case that `'git>=2.54'` in both jobs is accepted | X |

**Why batch X.** Both concern the CI-lock and pin checks in `tests/functional/test_ci_hash_pins.py`, the surface of SEC-T897-01, which was in X. Trigger: the next edit of `apk_adds`, and at the latest the next image bump that changes a package constraint (SEC-T909-02 bites first on a `>=` constraint). Line numbers are T909's and were not re-read.

## 4. Decisions since v33

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-21 | "Root refresh" | The approval for the root refresh of plan-198 (TL-T753-05), folded into MR !726 | plan-198 Outcome |
| 2026-11-21 | "X go" | Batch X, plan-199 (SEC-T897-01) | plan-199 § User decision; T908 brief |
| 2026-11-21 | "v34 go" | This register | plan-200 § User decision; T910 brief |

The orchestrator corrected this table: the tech-lead's draft said no user words were recorded for plan-199, but plan-199 § User decision and the T908 brief quote "X go"; its § Approval box is left unticked on purpose. I did not verify the words beyond those records. No risk was accepted by the user in the range.

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T909-01 and -02 tracked, not fixed in the MR | LOW, tracked under the user's LOW policy, to batch X | the orchestrator | T909 addendum |
| The checklist wording gap belongs to SEC-T897-01 | SEC-T891-02 stays fixed (v31); no id re-opened | the orchestrator; confirmed by me | T909 addendum; section 4.3 |
| TL-T753-05 fixed | Fix shipped with mirrors and the root refresh in one MR | the orchestrator | plan-198 Outcome |
| SEC-T909-01, -02 in batch X | The same surface as SEC-T897-01 | **mine** | section 5 |
| Merges, pipelines, ledger | As plan-200 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none.** Ids 776, fixed 623, accepted 46, obsolete 14, open 1, tracked-LOW 92, section 5 of 93, batch Y of 2 (SEC-T904-01, SEC-T904-03) and batch X of 4 (SEC-T756-02, SEC-T881-02, SEC-T909-01, SEC-T909-02) all agree. I derived each from v33 and the delta, not copied them (section 1, section 5).
- **T909's SEC-T891-02 row.** The status table lists "SEC-T891-02 checklist wording | Fixed". v31 already counts SEC-T891-02 as fixed (fix commit `887b6bcc`). Counting it again would double a v31 fix; I follow the orchestrator's addendum and attribute the wording to SEC-T897-01.
- **Ledger.** Plan-200 § Facts: "0 active, 705 completed". Not re-counted row by row; the T910 row is the one active row (the plan-200 commit adds it). See section 8.

## 5. Open items by LOW batch

Carried from v33 § 5; **X and Y change members**; all other rows unchanged.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---|---|---|
| I | Installer and generator | as v33 § 5 (includes TD-T888-01) | 25 | as v33 | as v33 |
| K | Security runtime | as v33 § 5 | 8 | as v33 | as v33 |
| L | CWSO helper scripts in emage.code | as v33 § 5 | 5 | as v33 | as v33 |
| M | CWSO repository | as v33 § 5 | 12 | as v33 | as v33 |
| N | Release tooling, second round | as v33 § 5 | 10 | as v33 | as v33 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v33 | as v33 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v33 | each release's preparation |
| R | Release-gate text, second round | as v33 § 5 | 7 | as v33 | as v33 |
| V | Release gate, fourth round | SEC-T900-02, SEC-T900-04, SEC-T900-06 | 3 | devops-engineer | the next change to `scripts/verify-release-docs.py`; at the latest before the tag's release document is gated (item 52) |
| **X** | CI images, the CA control, the CI locks and the pin-age check | **stay:** SEC-T756-02, SEC-T881-02. **new:** SEC-T909-01, SEC-T909-02. **Left (fixed):** SEC-T897-01 | 4 | devops-engineer (SEC-T909-01, -02: my suggestion; no source names one) | SEC-T756-02, SEC-T881-02: as v33; SEC-T909-01, -02: the next edit of `apk_adds`, and at the latest the next image bump that changes a package constraint |
| **Y** | Shipped text and records | **stay:** SEC-T904-01, SEC-T904-03. **Left (fixed):** TL-T753-05 | 2 | technical-writer (SEC-T904-01); devops-engineer (SEC-T904-03) (as v33) | SEC-T904-01: the next edit of the checklist page, and at the latest before the next image bump; SEC-T904-03: the next edit of the `.gitlab-ci.yml` header |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v33 | as v33 |
| U | Live checks and user | as v33 § 5 | 6 | as v33 | as v33 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v33 | as v33 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 4 + 2 + 2 + 6 + 3 = **93** = 92 tracked-LOW + 1 open (K-20). Against v33's 93: minus 1 in Y, minus 1 and plus 2 in X, so the total is the same (93 - 1 - 1 + 2 = 93; tracked-LOW stays 92 because two leave and two enter). **No open item carries a grade above LOW** on any scale; K-20, TD-T808-01 and TD-T888-01 have no reviewer's grade.

**Rows changed against v33: X and Y only.**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v33 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range.

### 6.2 Next release checklist (the release after v12.0.0)

v33 § 6.2 stands with its numbers and text (36 numbers; item 8 open; item 17 as amended in v29 and v31; item 52 with 16 points). **No change from this range.** Checked against the range:

- **plan-198 (T906).** The changed text is shipped text a target gets (orchestrator, `prepare-release`, `release-workflow`, `verification-before-completion`): it says `scripts/verify-release-docs.py` is run in the authoring repository and a target lacks it. It adds no step and removes none for the preparer of the next release, who works in the authoring repository; the gate itself is unchanged (no change to `scripts/` or `.gitlab-ci.yml`). It is not a new item.
- **plan-199 (T908).** A test file and one checklist sentence; no job, digest or pin changed (read here: `.gitlab-ci.yml` not in the range). The new sentence on `--allow-young` and a future time is in the pin-bump checklist, not in the release checklist. SEC-T909-01 and -02 are batch X debt, not a release condition.
- **Item 8** stays open: no tag pipeline ran in the range. Items 43, 44, 46 to 51 and points 1 to 16 of item 52: as v33.

Count: 36 numbers carried, 0 new; item 52 has 16 points.

### 6.3 Dates

Unchanged from v33 § 6.3 (the first two are close on 2026-11-21): the young-pin exceptions lapse about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0 7 days old about 2026-11-26 **(derived, unverified)**; **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19`; the range changes no `.gitlab-ci.yml` line and the test change is the pairing check, not that key), 2027-03-19 the last passing day.

## 7. User actions

v33 § 7 stands, less one item:

- **The CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists. Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).
- The SEC-T881-02 choice stays decided ("Keep the lock (Recommended)", 2026-11-21); nothing remains for the user on it. SEC-T756-02 stays with the user's runner and variable side (A-21).
- **Dropped: the root refresh for TL-T753-05.** It is done (plan-198 Outcome: the user's "Root refresh", 14 derived files, drift as the plan records). The only drift the plan reports is `.vscode/mcp.json`, the user's own uncommitted edit; I did not read it **(unverified)**.

## 8. Method, limits and validation

- **Carried statuses**: v33's rows and lists, plus the sources in Based on. Plan-200 § Facts and the two Outcomes are the only sources for the merges (!726, !727), the pinned shas (`a58539b2`, `f3129407`), the pipelines (3098006469, 3098006356, 3098092037, 3098091973) and the clean suites (2883 OK, skipped=25 each). The ledger figure "0 active, 705 completed" is the plan's. No network call was made.
- **The search for changes**: every id-like token was extracted from the lines added in `1c835d3a..229459a2` (no diff under `tests/golden/` or `.vscode/`) and set against the text of registers v1 to v33; the result is section 1.2 (14 distinct tokens, 2 in no register).
- **Counting**: 2 ids named new by T909; 2 counted (no duplicate), both tracked-LOW; 2 status changes into `fixed` from tracked-LOW. Section 5 expands to 93 ids; the sizes of unchanged batches are v33's, not recounted id by id.
- **Still unverified**:
  - Carried from v33 § 8.
  - T909's reading (no shell; the engineer's and the orchestrator's runs of the tests, the gates and the suite are taken as given).
  - The line numbers in SEC-T909-01 and -02; the number of edits in plan-198; the root-refresh result and drift (the plan's record).
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - The batch membership behind "as v33 § 5".
- **Not run here**: the suite, the pipelines, the mutations.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v33.md`; registers v1 to v33 (the token scan, by grep); `-v26.md`, `-v24.md`, `-v15.md` (precedents); `-v31.md`, `-v12.md`; `plan-200-tracked-debt-register-v34.md`; `plan-198-tl-t753-05-root-refresh.md` and `plan-199-batch-x-sec-t897-01.md` (Outcomes); `security-review-t908-batch-x-v1.md` (all sections, addendum);
  - `git diff --shortstat`, `--name-only` and `-U0` of `1c835d3a..229459a2`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
