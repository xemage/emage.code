# Security Review: T888 — plan-186 batch V third round (T887 fixes)

**Based on:** `docs/plans/plan-186-batch-v-third-round.md`; `docs/tasks/task-T888.md`; `docs/artifacts/security-review-t885-batch-v-v1.md` (its "Ruling on SEC-T751-08" and its SEC-T885-01..03 rows say what was needed); the fix diff `git diff e93f89fb 88bf0fcc` on `agent/devops-engineer/T887` (56f82e41 SEC-T885-03, 88bf0fcc SEC-T751-08, SEC-T885-01, SEC-T885-02; MR !714, draft); the orchestrator's evidence at 88bf0fcc (CI lint valid, no warnings; removed test lines read); `docs/checkpoints/checkpoint-044-release-v12.0.0.md`. The locked parser is markdown-it-py 4.2.0 (`ci/requirements-release.txt`, `ci/requirements-ci.txt`).
**Reviewer:** security-engineer (read-only; no shell, so what is not run below is reasoned from the code). **Date:** 2026-11-20.
**User's words (verbatim):** "V go"; plan approval: "Approve (Recommended)".

## Summary
- **Risk Level:** LOW
- **Findings:** 0 CRITICAL, 0 HIGH, 0 MEDIUM, 4 new LOW
- **Status:** PASS

## Per-id status

| Id | Status | Basis |
|----|--------|-------|
| SEC-T885-03 | fixed (runtime unproven) | `release` runs `python3 -I scripts/publish-release.py ...`. All three Python lines of the job run with `-I`: the `apk` helper in before_script, the CA check and the publish line. `RELEASE_COMMAND` is pinned with `-I` in third place. `python_child_problems` now covers the `release` job's before_script and script. Three mutations are refused by both the child rule and the job pin: no `-I`, `-I` after the script, and `python3.12`. `publish-release.py` is in the AST no-sibling-import test. Adding `after_script` or `hooks` to a pinned job is already refused (existing mutations). There is no `default` before_script or after_script, and the top level refuses both. `-I` stops a module from being shadowed. It does not protect against a committed change to `publish-release.py` itself; that is reviewed code at the tag, by design. |
| SEC-T751-08 (residual) | fixed | The ruling asked for a second HTML check on a parse with the GFM table rule enabled. `markdown_tokens(text, True)` gives that parse, under the same size and line caps and cached per text and kind. `table_html_refusal` runs the nesting check and `live_html_line` on it. The narrow rule was also widened to "a code span with `\|` and a code span with `<` in one paragraph that may be a table", and it is kept. Correction to T885: my bypass shape in header position is not a table under the GFM spec either (header and delimiter rows must have the same number of cells). The real hazard is that shape as a body row, and both checks refuse it (test: line 5 under the table parse). A residual class remains for non-code-span hiding: SEC-T888-01. |
| SEC-T885-01 | fixed | `LINK_RE = \[[^\[\]]+\]\(([^()\n]+)\)`. Each start is at a `[`. The text part stops at the next `[` or `]` and the target stops at the next `(`, `)` or line break. Neither quantifier can match its own closing character, so failed attempts backtrack linearly, and the text and target segments of different starts do not overlap: linear in total. A timing test covers `[a](`, `[a](\n` and `[a](` + 60 characters at the cap. Coverage loss: SEC-T888-03. |
| SEC-T885-02 | fixed (letters) | `folded` applies NFKC (full-width, mathematical and Roman-numeral forms become ASCII) and drops Cf, Mn and Me. `reads_as` compares at the same length and lets any non-ASCII letter stand for any letter, which fails closed. Precomposed and decomposed Latin letters with diacritics are both caught: NFKC composes É, which stays a non-ASCII letter (wildcard), and a mark with no precomposed form is dropped. Tests cover Cyrillic, Greek, a combining acute, full-width letters and Roman numerals. U+2800 and the Hangul fillers are in `INVISIBLE_LETTERS`. Gaps: SEC-T888-02. False-positive risk is negligible: a heading matches only if it has exactly the name's length and every ASCII letter agrees, and the tests show `RELEASE VERDICTS` and `RELEASE VERDICT notes` stay allowed. |

## Answers to the questions

**1. SEC-T751-08.** Together, the two checks close the code-span route.
- If markdown-it-py sees a table, the table parse shows any tag left live by a split cell.
- If markdown-it-py does not see a table, the paragraph rule still refuses a `|` span next to a `<` span, whatever the cell counts are.

