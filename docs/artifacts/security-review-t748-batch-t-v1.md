# Artifact: security-review-t748-batch-t-v1.md

> Immutable once produced; revisions bump `<N>`.

**Based on:** `docs/plans/plan-142-verdict-check-tokens.md`, `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4 (SEC-T739-07), `docs/artifacts/security-review-t745-batch-s-v1.md` § 1, § 4 (TD-T739-01, SEC-T745-01), `t747-script.diff` and `t747-tests.diff` (`679e6adc` to `d400b851`), `scripts/verify-release-docs.py` at `d400b851` (read by range), `tests/functional/test_verify_release_docs.py` (the diff and lines 1-60).

- **Reviewer:** security-engineer, read-only, no shell. **Gate:** security. **Date:** 2026-11-06. **Target:** T747 on `agent/devops-engineer/T747` at `d400b851`.
- **Method:** hand traces only. "Traced" means I followed the shape through the script and, for fences and line splitting, through `markdown_it` 3.0.0 source. No code was run, so section 6 lists the shapes the orchestrator should run.

## Verdict: CONDITIONAL_PASS

- 0 CRITICAL, 0 HIGH, 0 MEDIUM, 9 LOW. Nothing blocks the merge.
- The only condition is that the LOW findings be tracked as debt. Section 3 is the record, and the next register takes them over.
- No Immutable Security Constraint is breached. I do not read this verdict check as a control that `security-guidelines.md` requires, so item 2 of the Security Gate Protocol does not apply.
- **Why LOW:** each route needs a document that survives merge request review, with the unfilled value visible in the diff. The new weakenings (SEC-T748-01, -02, -04) need an unusual or crafted shape. T747 is a net gain.

**The orchestrator should look at two things.**
- SEC-T748-01 is a real regression that no ruling covers: a section holding only `## &#32;` now passes as filled, and the old code failed it.
- SEC-T748-02 is the same class as SEC-T739-07 (b), a hidden heading that ends the section, in a form T747 did not close. Both fixes are a few lines.

## 1. Answers

### Q1. Is SEC-T739-07 closed?

**Yes, as written.** All three shapes in the review now fail. T739's fallback fix, "refuse a second occurrence of the heading", is also done.

| Shape | Trace at `d400b851` | Result |
|---|---|---|
| (a) Heading first in a comment | The comment is `html_block`, so `section_heading_indexes` finds only the real heading, and the field is read | Fails |
| (b) Comment holding `## x` | No heading token, so the section runs on and the field is read | Fails |
| (c) Two ``` in paragraphs | Neither line opens a fence, because each starts with text. `FENCED_CODE_RE` is no longer on this path | Fails |
| (d) Second real heading | `count > 1`, `:420-421` | Fails |
| (f) Heading only in a comment | Absent, `:601` | Fails |
| (h) Setext heading | The `heading_open` has tag h2, and the text matches | Fails on the placeholder |
| (i) Heading only in a blockquote | `level != 0` | Fails: absent |

The implementer's claim on these shapes holds by trace. **Residual:** (b)'s class, "a hidden heading line that ends the section early", survives where the heading's text is invisible but not empty. That is tracked as SEC-T748-02 rather than as a reopening.

### Q2. Which route still lets a visible unfilled verdict pass?

All of these are **traced**, none run. "Old" gives the result at `679e6adc`.

| # | Shape, in or near the section | Old | New | Finding |
|---|---|---|---|---|
| 1 | `## RELEASE VERDICT\n\n## &#32;\n` or `## <!-- x -->`: an empty section | caught | **passes** | -01 |
| 2 | `&#8203;\n---\n\n- Status: pending`, also ` ## &#8203;`, `##\t&#8203;`, `# &#8203;` | caught | **passes** | -02 |
| 3 | `## &#8203;\n\n- Status: pending`, `## <span hidden>x</span>\n\n- Status: pending` | passes | passes | -02 |
| 4 | `Text\n---\n\n- Status: pending`, ` ## Next`, `##\tNext`, `# Next` | caught | passes (ruling 1, plan) | -03 |
| 5 | `<div>\n## RELEASE VERDICT\n- Status: pending\n</div>` above a filled real section; the HTML block's text is displayed | caught | **passes** | -04 |
| 6 | Filled section, then `## RELEASE&nbsp;VERDICT`, `## RELEASE VERDICT&#8203;` or `## Release Verdict` with the pending field. Or those first and the real heading second | passes | passes | -05 |
| 7 | `## Gate verdicts`, `### Gate Verdicts`, `> ## Gate Verdicts` with a pending field | passes | passes (ruling 5) | -05 |
| 8 | `> - Status: pending`, `1. Status: pending`, `+ Status: pending` | passes | passes (known) | -06 |
| 9 | `Status: pending`, `**Status:** pending`, `### Status: pending`, `\| Status \| pending \|`, `<p>Status: pending</p>` | passes | passes | -06 |
| 10 | `- Status:\n  - pending`: the `nested_follows` rule accepts the empty value, and the sub-item has no colon, so it is no field | passes | passes | -06 |
| 11 | `- Status: _pending_`, `__pending__`, `(pending)`, `&#112;ending`, `- Status:&#32;pending`; the value does not start with `pending` after only `*` and `` ` `` are removed | passes | passes | -06 |
| 12 | `- Status: not filled yet`, or any free text | passes | passes | none: the field contract is deliberately not in this gate |
| 13 | A field in a closed ``` fence, shown as code | passes | passes (by design, `test_placeholders_in_a_fenced_block_or_another_section_do_not_count`) | none |
| 14 | A pending field above the section with no raw heading line | passes | passes | none: outside the sections by definition |

