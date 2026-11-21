# Security Review: T900 — plan-194 batch V fourth round (T899 fixes)

**Based on:** `security-review-t888-batch-v-v1.md` (SEC-T888-01, -02(b), -03 rows and remediations); `security-review-t894-batch-v-v1.md` (format, SEC-T894-01 fold-order regression); `docs/plans/plan-194-batch-v-fourth-round.md` (not found at the path given, not read); the diff `t899.diff` for `f6ca9470` on `agent/devops-engineer/T899`; the orchestrator's `t900-evidence.md`; `scripts/verify-release-docs.py` as on develop for `may_be_table_line`, `QUOTE_PREFIX_RE` and `table_code_html_line`; the diff text for everything else.
**Reviewer:** security-engineer (read-only; no shell, so every claim is reasoned, none run).
**Date:** 2026-11-21.

## Summary
- **Risk Level:** MEDIUM
- **Findings:** 0 CRITICAL, 0 HIGH, 1 MEDIUM, 5 LOW (new)
- **Status:** CONDITIONAL_PASS

## Per-id status

| Id | Status | Basis |
|----|--------|-------|
| SEC-T888-03 | fixed for every shape the finding named | `unchecked_link_excerpts` is one `find("](")` scan, linear. `matched = {m.start(1) - 2}` is exactly each match's own `"]("`, because group 1 follows `\]\(` in both regexes, so there is no off-by-one fail-open. A link whose target has a parenthesis or starts on the next line is refused. The `[![i](s)](t)` case is covered: LINK_RE matches the inner image from the second `[`, and IMAGE_LINK_RE accounts for the outer `"]("`. The residual fail-opens and new false refusals are in SEC-T900-03, -04 and -06, all LOW. |
| SEC-T888-02(b) | fixed per its remediation (non-ASCII), ASCII residual | `is_wildcard_char` implements the remediation: any non-ASCII, non-space, non-mark character is a wildcard. `∨`, `∣` and U+2014 are caught. ASCII look-alikes (`\|`, `l`, `1`, `0`) stay no wildcard, and the test pins `VERD1CT` as not caught. The original finding named ASCII `\|`; that part is a design limit, since a wildcard for ASCII would flag real words. Tracked as LOW in SEC-T900-05. |
| SEC-T888-01 | partly fixed | The widened rule was added as the finding asked. But the "outside code or comment" exclusion is textual, not syntactic, and the regex that does it is exponential: SEC-T900-01 (MEDIUM) and SEC-T900-02 (LOW). The control as written can hang the gate, and its backstop role can be bypassed. |

## Answers to the probes

**1. Link shapes past "cannot check"** (reasoned)
- Closed:
  - `](` inside an inline code span: `strip_code(text, "x")` turns the span into `x`, so the `](` is gone and no false hit follows.
  - Linked image with parentheses in the inner part, `[![i](a_(b).png)](t.md)`: both the inner and the outer `](` are unmatched, so both are refused.
  - Image-only `![alt](src)`: LINK_RE matches it from the `[`.
  - `[a](<b (c).md>)`: refused (the target has parentheses).
- Open, all pre-existing or outside the finding's wording:
  - Reference-style links (`[a][r]`, `[r]: missing.md`) and `<autolinks>` have no `](`, so they are neither checked nor flagged. The help text says only `](`, so this is accurate, but the gate does not check them: SEC-T900-06.
  - The inline-code regex has no backslash awareness. an escaped-backtick pair around a link with a parenthesised target is a live link in CommonMark with escaped backticks. `INLINE_CODE_RE` strips it, so the link is in neither scan: fail-open.
  - `FENCED_CODE_RE` pairs the first three backticks it sees. In a text with a double-backtick span, a link with a parenthesised target and then a triple-backtick run, CommonMark has a code span and then a live link, while the regex removes the link. Same class: SEC-T900-06.
  - The fail-open consequence is an unchecked link target only. It is not a security bypass, which is why it is LOW.
- Not fail-open: `matched` cannot be off by two. A `](` inside a matched LINK_RE target (`[a](x](y.md)`) is refused, which is the safe direction.