Remaining shape: the narrow rule looks only at code spans. A `<b>` can also be hidden by a `|` inside a link title or destination: `| [x](y "|<b>") |` in a table body. CommonMark reads `|<b>` as a title, while a GFM cell split leaves `<b>` live in the next cell. Only the table parse catches this, so it holds only while markdown-it-py and GitLab agree on table recognition and cell splitting. Candidate differences are unverified: how a backslash before a pipe is counted (`\\|`), and start rules in GitLab's renderer. I know of no confirmed shape: SEC-T888-01, LOW.

**2. SEC-T885-02.** The fix is sufficient for letters, with two fail-opens (SEC-T888-02):
- (a) `casefold` runs after the mark drop. `İ` (U+0130) casefolds to `i` + U+0307, so `## RELEASE VERDİCT` is one character too long and is not a look-alike. Reasoned, not run.
- (b) Non-letter look-alikes are not wildcards: U+2228 `∨` for V, U+2223 `∣` for I, and ASCII `|` for I. ASCII `1` is excluded on purpose (tested).

NFKC expansions happen before the length compare, so they are handled. False-positive risk: see the table.

**3. SEC-T885-01.** The regex is linear on every shape. Links a reader sees that the check now misses (SEC-T888-03):
- a destination with balanced parentheses, `[a](b_(c).md)`;
- a title holding parentheses, `[a](b.md "t (x)")`;
- a pointed destination holding parentheses;
- a destination after a line break, `[a](\nb.md)`.

The old regex mangled the first three anyway. The evidence reports 0 differences over 2221 tracked `.md` files. This is the broken-link check, not a security control.

**4. SEC-T885-03.** The release job's Python lines are isolated, and the pin covers all of them: before_script and script are pinned whole, adding `after_script` or `hooks` is refused, and there is no `default` script. Runtime proof is only the next `v*` tag pipeline.