**Suspected only, not traced:** GitLab-specific syntax such as `>>>` blocks may place the heading differently from CommonMark, but the field lines are still read. This stays under SEC-T716-03. It is **(unverified)**.

### Q3. Does any check get weaker than at `679e6adc`, beyond the rulings?

**Yes, in three places.** All three are traced and LOW. Beyond those, I compared the old rules one at a time and found nothing else. A heading after a fence, adjacent-line blanking, trailing white space and the `nested_follows` adjacency all behave as before. `has_cursor_migration_item` gets the same tokens under the same guard.

- **SEC-T748-01:** the "empty section" check. The old `## ` line rule ended the section at `## &#32;`, leaving an empty body and a problem. The new rule keeps the empty heading's source line in the body, so `not body.strip()` is false and there are 0 problems. `test_a_real_heading_with_an_empty_section_stays_a_problem_in_every_form` only uses `## Next`.
- **SEC-T748-02:** ruling 1 rests on "because a reader sees it". A setext, indented, tab or H1 heading whose text is only U+200B, U+00AD or U+2060 is seen by no reader, yet it ends the section. `str.strip()` does not remove those characters, because they are format characters rather than white space. The old check read on through these forms.
- **SEC-T748-04:** ruling 3 rests on "hidden". For a comment that holds. A non-comment HTML block with no blank line displays its text, and the old check caught it through the raw heading line.

**The rulings:**

| Ruling | My position | Grade |
|---|---|---|
| 1. A real heading with text ends the section | Accept for visible text, with a cheap fail-closed option to refuse a section that ends at a setext or `# ` heading | LOW, SEC-T748-03 |
| 2. Field really inside a closed fence | **Agree, no finding.** It matches the rendered document and the tested fenced-block rule. The old result came from the mispairing that SEC-T739-07 (c) reports | none |
| 3. Comment holding the heading and a pending field | **Agree for comments.** It does not extend to other HTML blocks | LOW, SEC-T748-04 |
| 4. `lru_cache(maxsize=None)` | **Agree, no finding.** See Q4 | none |
| 5. Misspelt optional heading | Accept as tracked debt, not as correct. It belongs with the near-duplicate shapes, and one fix closes both | LOW, SEC-T748-05 |
| Known: `>`, `1.`, `+` | Grade LOW. The template's form is `- **Status**:` (`docs/releases/_template.md:77`), so reaching these takes a departure from the template | LOW, SEC-T748-06 |

### Q4. A route round the long line guard? Can shared tokens leak between checks?

**No to both, by trace.**

- **Guard.** `MarkdownIt` is called once, at `:344`, after the `long_line_number` check at `:342`. An AST test and a functional test pin this.
  - The guard splits on `\n` only, which is the parser's model after it normalises CR, so the parser never sees a longer line than the guard saw.
  - `None` is handled at every caller: `:414-415`, `:397` (`or []`), `:601` (`or []`, unreachable after `document_refusal` at `:584-587`), and `:744-745`.
  - The cache is keyed on the text alone, `MAX_LINE_CHARS` is a constant, and exceptions are not cached.
- **Shared tokens.** I read every consumer: `heading_text`, `section_heading_indexes`, `section_line_span`, `is_closed_backtick_fence`, `section_text`, `migration_section_span`, `holds_live_html`, `anchor_text`, `bold_lead_text`, `has_cursor_migration_item`. None assigns to a token or to the list. `tokens[:end]` and the filter in `bold_lead_text` build new lists. The risk is only future code, and the docstring warns against it.
- **Memory.** The cache is bounded by the release documents named on a Cursor line plus the tag's own, in a short process. No finding.
- **Reach of SEC-T745-01: note for the register, no new id.** The own document is now parsed on every run, where before it was parsed only if `install.sh` named it on a Cursor line. The cost does not double, because the cache works. The worst case is unchanged and fails closed on the job timeout. TD-T739-01 and SEC-T745-01 stay open as recorded.

### Q5. Is the `RELEASE VERDICT` presence rule sound?

**Sound for what it states, and stronger than the old substring.** The heading must be real, top-level, level 2 and exact, in ATX or setext form. Comment, fence, blockquote, list, past-the-nesting-limit and swallowed forms all fail closed. Three limits remain:

