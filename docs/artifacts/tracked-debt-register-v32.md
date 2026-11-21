# Artifact: tracked-debt-register-v32.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v31.md` (765 ids; v31 and earlier stay the record for the text of every id that did not change, and for every id that was `fixed` or `obsolete` there; its § 5 and § 6 are carried by reference where this register says "as v31"); `docs/artifacts/tracked-debt-register-v26.md`, `-v24.md` and `-v15.md` (the precedents for counting an id minted before merge); `docs/plans/plan-195-tracked-debt-register-v32.md` (§ User decision, § Facts since v31, § The orchestrator's expected delta, § Task Decomposition) and `docs/tasks/task-T901.md` (the user's "v32 go"); `docs/plans/plan-194-batch-v-fourth-round.md` (Outcome); `docs/artifacts/security-review-t900-batch-v-v1.md` (per-id table, new findings, the orchestrator's addendum). Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-011, ADR-015, ADR-016 (carried in section 6.1; no decision in the range).

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written in the repository is this artifact). **Task**: T901 (plan-195; the user's answer of 2026-11-21, verbatim: "v32 go"). **Date**: 2026-11-21.
- **Tree read**: branch `agent/tech-lead/T901` (develop `9493946b` plus the plan-195 commit `4369980a`). The range for "lines added since v31" is `b04ec271..9493946b`: 10 files, 830 lines added and 9 removed (read here: `git diff --shortstat`). Code in two files: `scripts/verify-release-docs.py` and `tests/functional/test_verify_release_docs.py`. The plan-195 commit is outside the searched range.
- **Review mode**: read-only. "Unchanged" means no source in the range names the id with a change of status, checked by searching the added lines for every id-like token (section 1.2). "Read here" means a grep, line read or `git` query on this tree. Anything not traced is **(unverified)**.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, any token file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/*.json`, the CWSO repository, any GitLab job log. Registers v1 to v31 only by grep (the token scan). The code was not read beyond what T900 and plan-194 report. No network call was made. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary, id prefixes and what counts as a debt id: as in v5 and v26.
- **Batch letters**: **V** drops SEC-T888-01, SEC-T888-02 and SEC-T888-03 (fixed) and gains SEC-T900-02, SEC-T900-04 and SEC-T900-06 (new), so V stays at **3** (3 - 3 + 3). Plan-194 Outcome says "Batch V is empty" and asks where the three belong; I keep them in V as a **fourth-round remainder** ("release gate, fourth round"), because they sit on the same surface (`scripts/verify-release-docs.py`). No other batch changes; no new letter, no letter ends.

## 1. Summary

v32 holds **771 ids**: the 765 of v31 and **6 new** (SEC-T900-01 to -06, found by T900 in the review of MR !722). After v32: **612 fixed**, **46 accepted**, **12 obsolete**, **1 open**, **100 tracked-LOW**.

- **Open above LOW: nothing.** T900 found 1 MEDIUM, SEC-T900-01, but it was **fixed before merge** (`2584bb45`, same MR) and never shipped; it is not open and not an acceptance under ADR-011. The one open id is K-20 (live checks, the user; no grade). TD-T789-01, TD-T808-01 and TD-T888-01 have no reviewer's grade (the orchestrator's ids, called LOW). SEC-T660-01 and SEC-T665-01 stay **accepted MEDIUM for v12.0.0 only** (accepted, not open). TD-T697-07 (MEDIUM) stays accepted, not release-shipped, ending 2027-01-29.
- **Fixed since v31, from tracked-LOW (3)**: SEC-T888-01, SEC-T888-02, SEC-T888-03 (batch V; section 2.2).
- **New, minted and fixed in the same MR (3)**: SEC-T900-01 (MEDIUM), SEC-T900-03, SEC-T900-05 (section 3.1). Precedent v26, v24, v15: counted once, as new and fixed.
- **New, tracked-LOW (3)**: SEC-T900-02, SEC-T900-04, SEC-T900-06 (batch V; section 3.2).
- **How SEC-T900-05 is counted**: as **one id, fixed**. It combined two points: the vacuous assertion (`.count("x")`) with the missing timing tests, both fixed in `2584bb45` (plan-195 § Facts), and the ASCII look-alikes `|`, `l`, `1`, `0`, which stay non-wildcards **by design** (SEC-T888-02's residual; the review's own text calls it a design limit). The look-alike point is not a second id and not tracked debt: no remediation is planned, and the limit is recorded here and in section 2.2 (SEC-T888-02). If the user wants the ASCII limit noted in the gate's help text, that is a wording edit with the next change to the script, not an item.
- **Next-release checklist**: 36 numbers carried, none new; item 52 gains one point (section 6.2). **Dates**: as v31 (section 6.3). **User actions**: v31's (section 7).

Arithmetic, from the v31 totals:

| Status | v31 | leaves | enters | v32 |
|---|---:|---|---|---:|
| fixed | 606 | | + 3 tracked-LOW (SEC-T888-01, -02, -03); + 3 new fixed (SEC-T900-01, -03, -05) | **612** |
| accepted | 46 | | | **46** |
| obsolete | 12 | | | **12** |
| open | 1 | | | **1** |
| tracked-LOW | 100 | - 3 fixed (SEC-T888-01, -02, -03) | + 3 new (SEC-T900-02, -04, -06) | **100** |
| **all** | **765** | | + 6 new ids | **771** |

Check: 612 + 46 + 12 + 1 + 100 = 771. Open or tracked: 100 + 1 = 101, the size of section 5.

### 1.1 Ids by v31 status and status now

| v31 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 1 | 0 | 0 | 0 | 1 | 0 |
| tracked-LOW | 100 | 3 | 0 | 0 | 0 | 97 |
| accepted | 46 | 0 | 46 | 0 | 0 | 0 |
| fixed | 606 | 606 | 0 | 0 | 0 | 0 |
| obsolete | 12 | 0 | 0 | 12 | 0 | 0 |
| **all v31 ids** | **765** | **609** | **46** | **12** | **1** | **97** |
| new in v32 | 6 | 3 | 0 | 0 | 0 | 3 |
| **all v32 ids** | **771** | **612** | **46** | **12** | **1** | **100** |

### 1.2 New ids by source and final status

| Source | new | fixed | obsolete | tracked-LOW |
|---|---:|---:|---:|---:|
| `security-review-t900-batch-v-v1.md` § New findings: SEC-T900-01 to -06 | 6 | 3 | 0 | 3 |
| **All new** | **6** | **3** | **0** | **3** |

**Ids minted in the range beyond T900's list: none.** A search of the 830 lines added in `b04ec271..9493946b` (no diff under `tests/golden/` or `.vscode/`) for every token of the form `<LETTERS>-<T-number>-<suffix>` or `<LETTERS>-<digits>` (45 distinct tokens; the register v31 itself is among the added files), set against the text of registers v1 to v31, finds as in no register exactly the six ids **SEC-T900-01, -02, -03, -04, -05, -06**. The other 39 id tokens are in earlier registers (among them SEC-T888-01 to -03, SEC-T891-01, -02, SEC-T897-01, ADR-011, ADR-015, ADR-016). Most of the added lines are register v31, plan-193, plan-194, the review document, the task briefs and the code changes of section 2.2.

**Duplicates: none.** SEC-T900-02 is the residue of SEC-T888-01 (the textual exclusion), but a different finding of its own: SEC-T888-01 is counted fixed in the form the review asked for, and SEC-T900-02 is the new residue (the v26 precedent: an id for a residue of a fixed id is counted once, as new). SEC-T900-06 is pre-existing in shape (the code-strip regexes) but was first named by T900 and has no earlier id.

**Ids named with no change of status** (in the range; carried and not re-traced beyond the grep): SEC-T891-01, -02, SEC-T897-01 and the rest of the 39.

## 2. v31 ids re-checked

Every v31 `open`, `tracked-LOW` and `accepted` id (147) is covered: the changed ones have a row here, the rest are unchanged and carried. The v31 `fixed` and `obsolete` ids stay as v31 records them.

### 2.1 v31 `open` (1)

**Unchanged (1)**: K-20 (batch U, A-7). No source in the range records a live client check.

### 2.2 v31 `tracked-LOW` (100)

**Changed to fixed (3).** Basis is T900's per-id table, plan-194 Outcome and the orchestrator's addendum; fix commits `f6ca9470` (first pass) and `2584bb45` (linear scans); MR !722, develop `9493946b`, pinned `f41bccea`; pipelines 3097540465 and 3097540427; clean suite 2883 OK, skipped=25 (plan-195 § Facts).

| Id | v31 batch | now | Evidence and remainder |
|---|---|---|---|
| SEC-T888-03 | V | **fixed** (T899, `f6ca9470`) | `unchecked_link_excerpts` in `scripts/verify-release-docs.py` is one linear `find("](")` scan: a `](` that no link pattern matches is reported as "cannot check" and refused. Linear `IMAGE_LINK_RE` and a read of inline code as `x` keep real files from being refused. Tests for `[a](b_(c).md)` and `[a](\nb.md)`. Sweep of 2,149 markdown files: 0 "cannot check", 0 new broken link. T900: fixed for every shape the finding named. **Residues**: SEC-T900-03 (error text; fixed in `2584bb45`), SEC-T900-06 (some links left unchecked; tracked) |
| SEC-T888-02 | V | **fixed** (T899, `f6ca9470`); part (b) | `is_wildcard_char` makes any non-ASCII character that is no space and no mark a wildcard in `reads_as`, so `∨` (U+2228), `∣` (U+2223) and U+2014 are caught. Sweep of 14,675 headings: 0 newly flagged. T900: fixed per its remediation. **ASCII look-alikes** (`|`, `l`, `1`, `0`) stay non-wildcards by design (a wildcard for ASCII would flag real words; the test pins `VERD1CT` as not caught). That limit is recorded in SEC-T900-05, which is counted fixed (section 1) |
| SEC-T888-01 | V | **fixed** (T899, `f6ca9470`; in the form the review asked for) | The table rule is widened: a paragraph that may be a table and holds a `|` and a `<` outside code spans and comments is refused (`pipe_and_tag_outside_code`). 29 paragraphs are newly flagged after the fix (31 before), none in a gated document or a `docs/releases/v*.md`. T900 called it "partly fixed": the textual exclusion (SEC-T900-02) and the ReDoS (SEC-T900-01, fixed). **Residue**: SEC-T900-02 (tracked) |

**Unchanged (97 tracked-LOW)**: by batch: I 25, K 8, L 5, M 12, N 10, P 1, Q 5, R 7, X 3 (SEC-T756-02, SEC-T881-02, SEC-T897-01), Y 11, F 2, U 5 (U's sixth id is K-20, open), AB 3. 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 11 + 2 + 5 + 3 = 97 = the 100 of v31 less SEC-T888-01, -02, -03. (Batch V's three v31 ids all leave; the sizes of unchanged batches are carried from v31 and not recounted id by id.)

### 2.3 v31 `accepted` (46)

**Unchanged (46)**, with their v31 qualifiers: SEC-T660-01 and SEC-T665-01 accepted MEDIUM for v12.0.0 only (shipped; review 2027-01-28); TD-T697-07 (MEDIUM; not release-shipped; ends 2027-01-29); the 40 LOW or INFO ids listed in v13 § 2.3; TL-T773-01, TL-T780-01, TL-T780-07. No source in the range names SEC-T660-01 or SEC-T665-01 other than as carried text.

## 3. New ids

The grade is the reviewer's own (T900 § New findings). Owner devops-engineer (the surface of batch V).

### 3.1 Minted and fixed in the same MR (3)

| Id | Grade | Short description | Status | Basis |
|---|---|---|---|---|
| SEC-T900-01 | SECURITY:MEDIUM (A04, availability) | `CODE_SPAN_RE` in `scripts/verify-release-docs.py`, run on every paragraph by `pipe_and_tag_outside_code`, was exponential (a redundant `\|\n` alternative under DOTALL), and `COMMENT_RE` was quadratic. A stray backtick followed by about 30 lines, or repeated `<!--`, could hang the release gate until the job timeout (fail-closed, but it blocks the release). | **fixed before merge**; never shipped; **not accepted** (no ADR-011 acceptance, no condition left) | Found by T900 (reasoned). Confirmed by the orchestrator's own timing on `f6ca9470`: 0.033 s (18 newlines), 0.128 s (20), 0.494 s (22), about four times per two newlines; `COMMENT_RE` 18.6 s on `<!--` x 32000. Fixed in `2584bb45`: linear `without_code_spans` and `without_comments`, timing tests at the cap. Shapes re-run at the 131072-character cap: 0.001 s to 0.037 s. A fuzz of 2,587 short paragraphs against markdown-it `code_inline` children: 0 differences. The old-pattern mutation hangs until killed (exit 124) instead of failing an assertion. No second security review: the condition named the orchestrator's confirmation. The MEDIUM was a condition of a CONDITIONAL_PASS, resolved before merge; it stands here only as the record |
| SEC-T900-03 | SECURITY:LOW (A04, quality) | The "cannot check" message blamed "a parenthesis or the next line" for shapes it did not fit (bracketed text, empty alt or text). | **fixed** (`2584bb45`) | Plan-195 § Facts, plan-194 Outcome via the addendum. Whether `LINK_RE` now reads empty text or bracketed text is not traced here **(unverified)**; the review's remediation was the message |
| SEC-T900-05 | SECURITY:LOW (A04, test quality) | The vacuous `.count("x")` assertion in the linear-time test; no timing test for the new regexes; ASCII look-alikes not wildcards (by design). | **fixed** (`2584bb45`); counted as one id | Section 1 (counting). Timing tests added at the cap |

### 3.2 New, tracked-LOW (3)

| Id | Grade | Short description | Status | Remediation | Batch |
|---|---|---|---|---|---|
| SEC-T900-02 | SECURITY:LOW (A03) | `pipe_and_tag_outside_code` removes code and comment text textually, not syntactically. A backslash-escaped backtick pair, or a `<!--` in one link title with a `-->` later in the paragraph, hides a `\|<b>` that CommonMark still sees as title text, so the rule passes. What remains is the table-rule parse, which the rule backs up. Committer-only, reviewed in the MR. This is the residue of SEC-T888-01 | **tracked-LOW** (new) | Compute the "outside code" text from the markdown-it token children (`code_inline`, `html_inline` comment tokens), or refuse a `\|` and `<` that stay after removing only `code_inline` content. Tests for the two shapes | V |
| SEC-T900-04 | SECURITY:LOW (A04, false refusal) | `table_pipe_tag_line` refuses any plain `<` in a table paragraph (`\| p95 \| < 100 ms \|`, `<=`, an autolink). Fail-closed; the message and help text say what to do; more than the hazard needs. No `docs/releases/v*.md` is hit (0 in gated documents; 29 paragraphs in non-gated docs) | **tracked-LOW** (new) | Count only a `<` followed by a letter, `/`, `!` or `?`, or document `&lt;` in the help text | V |
| SEC-T900-06 | SECURITY:LOW (A04) | `strip_code`, `INLINE_CODE_RE`, `FENCED_CODE_RE` ignore backslash escapes and mispair a triple-backtick run inside a double-backtick span, so some live links with a parenthesised target stay unchecked. Reference-style links (`[a][r]`) and autolinks are not checked at all. Pre-existing; the effect is an unchecked link target only, not a bypass | **tracked-LOW** (new) | Take links from the markdown-it tokens (`link_open`, `image` attributes) instead of regexes, or record it as the known limit of SEC-T888-03 | V |

**Why batch V.** Same file and same control (the release-document gate) as SEC-T888-01 to -03; the review ties them together. The batch is "release gate, fourth round". Trigger: the next change to `scripts/verify-release-docs.py`, and at the latest the tag's own release document (item 52).

## 4. Decisions since v31

### 4.1 The user's (words verbatim as recorded)

| Date | Words | What the source records | Source |
|---|---|---|---|
| 2026-11-21 | "V go" | Batch V fourth round (plan-194): SEC-T888-01, -02 (b), -03 in T899, then the review T900 | plan-194 § User decision |
| 2026-11-21 | "v32 go" | This register | plan-195 § User decision; T901 brief |

I did not verify the words beyond those records **(unverified)**. No risk was accepted by the user in the range.

### 4.2 The orchestrator's rulings, and mine

| Item | Decision | By | Source |
|---|---|---|---|
| SEC-T900-01 confirmed and fixed in the same MR, no second review | The condition named the orchestrator's confirmation | the orchestrator | T900 addendum; plan-194 Outcome |
| SEC-T900-01 not an acceptance | MEDIUM, fixed before merge, never shipped: no ADR-011 acceptance, no condition carried | **mine**, following the review and plan-195 | section 3.1 |
| SEC-T900-03 and -05 fixed in the same MR | `2584bb45` | the orchestrator | T900 addendum |
| SEC-T900-05 counted as one fixed id | The ASCII look-alike point is a design limit, not debt | **mine** | section 1 |
| SEC-T900-02, -04, -06 tracked-LOW in batch V | Plan-194 asks where they belong; the same surface as V | **mine** | section 5 |
| Merges, pipelines, ledger | As plan-195 § Facts | the orchestrator's record | section 8 |

### 4.3 Differences on the record

- **Against the orchestrator's expected delta: none.** Ids (771), fixed (606 + 3 + 3 = 612), accepted 46, obsolete 12, open 1, tracked-LOW (100 - 3 + 3 = 100), section 5 of 101 and batch V of 3 all agree, and the check 612 + 46 + 12 + 1 + 100 = 771 holds. The changed set (SEC-T888-01 to -03 fixed; SEC-T900-01, -03, -05 new and fixed; SEC-T900-02, -04, -06 new tracked-LOW) agrees.
- **Ledger.** Plan-195 § Facts: "0 active, 697 completed". Not re-counted row by row here beyond the plan's figure; the T901 row is the one active row. See section 8.
- **Plan-194 wording.** Its Outcome says "Batch V is empty"; with the three new ids it is not (3). Not a difference of count: batch V is the same size, with other members.

## 5. Open items by LOW batch

Carried from v31 § 5; V changes members (SEC-T888-01, -02, -03 leave, SEC-T900-02, -04, -06 join; size 3 to 3); all other rows unchanged.

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---|---|---|
| I | Installer and generator | as v31 § 5 (includes TD-T888-01) | 25 | as v31 | as v31 |
| K | Security runtime | as v31 § 5 | 8 | as v31 | as v31 |
| L | CWSO helper scripts in emage.code | as v31 § 5 | 5 | as v31 | as v31 |
| M | CWSO repository | as v31 § 5 | 12 | as v31 | as v31 |
| N | Release tooling, second round | as v31 § 5 | 10 | as v31 | as v31 |
| P | Upstream report to the Brave project | SEC-T702-08 (issue #377) | 1 | as v31 | as v31 |
| Q | Next release document and its gate rulings | TD-T723-01, SEC-T735-08, SEC-T735-09, TL-T780-09, TL-T821-01 | 5 | as v31 | each release's preparation |
| R | Release-gate text, second round | as v31 § 5 | 7 | as v31 | as v31 |
| **V** | Release gate, fourth round | **new:** SEC-T900-02, SEC-T900-04, SEC-T900-06. **Left (fixed):** SEC-T888-01, SEC-T888-02, SEC-T888-03 | 3 | devops-engineer | the next change to `scripts/verify-release-docs.py`; at the latest before the tag's release document is gated (item 52) |
| X | CI images, the CA control, the CI locks and the pin-age check | as v31 § 5 (SEC-T756-02, SEC-T881-02, SEC-T897-01) | 3 | devops-engineer | as v31 |
| Y | Shipped text and records | as v31 § 5 | 11 | as v31 | as v31 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | as v31 | as v31 |
| U | Live checks and user | as v31 § 5 | 6 | as v31 | as v31 (K-20) |
| AB | Opencode permission, third round | SEC-T856-02, SEC-T867-03, TL-T876-02 | 3 | as v31 | as v31 |

Total 25 + 8 + 5 + 12 + 10 + 1 + 5 + 7 + 3 + 3 + 11 + 2 + 6 + 3 = **101** = 100 tracked-LOW + 1 open (K-20). Against v31's 101: no change. **No open item carries a grade above LOW** on any scale; K-20, TD-T789-01, TD-T808-01 and TD-T888-01 have no reviewer's grade.

**Rows changed against v31: V only.**

## 6. Accepted risks, next release and dates

### 6.1 Accepted risks

Unchanged from v31 § 6.1: **SEC-T660-01 and SEC-T665-01 are accepted by the user for v12.0.0 only** ("Accept for v12.0.0 (Recommended)", 2026-11-19), after T871 (ADR-016); review **2027-01-28** (ADR-015); each returns at the next release that ships it, to be fixed or accepted again (item 43). TD-T697-07 stays accepted, not release-shipped, ending **2027-01-29**. No agent accepted a risk in the range. SEC-T900-01 (MEDIUM) was fixed before merge and never shipped, so it is no acceptance under ADR-011.

### 6.2 Next release checklist (the release after v12.0.0)

v31 § 6.2 stands with its numbers and text (36 numbers; item 8 open; item 17 as amended in v29 and v31; item 52 with 14 points). Change:

- **Item 52, point 15 (added).** The release gate now refuses a link it cannot read (a `](` that no link pattern matches: SEC-T888-03) and a table paragraph that holds a pipe and a tag-shaped `<` outside code and comments (SEC-T888-01; SEC-T900-04 notes it also refuses a plain `<`). The tag's own release document must therefore pass `scripts/verify-release-docs.py --tag` **before the tag is cut**, as item 52 already requires. A rewrite of a link or table cell may be needed; the sweep found 0 such cases in `docs/releases/v*.md` today.
- **Item 8** stays open: no tag pipeline ran in the range. Items 43, 44, 46 to 51 and points 1 to 14 of item 52: as v31.

Count: 36 numbers carried, 0 new; item 52 has 15 points.

### 6.3 Dates

Unchanged from v31 § 6.3 (all still ahead on 2026-11-21 except the first two, which are at hand): the young-pin exceptions lapse about **2026-11-24** (Brave 2.1.5) and **2026-11-25** (`server-filesystem` 2.4.0); Brave 2.2.0 7 days old about 2026-11-26 **(derived, unverified)**; **2027-01-28** GitLab token renewal and the SEC-T660-01 / SEC-T665-01 review; **2027-01-29** end of TD-T697-07; **2027-03-20** `test_ci_hash_pins.py` fails (`ci_images_reviewed_on: 2026-11-19`; the range does not change `.gitlab-ci.yml`), 2027-03-19 the last passing day.

## 7. User actions

v31 § 7 stands, unchanged:

- **The CI/CD variable check** (SEC-T751-05; item 52 point 7): on the project, group and instance CI/CD settings pages, confirm and record that no variable named `GIT_STRATEGY` or `CI_PROJECT_DIR` exists. Names only; no value is needed.
- **K-20 / A-7 stays open**: the one-time live client checks.
- **Recurring**: the runner patching rule (item 44). **Optional**: remove `/tmp/evidence-run` (not re-checked here).
- The SEC-T881-02 choice stays decided ("Keep the lock (Recommended)", 2026-11-21); nothing remains for the user on it.

## 8. Method, limits and validation

- **Carried statuses**: v31's rows and lists, plus the sources in Based on. Plan-195 § Facts and plan-194 Outcome are the only sources for the merges (!721, !722), the pinned sha `f41bccea`, the pipelines (3097540465, 3097540427) and the clean suite (2883 OK, skipped=25). The ledger figure "0 active, 697 completed" is the plan's (not re-counted here). No network call was made.
- **The search for changes**: every id-like token was extracted from the 830 lines added in `b04ec271..9493946b` (no diff under `tests/golden/` or `.vscode/`) and set against the text of registers v1 to v31; the result is section 1.2 (45 distinct tokens, 6 in no register).
- **Counting**: 6 ids named new by T900; 6 counted (no duplicate), 3 fixed in the MR and 3 tracked-LOW; 3 status changes into `fixed` from tracked-LOW. Section 5 expands to 101 ids; the sizes of unchanged batches are v31's, not recounted id by id.
- **Still unverified**:
  - Carried from v31 § 8.
  - T899's code beyond the added lines and T900's reading of it (T900 had no shell; its review is reasoned; the orchestrator ran the timing, the fuzz and the sweeps reported in plan-194 Outcome).
  - The runtime behaviour of the tag jobs (item 52); no tag pipeline ran in the range.
  - The batch membership behind "as v31 § 5".
- **Not run here**: the suite, the pipelines, the mutations.
- **Validators run before commit**: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs:
  - `tracked-debt-register-v31.md`; registers v1 to v31 (the token scan, by grep); `tracked-debt-register-v26.md`, `-v24.md`, `-v15.md` (precedents); `plan-195-tracked-debt-register-v32.md`; `plan-194-batch-v-fourth-round.md` (Outcome); `security-review-t900-batch-v-v1.md` (all sections, addendum);
  - `git diff --shortstat`, `--stat` and `-U0` of `b04ec271..9493946b`.
- Decision IDs: ADR-011, ADR-015, ADR-016.
