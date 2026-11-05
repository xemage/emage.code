# Artifact: security-review-t738-batch-n-two-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer, read-only, with no shell. The orchestrator recorded this artifact from the reviewer's report.
- **Gate**: security. **Date**: 2026-11-05.
- **Target**: T738 (plan-135) on `agent/devops-engineer/T738` at `921c08715067aee6e375d52bcccb74f4721865fc`, from an exported diff and the worktree files.
- **Based on**:
  - `docs/plans/plan-135-batch-n-two-gate-fixes.md`
  - `docs/artifacts/security-review-t730-t732-batch-g-v1.md` § 1 and § 4
  - `scripts/verify-release-docs.py`, `tests/functional/test_verify_release_docs.py`
- **Search tool**: `grep_content` fails on worktree paths, so the reviewer's searches reflect `develop` and were combined with Read. No read was refused.
- **Orchestrator's checks**, with `markdown-it-py` 3.0.0 (commonmark preset), gate result against what renders:

  | Shape | Old gate | New gate | Renders the anchor |
  |---|---|---|---|
  | Review § 4 (a), `<!-->` and `<?>` | True | False | no |
  | A real anchor after `<!-->` and after `<?>` | False | True | yes |
  | A spanning comment | False | False | no |
  | An end on the start line; a plain anchor | True | True | yes |
  | Residual (b), the fence form | True | True | no |
  | SEC-T738-01, the fence and `<?` forms | True | True | no |
  | SEC-T738-03, `x <!-->` and a heading | False | False | yes |

  On the new gate only, two routes the reviewer traced by hand:
  - **The wrong-section route (SEC-T738-03), with `x <!-->` and with `x <!--`:** the gate counts the anchor, and it renders under `## Other`. Confirmed.
  - **The non-fence form of (b) (SEC-T738-05):** the gate counts the anchor, and it does not render. Confirmed.
  - **`<pre/>` (SEC-T738-01's spec-only variant):** this parser treats it as the gate does. The anchor renders and the gate counts it. The spec text and other parsers are **(unverified)**.

## Verdict: CONDITIONAL_PASS; its one condition is met by this record

- 0 CRITICAL, 0 HIGH, 0 MEDIUM.
- No breach of an Immutable Security Constraint. The gate is not a control that `security-guidelines.md` requires, and T738 only tightens it.
- Nothing blocks the merge. The only condition is that the LOW findings be tracked as debt. Section 4 is that record; the next register version takes them over.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 9 | 3 | 6 (tracked, section 4) |

The nine are SEC-T731-07, SEC-T731-09(a), SEC-T731-09(b) and SEC-T738-01 to -06. The reviewer counted 2 resolved. SEC-T738-05 was applied after the review, with the reviewer's own wording, and was not re-reviewed (section 2).

**Why LOW.** Every route needs a crafted file, committed by someone with write access, that survives merge request review, and that person could equally remove the pointer or the word `Cursor`. The consequence is a release document without a visible migration item. It does not touch code execution, secrets or access.

## 1. Rulings

- **SEC-T731-07 is closed.**
  - Both paths through `main()` exit 1 on a crafted `install.sh`. A split pointer passes `check_migration_pointers` and is then refused. If that check errors for another reason, the gate returns at once and reports the separator only on a later run.
  - Both checks decode the file the same way. The eight characters equal the `str.splitlines()` list without `\n` and `\r`.
  - The error text is accurate and prints only the path, the line and `U+XXXX`.
  - "Neither Markdown nor a shell" is not an overclaim. It rests on POSIX and bash, from knowledge; the implementer ran bash only. GitLab's renderer is **(unverified)**.
- **SEC-T731-09(a) is closed.** The reviewer checked each rule against CommonMark 0.31.2 § 4.6. Behaviour changes only for start lines beginning `<!-->`, `<!--->` or `<?>`, and there the gate now agrees with CommonMark. The fix opens no new class of false PASS.
- **SEC-T731-09 as a whole stays open as SEC-T731-09(b).** T738 delivers the review's "document the residual" alternative, so the status is "documented, not fixed". It closes only with a parser or a fail-closed rule.
- **`test_the_known_false_passes_named_in_the_docstrings` is acceptable** as a characterisation test: its docstring says the behaviour is not wanted, and a real fix flips the asserts. The plan did not ask for it, and the implementer disclosed it.
- **Test quality (read, not run).** Removing either fix makes a guarding test fail.
- **The plan's wording.** "Each new test fails on the old code" applies to the tests that guard a fix. Four tests are controls or characterisation and pass on the old code by design. Two fail on the old code for an incidental reason: return type and error wording.

## 2. Resolved findings

| Id | Finding | Fix | Evidence |
|---|---|---|---|
| SEC-T731-07 | `install.sh` was outside the line-separator refusal | `31aae510` | `verify-release-docs.py`, the `check_line_breaks` call in `main()` |
| SEC-T731-09(a) | The end pattern was searched from the end of the start match | `c781c16f` | `html_block_opening`, `strip_hidden_markdown` |
| SEC-T738-05 | The new docstrings said "It is a false PASS when" and "so both remain", which read as sufficient and complete. Residual (b) is wider than fences, because the gate has no model of list containers | The reviewer's wording, applied by the orchestrator after the review | `html_block_opening`, `has_cursor_migration_item` |

## 3. OWASP coverage

| Category | Findings (open) |
|---|---|
| A08 Data Integrity (release gate) | SEC-T731-09(b), SEC-T738-01, -02, -03, -04, -06 |
| A01 to A07, A09, A10 | 0. No new regex and no dependency; the error reports only the code point |

## 4. Findings tracked as LOW debt (owner devops-engineer; next sprint)

All six are older than T738.

| Id | Location | Finding | Fix (reviewer) |
|---|---|---|---|
| SEC-T731-09(b) | `verify-release-docs.py`, `has_cursor_migration_item` docstring | Documented, not fixed. The gate has no model of list containers, so it can pair fences or close a comment where CommonMark does not, and a crafted document can hide an anchor that the gate counts. | A parser or a fail-closed rule. |
| SEC-T738-01 | `verify-release-docs.py:488-489` | A wrongly opened type 7 block hides a fence or `<?` line that CommonMark keeps live, so a hidden anchor counts. | Parse under both hypotheses (type 7 after a text line, and not), and count an anchor only if it survives both. Flip the assert in the characterisation test, and add the `<?` shape. |
| SEC-T738-02 | `verify-release-docs.py:437, 564` | `read_text` translates a CR in `install.sh` to a newline, so the line splits and the Cursor requirement drops, though bash does not end a line there. Adding CR to `NON_COMMONMARK_BREAK_RE` would do nothing, and would wrongly refuse CRLF Markdown. A plain newline has the same effect, by design: `install.sh:1295-1297` relies on the per-line rule. | Refuse CR in `install.sh` from the raw bytes. Add one sentence to `MIGRATION_POINTER_HELP`: the rule catches an omission on one line and does not defend against a crafted script. |
| SEC-T738-03 | `verify-release-docs.py:155`, and the claim at `:501` | `HTML_COMMENT_RE` does not close an inline `<!-->` or `<!--->`, and it crosses blank lines. The result is a false FAIL, and a false PASS for a visible anchor in the wrong section, as in SEC-T731-08. | Close the short forms and stop a span at a blank line, with fixtures for `x <!-->`, `x <!--->`, the section route, and comments in list items and blockquotes. Whether a test expects today's behaviour is **(unverified)**. Track it next to SEC-T731-08: a fix to the section end alone does not cover this route. |
| SEC-T738-04 | `verify-release-docs.py:153, 218-220, 501` | Three older claims contradict the corrected docstrings: "the anchor counts only where a reader sees it"; `--help` says such anchors "are ignored"; an unclosed comment hides the rest "as a Markdown renderer does". A reader of `--help` trusts a guarantee that SEC-T731-09(b) and SEC-T738-01 disprove. | Reword all three. `--help` adds: the gate has no Markdown parser, and a crafted document can still hide an anchor that it counts. |
| SEC-T738-06 | `tests/functional/test_verify_release_docs.py`, `LineBreakCharacterTests.CHARS` | The tuple holds raw U+2028 and U+2029, which render as spaces. | Use the ` ` and ` ` escapes. |

**The reviewer's order.** First SEC-T738-02, -04 and -06. Then SEC-T738-01 and -03 together with SEC-T731-08. Using `markdown-it-py` in the gate would close that whole class at the cost of a gate dependency, and that decision is the user's.

## 5. Not verified by the reviewer

- No code was run: the mutation behaviour and the shapes are hand traces, or rest on the orchestrator's runs above. The orchestrator ran the suite and gates before the merge.
- The worktree's HEAD against `921c0871`. The script's changed lines match the diff, and the test file was read only in part.
- CommonMark § 6.6, which the fetch did not return, so the inline-comment reading rests on the orchestrator's parser run.
- GitLab's real rendering of these shapes, and bash's behaviour on the eight characters and CR (knowledge, not a run).
- Uses of the old error text and of `html_block_opening` outside `scripts/`. The orchestrator's search, excluding the held-out set, finds the old error text only in plan-135.
