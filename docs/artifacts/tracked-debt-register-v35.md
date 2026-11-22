# Artifact: tracked-debt-register-v35.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v34.md` (776 ids; v34 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there; its § 5 and § 6 are carried by reference where this register says "as v34"); `docs/artifacts/tracked-debt-register-v32.md` and `-v33.md` (the precedents for counting a fixed id whose residue is a new id: SEC-T888-01 with SEC-T900-02; TD-T789-01 with SEC-T904-01), `-v26.md` (a restatement counts once); `docs/plans/plan-202-tracked-debt-register-v35.md` (§ User decision, § Facts since v34, § The orchestrator's expected delta, § Task Decomposition) and `docs/tasks/task-T913.md` (the user's "v35go"); `docs/plans/plan-201-batch-x-sec-t909.md` (Outcome); `docs/artifacts/security-review-t911-batch-x-v1.md` (per-id table, new findings, the orchestrator's addendum). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T913 (plan-202; the user's answer of 2026-11-22, verbatim: "v35go"). **Date**: 2026-11-22.
- **Tree read**: branch `agent/tech-lead/T913` (develop `cae94104` plus the plan-202 commit `4f342c3b`). The range for "lines added since v34" is `229459a2..cae94104`: 8 files, 526 lines added and 7 removed (read here: `git diff --shortstat`). The files are `tests/functional/test_ci_hash_pins.py` (plan-201), the T912 review, the v34 register, plans 200 and 201, two task briefs and the completed-tasks ledger. No change to `.gitlab-ci.yml`, `scripts/`, `docs/releases/`, `docs/wiki/`, `tests/golden/` or `.vscode/` (read here: `git diff --name-only`). The plan-202 commit is outside the searched range.
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on this tree. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **X** drops SEC-T909-01 and SEC-T909-02 (fixed) and gains SEC-T912-01 to -04, so X goes from **4 to 6**. No other batch changes; no new letter, no letter ends.

## 1. Summary

v35 holds **780 ids**: the 776 of v34 and **4 new** (SEC-T912-01 to -04, found by T912 in the review of MR !729). After v35: **625 fixed**, **46 accepted**, **14 obsolete**, **1 open**, **94 tracked-LOW**.