**2. False refusal for a legitimate future release document** (reasoned)
- The wildcard for headings is safe. A heading is flagged only if its folded length equals the name's and every ASCII position agrees, so U+2014 or other punctuation flags only a near-copy of the real heading. `RELEASE VERDICTS`, `RELEASE VERDICT notes` and `RELEASE VERDICT ✓` stay allowed (the evidence probes agree).
- The cannot-check scan has new false refusals, and its message is wrong for them: SEC-T900-03.
  - Link text with brackets, such as `[Notes [v10]](x.md)`, is refused: LINK_RE text excludes `[` and `]`.
  - An empty alt or empty text, `![](a.png)` and `[](x)`, is refused: LINK_RE needs one or more characters of text.
  - The message blames "a parenthesis or the next line" for both.
- The new pipe-and-tag rule refuses any `<` in a table paragraph, even a plain one such as `| p95 | < 100 ms |` or `<=`. A `<https://…>` autolink in a table row with another `|` is refused too. This is fail-closed and the message tells the author what to do, but it is more than the hazard needs: SEC-T900-04. The developer's sweep reports 0 hits in `docs/releases/v*.md` and 31 in non-gated docs (not re-run by me).

**3. Pipe-and-tag rule: bypass and ReDoS**

*Bypass* (reasoned)
- Unclosed backtick run: `CODE_SPAN_RE` does not match, nothing is excluded, so `|` and `<` stay and the rule fires. Fail-closed.
- `<!--` with no `-->`: `COMMENT_RE` does not match, so `<` stays. Fail-closed. Backticks that pair across a comment boundary also leave the `<!--` opener's `<` behind.
- The exclusion is textual and can hide a `<` that CommonMark still treats as title or destination text: SEC-T900-02.
- `may_be_table_line` misses nothing I could construct:
  - a delimiter row is always on its own line;
  - indentation is stripped;
  - blockquote markers are handled;
  - a list marker only ever sits on the header line, and the delimiter line then starts with `|` or is a delimiter row.

