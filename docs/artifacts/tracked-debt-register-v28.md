# Artifact: tracked-debt-register-v28.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v27.md` (754 ids; v27 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there); `docs/plans/plan-187-tracked-debt-register-v28.md` (§ User decision, § Facts since v27, § The orchestrator's expected delta, § Task Decomposition item 1) and `docs/tasks/task-T889.md` (the user's "v28 go"); `docs/plans/plan-186-batch-v-third-round.md` (Outcome); `docs/artifacts/security-review-t888-batch-v-v1.md` (per-id table, new findings, the release-job list, the orchestrator's addendum); `docs/checkpoints/checkpoint-044-release-v12.0.0.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T889 (plan-187; the user's answer of 2026-11-20, verbatim: "v28 go"). **Date**: 2026-11-20.
- **Tree read**: branch `agent/tech-lead/T889` at `56cbf8a6` (develop `94f6c09a` plus the plan-187 commit). The range for "lines added since v27" is `94e430b2..94f6c09a` (plan-187 § Facts): 9 files, 497 lines added and 25 removed (read here: `git diff --shortstat`). Neither `tests/golden/` nor `.vscode/` has a diff in the range. The plan-187 commit itself (plan, brief, ledger row) is outside the searched range and mints no id by its own plan text.
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on this tree. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v26 only by grep (v11, v12, v22 § 5 and v22 § 5 text for the flake precedent). Code files were read only as added lines, except `tests/functional/test_memory_indexing_pipeline.py:470-590` (line read, for TD-T888-01). No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **V** keeps size 4: its four v27 ids leave (fixed) and **SEC-T888-01 to -04** enter (my suggestion). **I** takes **TD-T888-01** (my suggestion), so 24 becomes 25. No new letter, no letter ends.

## 1. Summary

v28 holds **759 ids**: the 754 of v27 and **5 new**. After v28: **596 fixed**, **46 accepted**, **12 obsolete**, **1 open**, **104 tracked-LOW**.

- **Open above LOW: nothing.** No open or tracked id carries a `SECURITY:*` grade above LOW or QA's `Medium`. T888: "0 CRITICAL, 0 HIGH, 0 MEDIUM". The one open id is K-20 (live checks, the user; no grade). TD-T789-01, TD-T808-01 and the new TD-T888-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v27, from tracked-LOW (4)**: SEC-T885-01, -02, -03 and SEC-T751-08, all batch V (section 2.2).
- **New and tracked-LOW (5)**: SEC-T888-01, -02, -03, -04 (batch V), TD-T888-01 (batch I) (section 3; batches my suggestion).
- **Next-release checklist**: 36 numbers carried (35 + item 52), none new; **item 52 gains T888's six `release` job points** (section 6.2). **Dates**: as v27 (section 6.3). **User actions**: v27's (section 7).

Arithmetic, from the v27 totals:

| Status | v27 | leaves | enters | v28 |
|---|---:|---|---|---:|
| fixed | 592 | | + 4 tracked-LOW (SEC-T885-01, -02, -03, SEC-T751-08) | **596** |
| accepted | 46 | | | **46** |
| obsolete | 12 | | | **12** |
| open | 1 | | | **1** |
| tracked-LOW | 103 | - 4 fixed | + 5 new (SEC-T888-01 to -04, TD-T888-01) | **104** |
| **all** | **754** | | + 5 new ids | **759** |

Check: 596 + 46 + 12 + 1 + 104 = 759. Open or tracked: 104 + 1 = 105, the size of section 5.

### 1.1 Ids by v27 status and status now