1. A wrapper makes the heading real to the parser and hidden from a reader: `<div hidden>\n\n## RELEASE VERDICT\n\n- Status: PASS\n\n</div>`. The block ends at the blank line, so the heading token is top-level. Whether GitLab's sanitizer keeps `hidden` is **(unverified)**. `<details>` only collapses. This is SEC-T739-03's class, under SEC-T748-04.
2. Presence says nothing about content. The emptiness check that follows it is what SEC-T748-01 weakens.
3. `## Install` and `## Highlights` stay raw substrings at `:590-595`, so a comment satisfies them. This is older than T747 and outside the plan. SEC-T748-09.

### Q6. Is `is_closed_backtick_fence` sound, and do the tests pin it?

**Sound on 3.0.0 by source reading. The tests pin behaviour well.**

- **Numbers.** `rules_block/fence.py:93-99` sets `state.line = nextLine + (1 if haveEndMarker else 0)`, `map = [startLine, state.line]` and `content = getLines(startLine + 1, nextLine, length, True)`. So closed gives a difference of 2 and unclosed gives 1, provided the content count is exact.
- **Can the count fall short and fake a closure?** Only if an unclosed fence's map includes a line whose slice is empty with no LF, which can only be a line at the very end of the source. I traced each case:
  - A final white-space-only line with no LF is not a parser line at all (`state_block.py:75-83`, `continue`).
  - A final line empty inside a container, `> ```\n> x\n>`, gives `pos == len(src)`, so `state.src[pos]` raises `IndexError` and the loop breaks before counting it (`fence.py:65-69`). The map then excludes it.
  - Any other final line holds a non-space character, so its slice is not empty.
- **Fragility.** The second case rests on a `try/except IndexError` that a tidy upstream refactor could replace with a bounds check. The line would then be counted, the count would be short by one, and an unclosed fence would read as closed. `test_an_unclosed_fence_at_the_end_of_a_document_with_no_final_newline_is_read`, case 4, catches exactly this, so that is a good pin.
- **Direction.** `== 2` is exact, so most changes to these numbers read as unclosed and only over-read lines, which fails closed. The one direction that opens the route is the undercount above.
- **Upgrade path.** `ci/requirements-ci.txt:405` and `ci/requirements-release.txt:5` both pin 4.2.0, and `test_ci_hash_pins.py:452-454` refuses a difference (on `develop`). So a lock bump runs these tests on the new version, and `require_parser` fails in CI rather than skipping (`:52-59`).
- **Not read.** The 4.2.0 source is **(unverified)**. `master`'s `fence.py`, through a summarising fetch, shows the same `state.line`, `getLines` and `map` lines and the `IndexError` break. It also shows a `closing_matcher`, which I did not read. Whether the tests pass on both versions is the implementer's report.
- **Finding SEC-T748-07.** The docstring's "Pinned on markdown-it-py 3.0.0 and 4.2.0 by the tests" reads wider than it is: CI only ever runs 4.2.0. A source check on the closing line would remove the reliance on the quirk.

### Q7. Do the docstring and `--help` state the behaviour exactly?

**Mostly yes, with four overclaims, all in SEC-T748-08.**

Accurate: the section start and end rules, `whose text is not empty`, the second heading, the closed-fence list, the one call site and "never parses a long line or the same text twice". The exact fence-closing conditions match the code.

Overclaims:
1. `:275` "so a hidden 'pending' still fails" holds only inside a section. Ruling 3's comment above the section passes.
2. `:277-278` "a section swallowed by an unclosed fence or comment fails" holds only for a line starting exactly `## Gate Verdicts` at column 0. ` ## Gate Verdicts` in an unclosed fence gives 0 problems. It did on the old code too.
3. `:279` "both fail closed" is not true of the optional section. `"- " * 10 + "x\n\nGate Verdicts\n---\n\n- x: pending"` has a setext heading past the limit, so count 0, no raw line and 0 problems.
4. `:8` "a row or field that is still `pending`": a table row with `pending` is not read as a field. This is older than T747. `--help` is also silent on which lines count as fields, so the known `>`, `1.`, `+` residual appears nowhere a user would look.

## 2. Resolved

| Id | Ruling |
|---|---|
| SEC-T739-07 | Closed. See Q1 |

## 3. Findings (owner devops-engineer, proposed; next sprint; tracked as LOW debt)

Line numbers are `scripts/verify-release-docs.py` at `d400b851`.