*ReDoS* (reasoned, not run)
- `CODE_SPAN_RE = (`+)(?:(?!\1).|\n)*?\1` with DOTALL is **exponential**. With DOTALL, `.` already matches `\n`, so at every newline both alternatives match the same character. When an opener has no closing run (a failed search), the engine backtracks through each newline twice, giving 2^k paths for k newlines after the opener. Python's `re` has no memoisation. See SEC-T900-01.
- `COMMENT_RE = <!--.*?-->` is quadratic: each unclosed `<!--` scans to the end. At the 131072-char cap that is about 32768 openers times a scan of about 65k characters on average, roughly 2·10^9 steps in C, so seconds to tens of seconds. Not exponential, but still large.
- The link regexes stay linear: every part stops at the next bracket, parenthesis or line break. The `"]("` scan is linear.

**4. Tests**
- No old assertion is weakened.
- Vacuous: `self.assertEqual(self.link_errors(text).count("x"), 0)` in the linear-time test. A list of error strings never contains the string `"x"`, so it passes whatever `link_errors` returns. Only the 2 s bound has force. SEC-T900-05.
- No timing test for `CODE_SPAN_RE`, `COMMENT_RE` or the pipe-and-tag rule. That is why SEC-T900-01 passes the suite.
- No test for backslash-escaped backticks or for `<!--` inside a link title.
- The reported mutations cover each new branch once (cannot-check off, IMAGE_LINK_RE broken, letters-only wildcard, pipe-tag rule off, no code/comment exclusion). They do not cover a timing mutation.
- Not verified: the developer's sweeps (2149 files, 14675 headings, 31 paragraphs). I have not run them.

## New findings

| Id | Severity | OWASP | Location | Failure scenario | Remediation |
|----|----------|-------|----------|------------------|-------------|
| SEC-T900-01 | SECURITY:MEDIUM | A04 (availability; the "cap limits parser time" claim in the help text is now false for this regex) | `scripts/verify-release-docs.py`, `CODE_SPAN_RE`, called by `pipe_and_tag_outside_code` for **every** paragraph | A paragraph with one unclosed backtick followed by about 30 or more lines, for example "`" then `\n` repeated 40 times, makes `CODE_SPAN_RE.sub` take about 2^40 steps. A committer can hang the gate until the job timeout. A legitimate hard-wrapped paragraph with a stray backtick can hang it too. The failure is fail-closed (the job times out), but it blocks the release and is outside what the 131072-char cap bounds. The same function runs `COMMENT_RE` in quadratic time on repeated `<!--`. (Reasoned; not run.) | Remove the redundant `\|\n`: `(`+)(?:(?!\1).)*?\1` with DOTALL. Better, avoid the regex: take the code spans from the markdown-it children (`code_inline` contents) instead of re-lexing the text. For comments use `str.find("<!--")` and `find("-->", start)` in a loop. Add a timing test at the cap for `` "`" + "\n"*60 ``, `` "`\n"*N `` and `"<!--"*N`. Before merge the orchestrator should time one call: `python3 -c "import re,time;r=re.compile(r'(\`+)(?:(?!\1).\|\n)*?\1',re.S);t=time.time();r.sub('', '\`'+'\n'*24);print(time.time()-t)"`. Doubling per added newline confirms it. |
| SEC-T900-02 | SECURITY:LOW | A03 | `pipe_and_tag_outside_code` | The exclusion is textual. A backslash-escaped backtick pair, such as `\`\|<b>\``, or a `<!--` in one link title and a `-->` later in the paragraph, makes the regex hide a `\|<b>` that CommonMark still sees as title text. The rule then passes. What remains is the table-rule parse, which the rule was added to back up for the case where the two parsers disagree on cells. Committer-only, and reviewed in the MR. | Compute the "outside code" text from the token children (drop the `code_inline` and `html_inline` comment tokens that markdown-it reports), or refuse a `\|` and `<` that stay after removing only `code_inline` content. Add tests for the two shapes. |
| SEC-T900-03 | SECURITY:LOW | A04 (quality) | `check_links`, error text | Link text with brackets (`[Notes [v10]](x.md)`), an empty alt or text (`![](a.png)`, `[](x)`) and a linked image with empty alt are refused. The message says "its target holds a parenthesis or starts on the next line", which is wrong for these. | Say "a link the patterns cannot read (brackets in the text, an empty text, a parenthesis in the target, or a target on the next line)". Optionally let LINK_RE take empty text (`*`) and `[^\[\]]` nested text. |
| SEC-T900-04 | SECURITY:LOW | A04 (false refusal) | `table_pipe_tag_line` | Any plain `<` in a table paragraph is refused: `\| p95 \| < 100 ms \|`, `<=`, and an autolink. The help text and message cover it, but the hazard needs a tag-shaped `<`. | Count only a `<` followed by a letter, `/`, `!` or `?`, or document `&lt;` as the way to write it in the help text. |
| SEC-T900-05 | SECURITY:LOW | A04 (test quality, residual) | `tests/functional/test_verify_release_docs.py` (`...stays_linear...`); look-alikes | `.count("x")` is vacuous. No timing test for the new regexes. ASCII look-alikes (`\|`, `l`, `1`, `0`) are not wildcards, by design. | Drop the `.count` line or assert on the error list. Add the timing tests of SEC-T900-01. Note the ASCII limit in the help text. |
| SEC-T900-06 | SECURITY:LOW | A04 | `strip_code`, `INLINE_CODE_RE`, `FENCED_CODE_RE`; reference links | The code-strip regexes ignore backslash escapes and mispair triple backticks inside a double-backtick span, so some live links with a parenthesised target stay unchecked. Reference-style links and autolinks are not checked. Pre-existing; the effect is an unchecked link target only. | Take links from the markdown-it tokens (`link_open` and `image` attrs) instead of regexes, or record it as the known limit of SEC-T888-03. |