- **Open above LOW: nothing.** T912 found 0 CRITICAL, HIGH or MEDIUM. The one open id is K-20 (live checks, the user; no grade). TD-T808-01 and TD-T888-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v34, from tracked-LOW (2)**: SEC-T909-02 and SEC-T909-01 (plan-201; section 2.2).
- **My ruling on SEC-T909-01: counted fixed, its residue carried once by SEC-T912-01 and SEC-T912-03.** T912 calls it "Partly fixed". It names four closed forms (`ap""k`, `a\pk`, a variable program at a command position, `after_script` scanned) and puts the forms that still escape under two new ids, each with its own grade and remediation. The register has no state "partly fixed with no remainder of its own": v32 (SEC-T888-01 with SEC-T900-02) and v33 (TD-T789-01 with SEC-T904-01) count the parent fixed in the form the review asked for and the residue once as new, and v26 says a restatement is counted once. Keeping SEC-T909-01 tracked as well would count the same remainder twice. SEC-T912-01 is not wholly its residue: a `script` given as a string or a nested list is a new shape of the same scan gap, and it was equally unscanned before. SEC-T912-02 and -04 are defects of the new code and are not residue at all. The user loses nothing either way: every remainder is tracked in batch X once. This agrees with the orchestrator's expected delta.
- **New, tracked-LOW (4)**: SEC-T912-01 to -04 (batch X; section 3).
- **Nothing is minted and closed in the same MR, and nothing is obsolete, in this range.**
- **Unchanged in batch X**: SEC-T881-02 (the user chose "Keep the lock") and SEC-T756-02 (the user's runner and variable side, A-21).
- **Design option, not decided**: an exact-line allowlist for the apk check (T912 names it under SEC-T912-03; the orchestrator's addendum leaves it to the user's word). It is recorded in section 7 as a question, not a decision.
- **Next-release checklist**: 36 numbers carried, none new; no item changes (section 6.2). **Dates**: as v34, two close (section 6.3). **User actions**: v34's, plus the allowlist question (section 7).

Arithmetic, from the v34 totals:

| Status | v34 | leaves | enters | v35 |
|---|---:|---|---|---:|
| fixed | 623 | | + 2 tracked-LOW (SEC-T909-01, -02) | **625** |
| accepted | 46 | | | **46** |
| obsolete | 14 | | | **14** |
| open | 1 | | | **1** |
| tracked-LOW | 92 | - 2 fixed | + 4 new (SEC-T912-01 to -04) | **94** |
| **all** | **776** | | + 4 new ids | **780** |

Check: 625 + 46 + 14 + 1 + 94 = 780. Open or tracked: 94 + 1 = 95, the size of section 5.

### 1.1 Ids by v34 status and status now

| v34 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 92 | 2 | 0 | 0 | 0 | 90 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 623 | 623 | 0 | 0 | 0 | 0 |
| obsolete | 14 | 0 | 0 | 14 | 0 | 0 |
| **all v34 ids** | **776** | **625** | **46** | **14** | **1** | **90** |
| new in v35 | 4 | 0 | 0 | 0 | 0 | 4 |
| **all v35 ids** | **780** | **625** | **46** | **14** | **1** | **94** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t911-batch-x-v1.md` § New findings: SEC-T912-01, -02, -03, -04 | 4 | 0 | 0 | 4 |
| **All new** | **4** | **0** | **0** | **4** |

**Ids minted in the range beyond T912's list: none.** A search of the 526 lines added in `229459a2..cae94104` for every token of the form `<LETTERS>-<T-number>-<suffix>`, `<LETTERS>-<digits>` or `ADR-<digits>` (48 distinct tokens; most come from the v34 register and plan-200 added in the range), set against the text of registers v1 to v34, finds as in no register exactly the four ids **SEC-T912-01, SEC-T912-02, SEC-T912-03, SEC-T912-04**. The other 44 tokens are in earlier registers.

**Duplicates: none.** SEC-T912-01 and -03 are partly the residue of SEC-T909-01 (counted once, as new; section 1). SEC-T912-02 and -04 are defects of the T911 code and restate no earlier id.

**Ids named with no change of status** (carried, not re-traced beyond the grep): every other token of the search, named in the v34 register, plan-200 or the review as text only; SEC-T881-02 and SEC-T756-02 are named as unchanged.

## 2. v34 ids re-checked

Every v34 `open`, `tracked-LOW` and `accepted` id (139) is covered: the changed ones have a row here, the rest are unchanged and carried. The v34 `fixed` and `obsolete` ids stay as v34 records them.

### 2.1 v34 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v34 `tracked-LOW` (92)

Basis: plan-201 Outcome, T912's per-id table (reasoned; T912 had no shell) and the orchestrator's addendum. Plan-201: MR !729, develop `cae94104`, pinned `ca48cd5d`; clean suite 2884 OK, skipped=25; pipelines green (plan-202 § Facts). **Verified here in `git diff 229459a2..cae94104`:** only `tests/functional/test_ci_hash_pins.py` changes among code and CI files; no job, digest, pin, published `docs/releases/v*.md`, `tests/golden/` file or immutable `-vN` artifact (other than adding v34) is touched.

**Changed to fixed (2).**

| Id | v34 batch | now | Evidence and remainder |
|---|---|---|---|
| SEC-T909-02 | X | **fixed** (T911, plan-201; T912 PASS) | `<` and `>` leave the per-word refused set and are tested only on the text outside quotes. `'git>=2.54'` is accepted; `apk add x > /tmp/y` and `< /tmp/y` are still refused. The message and the docstring name the refused characters (T912, reasoned, not run). One flaw in the quote stripping is SEC-T912-02 (a defect of the new code, tracked) |
| SEC-T909-01 | X | **fixed** (T911, plan-201; T912 PASS); counted fixed by my ruling (section 1) | The named forms are closed (T912, reasoned, not run): quote-split and escape-split program names (the gate also tests `apk` in the line with quotes and backslashes removed); a variable program at a command position (`$PM add x`, `PM=apk; $PM add x`, `true && ${PM} add x`); `after_script` scanned in both jobs. The engineer's runs (15 new subtests, 142 tests OK, each refusal case accepted on the old code) are taken as given. **Residue**: SEC-T912-01 (`script`, `before_script`, `after_script` as a string or nested list) and SEC-T912-03 (the denylist misses `env $PM`, `X=1 $PM`, `then $PM`, `eval $X`, a later line of a block, a program built without the text `apk`; `extends:` and `default:` unresolved) (tracked). The orchestrator's addendum records the same split. The engineer's claim that `apk  add` is newly refused was wrong (the regex is `apk\s+add`); no behaviour change |

**Unchanged (90 tracked-LOW)**: by batch: I 25, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 3, X 2 (SEC-T756-02, SEC-T881-02), Y 2 (SEC-T904-01, SEC-T904-03), F 2, U 5 (U's sixth id is K-20, open), AB 3: 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 2 + 2 + 2 + 5 + 3 = 90 = the 92 of v34 less 2 fixed. The sizes of unchanged batches are carried from v34 and not recounted id by id.

### 2.3 v34 `accepted` (46)

**Unchanged (46)**, with their v34 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. No source in the range changes any of them.

## 3. New ids

The grade is the reviewer's own (T912 § New findings). Owner: devops-engineer (my suggestion; no source names one). All four are tracked-LOW (new); nothing is minted and closed in the same MR. Line numbers are T912's and were not re-read.

| Id | Grade | Short description | Status | Remediation | Batch |
|---|---|---|---|---|---|
| SEC-T912-01 | SECURITY:LOW (A08) | `apk_adds` in `tests/functional/test_ci_hash_pins.py` (lines 1489-1492): `for line in job.get(field, [])` with `if not isinstance(line, str): continue`. GitLab accepts `script`, `before_script` and `after_script` as a string or a nested list. A string iterates by character (no match); a nested list is skipped; either way an install is not scanned, now including the newly scanned `after_script`. No current exposure: both jobs use flat lists | **tracked-LOW** (new) | Normalise first (a string becomes a one-item list; flatten lists; return any other shape as a stray instead of `continue`); add a case for `after_script: "apk add x"` and a nested-list case | X |
| SEC-T912-02 | SECURITY:LOW (A08) | Same function, `unquoted` (line 1502): single-quoted regions are blanked before double-quoted ones, so a stray apostrophe in a double-quoted word pairs with a later one and hides what lies between them; `apk add "a'b" > /tmp/y 'c'` loses its `>`, and since `<` and `>` are no longer tested per word, the redirect is accepted (reasoned, not run). Limited to a redirect or here-string on an otherwise literal add line; `;`, `&`, `\|`, `$`, backtick and parentheses are still tested on shlex words | **tracked-LOW** (new) | Blank quoted regions in one left-to-right pass (alternation, first opener wins), or use `shlex.shlex` with `punctuation_chars=True` and refuse any punctuation token; add the case | X |
| SEC-T912-03 | SECURITY:LOW (A08) | `var_cmd` (line 1494): the variable-program test is a command-position denylist (after `^`, `;`, `&`, `\|`, `(`). It misses `env $PM add x`, `X=1 $PM add x`, `then $PM add x`, `eval $X`, a later line of a multi-line block (no `re.M`) and any program built without the text `apk`. Only the job's own three fields are read, so an `after_script` inherited through `default:` or `extends:` is not scanned. No current exposure. Partly the residue of SEC-T909-01 | **tracked-LOW** (new) | Prefer a positive rule: in these two jobs refuse any `before_script` or `after_script` line that has `$`, a backtick or `eval` outside an exact-line allowlist (the standard add line pinned to its full text); if a denylist is kept, add `re.M` and the missing command words; resolve `extends:` and `default:` for `after_script` or add a case that the jobs inherit none. The allowlist is a larger change and is the user's to rule on (section 7) | X |
| SEC-T912-04 | SECURITY:LOW (A08, maintainability) | `apk_adds` (line 1495) and `var_cmd`: any line that contains the substring `apk` (a path such as `/tmp/apkcache`, a file `x.apk`), or starts with or chains into a variable (`- $SOME_TOOL --check`), is a stray, with a message that names the add-line check. A plausible innocent edit can trip it and push a maintainer to loosen the rule | **tracked-LOW** (new) | Keep the new message; add a docstring sentence and a short checklist note naming the two refusals, and a test that documents each (`mkdir /tmp/apkcache` refused, with its reason). Do not loosen the code | X |

**Why batch X.** All four concern the CI-lock and pin checks in `tests/functional/test_ci_hash_pins.py`, the surface of SEC-T909-01 and -02. Trigger: the next edit of `apk_adds`, and at the latest the next image bump that changes a package constraint or a job's `script` shape. If the user rules for the allowlist (section 7), SEC-T912-03 and most of -01 and -04 close in one round.

## 4. Decisions since v34

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-22 | "X go" | Batch X round 2, plan-201 (SEC-T909-01, -02) | plan-201 § User decision |
| 2026-11-22 | "v35go" | This register | plan-202 § User decision; T913 brief |

I did not verify the words beyond those records. No risk was accepted by the user in the range. The allowlist option is **not decided**.

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T912-01 to -04 tracked, not fixed in the MR | LOW, tracked under the user's LOW policy, to batch X | the orchestrator | T912 addendum; plan-201 Outcome |
| Allowlist for the apk check | Left to the user's word | the orchestrator | T912 addendum |
| SEC-T909-01 counted fixed, residue SEC-T912-01 and -03 | v32 and v33 precedents; one remainder counted once | the orchestrator proposed; **I confirm** | section 1 |
| SEC-T912-01 to -04 in batch X | The same surface as SEC-T909-01 and -02 | **mine** | section 5 |
| Merges, pipelines, ledger | As plan-202 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none.** Ids 780, fixed 625, accepted 46, obsolete 14, open 1, tracked-LOW 94, section 5 of 95 and batch X of 6 (SEC-T756-02, SEC-T881-02, SEC-T912-01 to -04) all agree. I derived each from v34 and the delta (section 1, section 5), and the ruling on SEC-T909-01 is mine, reached against the review text, not copied.
- **T912's status word.** T912 says "Partly fixed" for SEC-T909-01. I count it fixed (section 1); the register's states are fixed, accepted, obsolete, open and tracked-LOW.
- **Ledger.** Plan-202 § Facts: "0 active, 707 completed". Not re-counted row by row; the T913 row is the one active row once added.

## 5. Open items by LOW batch

Carried from v34 § 5; **X changes members**; all other rows unchanged.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v34 § 5 (includes TD-T888-01) | 25 | as v34 | as v34 |
| K | Security runtime | as v34 § 5 | 8 | as v34 | as v34 |
| L | CWSO helper scripts in emage.code | as v34 § 5 | 5 | as v34 | as v34 |
| M | CWSO repository | as v34 § 5 | 12 | as v34 | as v34 |
| N | Release tooling, second round | as v34 § 5 | 10 | as v34 | as v34 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v34 | as v34 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v34 | each release's preparation |
| R | Release-gate text, second round | as v34 § 5 | 7 | as v34 | as v34 |
| V | Release gate, fourth round | SEC-T900-02, SEC-T900-04, SEC-T900-06 | 3 | devops-engineer | the next change to `scripts/verify-release-docs.py`; at the latest before the tag's release document is gated (item 52) |
| **X** | CI images, the CA control, the CI locks and the pin-age check | **stay:** SEC-T756-02, SEC-T881-02. **new:** SEC-T912-01, SEC-T912-02, SEC-T912-03, SEC-T912-04. **Left (fixed):** SEC-T909-01, SEC-T909-02 | 6 | devops-engineer (SEC-T912-01 to -04: my suggestion; no source names one) | SEC-T756-02, SEC-T881-02: as v34; SEC-T912-01 to -04: the next edit of `apk_adds`, and at the latest the next image bump that changes a package constraint or a job's `script` shape |
| Y | Shipped text and records | SEC-T904-01, SEC-T904-03 | 2 | technical-writer (SEC-T904-01); devops-engineer (SEC-T904-03) (as v34) | as v34 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v34 | as v34 |
| U | Live checks and user | as v34 § 5 | 6 | as v34 | as v34 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v34 | as v34 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 6 + 2 + 2 + 6 + 3 = **95** = 94 tracked-LOW + 1 open (K-20). Against v34's 93: minus 2 and plus 4 in X, so +2 (93 - 2 + 4 = 95; tracked-LOW 92 - 2 + 4 = 94). **No open item carries a grade above LOW** on any scale; K-20, TD-T808-01 and TD-T888-01 have no reviewer's grade.

**Rows changed against v34: X only.**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v34 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range.

### 6.2 Next release checklist (the release after v12.0.0)

v34 § 6.2 stands with its numbers and text (36 numbers; item 8 open; item 17 as amended in v29 and v31; item 52 with 16 points). **No change from this range.** The range changes one test file (plan-201): no job, digest, pin, checklist page or release-gate script. SEC-T912-01 to -04 are batch X debt, not a release condition. Item 8 stays open: no tag pipeline ran in the range. Count: 36 numbers carried, 0 new; item 52 has 16 points.

### 6.3 Dates

Unchanged from v34 § 6.3; the first three are close (today is 2026-11-22): the young-pin exceptions lapse about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0 7 days old about **2026-11-26** **(derived, unverified)**; **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19`; the range changes no `.gitlab-ci.yml` line), 2027-03-19 the last passing day.

## 7. User actions

v34 § 7 stands unchanged:

- **The CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists. Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).
- The SEC-T881-02 choice stays decided ("Keep the lock (Recommended)", 2026-11-21). SEC-T756-02 stays with the user's runner and variable side (A-21).
- The only drift the plan-198 Outcome reported was the user's own uncommitted edit of `.vscode/mcp.json`; I did not read it **(unverified)**.