| Id | Grade | OWASP | Location | Description | Proposed fix |
|---|---|---|---|---|---|
| SEC-T748-01 | SECURITY:LOW | A08 | `:408`, `:423` | **Regression.** A section holding only an empty heading (`## &#32;`, `## <!-- x -->`) passes as not empty, because the heading's source line stays in the body. Old: 1 problem. New: 0. Traced. Related and older: a section with only `<!-- x -->` passes on both | Blank the source lines of empty headings in `section_text`, and add `## &#32;` and `## <!-- x -->` to the empty-section test. See section 4 |
| SEC-T748-02 | SECURITY:LOW | A08 | `:349`, `:370` | A heading whose text is invisible ends the section: `## &#8203;`, U+00AD, U+2060, and `## <span hidden>x</span>` (GitLab sanitizer **(unverified)**). Residual of SEC-T739-07 (b). In the `&#8203;\n---`, ` ## `, `##\t` and `# ` forms it is also weaker than the old check. Traced | Drop `Cf` characters and do not treat a heading holding live HTML as text when deciding the end. Section 4 |
| SEC-T748-03 | SECURITY:LOW | A08 | `:370`; help `:270` | Ruling 1. `Text\n---` under the verdict moves a pending field out of the section. Not necessarily crafted, because a paragraph directly above a `---` separator is a common slip. The field stays visible and the reader may see a heading above it. Same for H1 (plan) | Keep the ruling and track it. Option: a verdict section that ends at a setext or `# ` heading is a problem, which fails closed. Any release document this would newly fail is **(unverified)** until the 34 are re-run. Section 4 |
| SEC-T748-04 | SECURITY:LOW | A08 | `:352-358`, `:601` | Ruling 3 does not extend to non-comment HTML. `<div>\n## RELEASE VERDICT\n- Status: pending\n</div>` above a filled section displays the field and passes. Old: caught. And `<div hidden>`, a blank line, then a real heading gives presence with no visible verdict (sanitizer **(unverified)**). Traced | Count a raw heading line inside a non-comment `html_block` as a second heading. The wrapper case stays documented, as SEC-T739-03's did |
| SEC-T748-05 | SECURITY:LOW | A08 | `:352-358` | Exact matching leaves near-duplicates, which also ends the section at them. (d) passes with `## RELEASE&nbsp;VERDICT`, a trailing `&#8203;` or `## Release Verdict`, which looks like or is close to the real heading. Includes ruling 5: `## Gate verdicts`, `### Gate Verdicts`, `> ## Gate Verdicts`. Same on old. Traced | A heading at any level or depth whose folded text equals a section name, but which is not the real form, is a problem. Section 4 |
| SEC-T748-06 | SECURITY:LOW | A08 | `:146`, `:427`, `:444-447` | Field logic. A visible unfilled value passes in shapes 8-11 of Q2. Same on old. The plan kept this logic, so this needs its own plan. Traced | Widen the marker and the value normalisation, and treat an empty field's sub-items as its value. Section 4. Check the golden contract first |
| SEC-T748-07 | SECURITY:LOW | A08 | `:381`, `:385-387` | Closure rests on the parser's numbers and, for one case, on an `IndexError` break. Pinned behaviourally. The docstring's "Pinned on 3.0.0 and 4.2.0 by the tests" overstates, since CI runs only the locked version | Reword to "tested on the locked version; 3.0.0 checked by hand on `<date>`". Optionally also require the closing line to end with the markup. Section 4 |
| SEC-T748-08 | SECURITY:LOW | A08 | help `:275`, `:277-279`; docstring `:8` | The four overclaims in Q7 | "Inside a section, a hidden 'pending' still fails"; "a `## Gate Verdicts` line at column 0"; limit "both fail closed" to the required section, or say what the optional one does; add one sentence on which lines count as fields and that `>`, `1.`, `+`, plain text and table rows do not. Update `test_the_help_and_the_docstring_describe_this_check` |
| SEC-T748-09 | SECURITY:LOW | A08 | `:590-595` | `## Install` and `## Highlights` are substring checks, so a comment satisfies them. Older than T747 | Use `section_heading_indexes` for them too, after re-running the 34 documents |

## 4. Remediation sketches

Not run. Line references are the same as above.

```python
# SEC-T748-01, in section_text: blank what renders as nothing
code |= {
    number for index, token in enumerate(tokens)
    if token.type == "heading_open" and token.level == 0 and token.tag in ("h1", "h2")
    and not heading_text(tokens, index)
    for number in range(*token.map)
}
# Effect: "## <!-- TBD -->" goes unread, as it did on the old code, where it ended the section.

# SEC-T748-02: what may end a section
def heading_ends_section(tokens: list, index: int) -> bool:
    visible = "".join(c for c in heading_text(tokens, index) if unicodedata.category(c) != "Cf").strip()
    return bool(visible) and not holds_live_html(tokens[index + 1])

# SEC-T748-03: option. Token.markup is "##" for ATX level 2 (lheading sets "-" or "=", from knowledge,
# not read this session), so a section's ending heading can be tested:
if ending_token.markup != "##":
    problems.append(f"{title}: the section ends at a setext or '# ' heading; end it with a '## ' heading")

# SEC-T748-05: near-miss of a section name
def fold(text: str) -> str:
    kept = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return " ".join(kept.split()).casefold()
# any heading_open, at any level or depth, with fold(text) == fold(title) and not one of
# section_heading_indexes(tokens, title) -> "a heading looks like this section but is not it"

# SEC-T748-06
FIELD_RE = re.compile(
    r"^[ \t]*(?:>[ \t]*)*(?:[-*+]|\d{1,9}[.)])[ \t]+"
    r"(?P<label>[^:\n \t](?:[^:\n]*[^:\n \t])?)[ \t]*:[ \t]*(?P<value>.*)$"
)
value = html.unescape(field.group("value")).strip("*_`~()[]\"' \t")