## Recommendations (priority order)
1. Fix SEC-T900-01 before MR merge. It is a one-line change plus a timing test, and the orchestrator runs the 24-newline timing call above to confirm it first.
2. Fix SEC-T900-02 together with SEC-T900-01 by using the token children, if cheap. Otherwise track it as LOW debt in register v32.
3. SEC-T900-03 to -06: fix the error message and the vacuous assertion in the same MR (cheap); track the rest as LOW debt.
4. Run the developer's sweeps again on the merged code, since I did not.

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 | 0 | 1 (SEC-T900-01) |
| LOW | 3 reviewed ids + 5 new | 2 (SEC-T888-03; SEC-T888-02(b) for non-ASCII) | 6 (SEC-T888-01 partly, SEC-T900-02 to -06) |

### Justification
SEC-T888-03 and SEC-T888-02(b) are fixed as their remediations asked, and the diff stays inside two files with no old assertion weakened. SEC-T888-01 is only partly fixed: the new rule's regex exclusion has a catastrophic-backtracking shape (SEC-T900-01), reasoned from the pattern and not run, and the exclusion is textual and can be bypassed (SEC-T900-02). No Immutable Security Constraint is breached and no control required by `security-guidelines.md` is removed, so the verdict is CONDITIONAL_PASS. The MEDIUM needs its fix, or at least a remediation plan with owner and deadline, before merge.

### Conditions (CONDITIONAL_PASS)
- SEC-T900-01: owner=@devops-engineer (T899 branch), remediation=drop `|\n` from `CODE_SPAN_RE` or use token children, replace `COMMENT_RE` by a `find` loop, add timing tests at the cap, deadline=before the T899 MR merges; the orchestrator confirms with the 24-newline timing call.
- SEC-T900-02 to -06: owner=@devops-engineer, remediation=as in the table, deadline=same MR or register v32 as tracked LOW debt.

### Blockers
None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | No (not in the diff) | 0 |
| A02: Cryptographic Failures | No (not in the diff) | 0 |
| A03: Injection | Yes (HTML hidden in table cells) | 1 (SEC-T900-02) |
| A04: Insecure Design | Yes (regex time, link check, look-alike headings, tests) | 5 (SEC-T900-01, -03 to -06) |
| A05: Security Misconfiguration | No (help text only; the time claim is in SEC-T900-01) | 0 |
| A06: Vulnerable Components | No (no dependency change) | 0 |
| A07: Auth Failures | No (not in the diff) | 0 |
| A08: Data Integrity Failures | Yes (`.gitlab-ci.yml` untouched per the evidence) | 0 |
| A09: Logging & Monitoring | Yes (error excerpts: `repr` escapes controls and bidi characters) | 0 |
| A10: SSRF | No (not in the diff) | 0 |

## What stays open
- SEC-T900-01 (MEDIUM, must be fixed or planned before merge).
- SEC-T888-01 (partly), SEC-T900-02 to -06, all LOW.
- Not run by me: every claim above, in particular the exponential timing of `CODE_SPAN_RE`, the quadratic timing of `COMMENT_RE`, the Unicode wildcard behaviour and the markdown-it table cell split on an escaped backtick.

## Orchestrator's addendum (2026-11-21)

The orchestrator ran the finding's own check on `f6ca9470` and confirmed SEC-T900-01: `CODE_SPAN_RE` took 0.033 s (18 newlines), 0.128 s (20) and 0.494 s (22), about four times more per two newlines; `COMMENT_RE` took 18.6 s on `<!--` x 32000. T899 fixed it in `2584bb45` (linear `without_code_spans` and `without_comments`, with timing tests at the cap). The orchestrator re-ran the shapes at the 131072-character cap on the fixed code: 0.001 s to 0.037 s. A fuzz of 2,587 short paragraphs compared the new code-span cut with markdown-it's `code_inline` children for the presence of `<` and `|` outside code: 0 differences. The condition named the orchestrator's confirmation, so no second security review was held. SEC-T900-03 (message) and SEC-T900-05 (vacuous assertion) were fixed in the same commit. SEC-T900-02, -04 and -06 stay open as tracked LOW debt (register v32), and so does SEC-T888-01's textual exclusion (SEC-T900-02). The sweep of the new table rule gives 29 flagged paragraphs after the fix (31 before): the two that dropped out held a lone triple-backtick run that the old pairing read differently from CommonMark. None is a `docs/releases/v*.md`.
