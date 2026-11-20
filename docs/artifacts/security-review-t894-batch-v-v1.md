# Security Review: T894 — plan-190 batch V short round (T893 fixes)

**Based on:** `docs/plans/plan-190-batch-v-short-round.md`; `docs/tasks/task-T894.md`; `docs/artifacts/security-review-t888-batch-v-v1.md` (SEC-T888-02(a), SEC-T888-04 and the orchestrator's addendum); the diff `git diff 172eef58 3c97074a` on `agent/devops-engineer/T893` (4d71af64 SEC-T888-02(a), 3c97074a SEC-T888-04; MR !718, draft); the orchestrator's evidence `t894-evidence.md` (2026-11-20); the tree at 3c97074a read in `/home/emage/Code/emage/worktrees/agent-devops-engineer-T893`.
**Reviewer:** security-engineer (read-only; no shell, so everything below is reasoned from the code and from Unicode data, none of it run).
**Date:** 2026-11-20.
**User's words (verbatim):** "V go"; plan approval: "Approve (Recommended)".

## Summary
- **Risk Level:** LOW
- **Findings:** 0 CRITICAL, 0 HIGH, 0 MEDIUM, 3 new LOW
- **Status:** CONDITIONAL_PASS

## Per-id status

| Id | Status | Basis |
|----|--------|-------|
| SEC-T888-02(a) | partly fixed | The `İ` hole is closed. `folded` is now casefold, NFKD, drop Cf/Mn/Me (INVISIBLE_LETTERS become a blank), NFKC, collapse white space. `İ` casefolds to `i` + U+0307, the drop removes U+0307, and `RELEASE VERDİCT` folds to the name's length (the orchestrator ran it: caught). The reorder opens a new fail-open for characters that have a compatibility decomposition to an upper-case letter but no case folding of their own: SEC-T894-01. The control is net-weaker for that class than at 88bf0fcc until SEC-T894-01 is fixed. |
| SEC-T888-04 | fixed | Every sentence of the new help text is backed by the code (answer 3). One unbacked word remains: SEC-T894-02, LOW. |
| SEC-T888-02(b) | open, unchanged | Non-letter look-alikes (`∨` U+2228, `∣` U+2223, ASCII `\|`) are still no wildcards. `reads_as` is untouched and the evidence confirms `∨ERDICT` is still not caught. Out of scope by plan. |
| SEC-T888-01 | open, unchanged | `table_code_html_line`, `parsed_refusal` and `table_html_refusal` have the same logic. Only the help text and docstring wording changed. |
| SEC-T888-03 | open, unchanged | `LINK_RE` and `check_links` are not in the diff. |

## Answers to the questions

**1. Does the new order close `İ`, and what do other characters do?** (all reasoned, not run)
- `İ` (U+0130): casefold gives `i` + U+0307; NFKD leaves it; the drop removes U+0307; the result is `i`. Closed.
- Dotless `ı` (U+0131): no case folding, no decomposition, a non-ASCII letter, so a wildcard. Caught, as before.
- `ſ` (U+017F): casefold gives `s`, an ASCII match. `ẞ` (U+1E9E) gives `ss`, `ß` gives `ss`, `ŉ` gives `ʼn` (modifier apostrophe plus `n`), `ǰ` gives `j`, `ǅ`/`ǆ`/`Ǆ` give `dz`, `ﬁ`/`ﬂ`/`ﬀ`/`ﬆ`/`ﬅ` give `fi`/`fl`/`ff`/`st`/`st`.
  - The strings `ss`, `ʼn`, `dz`, `fi`, `fl`, `ff` and `st` appear in neither name: `release verdict` and `gate verdicts` hold no `ss`, `st`, `ff`, `fi`, `fl`, `dz`, `ij`, `lj`, `nj` or `n`, and `j` is absent too.
  - So a heading using these characters folds to a different length than the name, and no real look-alike of these two names can depend on them. The expansion does not matter for the two names guarded here. The expansion is not a fail-open for these names. The test pins `ß`, `ﬁ` and `ǆ` on `folded` only, which is the right scope.
- Small capitals such as `ᴀ` (U+1D00), and `ᴄ`, `ᴇ`: Ll, no decomposition, non-ASCII letters, so wildcards. Caught.
- Hangul syllables go to jamo under NFKD and back under NFKC, so the length is kept. Latin letters with marks (`é`, `ǵ`) lose the mark and become ASCII or a wildcard. Both stay caught.
- NOT caught: SEC-T894-01 below. I did not enumerate every compatibility character that expands to a substring of the two names (for example the CJK squared units such as `㏄`). I expect none matches, since the squared forms use unit abbreviations and the names are plain words. This is not run.
- **New false positive for a legitimate heading:** none found. A heading is flagged only if its folded length equals the name's and every ASCII position agrees. The real heading is excluded by index, and `RELEASE VERDICTS`, `RELEASE VERDICT notes` and `Gate Verdict` stay allowed (the test asserts it). A refusal here is fail-closed anyway.

**2. Is the drop of Mn/Me/Cf after NFKD safe?**
- It was already done after NFKC. After NFKD it also removes the marks of every decomposable letter: `é` becomes `e`, `Ё` becomes `Е`, Greek `ά` becomes `α`. The NFKC after the drop recomposes what is left (Hangul).
- Direction of each risk:
  - Dropping a mark that the reader sees makes the folded text shorter or equal to what is shown. A heading `RELEASE VERD́ICT` (combining acute) folds equal to the name and is flagged. False positive, fail-closed.
  - A visible Cf or Me (for example U+20DD, U+0600) is dropped. Likewise fail-closed: a heading is flagged that a reader sees as slightly different.
  - Could a dropped character hide a letter a reader sees as a Latin letter? Marks and format characters carry no Latin glyph, so no fail-open from the drop itself.
- The real risk is the case-fold-then-decompose order, not the drop: SEC-T894-01.

**3. Is the SEC-T888-04 help text accurate against the code?**
- "holds a code span with '|' and a code span with '<', the same span or two": `table_code_html_line` requires `any('|' in span)` and `any('<' in span)` over the paragraph's `code_inline` children. Matches.
- "a paragraph that may be a GFM table (a line starts with '|' or is a delimiter row)": `may_be_table_line` (blockquote markers are also stripped, a harmless omission). Matches.
- "named with its first line": returns `token.map[0] + 1`. Matches.
- "for a text holding a '|', the same text is parsed a second time with the GFM table rule, and the nesting and HTML rules apply to that parse": `parsed_refusal` calls `markdown_tokens(text, True)` only `if "|" in text`, and `table_html_refusal` runs `nesting_limit_line` and `live_html_line`. Matches.
- "A refused document is not checked for links": unchanged.
- "it at most doubles the parse time and is NOT measured": "NOT measured" is accurate. "At most doubles" is stated as a bound, but it assumes the table-rule parse costs no more than the commonmark parse, which is also unmeasured. The table rule adds cell tokens and the 48 s single-parse figure on the same page is for the commonmark preset. This is the overclaim class of SEC-T748-08, in smaller form: SEC-T894-02, LOW.
- The old one-span wording is gone from the help text and the module docstring, and the tests assert its absence.

**4. Tests weakened? Out-of-scope changes?**
- No test is weakened. The only changed existing line is the phrase tuple, which keeps every old phrase and adds three. Two `assertNotIn` lines and one docstring `assertNotIn` are added. The diff touches two files (`scripts/verify-release-docs.py`, `tests/functional/test_verify_release_docs.py`) and `.gitlab-ci.yml` is untouched. Nothing is out of scope.
- One test case is vacuous: in `test_sec_t888_02a_...`, `name.replace("I", "\u0130", 1).replace("C", "\u0421", 1)` changes `RELEASE VERDICT` but not `Gate Verdicts`, which holds no capital `I` or `C`. For that name the loop asserts `reads_as(name, name)`. It does not test the intended shape: SEC-T894-03, LOW.
- No test covers math alphanumerics or letterlike capitals (`𝐕`, `ℛ`, `ᴿ`), which is why SEC-T894-01 passes the suite. The other `folded` assertions I recomputed by hand (`ß` to `ss`, `ﬁ` to `fi`, `ǆ` and `Ǆ` to `dz`, `\uff32\uff25\u2164` to `rev`, the five fillers to `a b`) and they hold. These are reasoned, not run.

**5. Do -02(b), -01 and -03 change?** No. See the per-id table. The evidence run `∨ERDICT` not caught confirms (b).

## New findings

| Id | Severity | OWASP | Location | Description | Remediation |
|----|----------|-------|----------|-------------|-------------|
| SEC-T894-01 | SECURITY:LOW | A04 | `scripts/verify-release-docs.py`, `folded` (line 455) | Regression from the reorder (reasoned, not run). `casefold()` now runs before NFKD. Characters that decompose to an upper-case ASCII letter but have no case folding of their own, such as the mathematical alphanumerics (`𝐕` U+1D415), letterlike capitals (`ℛ` U+211B, `ℰ`, `ℐ`, `ℒ`) and superscript capitals (`ᴿ` U+1D3F), are not lowered before NFKD turns them into `V`, `R` and so on. The result keeps the upper case, so `## RELEASE 𝐕ERDICT` folds to `release Verdict`. In `reads_as` the position compares `'V'` with `'v'`: unequal, and `'V'` is ASCII so no wildcard. Not flagged. At 88bf0fcc (NFKC, then casefold) it was caught; the tests do not cover it, since full-width forms and Roman numerals have case mappings. The effect is the SEC-T748-05 hazard, committer-only, as SEC-T888-02. | Casefold again after the final NFKC: `return " ".join(unicodedata.normalize("NFKC", kept).casefold().split())` (keep the first casefold so `İ` still loses its dot before the drop). Add tests for `𝐕ERDICT`, `ℛELEASE` and `ᴿELEASE` on `reads_as` and `folded`. |
| SEC-T894-02 | SECURITY:LOW | A05 | help text, line 282 | "at most doubles the parse time" is a bound the code does not back (the second parse uses another rule set and its cost is not measured); only "NOT measured" is true. | Say "adds a second parse, about the same cost as the first if the table rule costs no more (not measured)". The help-text test asserts the phrase, so change both together. |
| SEC-T894-03 | SECURITY:LOW | A04 (test quality) | `tests/functional/test_verify_release_docs.py`, `test_sec_t888_02a_...` | The "expanding character plus look-alike" loop is a no-op for `Gate Verdicts` (no capital `I` or `C` to replace). | Build the shown form from characters that occur in each name, for example `Gate Verd\u0130cts` with `\u0455` for the final `s`, or take a per-name replacement table. |

## Recommendations (priority order)
1. Fix SEC-T894-01 in MR !718 before merge (one line plus three test cases). With it, SEC-T888-02(a) is fixed.
2. Fix SEC-T894-02 and SEC-T894-03 in the same MR if cheap, otherwise track them as LOW debt in register v29.
3. Ask the orchestrator to run, before merge, `folded('\U0001D415ERDICT')`, `folded('\u211bELEASE')`, `reads_as('RELEASE \U0001D415ERDICT', 'RELEASE VERDICT')` on 3c97074a to confirm SEC-T894-01, and the same after the fix. The reasoning rests on Python `str.casefold` having no mapping for U+1D400..U+1D7FF and U+211B, per Unicode CaseFolding.txt. I did not run it.
4. SEC-T888-01, -02(b) and -03 stay tracked LOW debt (register v28).

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 2 reviewed ids + 3 new | 1 (SEC-T888-04) | 4 (SEC-T888-02, SEC-T894-01..03; SEC-T888-01/-03 unchanged, not reviewed here) |

### Justification
SEC-T888-02(a) closes the `İ` case and SEC-T888-04 is fixed and test-backed; no test is weakened and the diff stays inside two files. The new casefold-first order, however, loses the lower-casing of characters that only gain their upper-case ASCII form in NFKD, so a heading such as `RELEASE 𝐕ERDICT` is no longer flagged although the old order caught it (SEC-T894-01, reasoned). That is committer-only and LOW, and there is no Immutable Security Constraint breach and no control required by `security-guidelines.md` is removed. A one-line fix exists, so the verdict is CONDITIONAL_PASS rather than PASS.

### Conditions (CONDITIONAL_PASS)
- SEC-T894-01: owner=@devops-engineer (T893 branch), remediation=casefold again after the final NFKC plus three tests (`𝐕`, `ℛ`, `ᴿ`), deadline=before MR !718 merges; the orchestrator confirms by running the three calls in recommendation 3.
- SEC-T894-02, SEC-T894-03: owner=@devops-engineer, remediation=as in the table, deadline=same MR, or register v29 as tracked LOW debt.

### Blockers
None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | No (not in the diff) | 0 |
| A02: Cryptographic Failures | No (not in the diff) | 0 |
| A03: Injection | Yes (HTML in release documents, help text of the table rules) | 0 |
| A04: Insecure Design | Yes (look-alike heading check) | 2 (SEC-T894-01, -03) |
| A05: Security Misconfiguration | Yes (help text) | 1 (SEC-T894-02) |
| A06: Vulnerable Components | No (no dependency change) | 0 |
| A07: Auth Failures | No (not in the diff) | 0 |
| A08: Data Integrity Failures | Yes (`.gitlab-ci.yml` untouched) | 0 |
| A09: Logging & Monitoring | No (not in the diff) | 0 |
| A10: SSRF | No (not in the diff) | 0 |

## What stays open
- SEC-T888-02(b) (non-letter look-alikes), SEC-T888-01 (pipe in a link title or destination), SEC-T888-03 (link check misses on parentheses or a line break), all LOW and tracked (register v28).
- SEC-T894-01 (until fixed), SEC-T894-02, SEC-T894-03.
- Not run: every claim above is reasoned; the PyYAML-only path and the full suite are not reviewed by me.

## Addendum — the conditions, and the orchestrator's runs (2026-11-20)

The review above is of `3c97074a`. T893 then committed `e570a268` for SEC-T894-01, -02 and -03. The CONDITIONAL_PASS named the orchestrator's run of the three calls as the confirmation. **No second review by the security-engineer was held.** What the orchestrator ran:

1. **SEC-T894-01 confirmed at `3c97074a`.** `folded('\U0001D415ERDICT')` gave `'Verdict'`, `folded('ℛELEASE')` gave `'Release'`, and the verdict check gave no problem for a second heading `## RELEASE \U0001D415ERDICT` or `## ℛELEASE VERDICT`. At `88bf0fcc` the first one was caught. The reasoning of the review was right.
2. **After `e570a268`:** `folded` gives `'verdict'` and `'release'`, and `reads_as('RELEASE \U0001D415ERDICT', 'RELEASE VERDICT')` is `True`.
3. **A sweep of `88bf0fcc` against `e570a268`:** every code point from U+0080 to U+2FA1F, put in each letter position of `RELEASE VERDICT` and `Gate Verdicts` (5,016,128 headings), through `reads_as(folded(heading), folded(name))`.
   - **Caught by `88bf0fcc` but not by `e570a268`: 11,884.** Every one is a character whose NFKD base, with marks dropped and case folded, is a single **different** ASCII letter than the name's letter at that position (for example `À` in place of the `R` of `RELEASE`). None is a character without an ASCII base. `À` does not look like `R`, so these are over-flagged shapes of the old wildcard, not look-alikes that now pass.
   - **Caught by `e570a268` but not by `88bf0fcc`: 497**, for example U+0345, U+0390 and U+1F50.
   - The sweep is the orchestrator's own run (the scripts are in the scratchpad `sweep/`); the claim that a different-letter base is no look-alike is a visual judgement, **(unverified)** for every one of the 11,884.
4. **SEC-T894-01, -02 and -03:** fixed in `e570a268` (T893's report: the second casefold after the final NFKC, with a test and a mutation; the help-text phrase and its test reworded; the no-op loop built per name). The published documents give 0 differences on markdown-it-py 3.0.0 and 4.2.0.

**Status after the addendum:** SEC-T888-02(a) fixed, SEC-T888-04 fixed, SEC-T894-01 to -03 fixed. SEC-T888-01, -02(b) and -03 stay open as tracked LOW.