# SEC-T748-07: closed only if the numbers and the source agree; a disagreement reads the lines
return end - first - content_lines == 2 and lines[end - 1].rstrip(" \t").endswith(token.markup)
```

## 5. OWASP and verdict blocks

## Gate Verdict: Security

**Gate:** security
**Executor:** security-engineer
**Date:** 2026-11-06
**Target:** T747 (plan-142) at `d400b851`

### Verdict: CONDITIONAL_PASS

### Findings

SEC-T748-01 to -09, as in section 3. Each has severity `low`, category `security`. The recommendations are the fixes in section 3.

### Conditions

- [ ] SEC-T748-01 to -09 recorded as tracked debt in the next register. Owner: devops-engineer (proposed). Due: next sprint.

### Summary

SEC-T739-07 is closed, and the check is stronger overall. One regression and two narrow weakenings beyond the rulings are LOW, and none blocks the merge.

## VERDICT: CONDITIONAL_PASS

### Findings Summary

| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 9 | 0 | 9 (tracked, section 3) |

SEC-T739-07, the earlier LOW id, is resolved and is not counted in these 9.

### Justification

The token-based finder removes the three shapes and (d), (f), (h), (i), by trace. The remaining routes need a document that survives review with the value visible in the diff, which is the grade the T739 and T745 reviews set.

### Conditions

- SEC-T748-01 to -09: owner=@devops-engineer (proposed), remediation=section 3, deadline=next sprint. The user's policy tracks LOW as debt. SEC-T748-01 and -02 are the two worth taking first, because they are small and -01 is a regression.

### Blockers

None for the verdict.

- `technical`, `minor`: `grep_content` errors on a worktree root, as review T745 noted. I read the worktree by range and used the tool on `develop` as a pointer only.

### OWASP Coverage

| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (nothing in the diff) | 0 |
| A02: Cryptographic Failures | Yes (nothing in the diff) | 0 |
| A03: Injection | Yes (`re.escape` on constants; tokens are never rendered) | 0 |
| A04: Insecure Design | Yes (SEC-T745-01's reach, noted in Q4) | 0 new |
| A05: Security Misconfiguration | Yes (no CI change in the diff) | 0 |
| A06: Vulnerable Components | No (no dependency changed; no audit ran) | 0 |
| A07: Auth Failures | Yes (nothing in the diff) | 0 |
| A08: Data Integrity Failures | Yes | 9 |
| A09: Logging & Monitoring | Yes (new messages hold only constants and counts; `_line_problems` is unchanged) | 0 |
| A10: SSRF | Yes (no URL handling in the diff) | 0 |

## 6. Not verified, and what to run

- **No code was run.** These are the implementer's report: 31 + 11 mutations, the 34 documents on both parser versions, `--tag v9.0.0`, and the test results on 4.2.0.
- **The orchestrator should run these on `d400b851`,** and the old code where the table says the old caught them. Expected values are in Q2:
  - -01: `## RELEASE VERDICT\n\n## &#32;\n`
  - -02: `## RELEASE VERDICT\n\n- Version: 1\n\n&#8203;\n---\n\n- Status: pending\n`
  - -04: `<div>\n## RELEASE VERDICT\n- Status: pending\n</div>\n\n## RELEASE VERDICT\n\n- Status: PASS\n`
  - -05: `## RELEASE VERDICT\n\n- Status: PASS\n\n## RELEASE&nbsp;VERDICT\n\n- Status: pending\n`
  - -06: `## RELEASE VERDICT\n\n- Status:\n  - pending\n` and `## RELEASE VERDICT\n\n- Status: _pending_\n`
  - The Q7 shape past the nesting limit.
- **Parser source read:** `markdown_it` 3.0.0 `fence.py` in full, and `state_block.py` lines 30-139 and 214-249 (`__init__`, `push`, `getLines`, cut off at its last assignment). Not read: `heading.py`, `lheading.py`, `html_block.py`, `blockquote.py` (from knowledge, and blockquote traces rest on that). 4.2.0 **(unverified)**, `master`'s `fence.py` only through a summarising fetch.
- **GitLab (unverified):** its rendering of these shapes, whether the sanitizer keeps `hidden` or the zero-width entities, and whether a `<div>` block's text displays as CommonMark says.
- **Callers:** that `verdict_placeholder_problems` and `section_text` have no callers outside the script and its test comes from a search of `develop`, not of `d400b851`. The diff adds none.
- **Tests:** I read the diff and lines 1-60 of the test file, not the whole file. No test was run. `tests/golden/` was not opened.

## 7. Task completion

- **Artifacts:** this report, as text, for you to commit as `docs/artifacts/security-review-t748-batch-t-v1.md`. Nothing was written or modified.
- **Acceptance:** all seven questions answered with evidence, each finding has id, grade, location, description and fix, and each route is marked traced or suspected.
- **Follow-up for register v11:**
  - SEC-T739-07 is closed.
  - SEC-T748-01 to -09 are added.
  - SEC-T745-01 gets the note on the own document.
  - Plan-142's line "Nothing the old check caught may start to pass, other than the two listed" no longer holds as written. Rulings 1-3 and SEC-T748-01, -02, -04 add to it, so its outcome section should say so.

