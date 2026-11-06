# plan-142 — The verdict check reads the parser's tokens (batch T)

**Created:** 2026-11-06
**Based on:** `docs/artifacts/tracked-debt-register-v10.md` § 5 (batch T), `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4 (SEC-T739-07), `docs/plans/plan-136-release-gate-markdown-parser.md`, `docs/artifacts/security-review-t745-batch-s-v1.md`. The user's answer of 2026-11-06, verbatim: "T go".
**Scopes:** `T747`, `T748`.

## Goal

The release gate's placeholder check fails a release document whose verdict is still unfilled. It finds the sections with line rules, so crafted or accidental layouts pass with `- Status: pending` in place. The Cursor check moved to `markdown-it-py` in plan-136. This plan moves the verdict check's section finding to the same tokens and keeps its field logic.

## What the orchestrator ran on `06b903aa`

`verify-release-docs.py` on small documents, each with `- Status: pending` in the verdict section unless stated. Nothing was written.

| Shape | Problems today | Should be |
|---|---:|---|
| Control: heading, pending field | 1 | fails |
| (a) The heading first inside a comment, then the real one (SEC-T739-07) | 0 | fails |
| (b) A comment holding a `## x` line between the heading and the field (SEC-T739-07) | 0 | fails |
| (d) A filled real heading, then a second real heading with the pending field | 0 | refused |
| (f) The heading and its filled field only inside a comment, no real heading | 0 | fails: no `RELEASE VERDICT` section |
| (h) A setext `RELEASE VERDICT` heading with a pending field | 0 problems; the separate presence check fails it | fails, on the placeholder |
| (i) The heading only inside a blockquote | 0 | fails: no `RELEASE VERDICT` section |

Shape (c), two ` ``` ` in a paragraph pairing up around the field (SEC-T739-07), was confirmed by review T739. **The orchestrator's own attempt, with the two ` ``` ` outside the section, reported 1 problem, so it did not reproduce the shape.** T747 writes the test from the review's wording and confirms that it passes on the old code before fixing it.

(d), (f) and (i) are not in the review's finding. They are the same class and this plan covers them.

## Design

- **One parse.** A helper such as `markdown_tokens(text)` becomes the only call of `MarkdownIt`, used by `has_cursor_migration_item` and by the new section finder. It caches the last text, so the document is not parsed twice and SEC-T745-01's worst case does not double. A long line stays unparsed: the guard moves into or stays in front of the helper. `test_the_parser_has_one_call_site` changes with it, in the open, and keeps its purpose.
- **Section finding.** A section starts at the first top-level level 2 heading whose text is exactly the section's name, ATX or setext, as `migration_section_span` reads it. It ends at the next top-level level 1 or 2 heading whose text is not empty.
- **An empty heading does not end a section.** A heading such as `## &#32;` or `## <!-- x -->` renders as nothing. Text here is what the Cursor check calls text: text and inline code.
- **A second top-level heading with the same name is a problem.** The message names the section.
- **The field logic does not change.** `_line_problems` and the `nested_follows` rule still read the section's source lines, taken from the tokens' `map`. Lines are split on `\n` only, so that they line up with the parser's numbering.
- **What is skipped.** Only the lines of `fence` and `code_block` tokens, at any depth, as fenced code is skipped today (`test_placeholders_in_a_fenced_block_or_another_section_do_not_count`). HTML lines stay scanned: a hidden `pending` still fails, as it does today. Nothing the old check caught may start to pass, other than the two listed below.
- **Presence.** `RELEASE VERDICT` must be a real top-level heading, in place of the `"## RELEASE VERDICT" in brief_text` substring. `Gate Verdicts` stays optional. A raw `## Gate Verdicts` line with no real heading stays a problem, as the "heading is present" message has it today, so a section swallowed by an unclosed fence or comment fails closed.
- **The parser's nesting limit.** Blocks past the limit produce no tokens. So a section with no later heading token runs to the end of the document, and a heading past the limit is absent. Both fail closed. T747 tests this.
- **`strip_code` and `FENCED_CODE_RE` stay** for `check_links`. Moving link checks is not in this plan.

**Two things the old check caught that may stop counting, on purpose:** text after a top-level level 1 heading, now outside the section as in the Cursor check; and a `## x` line that is really inside a code block or a comment, which no longer ends the section at all. T747 lists any other change it finds.

## Task Decomposition

1. **T747** (devops-engineer): the change above, in `scripts/verify-release-docs.py` and `tests/functional/test_verify_release_docs.py`, plus the docstring and `--help` wherever they describe this check or say which check uses the parser.
   - *Acceptance:*
     - each shape in the table has a test, and (a), (b), (c), (d), (f) and (i) each fail on the old code and pass on the new, shown by a throwaway run on a copy;
     - shape (c) is written from the review's wording;
     - also tested: an empty heading does not end a section; a field in a fence inside a list or a blockquote is skipped; a heading past the nesting limit is absent; a document with `\f` or U+2028 reached directly by the function keeps its lines aligned, or the function refuses it;
     - the document is parsed once per run of the gate, and a test says so;
     - a mutation of each new rule is caught: on a throwaway copy under the session's scratchpad, excluding `tests/golden`, with each run under `subprocess.run(..., timeout=120, preexec_fn=...)` and `RLIMIT_AS` of 3 GiB, one at a time, stopping below 3 GB available. A timeout counts as caught. Never in a worktree. List the mutations and results;
     - `python3 scripts/verify-release-docs.py --tag v9.0.0` passes. Every `docs/releases/v*.md` is run through the old and the new `verdict_placeholder_problems`, and any difference is listed with its reason;
     - `tests/functional/test_verify_release_docs.py`, `test_ci_hash_pins.py`, `test_link_integrity` and `validate-tasks.py` pass. No full suite.
