# plan-136 — A Markdown parser in the release gate

**Created:** 2026-11-05
**Based on:**
- `docs/artifacts/security-review-t738-batch-n-two-v1.md` § 4 and its closing paragraph ("The reviewer's order").
- `docs/artifacts/security-review-t730-t732-batch-g-v1.md` § 4 (SEC-T731-08).
- `docs/plans/plan-135-batch-n-two-gate-fixes.md` § Outcome.
- The user's answer of 2026-11-05, verbatim: "parser go". The question was whether the release gate should use `markdown-it-py`, which would close the false-pass group at the cost of a gate dependency.

**Scopes:** `T739`.

## Goal

The gate decides with hand-written line rules whether a release document has a visible Cursor migration item. Each round found another shape that fools those rules. Parse the document instead, so the gate reads the same blocks a CommonMark renderer does.

This closes SEC-T731-09(b), SEC-T738-01, SEC-T738-03 and SEC-T731-08. It also makes the claims of SEC-T738-04 true or removes them. The reviewer's fixes for the first two (parse under both hypotheses; correct the regex) are replaced by this plan.

## Design

- **Scope of the parser.** Only `has_cursor_migration_item`. `section_text`, `verdict_placeholder_problems`, `has_marker`, the link checks and the pointer rules of `install.sh` keep their logic.
- **The parser.** `MarkdownIt("commonmark")` from `markdown-it-py`, read through its token stream.
- **Fail closed.** `main()` checks for the parser first, on every run, so a job without it fails whether or not a Cursor pointer exists. A missing parser prints one clear error that names the install command, and exits 1 without a traceback. There is no fallback to line rules and no skip.
- **The section.** The first top-level (`level == 0`) `h2` heading whose text is exactly `Migration Guide`. It ends at the next top-level `h1` or `h2`, in either ATX or setext form. A heading inside a blockquote or list neither opens nor ends it.
- **An anchor** is either of these, in the section, with text that matches `CURSOR_WORD_RE` (case-sensitive):
  - a top-level heading of level 3 to 6;
  - a paragraph, top-level or with only list containers around it, whose first non-empty inline token opens a `**` strong span. Only the text inside that span counts.
- **What counts as text.** `text` and `code_inline` children, with a soft or hard break read as a space. An image's alt text and `html_inline` never count.
- **Kept deliberately:** anchors stay as strict as today. `__bold__`, an anchor in a blockquote and a heading inside a list do not count. A wrong guess here is a false FAIL.
- **Kept unchanged:** the refusal of the eight line separators (`check_line_breaks`). No check is removed or weakened.
- **The job.** `release-docs-gate` installs a new, small lock, `ci/requirements-release.txt` (input `ci/requirements-release.in`, holding `markdown-it-py`), with the project's exact install form: `--require-hashes --only-binary=:all:`. The name has no hyphen after `requirements-`, because `test_ci_hash_pins.py` requires `ci/requirements-[a-z]+\.txt`. The heavy CI lock is not reused: this job needs two pure-Python packages.
- **Versions.** `markdown-it-py` and `mdurl` stay at the versions of `ci/requirements-ci.txt` (4.2.0 and 0.1.2), with the same cut-off (`--exclude-newer 2026-10-22T12:00:00Z`), so no new package version enters the project. A test enforces the match.
- **Local runs.** `CONTRIBUTING.md` step 4 of the release steps names the install. A developer's system package may be another version; the job's locked run is the one that decides.
- **No knowledge edit**, so no regeneration and no root refresh. `orchestrator.md:136` still says to run the gate locally, and the gate's own error tells a reader what to install. Report any knowledge text that the change makes false, and do not edit it.

## Task Decomposition