| v27 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 103 | 4 | 0 | 0 | 0 | 99 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 592 | 592 | 0 | 0 | 0 | 0 |
| obsolete | 12 | 0 | 0 | 12 | 0 | 0 |
| **all v27 ids** | **754** | **596** | **46** | **12** | **1** | **99** |
| new in v28 | 5 | 0 | 0 | 0 | 0 | 5 |
| **all v28 ids** | **759** | **596** | **46** | **12** | **1** | **104** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t888-batch-v-v1.md` § New findings: SEC-T888-01, -02, -03, -04 | 4 | 0 | 0 | 4 |
| `plan-187` § Facts (the orchestrator's id, no reviewer's grade): TD-T888-01 | 1 | 0 | 0 | 1 |
| **All new** | **5** | **0** | **0** | **5** |

**Ids minted in the range beyond the plan's and T888's lists: none.** A search of the 497 added lines in `94e430b2..94f6c09a` (no diff under `tests/golden/` or `.vscode/`) for every token of the form `<LETTERS>-<T-number>-<suffix>` or `<LETTERS>-<digits>` (13 distinct id tokens), set against the text of registers v1 to v27, finds as in no register exactly SEC-T888-01, -02, -03, -04. The other id tokens are in earlier registers: SEC-T745-01, SEC-T748-05, SEC-T748-08, SEC-T751-06, SEC-T751-07, SEC-T751-08, SEC-T885-01, -02, -03. The non-id matches are file-name tokens (`api-v4`, `checkpoint-044`, `plan-184`, `plan-186`, `register-v27`, `release-v12`, `review-t885`, `review-t888`, `task-T888`, `v-v1`). **TD-T888-01 is in no added line of the range**: plan-187 § Facts, a file outside the range, names it, and no register v1 to v27 holds it (grep).

**Ids named with no change of status** (in the range; carried and not re-traced beyond the grep): SEC-T745-01 (fixed, v11 or earlier), SEC-T748-05, SEC-T748-08, SEC-T751-06, SEC-T751-07 (fixed, v27; named in T887's code comments and T888's text). **Ids named with a change** are those of sections 2 and 3. This register mints no id.

## 2. v27 ids re-checked

Every v27 `open`, `tracked-LOW` and `accepted` id (150) is covered: the changed ones have a row here, the rest are unchanged and carried. The v27 `fixed` and `obsolete` ids stay as v27 records them.

### 2.1 v27 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v27 `tracked-LOW` (103)

**Changed to fixed (4).** Status and basis are T888's per-id table (reviewer's words shortened); the fix commits are plan-186 § Outcome's (T887 `56f82e41` and `88bf0fcc`; MR !714, develop `94f6c09a`, pinned `42d9f573`).

| Id | v27 batch | now | Evidence and remainder |
|---|---|---|---|
| SEC-T885-03 | V | **fixed, runtime unproven** (T887, `56f82e41`) | `release` runs `python3 -I scripts/publish-release.py`; all three Python lines of the job run with `-I`; `RELEASE_COMMAND` is pinned with `-I`; `python_child_problems` covers the `release` job's before_script and script; three mutations refused (no `-I`, `-I` after the script, `python3.12`); `publish-release.py` is in the AST no-sibling-import test. `-I` does not protect against a committed change to `publish-release.py` itself (reviewed code at the tag, by design). **Runtime proof**: item 52 points 8 to 13 |
| SEC-T885-01 | V | **fixed** (T887, `88bf0fcc`) | `LINK_RE = \[[^\[\]]+\]\(([^()\n]+)\)` is linear on every shape; timing tests for `[a](`, `[a](\n` and `[a](` + 60 characters at the cap (plan-186 § Outcome: 17.35 s before, 0.003 s after); 0 differences over 2221 tracked `.md` files. **Coverage loss, a new id**: SEC-T888-03 |
| SEC-T885-02 | V | **fixed (letters)** (T887, `88bf0fcc`) | `folded` applies NFKC and drops Cf, Mn and Me; `reads_as` lets any non-ASCII letter stand for any letter (fails closed); tests for Cyrillic, Greek, combining acute, full-width letters, Roman numerals; `U+2800` and the Hangul fillers in `INVISIBLE_LETTERS`. **Two fail-opens, a new id**: SEC-T888-02 (`İ`, and non-letter look-alikes `∨` U+2228, `∣` U+2223, ASCII `\|`; both confirmed by the orchestrator's run, T888 addendum) |
| SEC-T751-08 | V | **fixed** (T887, `88bf0fcc`) | **What closed it**: T887's widening of the narrow rule ("a code span with `\|` and a code span with `<` in one paragraph that may be a table", kept) plus the table-rule parse (`markdown_tokens(text, True)`; `table_html_refusal` runs the nesting check and `live_html_line` on it; only for a text holding a `\|`, once per text, same size and line caps), and T888's correction of T885's bypass shape: the header-row shape is no table under the GFM spec either (header and delimiter rows must have the same number of cells); the real hazard, the same shape as a body row, is refused by both checks (test: line 5 under the table parse). All 38 `docs/releases/*.md` and `REQUIRED_FILES` keep their result on markdown-it-py 3.0.0 and 4.2.0 (plan-186 § Outcome, T887's run; not re-run here). **Residual class, a new id**: SEC-T888-01 (a `\|` in a link title or destination inside a table body, caught only by the table parse) |

**Unchanged (99 tracked-LOW; v27 and earlier stay the record of their text)**: by batch: I 24, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, X 6 (SEC-T756-02, TL-T761-11, SEC-T867-01 with TL-T876-04, SEC-T867-02 with TL-T876-04's date print, SEC-T881-02, SEC-T885-04), Y 11, F 2, U 5 (U's sixth id is K-20, open), AB 3. 24 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 6 + 11 + 2 + 5 + 3 = 99; with the 5 new, 104 tracked-LOW in section 5. (The sizes of unchanged batches are carried from v27 and not recounted id by id; V was traced through v27 § 5 and T888's per-id table.)

### 2.3 v27 `accepted` (46)

**Unchanged (46)**, with their v27 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. No source in the range names SEC-T660-01 or SEC-T665-01.

## 3. New ids

Grades are the reviewer's own (T888 § New findings), except TD-T888-01 (the orchestrator's id, called LOW; no reviewer's grade). Owner devops-engineer for the four SEC ids (the surface of batch V; the orchestrator assigns).

| Id | Grade | Short description | Status | Remediation | Batch |
|---|---|---|---|---|---|
| SEC-T888-01 | SECURITY:LOW (A03) | `scripts/verify-release-docs.py` `table_code_html_line`, `table_html_refusal`: a `\|` inside a link title or destination, `[x](y "\|<b>")` in a table body, can leave `<b>` live after GitLab splits the cell. Only the table parse catches it, so the check relies on markdown-it-py and GitLab agreeing on table recognition and cell splits (unverified; no confirmed differing shape). Committer-only, reviewed in an MR, GitLab's sanitiser applies | **tracked-LOW** | Widen the narrow rule to "a paragraph that may be a table holds a `\|` and a `<` anywhere outside a code span or comment, beyond what the table parse shows"; or record one confirmed GitLab rendering of `\\|` and of a link title holding `\|` in a table (T888 recommendation 3) | V |
| SEC-T888-02 | SECURITY:LOW (A04) | `folded`, `reads_as`: (a) `casefold` runs after the mark drop, so `İ` expands to `i` + U+0307 and `## RELEASE VERDİCT` is not a look-alike; (b) non-letter look-alikes (`∨`, `∣`, ASCII `\|`) are not wildcards. The real section ends early and the rest goes unchecked (the SEC-T748-05 hazard). (a) and (b) confirmed by the orchestrator's run | **tracked-LOW** | Casefold first, then NFKD, then drop Mn, Me and Cf, then NFKC; let any non-ASCII character that is not a space or mark be a wildcard; tests for `İ` and `∨`. (a) is a one-line reorder, the cheapest real gain (T888 recommendation 2) | V |
| SEC-T888-03 | SECURITY:LOW (A04, quality of the link check) | `LINK_RE`, `check_links` no longer report a broken link whose target holds parentheses (`[a](b_(c).md)`, a title with parentheses, a pointed destination) or comes after a line break (`[a](\nb.md)`). 0 such links today. This is the broken-link check, not a security control | **tracked-LOW** | Keep the linear regex; refuse, or report "cannot check", any `](` whose target the regex does not match, so a missed link fails closed; tests for `[a](b_(c).md)` and `[a](\nb.md)` | V |
| SEC-T888-04 | SECURITY:LOW (A05) | `verify-release-docs.py` help text (lines 276-286) still describes the old rule; it omits the table-parse refusal and that a text with a `\|` is parsed twice, and the time paragraph gives a single-parse measurement (the overclaim class of SEC-T748-08) | **tracked-LOW** | Update both paragraphs (widened rule, second parse, "at most doubles the time, not measured"); extend the help-text test to assert the new phrases. Take with SEC-T888-02(a) in the next batch (T888 recommendation 2) | V |
| TD-T888-01 | none (orchestrator id, called LOW) | `tests/functional/test_memory_indexing_pipeline.py:589` `test_an_at_sign_in_a_query_or_fragment_never_reaches_the_refusal` (T835, SEC-T835-01): `for secret in ("qsecret", "fsecret", "bob", "p?w"): assertNotIn(secret, stderr.lower())` is a substring check, and the random temporary directory name `tmpmbobp4tw` (in stderr) contained `bob`. At `42d9f573` four subtests failed on the final suite run; three re-runs of the module passed. Neither the test nor the code it checks is in MR !714 (plan-187 § Facts). Same kind as TD-T849-01 and TD-T746-01 | **tracked-LOW** | Check the secret as a whole token or as a field (strip the temporary-directory path from stderr first, or build the remote's user name from a string that cannot occur in a temp name, such as one holding a character the temp-name alphabet lacks); the secrets `qsecret` and `fsecret` are 7 letters and unlikely to recur, `bob` and `p?w` are the risk. A forced `bob`-named temp dir must fail the old assertion and pass the new one, as TD-T849-01's fix did | I |

**Why V for SEC-T888-01 to -04.** All four are findings of T888 on the code T887 changed in `scripts/verify-release-docs.py` (release gate, third round); same owner, same tests (`test_verify_release_docs`, `test_ci_hash_pins`), same trigger (the next change to that file). Batch V had no letter retired: its four old ids left (fixed) and these four take the batch's name.

**Why I for TD-T888-01 (the flake).** Precedent, read here: v11 § 5 filed the first flaky test (TD-T746-01) in its own batch W (a flaky test, "routed by the orchestrator"); W ended when TD-T746-01 was fixed (v12 Metadata: "Batch W ends", and the letter is not reused); v22 § 5 filed the second (TD-T849-01) in **I** "because the code under test is in I's scope", with the one-assertion fix needing no new letter (v22 "Why I for TD-T849-01"). This flake follows v22: the test exercises `implementation.runtime.memory.build.main` (read here, `test_memory_indexing_pipeline.py:477`), the memory index builder that the installer ships, and the memory-build refusals are the surface QA-T760 and T790 changed under I and Z (build.py's `--project-id`, platform root); the fix is one assertion; no new letter is needed. **Alternative**: K (Security runtime) if the owner reads it as a SEC-T835-01 regression test; I name I because the defect is in the test's assertion, not in a control. Owner and trigger as v22 gave TD-T849-01: devops-engineer or backend-developer, routed by the orchestrator; the next edit of the test file or its next CI failure. **Rate**: one failure in this range's final run; four subtests in the same run, the same cause; three re-runs passed.

## 4. Decisions since v27

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-20 | plan approval "Approve (Recommended)" (option: "All 4 items in one task (T887), then the security review (T888)") | Batch V third round (plan-186) | plan-186; T888 header ("V go"; "Approve (Recommended)") |
| 2026-11-20 | "v28 go" | This register | plan-187 § User decision; T889 brief |

I did not verify the words beyond those records **(unverified)**.

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| T888 corrects T885: the header-row bypass shape is no table; the real hazard is the body-row shape | Accepted; SEC-T751-08 fixed, residual class SEC-T888-01 | T888; the orchestrator | T888 per-id table; plan-186 § Outcome |
| SEC-T885-03 "runtime unproven" counted `fixed` | As T888's per-id status; the proof goes to item 52 points 8 to 13 | **mine** | section 2.2 |
| SEC-T885-02 counted `fixed (letters)` with SEC-T888-02 for the gaps; SEC-T885-01 `fixed` with SEC-T888-03 for the coverage loss | As T888's per-id table | **mine** | section 2.2 |
| TD-T888-01 as a tracked-LOW debt id without a reviewer's grade | Called LOW by the orchestrator | the orchestrator | plan-187 § Facts |
| Batches of the new ids | V (SEC-T888-01 to -04), I (TD-T888-01) | **mine** (suggestion) | section 3, section 5 |
| Merges, pipelines, ledger | As plan-187 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none in ids, statuses or totals.** 759 ids; fixed 592 + 4 = 596; accepted 46; obsolete 12; open 1 (K-20); tracked-LOW 103 - 4 + 5 = 104; section 5 sums to 105 (104 + K-20). Batch V 4 → 0 + 4 = 4. The placement of TD-T888-01 is mine (I, 24 → 25), as plan-187 asks.
- **Added lines.** Plan-187 gives no line count; the range holds 497 added lines in 9 files. Plan-186 § Outcome and T888 state "all four ids fixed"; T888's Summary reads "4 reviewed ids + 4 new" in its table; both agree with 4 fixed and 4 new SEC ids.
- **SEC-T885-03 "runtime unproven".** Counted `fixed` as T888 grades it; if the first `v*` tag pipeline does not show item 52 points 8 to 13, it reopens (as SEC-T751-01 and SEC-T768-04 reopen on points 3 to 6).
- **Budgets.** T887 used about 148k tokens against 120k and T888 about 106k against 60k (plan-186 § Outcome); noted, not a debt id.
- **Ledger.** Plan-187 § Facts: "0 active, 685 completed". Read here: `completed-tasks.md` holds 685 task rows and `active-tasks.md` one (T889, added by the plan-187 commit). No difference.

## 5. Open items by LOW batch

Carried from v27 § 5; V changes members, not size; I grows by one.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| **I** | Installer and generator | as v27 § 5; **new:** TD-T888-01 | 25 | as v27; for TD-T888-01 the orchestrator assigns (devops-engineer or backend-developer) | as v27; TD-T888-01 with the next edit of `tests/functional/test_memory_indexing_pipeline.py`, or at its next CI failure |
| K | Security runtime | as v27 § 5 | 8 | as v27 | as v27 |
| L | CWSO helper scripts in emage.code | as v27 § 5 | 5 | as v27 | as v27 |
| M | CWSO repository | as v27 § 5 | 12 | as v27 | as v27 |
| N | Release tooling, second round | as v27 § 5 | 10 | as v27 | as v27 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v27 | as v27 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v27 | each release's preparation |
| R | Release-gate text, second round | as v27 § 5 | 7 | as v27 | as v27 |
| **V** | Release gate, third round (after plan-186) | **new:** SEC-T888-01, SEC-T888-02, SEC-T888-03, SEC-T888-04. **Left (fixed):** SEC-T751-08, SEC-T885-01, SEC-T885-02, SEC-T885-03 | 4 | devops-engineer | the next change to `scripts/verify-release-docs.py`; SEC-T888-02(a) with SEC-T888-04 first (T888 recommendation 2), then SEC-T888-01 (recommendation 3) |
| X | CI images, the CA control, the CI locks and the pin-age check | as v27 § 5 (SEC-T756-02, TL-T761-11, SEC-T867-01, SEC-T867-02, SEC-T881-02, SEC-T885-04) | 6 | devops-engineer | as v27 |
| Y | Shipped text and records | as v27 § 5 | 11 | as v27 | as v27 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v27 | as v27 |
| U | Live checks and user | as v27 § 5 | 6 | as v27 | as v27 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v27 | as v27 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 4 + 6 + 11 + 2 + 6 + 3 = **105** = 104 tracked-LOW + 1 open (K-20). Against v27's 104: I + 1, V - 4 + 4. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01, TD-T808-01 and TD-T888-01 have no reviewer's grade.

**Rows changed against v27: I and V.**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v27 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range; T888 accepted none.

### 6.2 Next release checklist (the release after v12.0.0)

v27 § 6.2 stands with its numbers and text (36 numbers: 26 rules, item 8 open, items 43, 44, 46 to 49 carried, items 50, 51 and 52). Changes:

- **Item 8** stays open: no tag pipeline ran in the range.
- **Item 17** (rule): unchanged.
- **Item 52** keeps its seven points (v27 § 6.2; T885's list) and **gains six points for the `release` job's `-I` line** (T888 § What the next `v*` tag pipeline must show for the release job). They are points 8 to 13 and overlap points 2 to 6 where the job is the same; the proof for SEC-T885-03 (section 2.2):
    8. `release` ran on the dedicated runner (tag `release-gate`), after `release-docs-gate` and `main-develop-drift-gate` had both passed.
    9. The before_script `apk add` line and `--ca-release` both ran as `python3 -I` and passed before the publish line.
    10. The job log shows the line `python3 -I scripts/publish-release.py --tag ...` exactly as pinned, with no `ModuleNotFoundError` or import error (this proves the script needs nothing from `scripts/` on `sys.path`).
    11. The Release was created for the tag, and `CHANGELOG.md` was kept as an artifact.
    12. No line shows the job token (`[MASKED]` at most), and no line echoes an expanded variable.
    13. `release-docs-gate` passed with the table-rule parse in place: no `read as a GFM table` refusal on the tag's own document, and its duration is recorded for comparison with the 48 s single-parse measurement (plan-186 § Outcome; the job timeout is 10 minutes).

    If points 3 to 6 fail, SEC-T751-01 and SEC-T768-04 reopen; if point 7 finds a `GIT_STRATEGY` or `CI_PROJECT_DIR` variable, SEC-T751-05 reopens; **if points 8 to 12 fail, SEC-T885-03 reopens**; if point 13 shows the table parse refusing the tag's own document or a time near the timeout, record it against SEC-T751-08 (reopen only if a refusal is wrong). Point 1 also re-checks item 44's runner rule.

Count: 36 numbers carried, 0 new; item 52 has 13 points.

### 6.3 Dates

Unchanged from v27 § 6.3 (all still ahead on 2026-11-20): the young-pin exceptions lapse about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0 7 days old about 2026-11-26 **(derived, unverified)**; **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19`, `.gitlab-ci.yml:25`; the range changes `.gitlab-ci.yml` by 3 lines, the `release` job's `-I`, and not that line **(unverified beyond the stat)**), 2027-03-19 the last passing day.

## 7. User actions

v27 § 7 stands, unchanged:

- **The CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists (`CONTRIBUTING.md` rehearsal item). Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).

## 8. Method, limits and validation

- **Carried statuses**: v27's rows and lists, plus the sources in Based on. Plan-187 § Facts and plan-186 § Outcome are the only sources for the merges (!713, !714), the pinned sha `42d9f573`, the clean suite (2866 OK at `88bf0fcc`), the pipelines (3093927440, 3093927350) and the flake at `42d9f573`. `docs/tasks/completed-tasks.md` holds 685 task rows and `active-tasks.md` one (T889) (read here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 497 lines added in `94e430b2..94f6c09a` (no diff under `tests/golden/` or `.vscode/`) and set against the text of registers v1 to v27; the result is section 1.2.
- **Counting**: 5 ids new, 5 counted; 4 status changes into `fixed` from tracked-LOW. Section 5 expands to 105 ids; the sizes of unchanged batches are v27's, not recounted id by id; V was traced through T888's per-id table, I from the precedent in v22 § 5.
- **Still unverified**:
  - Carried from v27 § 8.
  - The T887 code beyond the added lines and T888's reading of it (T888 had no shell; the orchestrator ran SEC-T888-02 (a) and (b) only).
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - Whether SEC-T888-01 has a differing GitLab rendering (T888: no confirmed shape).
  - The flake's rate: one observed failure; the "about" rate of TD-T746-01 (0.5% per CI run) does not transfer.
  - The batch membership behind "as v27 § 5", and the statuses of the ids named with no change in section 1.2.
- **Not run here**: the suite, the pipelines, `verify-release-docs.py`, the generator.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v27.md`; registers v11, v12, v22 (§ 5 and the flake precedent) and v1 to v27 (the token scan, by grep); `plan-187-tracked-debt-register-v28.md`; `plan-186-batch-v-third-round.md` (Outcome); `security-review-t888-batch-v-v1.md` (all sections, addendum); `checkpoint-044-release-v12.0.0.md` (by reference);
  - by line read: `tests/functional/test_memory_indexing_pipeline.py:470-590`; `docs/tasks/completed-tasks.md`, `docs/tasks/active-tasks.md` (row counts);
  - `git diff --shortstat`, `--stat` and `-U0` of `94e430b2..94f6c09a`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