2. **T748** (security-engineer): review T747's diff, read-only. Write `docs/artifacts/security-review-t748-batch-t-v1.md` as text in the report, because the agent has no shell or write tool for the repository beyond what it lists; the orchestrator commits it.
   - *Questions:* is SEC-T739-07 closed; which route still lets a visible unfilled verdict pass; does any check get weaker; does the shared helper open a route round the long line guard; is the `RELEASE VERDICT` presence rule sound. Grade each finding `SECURITY:*`.

## Not changed

- `.gitlab-ci.yml`, `ci/`, and the field-level contract, which the golden suite encodes.
- `tests/golden/**` and `scripts/scorecard.py` are protected and out of scope.
- `check_links`, batch S and the flaky test TD-T746-01.
- `implementation/knowledge/`, so no root refresh is expected.
- A misspelt optional heading: `## Gate verdicts` with a pending field still passes, because the section is optional and the name is exact. It is visible to a reader. T748 may grade it.

## Constraints

- Plan-136 kept this check on line rules on purpose, to stay inside "parser go". The user's "T go" and register v10's note on batch T cover the wider use of the parser.
- Functions of at most 50 lines and 4 parameters. Conventional Commits. Never open `tests/golden/held-out/`; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file.
- Subagents never merge, push, tag or release. The orchestrator verifies and merges on a green pipeline.

## Not verifiable before the next tag

The real job has run the docs gate once, in the gate probe (plan-141), on a copy of the v9.0.0 document. It has not run this code. The local parser is 3.0.0 and the lock holds 4.2.0, so T747 runs the new tests on the locked version too, in a virtual environment under the scratchpad.

## Outcome (2026-11-06)

- **Done: T747 and T748.** SEC-T739-07 is closed. The verdict check finds its sections from `markdown-it-py` tokens, and the field logic is unchanged. `9b79c192` and `d400b851` are the DevOps Engineer's; `3cb4f739` and `99bfa0bc` are the orchestrator's.
- **The design in this plan was wrong in one place.** Skipping every `fence` and `code_block` token let a `~~~` fence, an unclosed fence and indented code pass, against this plan's own sentence "Nothing the old check caught may start to pass". The orchestrator confirmed those shapes on `9b79c192` and ruled that only closed ``` fences are skipped. The implementer's closure test uses the parser's `map` and `content`, not the last-line rule the orchestrator suggested, which called two unclosed shapes closed.
- **The orchestrator's first fix was wrong too.** `3cb4f739` blanked the lines of a heading that does not end a section, on the reasoning that the old check did not read them. That holds only for `## ` at column 0. Its tests put no marker on such a line, so its 8 mutations could not show it. The reviewer found it (SEC-T748-10, -11). `99bfa0bc` reads every line but closed fences and gives emptiness its own span.
- **An invalid run, redone.** The first run of those 8 mutations had a failing baseline on a thin copy, so its "caught" meant nothing. It was redone on a full copy with a clean baseline.
- **Review:** CONDITIONAL_PASS, `docs/artifacts/security-review-t748-batch-t-v1.md`; 0 CRITICAL, 0 HIGH, 0 MEDIUM; 13 LOW, 4 resolved (SEC-T748-01, -02, -10, -11), 9 tracked until the next register: SEC-T748-03, -04 in part, -05, -06, -07, -08, -09, -12, -13. The condition is that they are tracked, which the record does. The orchestrator stopped fix rounds here under the user's LOW policy, and told the reviewer so before its last read. The reviewer states that this changed no grade.
- **What the old check caught that now passes.** This plan's list of two is not the whole list. In full:
  - text after a top-level level 1 heading, and a real heading of any other form ending the section, such as `Text\n---`, ` ## Next` and `##\tNext` (ruling 1, SEC-T748-03);
  - a heading made of characters outside `Cf` that render as nothing, such as U+2800 (SEC-T748-12);
  - a field really inside a closed fence that the old regex mispaired (ruling 2);
  - a comment holding the heading and a pending field above a filled real section (ruling 3), and the same in a `~~~` fence or a reference title (under SEC-T748-04);
  - `## RELEASE VERDICT` followed by `## &#32;` and prose, and followed by a line of inline code in ``` marks (the reviewer's section 10; no finding).
- **What now fails that passed.** A marker on any heading that does not end the section, a real second heading, the heading only in a comment or a blockquote, a closing line with trailing text, a too-short closing fence, and an empty section whose next heading holds HTML.
- **Verified.**
  - Old and new agree on all files in `docs/releases/`, on parser 3.0.0 and the locked 4.2.0, in problems and in presence.
  - 42 mutations by the implementer and 10 by the orchestrator were caught, on throwaway copies with a timeout and a memory cap. The implementer's first-round mutations ran before the two fixes and were not repeated. One orchestrator mutant survived and is now pinned by a test.
  - `test_verify_release_docs.py` passes on both parser versions. The orchestrator's results for the gates and the full suite are in the merge request.
- **Not verified.** GitLab's rendering of these shapes and its sanitizer. The real `release-docs-gate` job has not run this code: the gate probe ran the code before this plan. The reviewer ran nothing and hand-traced all of it.
- **For the next register:** SEC-T739-07 closed; SEC-T748-01 to -13; SEC-T745-01's note that the tag's own document is now always parsed; TD-T746-01; A-19 if the tag is gone; and a release checklist item: a verdict section may hold a second heading of its name in neither a real heading nor displayed HTML.
- **Open for the user.** Batch S before the next tag, the route of SEC-T735-06 and -07, A-19.
- **Token use (the harness's count, which includes context).** T747 about 173k against 120k, plus its resume; T748 about 196k against 120k, across three reads.