**New question the user may rule on (not decided):** replace the denylist in `apk_adds` with an exact-line allowlist (the standard add line pinned to its full text; any other line in `before_script`, `script` and `after_script` of the two jobs that holds `apk`, `$`, a backtick or `eval` is refused). Each review round so far closed the forms the last one named and the next review named more (SEC-T909-01, then SEC-T912-01 and -03). The allowlist would end that cycle and close SEC-T912-03, and most of -01 and -04, in one change; the cost is that a legitimate edit of those lines then needs a test edit. A one-word answer ("allowlist" or "keep tracking") is enough.

## 8. Method, limits and validation

- **Carried statuses**: v34's rows and lists, plus the sources in Based on. Plan-202 § Facts and the plan-201 Outcome are the only sources for the merges (!728, !729), the pinned shas, the clean suite (2884 OK, skipped=25) and the pipelines. The ledger figure "0 active, 707 completed" is the plan's. No network call was made.
- **The search for changes**: every id-like token was extracted from the lines added in `229459a2..cae94104` and set against the text of registers v1 to v34; the result is section 1.2 (48 distinct tokens, 4 in no register).
- **Counting**: 4 ids named new by T912; 4 counted (no duplicate), all tracked-LOW; 2 status changes into `fixed` from tracked-LOW. Section 5 expands to 95 ids; the sizes of unchanged batches are v34's, not recounted id by id.
- **Still unverified**:
  - Carried from v34 § 8.
  - T912's reading (no shell; the engineer's and the orchestrator's test runs, the clean suite and the pipelines are taken as given).
  - The line numbers in SEC-T912-01 to -04 (T912's).
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - The batch membership behind "as v34 § 5".
- **Not run here**: the suite, the pipelines, the mutations.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v34.md`; registers v1 to v34 (the token scan, by grep); `-v26.md`, `-v32.md`, `-v33.md` (precedents); `plan-202-tracked-debt-register-v35.md`; `plan-201-batch-x-sec-t909.md` (Outcome); `security-review-t911-batch-x-v1.md` (all sections, addendum);
  - `git diff --shortstat`, `--name-only` and `-U0` of `229459a2..cae94104`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