1. **T739** (devops-engineer): implement the design.
   - **Reproduce first.** Add the tests below and see the false passes fail on the old code before changing the gate.
   - **Remove the replaced code.** `strip_hidden_markdown`, `html_block_opening`, `_filler_lines`, the HTML block and fence patterns, and the item patterns go if nothing else uses them. Check with a search first.
   - **Tests in `tests/functional/test_verify_release_docs.py`,** with the rendered result in mind:
     - **Must now be False:** the review's `<!-->` and `<?>` shapes; residual (b) in its fence form and its non-fence form (`- a`, `  <!--`, `x`, `<? -->`, blank, anchor, `?>`); SEC-T738-01 in its fence and `<?` forms; the wrong-section routes of SEC-T738-03 (`x <!-->` and `x <!--`, then `## Other`, `-->`, blank, anchor); SEC-T731-08's section ends (a setext `Next` over `---`, ` ## Next`, `##\tNext`); an anchor that only an image's alt text or an inline comment names.
     - **Must be True:** a real anchor after `<!-->` and after `<?>`; SEC-T738-03's false FAIL (`x <!-->`, blank, a level 3 heading naming Cursor, blank, `-->`); a plain heading; a bold lead; a list-form lead; the real `docs/releases/v9.0.0.md`.
     - **Flip** `test_the_known_false_passes_named_in_the_docstrings` to assert the wanted result, under a new name.
     - **Every existing shape** keeps its result, or appears in your report as a change, with the reason and what `markdown-it-py` renders. Batch G's deliberate false FAILs may change: `Some text`, `### M-3 ...` is a real heading, and so is `## Migration Guide <!-- x -->`.
     - **The parser missing:** with `markdown_it` unavailable, `main()` exits 1 with the clear error and no traceback, on a tree with no Cursor pointer as well. Parser-dependent tests follow the pattern of `tests/functional/test_publish_release_t716.py:79-85`: fail when `CI` is set, skip otherwise.
   - **Tests in `tests/functional/test_ci_hash_pins.py`:** register the new lock; pin that `release-docs-gate` installs it before the gate runs, in the exact form; pin that the two packages match the CI lock's versions. Each with a mutation that makes it fail.
   - **Rewrite the claims (SEC-T738-04).** The `--help` text (`MIGRATION_POINTER_HELP`), the module comments and the docstrings describe the parser, and drop the blank-line rule. They state what stays open:
     - the gate reads CommonMark, and GitLab's renderer may differ, for example on front matter at the start of a document **(unverified)**;
     - raw HTML around an anchor, such as `<details>` or `<div hidden>` followed by a blank line, is not modelled, so such an anchor counts because CommonMark parses it as live;
     - `install.sh` rules are per line and do not defend against a crafted script (the plain newline part of SEC-T738-02).
   - **Documents.** `docs/wiki/mcp-pin-bump-checklist.md` § CI Python lock files gains the new lock, and `CONTRIBUTING.md` the local install.
   - **Prove the job as far as an MR can.** Validate the CI file with the lint tool. In a fresh virtual environment, install `ci/requirements-release.txt` in the job's exact form and run the gate on the real tree. Report whether the wheels are pure Python, which is what makes them safe on the musl image.
   - *Acceptance:*
     - the listed shapes give the listed results, on both `markdown-it-py` 4.2.0 and the local 3.0.0;
     - reverting the parser's section end, the anchor's container rule, the parser check in `main()`, or the job's install step each makes a test fail (report the runs);
     - `python3 scripts/verify-release-docs.py --tag v9.0.0` passes;
     - the old and new `has_cursor_migration_item` are compared on tracked Markdown files that hold a `## Migration Guide` section, outside `tests/golden/`, and any difference is reported;
     - all gates and the full suite pass, with `CI=true` after `npm ci --ignore-scripts --prefix ci/js --no-audit --no-fund`.

A Security Engineer then reviews the change, including the supply chain of the new install in a tag pipeline.

## Not changed in this plan

- **SEC-T738-02's carriage return and SEC-T738-06.** They do not depend on the parser. The other ids of batch N stay as they are too.
- **`tests/golden/**`, `scripts/scorecard.py`, `implementation/knowledge/` and the root install.**

## Not verifiable before the next tag

`release-docs-gate` runs only in a tag pipeline, so no MR pipeline runs the new install. The next register's checklist must say to watch it in the next release, or in a release-candidate tag.

## Constraints