## 8. Orchestrator's record of the rounds after this report

Everything above this section is the reviewer's first report, on `d400b851`. The orchestrator then fixed SEC-T748-01, -02 and -04 itself (`3cb4f739`), the reviewer re-read that fix and found two regressions in it (SEC-T748-10, -11), and the orchestrator fixed those (`99bfa0bc`) and asked for one last read. Sections 9 and 10 are the reviewer's words. The orchestrator wrote the code of both fixes, so these two reads are its only independent check.

The orchestrator ran SEC-T748-13 on `99bfa0bc`: `## <span hidden>RELEASE VERDICT</span>` followed by `- Status: PASS` counts as present with 0 problems, and the old substring check is false on it. Confirmed, and tracked.

## 9. Narrow re-read of the first fix

**Short answer: the three shapes you ran are closed, but your reasoning in Q2 holds only for one form, and the fix opens two new regressions.** Both new ones come from `section_text` using one blanking set for the field scan and the emptiness test, so one change fixes both. All of this is hand traces. I ran nothing, and I read the tree's `:364-398` plus 3.0.0's `lheading.py` and `html_block.py`. 4.2.0 is **(unverified)**.

Your counts agree with my traces: -01 1/1, -02 1/1, -04 1/1, `Text\n---` 1/0. For -04 the new "1" is the HTML-block problem, not the pending field, which is correct. The zero-difference run shows real documents are unaffected. It says nothing about these shapes, because no release document holds them.

### Q1. Are -01, -02 and -04 closed?

| Id | Status | Evidence | What stays open |
|---|---|---|---|
| SEC-T748-01 | **Closed for the reported shapes**; the fix adds SEC-T748-11 | `## &#32;` and `## <!-- x -->` are not visible, so their lines are blanked and the body is empty, giving the EMPTY problem | Older, on both versions: a section holding only `<!-- x -->`, a `&#8203;` paragraph, or `### &#32;` passes as non-empty |
| SEC-T748-02 | **Closed for format characters and live HTML in the heading** | `&#8203;\n---`, ` ## &#8203;`, `##\t&#8203;`, `# &#8203;`, `&shy;`, `&#x2060;` and `<span hidden>` no longer end the section | Non-`Cf` invisibles and a wrapper around a visible heading: new row SEC-T748-12 |
| SEC-T748-04 | **Closed for the regression in displayed HTML** | Old matched a raw line exactly after `rstrip`; `html_block_holds_line` compares the same way, on every non-comment block, including `<?`, `<![CDATA[`, `<pre>` and a `--!>` comment | See below |

**What stays open under SEC-T748-04:**
- `<div hidden>`, a blank line and a real filled heading: presence passes and no verdict is visible. GitLab's sanitizer is **(unverified)**. This stays open under -04 and needs tag balancing, as SEC-T739-03 did.
- `~~~\n## RELEASE VERDICT\n- Status: pending\n~~~` above a filled section: old caught it, new passes. It displays as code, so ruling 2's logic applies.
- A multi-line reference definition title holding the same lines: old caught it, new passes. It is hidden, so ruling 3's logic applies.
- Both of those last two are remaining differences from `679e6adc`, so your plan outcome should list them.

### Q2. Does blanking let a marker hide?

**Yes. Your reasoning holds only for a heading starting `## ` at column 0.** `## <span>TBD</span>` was ended on by the old rule (`startswith("## ")`), so the line went unread, and the new code reads more after it. Every other form was **read** by the old code, because the old rule did not end the section there:

| Shape in the section | `679e6adc` | Now |
|---|---|---|
| `# <span>TBD</span>` | caught | **passes** |
| `<span>TBD</span>\n---` | caught | **passes** |
| ` ## <span>TBD</span>`, `##\t<span>TBD</span>` | caught | **passes** |
| `# <b>YYYY-MM-DD</b>` | caught | **passes** |
| `# <!-- TBD -->`, ` ## <!-- TBD -->` | caught | **passes** |
| `# ![TBD](u)` | caught | **passes** |
| `<b>Note</b>\n    - Status: pending\n---` | caught | **passes** |

- In the first rows the placeholder is visible in a heading.
- The last row is a real field line. A line indented 4 or more spaces continues the paragraph (`lheading.py:27-29`), so it sits inside the setext heading's `map` and gets blanked. `<b>Note</b>` is not an HTML block, because the type 7 pattern needs the tag alone on its line. FIELD_RE matches the line, so the old code caught it. The reader sees the text in the heading.
- This also contradicts `--help` ("so are HTML lines, so a hidden 'pending' still fails") and the `section_text` docstring ("Nothing else is skipped").
- No new test puts a marker on a blanked line, so your 8 mutations would not show this **(inferred from the diff; I did not see the mutation list)**.

### Q3. New routes or weakening?

