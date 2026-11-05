# plan-135 — Batch N, two gate fixes before the next tag

**Created:** 2026-11-05
**Based on:**
- `docs/artifacts/tracked-debt-register-v7.md` § 5, batch N.
- `docs/artifacts/security-review-t730-t732-batch-g-v1.md` § 4, which has the findings and the reviewer's fixes.
- The user's answer of 2026-11-05, verbatim: "N two go". The question named SEC-T731-07 and SEC-T731-09(a), the two small fixes the tech lead advised before the next tag.

**Scopes:** `T738`.

## Goal

The next release runs `scripts/verify-release-docs.py`. Close two false PASS routes in that gate. Both need a crafted file, so neither is urgent, and both fixes are small.

## Task Decomposition

1. **T738** (devops-engineer): fix both findings in `scripts/verify-release-docs.py`, with tests in `tests/functional/test_verify_release_docs.py`. For each fix, add the test first and confirm it fails on the old code.
   - **SEC-T731-07.** `scripts/install.sh` is outside the line-separator refusal, so `docs/releases/v9.0.0.md<U+2028>Cursor` on one shell line drops the Cursor requirement.
     - Add `INSTALL_SH` to the `check_line_breaks` call in `main()`. Today `install.sh` holds none of the refused characters, so the real tree must still pass.
     - The error text says "a line separator that Markdown does not treat as a line end", which is wrong for a shell script. Reword it to fit both kinds of file, keep the rule that it reports only the code point and never the character, and re-pin the test.
     - Test through `main()` or its real call order, not only by calling `check_line_breaks` with a hand-built list: a crafted `install.sh` must make the gate fail.
   - **SEC-T731-09(a).** CommonMark's end condition for an HTML block is searched on the whole start line, so `<!-->` and `<?>` close on their own line. The gate searches from the end of the start match, stays open, and so can hide too much.
     - Search the whole line. Remove the search-start value from `html_block_opening` if nothing else needs it, and correct the comment above `HTML_BLOCK_RULES` that states the old rule.
     - Tests: both reviewer shapes, `<!-->` and `<?>`, followed by an anchor as in review § 4, must now fail the Cursor check. A comment that spans lines and a block with its end on the start line must keep working.
     - Compare the new behaviour with `markdown-it-py` (in `ci/requirements-ci.in`) for these shapes, if it is installed, and report the result. Do not make the gate depend on it.
   - **The two claims.** Review § 4 says to correct them either way. In `html_block_opening` ("a false FAIL, never a false PASS") and `has_cursor_migration_item` ("a wrong guess is a false FAIL"), state only what holds, and name residual (b): the gate can pair two fences that CommonMark does not, as in the review's `- a` list shape, so a crafted document can still hide too much. Do not add `markdown-it-py` to the gate.
   - *Acceptance:*
     - each new test fails on the old code and passes on the new, and reverting either fix makes a test fail (report the runs);
     - `python3 scripts/verify-release-docs.py --tag v9.0.0` still passes on the real tree;
     - all gates and the full suite pass, with `CI=true` after `npm ci --ignore-scripts --prefix ci/js --no-audit --no-fund`.

A Security Engineer then reviews the fix.

## Not changed in this plan

- **The other nine ids of batch N**, and residual (b) of SEC-T731-09 beyond naming it. The user's answer covers these two fixes.
- **`implementation/knowledge/`, the root install and `tests/golden/**`.**

## Constraints

- Subagents never merge, tag or release. The orchestrator merges on `mergeable` with a green pipeline and a pinned sha.
- Never open `tests/golden/held-out/`; exclude it from recursive searches (`--exclude-dir=held-out`). Read no `.env*` or credential file.

## Outcome (2026-11-05)

- **T738 is done.** `scripts/verify-release-docs.py` now refuses the eight line separators in `scripts/install.sh`, and searches an HTML block's end on the whole start line.
- **The orchestrator's check.** A separate comparison with `markdown-it-py` 3.0.0 confirms the change on the old and new code; the table is in the review's Metadata. The real tree still passes. T738 reports that the old and new functions agree on all 2250 tracked Markdown files outside the held-out set; the orchestrator did not re-run that comparison.
- **Security review.** `docs/artifacts/security-review-t738-batch-n-two-v1.md` gives CONDITIONAL_PASS, and that record meets its one condition. 0 CRITICAL, 0 HIGH, 0 MEDIUM. Of 9 LOW findings, 3 are resolved and 6 are tracked until the next register: SEC-T731-09(b) and SEC-T738-01 to -04, -06.
- **A further false PASS route.** T738 found SEC-T738-01, and the review extended it with the wrong-section route of SEC-T738-03 and a non-fence form of (b). All are older than this plan and need a crafted file. The orchestrator confirmed each with the parser. So "before the next tag" closes the two known shapes, not the class.
- **Open for the user:** whether to use `markdown-it-py` in the gate, which would close that class at the cost of a gate dependency. No decision is made here.
- **Rulings.**
  - **SEC-T738-05** is applied with the reviewer's wording, because it corrects claims this change wrote. This is an orchestrator edit after the review, and it was not re-reviewed.
  - **The characterisation test** stays, as the review allows.
  - **The acceptance sentence** "each new test fails on the old code" is read as the review reads it: the tests that guard a fix.
- **A slip, disclosed to the user.** While preparing T738, a recursive search over `tests/` by the orchestrator scanned `tests/golden/held-out/` and printed one case's path. The file was not opened, and the id is not recorded anywhere. The orchestrator's notes now require `--exclude-dir=held-out`, and T738's brief says the same.
- **Token use against budget** (the harness's counts, which include context):

  | Task | Used | Budget |
  |---|---|---|
  | T738 | about 112k | 50k |
  | Security review | about 124k | 40k |