**5. Resource use and tests.**
- **Parse cost:** the second parse goes through the same `markdown_tokens`, with the same `MAX_DOCUMENT_CHARS` and `MAX_LINE_CHARS` caps. It runs only for a text holding a `|`, once per text (cache, tested by parser call count), so it at most doubles the parse time.
- **Known quadratic table output:** the cells the table rule fills in (markdown-it issue #1000) are capped from markdown-it-py 4.0.0 (changelog, PR #364). The locked 4.2.0 includes that cap; 3.0.0 does not and is not locked.
- **Measurement:** the 48 s worst case in the docstring was measured on one parse. Adding a `|` to that shape is not measured; an estimate of about 2 x 48 s is inside the 10-minute `release-docs-gate` timeout.
- **Tests:** none weakened. `RELEASE_COMMAND` gained `-I` (stricter), `python_child_problems` widened, and the other changes only add tests and mutations. No assertion was removed.

## New findings

| Id | Severity | OWASP | Location | Description | Remediation |
|----|----------|-------|----------|-------------|-------------|
| SEC-T888-01 | SECURITY:LOW | A03 | `scripts/verify-release-docs.py`, `table_code_html_line`, `table_html_refusal` | A `\|` inside a link title or destination, `[x](y "\|<b>")` in a table body, can leave `<b>` live after GitLab splits the cell. Only the table parse catches it, so the check depends on markdown-it-py and GitLab agreeing on table recognition and cell splits (unverified; no confirmed differing shape). Only a committer can write it, it is reviewed in an MR, and GitLab's sanitiser applies. | Widen the narrow rule to "a paragraph that may be a table holds a `\|` and a `<` anywhere outside a code span or comment, beyond what the table parse shows". Or record one confirmed GitLab rendering of `\\|` and of a link title holding `\|` in a table. |
| SEC-T888-02 | SECURITY:LOW | A04 | `folded`, `reads_as` | (a) `casefold` comes after the mark drop, so `İ` expands to `i` + U+0307 and `## RELEASE VERDİCT` is not a look-alike (reasoned). (b) Non-letter look-alikes (`∨` U+2228, `∣` U+2223, ASCII `\|`) are not wildcards. The effect is the SEC-T748-05 hazard: the real section ends early and the rest goes unchecked. | Casefold first, then NFKD, then drop Mn, Me and Cf, then NFKC. Let any non-ASCII character that is not a space or mark be a wildcard, not only letters. Add tests for `İ` and `∨`. |
| SEC-T888-03 | SECURITY:LOW | A04 (quality, the link check) | `LINK_RE`, `check_links` | The link check no longer reports a broken link whose target holds parentheses or comes after a line break (the four shapes in answer 3). The evidence shows 0 such links today. | Keep the linear regex, and refuse (or report as "cannot check") any `](` whose target the regex does not match, so a missed link fails closed. Add tests for `[a](b_(c).md)` and `[a](\nb.md)`. |
| SEC-T888-04 | SECURITY:LOW | A05 | `scripts/verify-release-docs.py` help text, lines 276-286 | The help text still describes the old rule ("a code span with both '\|' and '<'"). It does not mention the table-parse refusal or that a text with a `\|` is parsed twice, and the time paragraph still gives a single-parse measurement. This is the overclaim class of SEC-T748-08. | Update both paragraphs (the widened rule, the second parse, "at most doubles the time, not measured"), and extend the help-text test to assert the new phrases. |

## Recommendations (priority order)
1. Track SEC-T888-01..04 as LOW debt in register v28.
2. SEC-T888-02(a) is a one-line reorder and the cheapest real gain. Take it with SEC-T888-04 in the next batch.
3. SEC-T888-01: record one GitLab rendering check, or widen the narrow rule to non-code `\|`.

## What the next `v*` tag pipeline must show for the release job
1. `release` ran on the dedicated runner (tag `release-gate`), after `release-docs-gate` and `main-develop-drift-gate` both passed.
2. The before_script `apk add` line and `--ca-release` both ran as `python3 -I` and passed before the publish line.
3. The job log shows the line `python3 -I scripts/publish-release.py --tag ...` exactly as pinned, with no `ModuleNotFoundError` or import error. This proves the script needs nothing from `scripts/` on `sys.path`.
4. The Release was created for the tag, and `CHANGELOG.md` was kept as an artifact.
5. No line shows the job token (`[MASKED]` at most), and no line echoes an expanded variable.
6. `release-docs-gate` passed with the table-rule parse in place: no `read as a GFM table` refusal on the tag's own document, and its duration is recorded for comparison with the 48 s single-parse measurement.

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 4 reviewed ids + 4 new | 4 | 4 (SEC-T888-01..04) |

### Justification
SEC-T885-03, SEC-T751-08 (residual), SEC-T885-01 and SEC-T885-02 are fixed as the T885 ruling and rows required, and every control in scope was tightened. No test was weakened. There is no breach of an Immutable Security Constraint, and no required control was removed or weakened. The four new findings are LOW: the first two are committer-only gaps in the release document's look-alike and table HTML checks, and the other two are quality and documentation issues. PASS holds on the condition that the orchestrator tracks SEC-T888-01..04 as technical debt in register v28 (§ Verdict Rules).

### Conditions
None (PASS). SEC-T888-01..04 go to register v28 as tracked LOW debt.

### Blockers
None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (job token scope unchanged) | 0 |
| A02: Cryptographic Failures | Yes (CA line unchanged) | 0 |
| A03: Injection | Yes (HTML in release documents) | 1 (SEC-T888-01) |
| A04: Insecure Design | Yes | 2 (SEC-T888-02, -03) |
| A05: Security Misconfiguration | Yes | 1 (SEC-T888-04) |
| A06: Vulnerable Components | Yes (markdown-it-py 4.2.0 locked, includes the cap on filled-in table cells; audit not re-run) | 0 |
| A07: Auth Failures | Yes (token by name, JOB-TOKEN header) | 0 |
| A08: Data Integrity Failures | Yes (`-I` on the token job) | 0 |
| A09: Logging & Monitoring | Yes (no token in lines) | 0 |
| A10: SSRF | Yes (`--expected-host` unchanged) | 0 |

Sources consulted: [markdown-it issue #1000](https://redirect.github.com/markdown-it/markdown-it/issues/1000); [markdown-it-py CHANGELOG](https://fuchsia.googlesource.com/third_party/github.com/executablebooks/markdown-it-py/+/6aee77a8e80ed7d46d9b62c19b35c8a97125d010/CHANGELOG.md).

## Addendum — the orchestrator's run of SEC-T888-02 (2026-11-20)

`verdict_placeholder_problems` at `88bf0fcc`, on a document with a filled `## RELEASE VERDICT`, then a second heading and `- Status: pending`:

| Second heading | Problems |
|---|---|
| `## RELEASE VERDİCT` (U+0130) | none: **(a) confirmed by run** |
| `## RELEASE ∨ERDICT` (U+2228) | none: **(b) confirmed by run** |
| `## RELEASE VЕRDICT` (Cyrillic Е) | the SEC-T748-05 look-alike problem, as intended |
| `## Next` | none (an ordinary heading ends the section) |