- **`heading_is_visible`: yes, SEC-T748-11 and SEC-T748-12.** Its live-HTML clause makes a heading that a reader can see not end the section. For field scanning that fails closed. For the emptiness test it fails open: `## RELEASE VERDICT\n\n## <a name="x"></a>Rollback Plan\n\nSome text\n` has an empty verdict, the rollback prose counts as its content, and it gives 0 problems. Both `679e6adc` and `d400b851` reported it as empty. An anchor in a heading is a realistic form, so this one is not only crafted.
- **`html_block_holds_line`: nothing new.** It only adds a problem, so a false match is a false FAIL. `<div>\n<!--\n## RELEASE VERDICT\n-->\n</div>` above a filled section is one, and that is acceptable. ` ## RELEASE VERDICT` in a block is not matched, but the old code did not match it either.
- **`count and`: nothing new.** With count 0, `RELEASE VERDICT` already fails as absent, and `Gate Verdicts` fails through the raw `^## ` regex. A raw line in an HTML block inside a blockquote or list has count 0 and passes, as it did on the old code (the line starts with `>` or spaces).
- **Wording, in SEC-T748-08's scope:** the help says "one holding only format characters such as U+200B, or HTML other than comments", but the code applies to any heading that *contains* live HTML, such as `## Next <b>x</b>`. Fix the sentence along with SEC-T748-10.

### New findings

| Id | Grade | Location | Description | Fix |
|---|---|---|---|---|
| SEC-T748-10 | SECURITY:LOW | `section_text`, the `blank` set; `:376` | **Regression from the fix.** Blanking the lines of a heading that does not end the section hides markers and fields that `679e6adc` read, in every form except `## ` at column 0 (Q2 table) | Keep these lines for the field scan and exclude them only from the emptiness test. Sketch below. Add each Q2 shape as a test, and a mutation |
| SEC-T748-11 | SECURITY:LOW | `heading_is_visible` `:376`; `verdict_placeholder_problems`, the emptiness test | **Regression from the fix.** A visible heading holding live HTML does not end the section, so what follows counts as the verdict's content. An empty verdict passes (Q3) | Test emptiness up to the next top heading that has text, ignoring its HTML. The field scan keeps the longer, fail-closed span. A hidden heading followed by a filled field would then be a false FAIL, which is acceptable. Sketch below |
| SEC-T748-12 | SECURITY:LOW | `heading_is_visible` `:375` | **Residual of -02.** Characters outside `Cf` that render as nothing still count as text: U+2800 (So), U+3164, U+FFA0, U+115F, U+1160 (Lo), U+034F and variation selectors (Mn). `&#x2800;\n---\n\n- Status: pending`: old caught, new passes. Category values are from knowledge, and rendering depends on the font **(unverified)**. Separately, `<div hidden>`, a blank line, `Next\n---`, a blank line, `</div>`, then the field: the heading has no HTML of its own, so it ends the section. Old caught this too; sanitizer **(unverified)** | Replace the `Cf` filter with an allowlist: a heading is visible only if some character is alphanumeric and not a known filler; a heading of punctuation alone then fails closed. Leave the wrapper case documented with -04 |

```python
FILLERS = {"\u115f", "\u1160", "\u3164", "\uffa0"}

def heading_has_text(tokens, index):            # SEC-T748-12
    return any(c.isalnum() and c not in FILLERS for c in heading_text(tokens, index))

def heading_is_visible(tokens, index):
    return heading_has_text(tokens, index) and not holds_live_html(tokens[index + 1])

# section_text: blank closed fences only, so every marker and field line is read (SEC-T748-10).

# SEC-T748-01, -11: a separate emptiness test
def section_is_empty(tokens, lines, start):
    first = tokens[start].map[1]
    end = next((tokens[i].map[0] for i in range(start + 1, len(tokens))
                if is_top_heading(tokens[i]) and heading_has_text(tokens, i)), len(lines))
    skip = {n for i, t in enumerate(tokens)
            if is_closed_backtick_fence(t) or (is_top_heading(t) and not heading_has_text(tokens, i))
            for n in range(*t.map)}
    return not any(lines[n].strip() for n in range(first, end) if n not in skip)
```

Sketch only, not run. The caller still handles the raw-line case when count is 0. `## <span hidden>x</span>` on its own stays EMPTY under this, as your test expects.

### Updated verdict: CONDITIONAL_PASS

- 0 CRITICAL, 0 HIGH, 0 MEDIUM. No Immutable Security Constraint breach, and I do not read this check as a control that `security-guidelines.md` requires.
- **LOW:** SEC-T748-03, -05, -06, -07, -08, -09, -10, -11, -12 remain, with the -01 and -02 residuals and the -04 wrapper noted above. -01 and -02 are closed for their reported shapes and -04 for its displayed-HTML regression.
- The gate rules do not block the merge on these. **My recommendation is to fix -10 and -11 before merging anyway**, on your own standard: you fixed the first three because they were regressions against the plan's rule, and these two are the same kind, from the fix itself. One change closes both. -12 can be tracked.
- If you do change it, a short re-read of that diff is enough. Since you wrote the fix, I would not merge it on the current evidence alone until the Q2 and Q3 shapes have been run on both parser versions.

