# Artifact: tracked-debt-register-v30.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v29.md` (761 ids; v29 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/artifacts/tracked-debt-register-v28.md` (§ 2.2, § 3 and § 5: the text and batch of SEC-T888-01 to -04); `docs/artifacts/tracked-debt-register-v26.md` and `docs/artifacts/tracked-debt-register-v24.md` / `-v15.md` (the precedents for a duplicate id and for an id minted and fixed before merge); `docs/plans/plan-191-tracked-debt-register-v30.md` (§ User decision, § Facts since v29, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T895.md` (the user's "v30 go"); `docs/plans/plan-190-batch-v-short-round.md` (Outcome); `docs/artifacts/security-review-t894-batch-v-v1.md` (per-id table, new findings, the orchestrator's addendum); `docs/checkpoints/checkpoint-044-release-v12.0.0.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T895 (plan-191; the user's answer of 2026-11-21, verbatim: "v30 go"). **Date**: 2026-11-21.
- **Tree read**: branch `agent/tech-lead/T895` (develop `a0c375e6` plus the plan-191 commit `24a47408`). The range for "lines added since v29" is `5fbb71de..a0c375e6` (plan-191 § Facts): 7 files, 366 lines added and 10 removed (read here: `git diff --shortstat`); code in two files, `scripts/verify-release-docs.py` and `tests/functional/test_verify_release_docs.py` (74 added, 10 removed). Neither `tests/golden/` nor `.vscode/` has a diff in the range. The plan-191 commit itself is outside the searched range.
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on this tree. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v29 only by grep (v28 § 2.2, § 3, § 5 and v29 in full by line read). The code was not read beyond what T894 reports. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **V** drops SEC-T888-04 (fixed), so 4 becomes 3; SEC-T888-02 stays in V for part (b). **The three SEC-T894 ids enter as `fixed` and sit in no batch.** No other batch changes; no new letter, no letter ends.

## 1. Summary

v30 holds **764 ids**: the 761 of v29 and **3 new** (SEC-T894-01, -02, -03, each minted and fixed in MR !718). After v30: **604 fixed**, **46 accepted**, **12 obsolete**, **1 open**, **101 tracked-LOW**.