- Subagents never merge, tag or release. The orchestrator merges on `mergeable` with a green pipeline and a pinned sha.
- Never open `tests/golden/held-out/`; exclude it from recursive searches (`--exclude-dir=held-out`). Read no `.env*` or credential file.

## Outcome (2026-11-05)

- **T739 is done.** The gate reads the Migration Guide with `markdown-it-py`, and `release-docs-gate` installs `ci/requirements-release.txt`, which pins `markdown-it-py` 4.2.0 and `mdurl` 0.1.2 with the CI lock's hashes. Without the parser, every gate run exits 1 with the install command. Fourteen names of the old logic are gone.
- **The orchestrator's check.** About 45 shapes compared with the rendered HTML gave identical results on 3.0.0 and 4.2.0, and the real tree passes after a clean install from the lock. The review's Metadata has the detail. T739 reports 0 differences between old and new on the 17 tracked files that hold the section, and the install and the gate in the pinned image under Docker. The orchestrator did not re-run those two.
- **Security review.** `docs/artifacts/security-review-t739-gate-parser-v1.md` gives CONDITIONAL_PASS, and that record meets its one condition. 0 CRITICAL, 0 HIGH, 0 MEDIUM.
  - **Closed:** SEC-T731-08, SEC-T731-09(b), SEC-T738-01, -03, -04.
  - **Still tracked:** SEC-T738-02, -06.
  - **New and tracked until the next register:** SEC-T739-01 to -09. By the user's LOW policy ("Track LOW items as debt, stop chasing (Recommended)"), none is folded in here.
- **So the false-pass group is smaller, not gone.** SEC-T739-01, -02, -03 and -04 are routes that remain for the Cursor check. SEC-T739-07 is the same class in the verdict's placeholder check: the orchestrator confirmed that three crafted shapes pass with `- Status: pending` in place. Plan-136 kept that check on line rules on purpose, and it needs its own plan.
- **Rulings on what T739 left open.**
  - **The order in `main()`** stands: "first, on every run" means gate runs. The review agrees.
  - **`parse_arguments`,** extracted to keep `main` under the limit, stands.
  - **No knowledge edit.** The bare gate commands are not false, and the gate names the install, so there is no root refresh. The review lists them; `CONTRIBUTING.md` lines 405 and 436 are in SEC-T739-08.
- **For the next release, and the next register's checklist:**
  - **Watch `release-docs-gate` in the first tag pipeline.** No MR pipeline runs its install. A release candidate would prove it first.
  - **A regeneration of `ci/requirements-ci.txt`** now needs `ci/requirements-release.txt` too; a test enforces the match.
  - **Register v7 § 6.2 item 7** is partly out of date: the blank-line rule for the Cursor item is gone, and `## Migration Guide <!-- x -->` now counts.
- **A first pipeline failed, and what it showed.** Pipeline 3031259271 failed `unit-tests` on `test_a_long_tag_line_does_not_slow_the_gate`: 1.23 s against a limit of 1.0 s. All local runs had passed, and the review had warned the test could flake on a loaded runner. The limit came from the old regex, so the orchestrator raised it to 5.0 s, which still catches a hang. The test was not skipped and its inputs did not change.
- **TD-T739-01 (new, tracked until the next register; the orchestrator's id, not graded by a reviewer).** Measuring that failure showed the parser scales worse than linearly on a line of many attributes, `<a` followed by ` x="y"` repeated, on 3.0.0: 0.059 s, 0.141 s, 0.376 s and 1.423 s at 10000, 20000, 40000 and 80000 repeats. Other long-line shapes tried (an unclosed tag, `<`, `[`) stayed about linear. Only a crafted document in the repository reaches it, and the cost is job time, so it is not a false PASS. A fix would be a limit on line or document length in the gate. The locked 4.2.0 was not measured.
- **Disclosed.** T739 ran the pinned Python image in a throwaway Docker container for the extra proof, and removed `/tmp/emage-install-gh-njpx74_h`, which its own killed suite run had left. It changed no running container.
- **Token use against budget** (the harness's counts, which include context):

  | Task | Used | Budget |
  |---|---|---|
  | T739 | about 185k | 90k |
  | Security review | about 193k | 60k |