Blockers: none.

## 10. Last read of the second fix

**SEC-T748-10 and -11 are closed, and CONDITIONAL_PASS stands, with nothing above LOW.** These are hand traces of the diff. I ran nothing. The diff is script-only, so the new test you mention is **(unverified)**. Your 3.0.0 and 4.2.0 results are your report, and they match my traces on every shape below.

### 1. -10 and -11: closed

- **SEC-T748-10: closed.** `section_text` now blanks closed ``` fences only, so every heading line reaches `_line_problems`.
  - All your Q2 rows are read: each is a top-level heading that does not end the scan, or its line is in the span. `# <span>TBD</span>`, `<span>TBD</span>\n---`, ` ## ` and `##\t` forms, `# <b>YYYY-MM-DD</b>`, `# <!-- TBD -->` and `# ![TBD](u)` all hit a marker.
  - `<b>Note</b>\n    - Status: pending\n---` hits the field rule, because live HTML keeps the heading from ending the scan.
- **SEC-T748-11: closed.** `section_is_empty` ends at the next top heading with text, ignoring its HTML. The anchor shape has nothing before `## <a name="x"></a>Rollback Plan`, so it is empty and gives 1 problem.
- **-01 stays closed under the split.** `## &#32;` and `## <!-- x -->` have no text, so their lines are skipped and the section is empty. `## <span hidden>x</span>` has text, so it ends the emptiness span, also empty.
- **The no-real-heading branch is unchanged.** With `starts` empty, the raw `^## ` search gives the old result.
- **The split can only add failures on these paths.** A hidden heading followed by a filled field, `## <span hidden>x</span>\n\n- Status: PASS`, reports EMPTY, as the old code did. `Text\n---` directly under the heading, with nothing above it, now also reports EMPTY, where the old code gave 0 if the rest was filled. Your 1/0 for ruling 1 still holds when a field sits above the heading.
- **Wording:** the help sentence I flagged last round ("holding only ... HTML") is fixed, and "Such a heading's own line is still read" matches the code.

### 2. New regressions

**None from this diff.**

Re-checking against `679e6adc`, I found one I missed in my Q5 answer. It comes from the first commit, not this diff: my first report called the presence rule "stronger than the old substring" and did not name this exception.

| Id | Grade | Location | Description | Fix |
|---|---|---|---|---|
| SEC-T748-13 | SECURITY:LOW | `section_heading_indexes`, used for presence in `check_release_brief` | `inline_text` reads the text between inline tags, so `## <span hidden>RELEASE VERDICT</span>\n\n- Status: PASS` counts as a real heading. Old: fails the literal substring check. New: 0 errors. The heading may be hidden while the fields stay visible, and the sanitizer is **(unverified)**. It also pairs with -05: a hidden real heading, then a visible `## Release Verdict` with a pending field, passes. Traced, not run | For presence, also require `not holds_live_html(tokens[index + 1])` |

**Two count differences from `679e6adc` that I do not make findings.** Neither comes from this diff, but both belong in plan-142's outcome, because the plan says nothing else may start to pass:
- `## RELEASE VERDICT\n\n## &#32;\n\nprose` goes 1/0. The plan says an empty heading does not end a section, the prose is visibly under the verdict, and free text already passes as content.
- `## RELEASE VERDICT\n\n``` x ```\n` goes 1/0. This is the mispairing class from ruling 2: the line is inline code that a reader sees.

### 3. Final verdict: CONDITIONAL_PASS

The grades use the same criteria as before. The no-more-rounds policy did not change any of them. There is no Immutable Security Constraint breach, and I do not read this check as a control that `security-guidelines.md` requires.

| Severity | Count | Resolved | Remaining |
|---|---:|---:|---:|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 13 | 4 | 9 (tracked) |

SEC-T739-07 is closed and is not counted in these 13.

- **Resolved (4):** SEC-T748-01, -02, -10, -11. The residuals of -01 and -02 move to the rows below.
- **Tracked (9), owner devops-engineer (proposed), next sprint:**
  - **-03:** ruling 1.
  - **-04:** open in part. The displayed-HTML regression is closed. Still open are `<div hidden>`, a blank line and a real heading, plus `~~~` and reference-title quoting above the section, which still differ from `679e6adc`.
  - **-05:** near-duplicate headings and ruling 5.
  - **-06:** field logic. Add here the older -01 residual: a section holding only `<!-- x -->`, a `&#8203;` paragraph or `### &#32;` passes as non-empty.
  - **-07:** closure rests on parser numbers, and the "pinned on 3.0.0 and 4.2.0" wording.
  - **-08:** the four help and docstring overclaims.
  - **-09:** `## Install` and `## Highlights` are substring checks.
  - **-12:** non-`Cf` invisible characters such as U+2800 and U+3164, and a visible heading inside a hidden wrapper. Your choice to keep the `Cf` test leaves this as it was.
  - **-13:** above.
- **Register notes:** SEC-T745-01 gets the note that the own document is now always parsed, and TD-T739-01 stays open in part.

Blockers: none.