- **Open above LOW: nothing.** T894: "0 CRITICAL, 0 HIGH, 0 MEDIUM". The one open id is K-20 (live checks, the user; no grade). TD-T789-01, TD-T808-01 and TD-T888-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v29, from tracked-LOW (1)**: SEC-T888-04 (batch V; section 2.2).
- **New, minted and fixed in the same MR (3)**: SEC-T894-01 (a regression from the first T893 commit, found by T894, confirmed by the orchestrator's run), SEC-T894-02, SEC-T894-03 (section 3). They add to `fixed` and never sit in a batch.
- **SEC-T888-02 is split and stays tracked-LOW, one id**: part (a) is fixed; part (b) is open and untouched (section 2.2). It is counted once, as tracked-LOW.
- **SEC-T888-01 and SEC-T888-03 stay tracked-LOW**, untouched (section 2.2).
- **SEC-T881-02 stays tracked-LOW.** The user has **not** answered the choice (section 7). T891's recommendation is the standing position, not a decision.
- **Next-release checklist**: 36 numbers carried; **item 52 gains point 14** (section 6.2). **Dates**: as v29 (section 6.3). **User actions**: v29's, including the open SEC-T881-02 choice (section 7).

Arithmetic, from the v29 totals:

| Status | v29 | leaves | enters | v30 |
|---|---:|---|---|---:|
| fixed | 600 | | + 1 tracked-LOW (SEC-T888-04) + 3 new (SEC-T894-01, -02, -03) | **604** |
| accepted | 46 | | | **46** |
| obsolete | 12 | | | **12** |
| open | 1 | | | **1** |
| tracked-LOW | 102 | - 1 fixed (SEC-T888-04) | | **101** |
| **all** | **761** | | + 3 new ids | **764** |

Check: 604 + 46 + 12 + 1 + 101 = 764. Open or tracked: 101 + 1 = 102, the size of section 5.

### 1.1 Ids by v29 status and status now

| v29 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 102 | 1 | 0 | 0 | 0 | 101 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 600 | 600 | 0 | 0 | 0 | 0 |
| obsolete | 12 | 0 | 0 | 12 | 0 | 0 |
| **all v29 ids** | **761** | **601** | **46** | **12** | **1** | **101** |
| new in v30 | 3 | 3 | 0 | 0 | 0 | 0 |
| **all v30 ids** | **764** | **604** | **46** | **12** | **1** | **101** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t894-batch-v-v1.md` § New findings: SEC-T894-01, -02, -03 (fixed in `e570a268`, per its addendum) | 3 | 3 | 0 | 0 |
| **All new** | **3** | **3** | **0** | **0** |

**Ids minted in the range beyond T894's list: none.** A search of the 366 added lines in `5fbb71de..a0c375e6` (no diff under `tests/golden/` or `.vscode/`) for every token of the form `<LETTERS>-<T-number>-<suffix>` or `<LETTERS>-<digits>` (18 distinct tokens), set against the text of registers v1 to v29, finds as in no register exactly SEC-T894-01, -02, -03. The other id tokens are in earlier registers: SEC-T888-01, -02, -03, -04, SEC-T748-05, -06, -08, -12, SEC-T751-06, -08. The non-id matches are file-name tokens (`plan-190`, `plan-190-batch`, `plan-186-batch`, `task-T894`, `engineer-T893`). Most of the added lines are the review document, plan-190 and the two task briefs; the code changes are in section 2.2.

**Duplicates: none.** SEC-T894-01 to -03 restate no earlier id: SEC-T894-01 is a regression of the reorder that fixed SEC-T888-02(a), and names the SEC-T748-05 hazard as the effect, not as a duplicate; -02 is an unbacked word in the help text that SEC-T888-04 rewrote; -03 is a no-op test loop in T893's new test. Each is counted as an id of its own, as v24 (SEC-T860-03, SEC-T862-01) and v15 (SEC-T796-01) count an id minted and fixed before merge. The v26 duplicate precedent (counted once) does not apply.

**Ids named with no change of status** (in the range; carried and not re-traced beyond the grep): SEC-T748-05, -06, -08, -12 and SEC-T751-06, -08 (all fixed in earlier registers, named in the review text only). **Ids named with a change** are those of sections 2 and 3. This register mints no id.

## 2. v29 ids re-checked

Every v29 `open`, `tracked-LOW` and `accepted` id (149) is covered: the changed ones have a row here, the rest are unchanged and carried. The v29 `fixed` and `obsolete` ids stay as v29 records them.

### 2.1 v29 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v29 `tracked-LOW` (102)

**Changed to fixed (1).** Status and basis are T894's per-id table; fix commit `3c97074a` (plan-190 Outcome; MR !718, develop `a0c375e6`, pinned `ac5967f4`; pipelines 3095706890 and 3095706810; clean suite 2874 OK, skipped=25, per plan-191 § Facts).

| Id | v29 batch | now | Evidence and remainder |
|---|---|---|---|
| SEC-T888-04 | V | **fixed** (T893, `3c97074a`) | The help text of `scripts/verify-release-docs.py` states the widened narrow rule and the second parse with the GFM table rule; T894 checked each sentence against the code (answer 3) and found them backed. The word "at most doubles the parse time" was unbacked: SEC-T894-02, minted and fixed (section 3). The old one-span wording is gone from the help text and the module docstring, and tests assert its absence |

**Partly fixed, stays tracked-LOW (1, one id).**

| Id | batch | status | What the range says |
|---|---|---|---|
| SEC-T888-02 | V | **split: (a) fixed, (b) open; counted once as tracked-LOW** | **(a) fixed** (T893, `4d71af64`, with `e570a268`): `folded` casefolds, applies NFKD, drops Cf, Mn and Me (INVISIBLE_LETTERS become a blank), applies NFKC, casefolds again, then collapses white space; `## RELEASE VERDİCT` folds to the name's length and is caught (the orchestrator ran it, T894). The first commit (`4d71af64`, reviewed at `3c97074a`) had a regression, SEC-T894-01 (section 3), found by T894, confirmed by the orchestrator's run and fixed before merge; no second security review was held (the condition named the orchestrator's run). **(b) open, untouched**: non-letter look-alikes such as `∨` U+2228, `∣` U+2223 and ASCII `\|` are still no wildcards in `reads_as`; the orchestrator's run confirms `∨ERDICT` is not caught. Out of scope by plan-190. The v28 remediation for (b): let any non-ASCII character that is not a space or mark be a wildcard; tests for `∨`. **Cost of the fix on record (the orchestrator's own sweep, T894 addendum)**: of every code point from U+0080 to U+2FA1F put in each letter position of both names (5,016,128 headings), **11,884** shapes the old gate (`88bf0fcc`) caught are not caught now, all characters whose accent-stripped base is a **different** ASCII letter than the name's letter at that position (`À` in place of the `R`), and **497** the old gate missed are caught now. That a different-letter base is no look-alike is a visual judgement, **(unverified)** for every one of the 11,884; the reviewer reasoned and did not run (T894), the orchestrator ran the sweep, I did not re-run it |

**Unchanged, tracked-LOW (2 named here, 99 in all other batches; v28 and earlier stay the record of their text).**

| Id | batch | status | What the range says |
|---|---|---|---|
| SEC-T888-01 | V | **tracked-LOW, unchanged** | `table_code_html_line`, `parsed_refusal` and `table_html_refusal` have the same logic; only the help text and docstring wording changed (T894) |
| SEC-T888-03 | V | **tracked-LOW, unchanged** | `LINK_RE` and `check_links` are not in the diff (T894) |

**Unchanged (101 tracked-LOW in all, v28 and earlier stay the record of their text)**: by batch: I 25, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, V 3 (SEC-T888-01, SEC-T888-02 (b), SEC-T888-03), X 4 (SEC-T756-02, SEC-T881-02, SEC-T891-01, SEC-T891-02), Y 11, F 2, U 5 (U's sixth id is K-20, open), AB 3. 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 4 + 11 + 2 + 5 + 3 = 101 = the 102 of v29 less SEC-T888-04. (The sizes of unchanged batches are carried from v29 and not recounted id by id; V was traced through v28 § 5, T894's per-id table and plan-190 Outcome. SEC-T881-02 is as v29 § 2.2: the six-pin count, T891's recommendation, no answer from the user.)

### 2.3 v29 `accepted` (46)

**Unchanged (46)**, with their v29 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. No source in the range names SEC-T660-01 or SEC-T665-01.

## 3. New ids

Grades are the reviewer's own (T894 § New findings). Owner devops-engineer (the surface of batch V). All three were fixed in `e570a268` (T893, in MR !718) before merge; the orchestrator confirmed SEC-T894-01 by running it before the fix and after it (T894 addendum, items 1, 2 and 4). T894 held no second review of `e570a268`; the fixes for -02 and -03 are T893's report and the orchestrator's read of the removed test lines (plan-190 Outcome), not a reviewer's check **(unverified by a reviewer)**.

| Id | Grade | Short description | Status | Remediation | Batch |
|---|---|---|---|---|---|
| SEC-T894-01 | SECURITY:LOW (A04) | **A regression from T893's first commit** (`4d71af64`, reviewed at `3c97074a`), found by T894's review (reasoned, not run) and confirmed by the orchestrator's run. `folded` casefolded before NFKD, so characters that have no case folding of their own but decompose to an upper-case ASCII letter (mathematical alphanumerics such as `𝐕`, letterlike capitals such as `ℛ`, superscript capitals such as `ᴿ`) kept the capital: `folded('\U0001D415ERDICT')` gave `'Verdict'`, and `## RELEASE 𝐕ERDICT` and `## ℛELEASE VERDICT` gave no problem. `88bf0fcc` caught the first. The effect is the SEC-T748-05 hazard (the real section ends early), committer-only | **fixed** (T893, `e570a268`) | A second casefold after the final NFKC (the first kept, so `İ` still loses its dot); tests for `𝐕`, `ℛ` and `ᴿ` on `reads_as` and `folded`, with a mutation (T893's report). After: `folded` gives `'verdict'` and `'release'`, `reads_as('RELEASE \U0001D415ERDICT', 'RELEASE VERDICT')` is `True` (the orchestrator's run) | none (fixed) |
| SEC-T894-02 | SECURITY:LOW (A05) | The help text said a second parse "at most doubles the parse time", a bound the code does not back (the second parse uses another rule set and its cost is not measured) | **fixed** (T893, `e570a268`) | Phrase reworded, its test changed with it (plan-190 Outcome; not re-read by a reviewer) | none (fixed) |
| SEC-T894-03 | SECURITY:LOW (A04, test quality) | The "expanding character plus look-alike" loop in `test_sec_t888_02a_...` was a no-op for `Gate Verdicts` (no capital `I` or `C` to replace) | **fixed** (T893, `e570a268`) | The loop is built per name (plan-190 Outcome; the orchestrator read the removed test lines) | none (fixed) |

**Why no batch.** Each is minted and fixed inside one merge request, so it never sat open (v15 § 3 and v24 § 3 do the same for SEC-T796-01, SEC-T860-03 and SEC-T862-01). If the orchestrator wants an id that stays tied to a surface, they belong with batch V (`scripts/verify-release-docs.py`); nothing is open for them.

## 4. Decisions since v29

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-20 | "V go"; plan approval "Approve (Recommended)" | Batch V short round (plan-190) | T894 header; plan-190 |
| 2026-11-21 | "v30 go" | This register | plan-191 § User decision; T895 brief |

I did not verify the words beyond those records **(unverified)**. **The user has not decided SEC-T881-02** (section 7).

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| Confirmation of SEC-T894-01 by the orchestrator's run, no second security review | The CONDITIONAL_PASS named the run as the confirmation | T894; the orchestrator | T894 addendum; plan-190 Outcome |
| The "different ASCII letter is no look-alike" reading of the 11,884 | A visual judgement, unverified | the orchestrator | T894 addendum |
| SEC-T888-02 split | One id, tracked-LOW, part (a) fixed and part (b) open | **mine**, following the plan's expected delta | section 2.2 |
| SEC-T894-01, -02, -03 counted as 3 new, fixed | Not duplicates; v15 and v24 precedent for ids minted and fixed before merge | **mine** | section 1.2, section 3 |
| No batch for SEC-T894-01 to -03 | They are fixed | **mine** | section 3, section 5 |
| Item 52 gains point 14 | See section 6.2 | **mine** | section 6.2 |
| Merges, pipelines, ledger | As plan-191 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none.** Ids (764), fixed (600 + 1 + 3 = 604), accepted 46, obsolete 12, open 1, tracked-LOW (102 - 1 = 101), section 5 of 102 and batch V of 3 all agree, and the check 604 + 46 + 12 + 1 + 101 = 764 holds. The changed set (SEC-T888-04 fixed; SEC-T888-02 part (a) fixed, part (b) open; SEC-T888-01 and -03 unchanged; SEC-T894-01 to -03 new and fixed) agrees. No SEC-T894 id restates an existing id, so the v26 once-only precedent is not used.
- **Ledger.** Plan-191 § Facts: "0 active, 691 completed". Read here: `completed-tasks.md` holds 691 task rows and `active-tasks.md` one (T895, added by the plan-191 commit). No difference.
- **Budgets.** T893 about 159k tokens against 70k, T894 about 79k against 40k (plan-190 § Outcome); noted, not a debt id.

## 5. Open items by LOW batch

Carried from v29 § 5; V changes members and size (4 to 3); all other rows unchanged.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| I | Installer and generator | as v29 § 5 (includes TD-T888-01) | 25 | as v29 | as v29 |
| K | Security runtime | as v29 § 5 | 8 | as v29 | as v29 |
| L | CWSO helper scripts in emage.code | as v29 § 5 | 5 | as v29 | as v29 |
| M | CWSO repository | as v29 § 5 | 12 | as v29 | as v29 |
| N | Release tooling, second round | as v29 § 5 | 10 | as v29 | as v29 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v29 | as v29 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v29 | each release's preparation |
| R | Release-gate text, second round | as v29 § 5 | 7 | as v29 | as v29 |
| **V** | Release gate, third round | SEC-T888-01, SEC-T888-02 (part (b) only), SEC-T888-03. **Left (fixed):** SEC-T888-04, and SEC-T888-02 part (a) | 3 | devops-engineer | the next change to `scripts/verify-release-docs.py`; SEC-T888-02 (b) with SEC-T888-01 (T888 recommendation 3) |
| X | CI images, the CA control, the CI locks and the pin-age check | SEC-T756-02, SEC-T881-02, SEC-T891-01, SEC-T891-02 | 4 | devops-engineer | as v29 |
| Y | Shipped text and records | as v29 § 5 | 11 | as v29 | as v29 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v29 | as v29 |
| U | Live checks and user | as v29 § 5 | 6 | as v29 | as v29 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v29 | as v29 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 4 + 11 + 2 + 6 + 3 = **102** = 101 tracked-LOW + 1 open (K-20). Against v29's 103: V - 1 (4 to 3: SEC-T888-04 leaves). **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01, TD-T808-01 and TD-T888-01 have no reviewer's grade.

**Rows changed against v29: V only.**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v29 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range; T894 accepted none.

### 6.2 Next release checklist (the release after v12.0.0)

v29 § 6.2 stands with its numbers and text (36 numbers; item 8 open; item 17 as amended in v29; item 52 with 13 points). Change:

- **Item 52 gains point 14.** The release-document gate now folds case, then NFKD, drops marks and format characters, then NFKC, then folds case again, before it compares a heading with the names of the guarded sections (SEC-T888-02(a), SEC-T894-01). The tag's own release document must therefore pass `scripts/verify-release-docs.py --tag` **before the tag is cut**, as already required; the gate over-flags 11,884 accent-stripped different-letter shapes that the older gate allowed (the orchestrator's sweep, **unverified** as to look-alikes), so a heading that is refused for a letter with a mark is a real refusal, not a bug. Part (b) of SEC-T888-02 (non-letter look-alikes such as `∨`) is **not** closed by it.
- **Item 8** stays open: no tag pipeline ran in the range. Items 17, 43, 44, 46 to 51: as v29; points 1 to 13 of item 52: as v29.

Count: 36 numbers carried, 0 new; item 52 has 14 points.

### 6.3 Dates

Unchanged from v29 § 6.3 (all still ahead on 2026-11-21 except the first two, which are at hand): the young-pin exceptions lapse about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0 7 days old about 2026-11-26 **(derived, unverified)**; **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19`, `.gitlab-ci.yml:25`; the range does not change `.gitlab-ci.yml`, T894 and plan-190), 2027-03-19 the last passing day.

## 7. User actions

v29 § 7 stands, unchanged:

- **The CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists. Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).

**Open, unanswered: the SEC-T881-02 choice.** The user has not answered; this register records no decision. Options:
1. **Keep the lock and header lines 3-6 as the record** (T891's recommendation, **the standing position**): no change now; the one-cut-off regeneration at the next full regeneration (item 17), with the 14-day review and the advisory audit; sooner only if an advisory names one of the six committed pins.
2. **Regenerate now** with the 14-day review: moves the six pins (certifi, pycparser, pydantic, pydantic-core, sse-starlette, starlette) and needs the review, provenance where available, an advisory audit with hashes and a diff read.

## 8. Method, limits and validation

- **Carried statuses**: v29's rows and lists, plus the sources in Based on. Plan-191 § Facts and plan-190 § Outcome are the only sources for the merges (!717, !718), the pinned sha `ac5967f4`, the pipelines (3095706890, 3095706810) and the clean suite (2874 OK, skipped=25). `docs/tasks/completed-tasks.md` holds 691 task rows and `active-tasks.md` one (T895) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 366 lines added in `5fbb71de..a0c375e6` (no diff under `tests/golden/` or `.vscode/`) and set against the text of registers v1 to v29; the result is section 1.2.
- **Counting**: 3 ids named new by T894, 3 counted (none a duplicate), all fixed; SEC-T888-02 counted once as tracked-LOW (split by part); 1 status change into `fixed` from tracked-LOW (SEC-T888-04). Section 5 expands to 102 ids; the sizes of unchanged batches are v29's, not recounted id by id; V was traced through v28 § 5, T894 and plan-190.
- **Still unverified**:
  - Carried from v29 § 8.
  - T893's code beyond the added lines and T894's reading of it (T894 had no shell; everything in its review is reasoned from the code and from Unicode data; the orchestrator ran SEC-T894-01 and the sweep only).
  - `e570a268` was not reviewed by a security reviewer (the condition named the orchestrator's run); the fixes for SEC-T894-02 and -03 rest on T893's report and the orchestrator's read.
  - The sweep numbers (5,016,128; 11,884; 497) are the orchestrator's own run, not re-run here, and the "different ASCII letter is no look-alike" reading is a visual judgement, unverified.
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - The batch membership behind "as v29 § 5".
- **Not run here**: the suite, the pipelines, the sweep, `verify-release-docs.py`.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v29.md`; `tracked-debt-register-v28.md` (§ 2.2, § 3, § 5); `tracked-debt-register-v26.md`, `-v24.md`, `-v15.md` (precedents); registers v1 to v29 (the token scan, by grep); `plan-191-tracked-debt-register-v30.md`; `plan-190-batch-v-short-round.md` (Outcome); `security-review-t894-batch-v-v1.md` (all sections, addendum); `checkpoint-044-release-v12.0.0.md` (by reference);
  - `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md` (row counts);
  - `git diff --shortstat`, `--stat` and `-U0` of `5fbb71de..a0c375e6`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
